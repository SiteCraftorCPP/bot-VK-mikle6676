#!/bin/bash
# Скрипт для обновления PHOTO_ATTACHMENT на VPS

cd /opt/bot-vk-mikle6676

# Устанавливаем сервис (если не установлен)
if [ ! -f "/etc/systemd/system/bot-vk.service" ]; then
    echo "📦 Устанавливаю сервис..."
    cp bot.service /etc/systemd/system/bot-vk.service
    systemctl daemon-reload
    systemctl enable bot-vk.service
    echo "✅ Сервис установлен"
fi

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

# Перезапускаем сервис
echo "🔄 Перезапускаю бота..."
systemctl restart bot-vk.service
sleep 2
systemctl status bot-vk.service --no-pager
