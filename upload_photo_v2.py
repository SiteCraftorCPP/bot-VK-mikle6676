#!/usr/bin/env python3
"""
Альтернативный способ загрузки фото через документы
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
    print("❌ GROUP_TOKEN не найден")
    sys.exit(1)

bot = Bot(token=GROUP_TOKEN)

async def upload_photo_alternative(file_path: str):
    """Пробуем загрузить через документы или другой метод"""
    try:
        # Метод 1: Через documents.getMessagesUploadServer
        print("🔄 Пробую загрузить через documents...")
        try:
            upload_url = await bot.api.docs.get_messages_upload_server(type="photo", peer_id=2000000001)
            print(f"✅ URL получен через docs")
            
            async with aiohttp.ClientSession() as session:
                with open(file_path, 'rb') as f:
                    data = aiohttp.FormData()
                    data.add_field('file', f, filename=os.path.basename(file_path))
                    
                    async with session.post(upload_url.upload_url, data=data) as resp:
                        upload_result = await resp.json()
            
            doc = await bot.api.docs.save(
                file=upload_result['file'],
                title='photo1.jpg'
            )
            
            attachment = f"doc{doc[0].owner_id}_{doc[0].id}"
            print(f"✅ Загружено через docs: {attachment}")
            return attachment
        except Exception as e1:
            print(f"❌ Метод docs не сработал: {e1}")
        
        # Метод 2: Прямая загрузка через photos.getWallUploadServer
        print("🔄 Пробую загрузить через wall...")
        try:
            upload_url = await bot.api.photos.get_wall_upload_server()
            
            async with aiohttp.ClientSession() as session:
                with open(file_path, 'rb') as f:
                    data = aiohttp.FormData()
                    data.add_field('photo', f, filename=os.path.basename(file_path))
                    
                    async with session.post(upload_url.upload_url, data=data) as resp:
                        upload_result = await resp.json()
            
            photo = await bot.api.photos.save_wall_photo(
                photo=upload_result['photo'],
                server=upload_result['server'],
                hash=upload_result['hash']
            )
            
            attachment = f"photo{photo[0].owner_id}_{photo[0].id}"
            print(f"✅ Загружено через wall: {attachment}")
            return attachment
        except Exception as e2:
            print(f"❌ Метод wall не сработал: {e2}")
        
        # Метод 3: Стандартный метод messages
        print("🔄 Пробую стандартный метод messages...")
        upload_url = await bot.api.photos.get_messages_upload_server()
        
        async with aiohttp.ClientSession() as session:
            with open(file_path, 'rb') as f:
                data = aiohttp.FormData()
                data.add_field('photo', f, filename=os.path.basename(file_path))
                
                async with session.post(upload_url.upload_url, data=data) as resp:
                    upload_result = await resp.json()
        
        photo = await bot.api.photos.save_messages_photo(
            photo=upload_result['photo'],
            server=upload_result['server'],
            hash=upload_result['hash']
        )
        
        attachment = f"photo{photo[0].owner_id}_{photo[0].id}"
        print(f"✅ Загружено: {attachment}")
        return attachment
        
    except Exception as e:
        print(f"❌ Все методы не сработали: {e}")
        print("\n💡 Возможные причины:")
        print("   1. Токен не имеет права 'photos' - проверьте права токена")
        print("   2. Токен группы может иметь ограничения")
        print("   3. Попробуйте загрузить фото вручную в VK и получить attachment")
        return None

async def update_env(attachment):
    """Обновляет .env"""
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
        print(f"💡 Добавьте вручную: PHOTO_ATTACHMENT={attachment}")
        return False

async def main():
    if len(sys.argv) < 2:
        print("Использование: python3 upload_photo_v2.py <путь_к_фото>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"❌ Файл {file_path} не найден!")
        sys.exit(1)
    
    print("=" * 50)
    print("Загрузка фото (пробую разные методы)")
    print("=" * 50)
    
    attachment = await upload_photo_alternative(file_path)
    
    if attachment:
        await update_env(attachment)
        print("\n✅ Готово!")
    else:
        print("\n❌ Не удалось загрузить. Попробуйте:")
        print("   1. Проверить права токена в настройках группы")
        print("   2. Загрузить фото вручную в VK и получить attachment")

if __name__ == "__main__":
    asyncio.run(main())
