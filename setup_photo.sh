#!/bin/bash
# Скрипт для загрузки фото на VPS и получения attachment

cd /opt/bot-vk-mikle6676

# Проверяем наличие фото
if [ ! -f "Image/photo1.jpg" ]; then
    echo "Фото не найдено в Image/photo1.jpg"
    echo "Пожалуйста, скопируйте фото на VPS:"
    echo "scp Image/photo1.jpg root@85.239.35.34:/opt/bot-vk-mikle6676/Image/"
    exit 1
fi

# Активируем venv и загружаем фото
source venv/bin/activate
python3 upload_photo.py Image/photo1.jpg
deactivate

# Получаем attachment из вывода (последняя строка с PHOTO_ATTACHMENT=)
ATTACHMENT=$(python3 upload_photo.py Image/photo1.jpg 2>&1 | grep "PHOTO_ATTACHMENT=" | sed 's/.*PHOTO_ATTACHMENT=//')

if [ -z "$ATTACHMENT" ]; then
    echo "Не удалось получить attachment. Запустите вручную:"
    echo "source venv/bin/activate"
    echo "python3 upload_photo.py Image/photo1.jpg"
    exit 1
fi

# Обновляем .env
if [ -f ".env" ]; then
    # Удаляем старую строку PHOTO_ATTACHMENT если есть
    sed -i '/^PHOTO_ATTACHMENT=/d' .env
    # Добавляем новую
    echo "PHOTO_ATTACHMENT=$ATTACHMENT" >> .env
    echo "✅ .env обновлен: PHOTO_ATTACHMENT=$ATTACHMENT"
else
    echo "❌ Файл .env не найден!"
    exit 1
fi
