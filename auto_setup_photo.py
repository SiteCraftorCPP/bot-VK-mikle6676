#!/usr/bin/env python3
"""
Автоматическая загрузка фото и обновление .env
"""
import os
import asyncio
import sys
from pathlib import Path
from vkbottle import Bot
import aiohttp

# Читаем токен из .env
env_path = Path(__file__).parent / ".env"
GROUP_TOKEN = None

if env_path.exists():
    with open(env_path, 'r', encoding='utf-8-sig') as f:
        for line in f:
            line = line.strip()
            if line.startswith('GROUP_TOKEN='):
                GROUP_TOKEN = line.split('=', 1)[1]
                break

if not GROUP_TOKEN:
    print("❌ GROUP_TOKEN не найден в .env")
    sys.exit(1)

bot = Bot(token=GROUP_TOKEN)

async def upload_photo_from_url_or_create():
    """Загружает фото в VK"""
    try:
        # Получаем URL для загрузки
        upload_url = await bot.api.photos.get_messages_upload_server()
        
        # Создаем простое тестовое изображение (1x1 пиксель PNG)
        import base64
        # Минимальный валидный PNG (1x1 пиксель, прозрачный)
        png_data = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==')
        
        # Загружаем через API
        async with aiohttp.ClientSession() as session:
            data = aiohttp.FormData()
            data.add_field('photo', png_data, filename='photo.png', content_type='image/png')
            
            async with session.post(upload_url.upload_url, data=data) as resp:
                upload_result = await resp.json()
        
        # Сохраняем фото
        photo = await bot.api.photos.save_messages_photo(
            photo=upload_result['photo'],
            server=upload_result['server'],
            hash=upload_result['hash']
        )
        
        attachment = f"photo{photo[0].owner_id}_{photo[0].id}"
        return attachment
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

async def main():
    print("🔄 Загружаю фото в VK...")
    attachment = await upload_photo_from_url_or_create()
    
    if attachment:
        print(f"✅ Фото загружено: {attachment}")
        
        # Обновляем .env
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8-sig') as f:
                lines = f.readlines()
            
            updated = False
            with open(env_path, 'w', encoding='utf-8') as f:
                for line in lines:
                    if line.startswith('PHOTO_ATTACHMENT='):
                        f.write(f'PHOTO_ATTACHMENT={attachment}\n')
                        updated = True
                    else:
                        f.write(line)
                
                if not updated:
                    f.write(f'PHOTO_ATTACHMENT={attachment}\n')
            
            print(f"✅ .env обновлен: PHOTO_ATTACHMENT={attachment}")
        else:
            print(f"⚠️ Файл .env не найден. Добавьте вручную: PHOTO_ATTACHMENT={attachment}")
    else:
        print("❌ Не удалось загрузить фото")

if __name__ == "__main__":
    asyncio.run(main())
