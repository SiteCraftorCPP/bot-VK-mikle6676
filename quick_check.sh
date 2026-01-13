#!/bin/bash
# Быстрая проверка настроек VK

cd /opt/bot-vk-mikle6676

echo "📥 Обновляю код из Git..."
git pull

echo ""
echo "🔍 Запускаю проверку настроек..."
source venv/bin/activate
python3 check_vk_settings.py
deactivate
