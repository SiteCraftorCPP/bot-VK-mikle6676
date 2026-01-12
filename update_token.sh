#!/bin/bash
# Скрипт для обновления токена в .env

cd /opt/bot-vk-mikle6676

echo "⏸️ Останавливаю бота..."
systemctl stop bot-vk.service

echo ""
echo "📝 Текущий токен в .env:"
grep "^GROUP_TOKEN=" .env | sed 's/GROUP_TOKEN=\(.\{20\}\).*/\1.../'

echo ""
echo "✏️ Откройте .env для редактирования:"
echo "   nano .env"
echo ""
echo "📋 Инструкция по получению нового токена:"
echo "   1. Откройте https://vk.com/atservice_official"
echo "   2. Управление → Настройки → Работа с API"
echo "   3. Создайте новый токен с правами: messages, photos"
echo "   4. Скопируйте токен и замените GROUP_TOKEN= в .env"
echo ""
echo "После обновления токена запустите:"
echo "   systemctl start bot-vk.service"
echo "   systemctl status bot-vk.service"
