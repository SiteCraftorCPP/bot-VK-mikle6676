"""
Скрипт для загрузки фото в VK из URL и получения attachment строки
"""
import os
import asyncio
import sys
import tempfile
from pathlib import Path
from vkbottle import Bot
import aiohttp

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
    raise ValueError(f"GROUP_TOKEN не установлен в .env файле. Проверьте файл: {env_path}")

bot = Bot(token=GROUP_TOKEN)


async def download_image(url: str, temp_file: str):
    """Скачивает изображение по URL"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://vk.com/',
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                with open(temp_file, 'wb') as f:
                    async for chunk in resp.content.iter_chunked(8192):
                        f.write(chunk)
                return True
            else:
                print(f"❌ Ошибка скачивания: HTTP {resp.status}")
                print(f"💡 Попробуйте скачать изображение вручную и использовать upload_photo.py")
                return False


async def upload_photo_from_url(image_url: str):
    """Скачивает фото по URL, загружает в VK и возвращает attachment строку"""
    temp_file = None
    try:
        print(f"📥 Скачиваю изображение с {image_url}...")
        
        # Создаём временный файл
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        temp_file.close()
        
        # Скачиваем изображение
        if not await download_image(image_url, temp_file.name):
            return None
        
        print(f"✅ Изображение скачано: {temp_file.name}")
        print(f"🔄 Загружаю в VK...")
        
        # Получаем URL для загрузки
        upload_url = await bot.api.photos.get_messages_upload_server()
        
        # Загружаем файл
        async with aiohttp.ClientSession() as session:
            with open(temp_file.name, 'rb') as f:
                data = aiohttp.FormData()
                data.add_field('photo', f, filename='photo.jpg', content_type='image/jpeg')
                
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
        print(f"\n✅ Фото успешно загружено!")
        print(f"📎 Attachment: {attachment}")
        
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
            print(f"\n⚠️ Файл .env не найден. Добавьте вручную:")
            print(f"PHOTO_ATTACHMENT={attachment}")
        
        return attachment
        
    except Exception as e:
        print(f"❌ Ошибка при загрузке фото: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        # Удаляем временный файл
        if temp_file and os.path.exists(temp_file.name):
            os.unlink(temp_file.name)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python upload_photo_from_url.py <URL_изображения>")
        print("Пример: python upload_photo_from_url.py https://sun9-6.userapi.com/...")
        sys.exit(1)
    
    image_url = sys.argv[1]
    
    asyncio.run(upload_photo_from_url(image_url))
