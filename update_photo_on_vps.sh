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

# Проверяем, установлен ли сервис
if systemctl list-unit-files | grep -q "bot-vk.service"; then
    echo "🔄 Перезапускаю бота..."
    systemctl restart bot-vk.service
    systemctl status bot-vk.service --no-pager
elif systemctl list-unit-files | grep -q "bot.service"; then
    echo "🔄 Перезапускаю бота..."
    systemctl restart bot.service
    systemctl status bot.service --no-pager
else
    echo "⚠️ Сервис не найден. Устанавливаю..."
    if [ -f "bot.service" ]; then
        cp bot.service /etc/systemd/system/bot-vk.service
        systemctl daemon-reload
        systemctl enable bot-vk.service
        systemctl start bot-vk.service
        systemctl status bot-vk.service --no-pager
    else
        echo "❌ Файл bot.service не найден!"
        echo "💡 Установите сервис вручную:"
        echo "   cp bot.service /etc/systemd/system/bot-vk.service"
        echo "   systemctl daemon-reload"
        echo "   systemctl enable bot-vk.service"
        echo "   systemctl start bot-vk.service"
    fi
fi
