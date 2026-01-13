#!/usr/bin/env python3
"""Проверка настроек VK и токена"""
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
        group = groups[0]
        print(f"✅ Токен валиден")
        print(f"📋 Группа: {group.name}")
        print(f"🆔 ID группы: {group.id}")
        
        # Проверяем настройки Long Poll
        try:
            long_poll = await bot.api.groups.get_long_poll_server(group_id=group.id)
            print(f"\n✅ Long Poll API настроен")
            print(f"   Server: {long_poll.server}")
            print(f"   Key: {long_poll.key[:20]}...")
            print(f"   Ts: {long_poll.ts}")
        except Exception as e:
            print(f"\n❌ Ошибка получения Long Poll: {e}")
        
        # Проверяем права токена
        print(f"\n📋 Проверка прав токена:")
        try:
            await bot.api.photos.get_messages_upload_server()
            print("   ✅ Права на загрузку фото: есть")
        except Exception as e:
            print(f"   ❌ Права на загрузку фото: нет ({e})")
        
        try:
            await bot.api.messages.send(peer_id=group.id, message="test", random_id=0)
            print("   ✅ Права на отправку сообщений: есть")
        except Exception as e:
            print(f"   ⚠️ Права на отправку сообщений: ограничены ({e})")
        
        print(f"\n📝 Инструкция по настройке:")
        print(f"   1. Откройте https://vk.com/atservice_official")
        print(f"   2. Управление → Настройки → Работа с API")
        print(f"   3. Убедитесь, что Long Poll API включен")
        print(f"   4. В разделе 'События' включите:")
        print(f"      ✅ Входящее сообщение")
        print(f"      ✅ Разрешение на получение (MESSAGE_ALLOW) - ОБЯЗАТЕЛЬНО!")
        print(f"   5. Управление → Настройки → Сообщения")
        print(f"      ✅ Сообщения сообщества - включены")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(check())
