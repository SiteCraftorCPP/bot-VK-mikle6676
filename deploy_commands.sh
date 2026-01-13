#!/bin/bash
# Команды для деплоя на новой VPS
# Выполняйте по порядку

# 1. Обновление системы
apt update && apt upgrade -y

# 2. Установка Python и pip
apt install -y python3 python3-pip python3-venv git

# 3. Создание директории для бота
mkdir -p /opt/bot-vk-mikle6676
cd /opt/bot-vk-mikle6676

# 4. Клонирование репозитория
git clone https://github.com/SiteCraftorCPP/bot-VK-mikle6676.git .

# 5. Установка зависимостей
pip3 install -r requirements.txt

# 6. Создание .env файла (замените значения на свои!)
cat > .env << EOF
GROUP_TOKEN=ваш_токен_группы_vk
ADMIN_IDS=782498140,325219251
PHOTO_ATTACHMENT=ваш_photo_attachment
EOF

# 7. Установка systemd сервиса
cp bot.service /etc/systemd/system/bot-vk.service
sed -i "s|/opt/bot-vk-mikle6676|$(pwd)|g" /etc/systemd/system/bot-vk.service

# 8. Перезагрузка systemd и запуск
systemctl daemon-reload
systemctl enable bot-vk.service
systemctl start bot-vk.service

# 9. Проверка статуса
systemctl status bot-vk.service

# 10. Просмотр логов (в отдельном терминале)
# journalctl -u bot-vk.service -f
