#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Скрипт для проверки разрешения на отправку сообщений"""
import asyncio
import sys
import io
from vkbottle import Bot
from pathlib import Path
import os

# Устанавливаем UTF-8 для консоли Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

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
    print("GROUP_TOKEN не найден")
    exit(1)

bot = Bot(token=GROUP_TOKEN)

async def test_send(user_id: int):
    """Пытается отправить тестовое сообщение пользователю"""
    try:
        print(f"Попытка отправить сообщение пользователю {user_id}...")
        result = await bot.api.messages.send(
            peer_id=user_id,
            message="Тестовое сообщение для проверки разрешения",
            random_id=0
        )
        print(f"[OK] Сообщение отправлено успешно! ID: {result}")
        print("Разрешение есть - пользователь может получать сообщения")
    except Exception as e:
        error_msg = str(e)
        print(f"[ERROR] Ошибка отправки: {error_msg}")
        
        if "Can't send messages" in error_msg or "without permission" in error_msg:
            print("\n[WARN] НЕТ РАЗРЕШЕНИЯ на отправку сообщений")
            print("VK должен показать системное уведомление при следующей попытке")
            print("\nЧтобы проверить системное уведомление:")
            print("1. Пользователь должен отозвать разрешение в настройках VK")
            print("2. Или используйте другой аккаунт, который еще не разрешал")
        else:
            print(f"Другая ошибка: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Использование: python test_permission.py <user_id>")
        print("Пример: python test_permission.py 782498140")
        sys.exit(1)
    
    user_id = int(sys.argv[1])
    asyncio.run(test_send(user_id))
