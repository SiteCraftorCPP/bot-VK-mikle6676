#!/bin/bash
# Установка и запуск сервиса бота

cd /opt/bot-vk-mikle6676

# Копируем сервис
cp bot.service /etc/systemd/system/bot-vk.service

# Перезагружаем systemd
systemctl daemon-reload

# Включаем автозапуск
systemctl enable bot-vk.service

# Запускаем
systemctl start bot-vk.service

# Показываем статус
systemctl status bot-vk.service
