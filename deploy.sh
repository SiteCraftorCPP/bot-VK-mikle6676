#!/bin/bash

# Скрипт для деплоя бота на VPS

echo "Обновление кода из Git..."
git pull origin main

echo "Активация виртуального окружения и установка зависимостей..."
source venv/bin/activate
pip install -r requirements.txt
deactivate

echo "Перезапуск сервиса..."
sudo systemctl restart bot-vk.service

echo "Проверка статуса..."
sudo systemctl status bot-vk.service

echo "Готово!"
