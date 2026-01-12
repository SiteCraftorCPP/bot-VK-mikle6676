# Инструкция по деплою на VPS

## Подключение к VPS

```bash
ssh root@85.239.35.34
```

## Команды для деплоя (выполняйте по порядку)

### 1. Обновление системы
```bash
apt update && apt upgrade -y
```

### 2. Установка необходимых пакетов
```bash
apt install -y python3 python3-pip python3-venv git
```

### 3. Создание директории и клонирование репозитория
```bash
mkdir -p /opt/bot-vk-mikle6676
cd /opt/bot-vk-mikle6676
git clone https://github.com/SiteCraftorCPP/bot-VK-mikle6676.git .
```

### 4. Создание виртуального окружения и установка зависимостей
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
```

### 5. Создание .env файла
```bash
nano .env
```

Вставьте следующее (замените на свои значения):
```
GROUP_TOKEN=ваш_токен_группы_vk
ADMIN_IDS=782498140,325219251
PHOTO_ATTACHMENT=ваш_photo_attachment
```

Сохраните: `Ctrl+O`, `Enter`, `Ctrl+X`

### 6. Установка systemd сервиса
```bash
cp bot.service /etc/systemd/system/bot-vk.service
sed -i "s|/opt/bot-vk-mikle6676|$(pwd)|g" /etc/systemd/system/bot-vk.service
systemctl daemon-reload
systemctl enable bot-vk.service
systemctl start bot-vk.service
```

### 7. Проверка работы
```bash
systemctl status bot-vk.service
```

### 8. Просмотр логов
```bash
journalctl -u bot-vk.service -f
```

## Полезные команды

**Перезапуск бота:**
```bash
systemctl restart bot-vk.service
```

**Остановка бота:**
```bash
systemctl stop bot-vk.service
```

**Обновление кода:**
```bash
cd /opt/bot-vk-mikle6676
git pull
pip3 install -r requirements.txt
systemctl restart bot-vk.service
```
