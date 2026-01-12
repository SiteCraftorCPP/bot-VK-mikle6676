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
cat > .env << 'EOF'
GROUP_TOKEN=vk1.a.VlnzNFssC4gf-KhyP0IIWhNE0NU1DT4Cxm15aafDvWyXhLtyiBuD5yOVE33Swc2GuEvkS_9uQCTIFNXhcF6GQtQaqQzNYfw8eZmkpzGOlEVkbBRWAS98F0-5WpaGDweIt9Hdd4sbEkc2MSikyjHm40uW4jPujk8SqybMxvvt-C5V3frv2GvnfslKOOa5FQqNMipyJx7rSCmq22RiGx1kXA
ADMIN_IDS=782498140,325219251
PHOTO_ATTACHMENT=
EOF
```

### 6. Копирование фото на VPS (с локального компьютера)
```bash
# Выполните на ЛОКАЛЬНОМ компьютере:
scp Image/photo1.jpg root@85.239.35.34:/opt/bot-vk-mikle6676/Image/
```

Или создайте папку и загрузите фото вручную:
```bash
# На VPS:
mkdir -p Image
# Затем загрузите фото через SFTP или скопируйте другим способом
```

### 7. Загрузка фото в VK и получение attachment
```bash
cd /opt/bot-vk-mikle6676
source venv/bin/activate
python3 upload_photo.py Image/photo1.jpg
deactivate
```

Скопируйте полученный `PHOTO_ATTACHMENT=photo...` и обновите `.env`:
```bash
nano .env
# Замените PHOTO_ATTACHMENT= на полученное значение
```

Или используйте автоматический скрипт:
```bash
chmod +x setup_photo.sh
./setup_photo.sh
```

### 8. Установка systemd сервиса
```bash
cp bot.service /etc/systemd/system/bot-vk.service
sed -i "s|/opt/bot-vk-mikle6676|$(pwd)|g" /etc/systemd/system/bot-vk.service
systemctl daemon-reload
systemctl enable bot-vk.service
systemctl start bot-vk.service
```

### 9. Проверка работы
```bash
systemctl status bot-vk.service
```

### 10. Просмотр логов
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
source venv/bin/activate
pip install -r requirements.txt
deactivate
systemctl restart bot-vk.service
```
