#!/usr/bin/env python3
"""Проверка токена и прав"""
import asyncio
from vkbottle import Bot
from pathlib import Path

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
    exit(1)

bot = Bot(token=GROUP_TOKEN)

async def check():
    try:
        # Проверяем доступ к группам
        groups = await bot.api.groups.get_by_id()
        print(f"✅ Токен валиден. Группа: {groups[0].name if groups else 'N/A'}")
        
        # Проверяем права
        try:
            await bot.api.photos.get_messages_upload_server()
            print("✅ Права на загрузку фото: есть")
        except Exception as e:
            print(f"❌ Права на загрузку фото: нет ({e})")
            print("\n📝 Нужно создать новый токен с правами:")
            print("   - messages")
            print("   - photos")
            print("\nВ настройках группы -> Работа с API -> Создать токен")
            
    except Exception as e:
        print(f"❌ Токен недействителен: {e}")
        print("\n📝 Нужно создать новый токен в настройках группы VK")

asyncio.run(check())
