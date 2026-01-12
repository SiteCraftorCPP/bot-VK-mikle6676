#!/bin/bash

# Скрипт для деплоя бота на VPS

echo "Обновление кода из Git..."
git pull origin main

echo "Установка зависимостей..."
pip3 install -r requirements.txt

echo "Перезапуск сервиса..."
sudo systemctl restart bot-vk.service

echo "Проверка статуса..."
sudo systemctl status bot-vk.service

echo "Готово!"
