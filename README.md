# VK Бот для сообщества АТ СЕРВИС

Бот для автоматической обработки сообщений в VK сообществе.

## Функционал

- Автоматическое приветствие новых пользователей с фото
- Выбор типа услуги через 5 секунд (Ремонт, Обслуживание, Монтаж)
- Выбор категории услуги с подробными вариантами
- Запрос описания проблемы от пользователя
- Сбор контактных данных (имя, телефон, адрес)
- Подтверждение заявки с выбором типа обработки
- Отправка заявки администраторам с полной информацией

## Установка на VPS

### 1. Клонирование репозитория

```bash
cd /opt
git clone https://github.com/SiteCraftorCPP/bot-VK-mikle6676.git
cd bot-VK-mikle6676
```

### 2. Установка зависимостей

```bash
pip3 install -r requirements.txt
```

### 3. Настройка переменных окружения

```bash
cp env.example .env
nano .env
```

Заполните:
- `GROUP_TOKEN` - токен группы VK
- `ADMIN_IDS` - ID администраторов через запятую (например: `782498140,325219251`)
- `PHOTO_ATTACHMENT` - attachment для фото приветствия

### 4. Установка systemd сервиса

```bash
sudo cp bot.service /etc/systemd/system/bot-vk.service
sudo systemctl daemon-reload
sudo systemctl enable bot-vk.service
sudo systemctl start bot-vk.service
```

### 5. Проверка работы

```bash
sudo systemctl status bot-vk.service
sudo journalctl -u bot-vk.service -f
```

## Обновление

```bash
cd /opt/bot-vK-mikle6676
./deploy.sh
```

Или вручную:
```bash
git pull
pip3 install -r requirements.txt
sudo systemctl restart bot-vk.service
```

## Получение токена группы VK

1. Откройте сообщество VK
2. Управление сообществом → Настройки → Работа с API
3. Включите Long Poll API
4. Включите события: "Входящее сообщение" и "Разрешение на получение"
5. Создайте токен с правами: `messages` и `photos`
6. Скопируйте токен в `.env`

## Настройки бота в VK

- **Сообщения сообщества** - включены
- **Кнопка «Начать»** - опционально
- **Long Poll API** - включен
- **События**: Входящее сообщение, Разрешение на получение

## Структура проекта

```
bot-VK-mikle6676/
├── bot.py              # Основной файл бота
├── upload_photo.py     # Скрипт для загрузки фото
├── requirements.txt    # Зависимости
├── .env               # Конфигурация (не в git)
├── bot.service        # Systemd сервис
├── deploy.sh          # Скрипт деплоя
└── README.md          # Документация
```

## Логи

Просмотр логов:
```bash
sudo journalctl -u bot-vk.service -f
```

## Остановка/Запуск

```bash
sudo systemctl stop bot-vk.service
sudo systemctl start bot-vk.service
sudo systemctl restart bot-vk.service
```
