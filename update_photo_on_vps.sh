#!/bin/bash
# Скрипт для обновления PHOTO_ATTACHMENT на VPS

cd /opt/bot-vk-mikle6676

# Attachment string, полученный локально
ATTACHMENT="photo-184746682_457239108"

if [ ! -f ".env" ]; then
    echo "❌ Файл .env не найден!"
    exit 1
fi

# Обновляем .env
sed -i '/^PHOTO_ATTACHMENT=/d' .env
echo "PHOTO_ATTACHMENT=$ATTACHMENT" >> .env

echo "✅ .env обновлен: PHOTO_ATTACHMENT=$ATTACHMENT"
echo "🔄 Перезапускаю бота..."

systemctl restart bot.service
systemctl status bot.service --no-pager
