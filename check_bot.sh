#!/bin/bash
# Скрипт для проверки состояния бота

cd /opt/bot-vk-mikle6676

echo "=== 1. Статус сервиса ==="
systemctl status bot-vk.service --no-pager

echo ""
echo "=== 2. Последние логи (последние 20 строк) ==="
journalctl -u bot-vk.service -n 20 --no-pager

echo ""
echo "=== 3. Проверка .env файла ==="
if [ -f ".env" ]; then
    echo "✅ .env существует"
    echo "GROUP_TOKEN: $(grep "^GROUP_TOKEN=" .env | head -c 30)..."
    echo "ADMIN_IDS: $(grep "^ADMIN_IDS=" .env)"
    echo "PHOTO_ATTACHMENT: $(grep "^PHOTO_ATTACHMENT=" .env)"
else
    echo "❌ .env не найден!"
fi

echo ""
echo "=== 4. Проверка токена через API ==="
source venv/bin/activate
python3 check_token.py 2>&1 | tail -10
deactivate

echo ""
echo "=== 5. Процесс бота ==="
ps aux | grep "[b]ot.py" || echo "❌ Процесс не найден"

echo ""
echo "=== 6. Проверка подключения к VK ==="
echo "Запускаю тест подключения..."
source venv/bin/activate
python3 << 'PYEOF'
import asyncio
import os
from pathlib import Path
from vkbottle import Bot

env_path = Path("/opt/bot-vk-mikle6676/.env")
GROUP_TOKEN = None

if env_path.exists():
    with open(env_path, 'r', encoding='utf-8-sig') as f:
        for line in f:
            line = line.strip()
            if line.startswith('GROUP_TOKEN='):
                GROUP_TOKEN = line.split('=', 1)[1]
                break

if not GROUP_TOKEN:
    print("❌ Токен не найден")
    exit(1)

bot = Bot(token=GROUP_TOKEN)

async def test():
    try:
        groups = await bot.api.groups.get_by_id()
        print(f"✅ Подключение работает! Группа: {groups[0].name}")
        print(f"   ID группы: {groups[0].id}")
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")

asyncio.run(test())
PYEOF
deactivate
