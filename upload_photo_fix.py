#!/usr/bin/env python3
"""
Загрузка фото с проверкой токена и автоматическим обновлением .env
"""
import os
import asyncio
import sys
from pathlib import Path
from vkbottle import Bot
import aiohttp

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

async def upload_photo():
    """Загружает минимальное фото в VK"""
    try:
        print("🔄 Получаю URL для загрузки...")
        upload_url = await bot.api.photos.get_messages_upload_server()
        print(f"✅ URL получен: {upload_url.upload_url[:50]}...")
        
        # Создаем минимальный валидный PNG (1x1 пиксель)
        import base64
        # PNG 1x1 прозрачный
        png_base64 = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
        png_data = base64.b64decode(png_base64)
        
        print("🔄 Загружаю фото на сервер VK...")
        async with aiohttp.ClientSession() as session:
            data = aiohttp.FormData()
            data.add_field('photo', png_data, filename='welcome.png', content_type='image/png')
            
            async with session.post(upload_url.upload_url, data=data) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    print(f"❌ Ошибка загрузки (статус {resp.status}): {text}")
                    return None
                upload_result = await resp.json()
        
        print("🔄 Сохраняю фото в VK...")
        photo = await bot.api.photos.save_messages_photo(
            photo=upload_result['photo'],
            server=upload_result['server'],
            hash=upload_result['hash']
        )
        
        attachment = f"photo{photo[0].owner_id}_{photo[0].id}"
        print(f"✅ Фото загружено: {attachment}")
        return attachment
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("\n💡 Возможные причины:")
        print("   1. Токен недействителен - создайте новый в настройках группы")
        print("   2. Токен не имеет прав 'photos' - добавьте права при создании")
        print("   3. Long Poll API не включен - включите в настройках группы")
        return None

async def update_env(attachment):
    """Обновляет .env файл"""
    try:
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
        return True
    except Exception as e:
        print(f"❌ Ошибка обновления .env: {e}")
        print(f"💡 Добавьте вручную в .env: PHOTO_ATTACHMENT={attachment}")
        return False

async def main():
    print("=" * 50)
    print("Загрузка фото для приветственного сообщения")
    print("=" * 50)
    
    attachment = await upload_photo()
    
    if attachment:
        await update_env(attachment)
        print("\n✅ Готово! Теперь можно запускать бота.")
    else:
        print("\n❌ Не удалось загрузить фото.")
        print("\n📝 Инструкция по созданию нового токена:")
        print("   1. Откройте группу VK -> Управление")
        print("   2. Настройки -> Работа с API")
        print("   3. Long Poll API -> Включить")
        print("   4. Создать токен с правами: messages, photos")
        print("   5. Скопируйте токен в .env файл")
        print("   6. Запустите этот скрипт снова")

if __name__ == "__main__":
    asyncio.run(main())
