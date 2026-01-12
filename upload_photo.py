"""
Скрипт для загрузки фото в VK и получения attachment строки
"""
import os
import asyncio
from pathlib import Path
from vkbottle import Bot

# Читаем .env файл напрямую
env_path = Path(__file__).parent / ".env"
GROUP_TOKEN = None

if env_path.exists():
    # Используем utf-8-sig для автоматического удаления BOM
    with open(env_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('GROUP_TOKEN='):
                GROUP_TOKEN = line.split('=', 1)[1]
                break

if not GROUP_TOKEN:
    print(f"Файл .env существует: {env_path.exists()}")
    if env_path.exists():
        print(f"Содержимое файла: {open(env_path, 'rb').read()[:100]}")
    raise ValueError(f"GROUP_TOKEN не установлен в .env файле. Проверьте файл: {env_path}")

bot = Bot(token=GROUP_TOKEN)


async def upload_photo(file_path: str):
    """Загружает фото в VK и возвращает attachment строку"""
    try:
        # Получаем URL для загрузки
        upload_url = await bot.api.photos.get_messages_upload_server()
        
        # Загружаем файл
        import aiohttp
        async with aiohttp.ClientSession() as session:
            with open(file_path, 'rb') as f:
                data = aiohttp.FormData()
                data.add_field('photo', f, filename=os.path.basename(file_path))
                
                async with session.post(upload_url.upload_url, data=data) as resp:
                    upload_result = await resp.json()
        
        # Сохраняем фото
        photo = await bot.api.photos.save_messages_photo(
            photo=upload_result['photo'],
            server=upload_result['server'],
            hash=upload_result['hash']
        )
        
        # Формируем attachment строку
        attachment = f"photo{photo[0].owner_id}_{photo[0].id}"
        print(f"Фото успешно загружено!")
        print(f"Attachment: {attachment}")
        print(f"\nДобавьте в .env файл:")
        print(f"PHOTO_ATTACHMENT={attachment}")
        
        return attachment
        
    except Exception as e:
        print(f"Ошибка при загрузке фото: {e}")
        return None


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Использование: python upload_photo.py <путь_к_фото>")
        print("Пример: python upload_photo.py photo1.jpg")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"Файл {file_path} не найден!")
        sys.exit(1)
    
    asyncio.run(upload_photo(file_path))
