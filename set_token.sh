#!/bin/bash
# Скрипт для установки нового токена

cd /opt/bot-vk-mikle6676

NEW_TOKEN="vk1.a._5iP9hRsb80eBbrGy8fUrFXatUxc1T50M4rPUwwG7ixQ1LlJK5bA6T_Mr8KwrMxigoJnJQh7ASwzJGInrc45E_gUQWK7APPRx4oefJ0LDEy5cJZK_iMIH8E79f9-rv_9HjQRPZEvr7qz2gplJfY0E6sEs3nyiLnEMTqKNI3CHFi6qAOK1AZLoGw2O2KTKTwSSqgSaLkjJZt2hpWueQIl0w"

echo "🔄 Обновляю токен в .env..."

# Удаляем старую строку GROUP_TOKEN
sed -i '/^GROUP_TOKEN=/d' .env

# Добавляем новый токен в начало файла
sed -i "1iGROUP_TOKEN=$NEW_TOKEN" .env

echo "✅ Токен обновлен"
echo "🔄 Перезапускаю бота..."

systemctl restart bot-vk.service
sleep 2
systemctl status bot-vk.service --no-pager
