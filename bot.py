import asyncio
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from enum import Enum
from dotenv import load_dotenv
from vkbottle import Bot, Keyboard, KeyboardButtonColor, Text, Callback, GroupEventType
from vkbottle.bot import Message, MessageEvent
from vkbottle.dispatch.rules import ABCRule
from vkbottle.polling import BotPolling

# Загружаем .env с учетом возможного BOM
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path, encoding='utf-8-sig')
else:
    load_dotenv()

# Токен группы VK и ID администраторов
GROUP_TOKEN = os.getenv("GROUP_TOKEN")
ADMIN_IDS = []  # Список ID администраторов для отправки заявок
admin_ids_str = os.getenv("ADMIN_IDS", "")
if admin_ids_str:
    ADMIN_IDS = [int(id.strip()) for id in admin_ids_str.split(",") if id.strip()]
# Поддержка старого формата ADMIN_ID для обратной совместимости
old_admin_id = os.getenv("ADMIN_ID", "")
if old_admin_id and int(old_admin_id) not in ADMIN_IDS:
    ADMIN_IDS.append(int(old_admin_id))

if not GROUP_TOKEN:
    raise ValueError("GROUP_TOKEN не установлен в .env файле")

bot = Bot(token=GROUP_TOKEN)


# Состояния пользователя
class UserState(Enum):
    NEW = "new"
    WAITING_SERVICE_TYPE = "waiting_service_type"
    WAITING_SERVICE_CATEGORY = "waiting_service_category"
    WAITING_DESCRIPTION = "waiting_description"
    WAITING_CONTACTS = "waiting_contacts"
    WAITING_CONFIRMATION = "waiting_confirmation"


# Хранилище состояний пользователей
user_states: Dict[int, Dict] = {}


# Категории услуг
SERVICE_TYPES = {
    "repair": "Ремонт 🔧",
    "maintenance": "Обслуживание ⚙️",
    "installation": "Монтаж 🛠️"
}

SERVICE_CATEGORIES = {
    "repair": {
        "boiler_repair": "Ремонт котла 🔥",
        "water_heater": "Ремонт/замена бойлера 💧",
        "leak_repair": "Ремонт протечек 💦",
        "emergency": "Аварийные ситуации 🚨"
    },
    "maintenance": {
        "heating_cleaning": "Промывка систем отопления 🌡️",
        "water_heater_service": "Обслуживание бойлера 🔧",
        "boiler_service": "Обслуживание котлов 🔥",
        "filter_service": "Обслуживание фильтров 🔬",
        "filter_refill": "Обслуживание и перезасыпка 📦"
    },
    "installation": {
        "boiler_room": "Реконструкция котельной 🏗️",
        "filtration": "Системы фильтрации 💧",
        "full_project": "Проектирование и монтаж 📐"
    }
}


class IsNewUserRule(ABCRule[Message]):
    """Правило для определения новых пользователей"""
    async def check(self, message: Message) -> bool:
        user_id = message.from_id
        if user_id not in user_states:
            user_states[user_id] = {
                "state": UserState.NEW,
                "first_message_time": datetime.now(),
                "service_type": None,
                "service_category": None,
                "description": None,
                "contacts": None
            }
            return True
        return False


async def send_welcome_message(user_id: int, name: str):
    """Отправка приветственного сообщения с фото"""
    try:
        print(f"[WELCOME] Отправка приветствия пользователю {user_id} ({name})")
        photo_attachment = os.getenv("PHOTO_ATTACHMENT", "")
        
        welcome_text = f"""{name}, приветствуем Вас 🤝

Компания АТ СЕРВИС на связи.
Мы уже более 10 лет занимаемся проектированием, монтажом, ремонтом и обслуживанием инженерных систем для частных домов, квартир и коммерческих объектов.

💫 Более 500 успешно выполненных работ
🔧 Отопление, водоснабжение, котельные, фильтрация воды
🚨 Плановые и аварийные выезды"""
        
        if photo_attachment:
            await bot.api.messages.send(
                peer_id=user_id,
                message=welcome_text,
                attachment=photo_attachment,
                random_id=0
            )
        else:
            await bot.api.messages.send(
                peer_id=user_id,
                message=welcome_text,
                random_id=0
            )
        print(f"[WELCOME] Приветствие отправлено")
    except Exception as e:
        error_msg = str(e)
        print(f"[WELCOME] Ошибка: {error_msg}")
        # Если нет разрешения - VK покажет системное уведомление
        if "Can't send" in error_msg or "without permission" in error_msg:
            print(f"[WELCOME] Нет разрешения - VK покажет системное уведомление")
        raise


async def send_service_type_selection(user_id: int):
    """Отправка сообщения с выбором типа услуги через 5 секунд"""
    await asyncio.sleep(5)
    
    try:
        keyboard = Keyboard(inline=True)
        # Используем Text кнопки - они отправляют сообщение с текстом кнопки
        keyboard.add(Text("Ремонт 🔧"), color=KeyboardButtonColor.PRIMARY)
        keyboard.row()
        keyboard.add(Text("Обслуживание ⚙️"), color=KeyboardButtonColor.PRIMARY)
        keyboard.row()
        keyboard.add(Text("Монтаж 🛠️"), color=KeyboardButtonColor.PRIMARY)
        keyboard.row()
        keyboard.add(Text("Другие работы 📋"), color=KeyboardButtonColor.PRIMARY)
        
        message_text = """✨ Какие работы необходимо выполнить?

Выберите направление, и мы подберём для вас подходящие услуги:"""
        
        await bot.api.messages.send(
            peer_id=user_id,
            message=message_text,
            keyboard=keyboard.get_json(),
            random_id=0
        )
        
        user_states[user_id]["state"] = UserState.WAITING_SERVICE_TYPE
    except Exception as e:
        print(f"Ошибка при отправке выбора услуг: {e}")


async def send_service_category_selection(user_id: int, service_type: str):
    """Отправка сообщения с выбором категории услуги"""
    try:
        print(f"\n{'='*50}")
        print(f"[SEND] ОТПРАВКА КАТЕГОРИЙ УСЛУГ")
        print(f"[SEND] User ID: {user_id}")
        print(f"[SEND] Service type: {service_type}")
        
        keyboard = Keyboard(inline=True)
        categories = SERVICE_CATEGORIES[service_type]
        
        print(f"[SEND] Категории для {service_type}: {categories}")
        
        for key, value in categories.items():
            print(f"[SEND] Добавляю кнопку: {value}")
            keyboard.add(Text(value), color=KeyboardButtonColor.POSITIVE)
            keyboard.row()
        
        keyboard.add(Text("◀️ Назад"), color=KeyboardButtonColor.SECONDARY)
        
        message_text = """Выберите конкретную услугу:"""
        
        print(f"[SEND] Отправляю сообщение с клавиатурой...")
        await bot.api.messages.send(
            peer_id=user_id,
            message=message_text,
            keyboard=keyboard.get_json(),
            random_id=0
        )
        
        user_states[user_id]["state"] = UserState.WAITING_SERVICE_CATEGORY
        user_states[user_id]["service_type"] = service_type
        
        print(f"[OK] Категории отправлены. Состояние обновлено: {user_states[user_id]['state']}")
        print(f"{'='*50}\n")
    except Exception as e:
        print(f"[ERROR] ОШИБКА при отправке категорий: {e}")
        import traceback
        traceback.print_exc()


async def request_description(user_id: int):
    """Запрос описания проблемы"""
    try:
        message_text = """🔧 Опишите, пожалуйста, ваш вопрос и что именно требуется

Мы сразу направим запрос нужному специалисту и подготовим для вас оптимальное решение."""
        
        await bot.api.messages.send(
            peer_id=user_id,
            message=message_text,
            random_id=0
        )
        
        user_states[user_id]["state"] = UserState.WAITING_DESCRIPTION
    except Exception as e:
        print(f"Ошибка при запросе описания: {e}")


async def request_contacts(user_id: int):
    """Запрос контактных данных"""
    try:
        message_text = """🤝 Чтобы специалист мог с вами связаться, укажите, пожалуйста:

— ваше имя
— номер телефона
— адрес проведения работ

Мы свяжемся с вами в ближайшее время для уточнения деталей."""
        
        await bot.api.messages.send(
            peer_id=user_id,
            message=message_text,
            random_id=0
        )
        
        user_states[user_id]["state"] = UserState.WAITING_CONTACTS
    except Exception as e:
        print(f"Ошибка при запросе контактов: {e}")


async def send_confirmation(user_id: int):
    """Отправка сообщения с подтверждением заявки"""
    try:
        keyboard = Keyboard(inline=True)
        keyboard.add(Text("Да ✅"), color=KeyboardButtonColor.POSITIVE)
        keyboard.row()
        keyboard.add(Text("Хочу обратный звонок 📞"), color=KeyboardButtonColor.PRIMARY)
        
        message_text = """📋 Оформить заявку и подобрать удобное время?

Мы свяжемся с вами для согласования всех деталей."""
        
        await bot.api.messages.send(
            peer_id=user_id,
            message=message_text,
            keyboard=keyboard.get_json(),
            random_id=0
        )
        
        user_states[user_id]["state"] = UserState.WAITING_CONFIRMATION
    except Exception as e:
        print(f"Ошибка при отправке подтверждения: {e}")


async def process_button_click(user_id: int, payload_data, event=None):
    """Обработка нажатия кнопки"""
    try:
        print(f"process_button_click: user_id={user_id}, payload_data={payload_data}")
        
        # Отвечаем на событие сразу, чтобы кнопка не висела
        if event:
            try:
                # Используем правильный API метод для ответа на callback
                if hasattr(event, 'event_id'):
                    await bot.api.messages.send_message_event_answer(
                        event_id=event.event_id,
                        user_id=user_id,
                        peer_id=event.peer_id
                    )
                elif hasattr(event, 'object') and hasattr(event.object, 'event_id'):
                    await bot.api.messages.send_message_event_answer(
                        event_id=event.object.event_id,
                        user_id=user_id,
                        peer_id=event.object.peer_id
                    )
            except Exception as e:
                print(f"Ошибка при ответе на событие: {e}")
                # Пробуем альтернативный способ
                try:
                    if hasattr(event, 'answer'):
                        await event.answer()
                except:
                    pass
        
        # Получаем payload
        payload = {}
        if payload_data:
            if isinstance(payload_data, str):
                try:
                    payload = json.loads(payload_data)
                except:
                    payload = {}
            elif isinstance(payload_data, dict):
                payload = payload_data
        
        if not payload:
            print(f"Пустой payload от пользователя {user_id}")
            return
        
        action = payload.get("action")
        print(f"Обработка кнопки: user_id={user_id}, action={action}, payload={payload}")
        
        # Инициализируем состояние если его нет
        if user_id not in user_states:
            user_states[user_id] = {
                "state": UserState.NEW,
                "first_message_time": datetime.now(),
                "service_type": None,
                "service_category": None,
                "description": None,
                "contacts": None
            }
        
        if action == "service_type":
            service_type = payload.get("type")
            print(f"Выбран тип услуги: {service_type}")
            await send_service_category_selection(user_id, service_type)
        
        elif action == "service_category":
            category = payload.get("category")
            print(f"Выбрана категория: {category}")
            user_states[user_id]["service_category"] = category
            await request_description(user_id)
        
        elif action == "back_to_types":
            print("Возврат к выбору типа услуги")
            await send_service_type_selection(user_id)
        
        elif action == "confirm":
            confirmation_type = payload.get("type")
            print(f"Подтверждение заявки: {confirmation_type}")
            await send_order_to_admin(user_id, confirmation_type)
            
            await bot.api.messages.send(
                peer_id=user_id,
                message="✅ Спасибо! Ваша заявка принята.\n\nНаш специалист свяжется с вами в ближайшее время для уточнения деталей.",
                random_id=0
            )
            
            # Сбрасываем состояние
            user_states[user_id]["state"] = UserState.NEW
        else:
            print(f"Неизвестное действие: {action}")
    except Exception as e:
        print(f"Ошибка в process_button_click: {e}")
        import traceback
        traceback.print_exc()


async def send_order_to_admin(user_id: int, confirmation_type: str):
    """Отправка заявки администратору"""
    try:
        user_info = user_states.get(user_id, {})
        service_type = user_info.get("service_type", "не указано")
        service_category = user_info.get("service_category", "не указано")
        description = user_info.get("description", "не указано")
        contacts = user_info.get("contacts", "не указано")
        
        # Получаем название услуги
        if service_type == "other":
            service_type_name = "Другие работы 📋"
            category_name = "Другие работы"
        else:
            service_type_name = SERVICE_TYPES.get(service_type, service_type)
            category_name = SERVICE_CATEGORIES.get(service_type, {}).get(service_category, service_category)
        
        # Получаем имя пользователя
        try:
            user = await bot.api.users.get(user_ids=[user_id])
            user_name = f"{user[0].first_name} {user[0].last_name}" if user else f"ID: {user_id}"
        except:
            user_name = f"ID: {user_id}"
        
        confirmation_text = "Оформить заявку" if confirmation_type == "schedule" else "Обратный звонок"
        
        order_message = f"""🆕 Новая заявка от клиента

👤 Клиент: {user_name}
🔗 Профиль: vk.com/id{user_id}

📋 Тип работы: {service_type_name}
🔧 Услуга: {category_name}

💬 Описание:
{description}

📞 Контактные данные:
{contacts}

✅ Тип обработки: {confirmation_text}"""
        
        # Отправляем всем администраторам
        for admin_id in ADMIN_IDS:
            try:
                await bot.api.messages.send(
                    peer_id=admin_id,
                    message=order_message,
                    random_id=0
                )
                print(f"[OK] Заявка отправлена администратору {admin_id}")
            except Exception as e:
                error_msg = str(e)
                if "without permission" in error_msg or "Can't send messages" in error_msg:
                    print(f"[WARN] Администратор {admin_id} не разрешил сообществу писать ему. Пропускаю.")
                else:
                    print(f"[ERROR] Ошибка отправки заявки администратору {admin_id}: {e}")
        
        # Отправляем в чат сообщества (если нужно)
        # await bot.api.messages.send(peer_id=2000000001, message=order_message, random_id=0)
        
        print(f"Заявка от пользователя {user_id}:")
        print(order_message)
        
    except Exception as e:
        print(f"Ошибка при отправке заявки: {e}")


async def start_welcome_flow(user_id: int):
    """Запускает процесс приветствия для пользователя"""
    try:
        user_info = await bot.api.users.get(user_ids=[user_id])
        name = user_info[0].first_name if user_info else "Пользователь"
    except:
        name = "Пользователь"
    
    # Пытаемся отправить приветствие - если разрешения нет, VK покажет системное уведомление
    await send_welcome_message(user_id, name)
    # Автоматически отправляем второе сообщение через 5 секунд
    asyncio.create_task(send_service_type_selection(user_id))


@bot.on.message(IsNewUserRule())
async def handle_new_user(message: Message):
    """Обработка нового пользователя - когда пользователь пишет первым"""
    user_id = message.from_id
    print(f"[NEW_USER] Новый пользователь написал первым: {user_id}")
    await start_welcome_flow(user_id)


# Пробуем оба способа обработки событий кнопок
@bot.on.raw_event(GroupEventType.MESSAGE_EVENT)
async def handle_button_click_raw(event):
    """Обработка нажатия на кнопку (raw event)"""
    try:
        print(f"Raw event получен: {type(event)}, {event}")
        # Пробуем получить MessageEvent из события
        if hasattr(event, 'object'):
            event_obj = event.object
        else:
            event_obj = event
        
        user_id = getattr(event_obj, 'user_id', None) or getattr(event, 'user_id', None)
        payload = getattr(event_obj, 'payload', None) or getattr(event, 'payload', None)
        
        if not user_id:
            print("Не удалось получить user_id из события")
            return
        
        print(f"Raw event: user_id={user_id}, payload={payload}")
        await process_button_click(user_id, payload, event=event)
    except Exception as e:
        print(f"Ошибка в handle_button_click_raw: {e}")
        import traceback
        traceback.print_exc()


@bot.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def handle_button_click(event: MessageEvent):
    """Обработка нажатия на кнопку (MessageEvent)"""
    try:
        user_id = event.user_id
        payload_data = event.payload
        event_id = getattr(event, 'event_id', None) or (getattr(event, 'object', {}).get('event_id') if hasattr(event, 'object') else None)
        peer_id = getattr(event, 'peer_id', None) or (getattr(event, 'object', {}).get('peer_id') if hasattr(event, 'object') else user_id)
        
        print(f"MessageEvent получен: user_id={user_id}, event_id={event_id}, payload={payload_data}")
        
        # Сразу отвечаем на событие
        if event_id:
            try:
                await bot.api.messages.send_message_event_answer(
                    event_id=event_id,
                    user_id=user_id,
                    peer_id=peer_id
                )
                print(f"Ответ на событие отправлен: event_id={event_id}")
            except Exception as e:
                print(f"Ошибка при ответе на событие: {e}")
        
        await process_button_click(user_id, payload_data, event=event)
    except Exception as e:
        print(f"Ошибка в handle_button_click: {e}")
        import traceback
        traceback.print_exc()


@bot.on.raw_event(GroupEventType.MESSAGE_ALLOW)
async def handle_message_allow(event):
    """Обработка события, когда пользователь разрешает сообществу писать ему"""
    try:
        print(f"\n{'='*50}")
        print(f"[MESSAGE_ALLOW] ✅✅✅ ПОЛУЧЕНО СОБЫТИЕ РАЗРЕШЕНИЯ ✅✅✅")
        
        user_id = None
        
        # Пробуем разные способы получения user_id
        if hasattr(event, 'object'):
            if hasattr(event.object, 'user_id'):
                user_id = event.object.user_id
            elif isinstance(event.object, dict):
                user_id = event.object.get('user_id')
        
        if not user_id and hasattr(event, 'user_id'):
            user_id = event.user_id
        
        if not user_id and isinstance(event, dict):
            user_id = event.get('user_id') or (event.get('object', {}).get('user_id') if isinstance(event.get('object'), dict) else None)
        
        if not user_id:
            print(f"[MESSAGE_ALLOW] ⚠️ Не удалось получить user_id")
            print(f"[MESSAGE_ALLOW] Структура: {event}")
            return
        
        print(f"[MESSAGE_ALLOW] ✅ User ID: {user_id}")
        
        # Запускаем приветствие
        if user_id not in user_states:
            print(f"[MESSAGE_ALLOW] 🆕 Новый пользователь {user_id}, запускаю приветствие")
            user_states[user_id] = {
                "state": UserState.NEW,
                "first_message_time": datetime.now(),
                "service_type": None,
                "service_category": None,
                "description": None,
                "contacts": None
            }
            await start_welcome_flow(user_id)
            print(f"[MESSAGE_ALLOW] ✅ Приветствие запущено")
        print(f"{'='*50}\n")
        
    except Exception as e:
        print(f"[MESSAGE_ALLOW] ❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


@bot.on.message()
async def handle_message(message: Message):
    """Обработка обычных сообщений"""
    user_id = message.from_id
    text = message.text or ""
    
    print(f"\n{'='*50}")
    print(f"[MSG] ✅✅✅ ПОЛУЧЕНО СООБЩЕНИЕ ✅✅✅")
    print(f"[MSG] User ID: {user_id}")
    print(f"[MSG] Текст: '{text}'")
    print(f"[MSG] Текущие состояния: {list(user_states.keys())}")
    
    # Если пользователь новый, запускаем приветствие
    if user_id not in user_states:
        print(f"[NEW] 🆕 НОВЫЙ ПОЛЬЗОВАТЕЛЬ {user_id}")
        user_states[user_id] = {
            "state": UserState.NEW,
            "first_message_time": datetime.now(),
            "service_type": None,
            "service_category": None,
            "description": None,
            "contacts": None
        }
        
        # Пытаемся отправить приветствие
        print(f"[NEW] Пытаюсь отправить приветствие пользователю {user_id}...")
        try:
            await start_welcome_flow(user_id)
            print(f"[NEW] ✅ Приветствие отправлено!")
        except Exception as e:
            error_msg = str(e)
            print(f"[NEW] ❌ Ошибка отправки: {error_msg}")
            if "Can't send" in error_msg or "without permission" in error_msg:
                print(f"[NEW] ⚠️ Нет разрешения на отправку сообщений")
            import traceback
            traceback.print_exc()
        return
    
    user_state = user_states[user_id]["state"]
    print(f"[STATE] Текущее состояние пользователя {user_id}: {user_state}")
    print(f"[DATA] Данные пользователя: {user_states[user_id]}")
    
    # Обработка текстовых команд от кнопок
    if text in ["Ремонт 🔧", "Обслуживание ⚙️", "Монтаж 🛠️", "Другие работы 📋"]:
        print(f"[BUTTON] ОБРАБОТКА КНОПКИ: '{text}'")
        if text == "Ремонт 🔧":
            print(f"[BUTTON] -> Выбран РЕМОНТ")
            await send_service_category_selection(user_id, "repair")
        elif text == "Обслуживание ⚙️":
            print(f"[BUTTON] -> Выбрано ОБСЛУЖИВАНИЕ")
            await send_service_category_selection(user_id, "maintenance")
        elif text == "Монтаж 🛠️":
            print(f"[BUTTON] -> Выбран МОНТАЖ")
            await send_service_category_selection(user_id, "installation")
        elif text == "Другие работы 📋":
            print(f"[BUTTON] -> Выбраны ДРУГИЕ РАБОТЫ")
            # Сохраняем выбор для отчета
            user_states[user_id]["service_type"] = "other"
            user_states[user_id]["service_category"] = "other"
            # Сразу переходим к запросу описания
            await request_description(user_id)
        print(f"[OK] Обработка завершена")
        return
    
    # Обработка категорий услуг
    if user_state == UserState.WAITING_SERVICE_TYPE or user_state == UserState.WAITING_SERVICE_CATEGORY:
        print(f"[CHECK] Проверка категорий услуг...")
        service_type = user_states[user_id].get("service_type")
        print(f"[CHECK] Service type: {service_type}")
        
        if service_type and service_type in SERVICE_CATEGORIES:
            categories = SERVICE_CATEGORIES[service_type]
            print(f"[CHECK] Доступные категории: {list(categories.values())}")
            for key, value in categories.items():
                print(f"[CHECK] Сравнение: '{text}' == '{value}' ? {text == value}")
                if text == value:
                    print(f"[OK] НАЙДЕНА КАТЕГОРИЯ: {key} = {value}")
                    user_states[user_id]["service_category"] = key
                    await request_description(user_id)
                    return
        
        if text == "◀️ Назад":
            print(f"[BACK] Возврат к выбору типа услуги")
            await send_service_type_selection(user_id)
            return
        
        print(f"[ERROR] Категория не найдена для текста '{text}'")
    
    # Обработка подтверждения
    if user_state == UserState.WAITING_CONFIRMATION:
        print(f"[CONFIRM] Обработка подтверждения")
        if text in ["Да ✅", "Хочу обратный звонок 📞"]:
            confirmation_type = "schedule" if text == "Да ✅" else "callback"
            print(f"[CONFIRM] Тип подтверждения: {confirmation_type}")
            await send_order_to_admin(user_id, confirmation_type)
            await bot.api.messages.send(
                peer_id=user_id,
                message="✅ Спасибо! Ваша заявка принята.\n\nНаш специалист свяжется с вами в ближайшее время для уточнения деталей.",
                random_id=0
            )
            user_states[user_id]["state"] = UserState.NEW
            print(f"[OK] Заявка обработана")
            return
    
    # Обработка описания проблемы
    if user_state == UserState.WAITING_DESCRIPTION:
        print(f"[DESC] Получено описание проблемы")
        user_states[user_id]["description"] = text
        await request_contacts(user_id)
        return
    
    # Обработка контактных данных
    elif user_state == UserState.WAITING_CONTACTS:
        print(f"[CONTACTS] Получены контактные данные")
        user_states[user_id]["contacts"] = text
        await send_confirmation(user_id)
        return
    
    print(f"[WARN] Сообщение не обработано. Состояние: {user_state}, Текст: '{text}'")
    print(f"{'='*50}\n")


# Универсальный обработчик удален


if __name__ == "__main__":
    import sys
    import io
    # Устанавливаем UTF-8 для консоли Windows
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    print("="*60)
    print("БОТ ЗАПУЩЕН")
    print("="*60)
    print("\nАктивные обработчики:")
    print("   - MESSAGE_ALLOW - обработка разрешений")
    print("   - MESSAGE - обработка сообщений")
    print("   - MESSAGE_EVENT - обработка кнопок")
    print("\nЛОГИРОВАНИЕ: ВКЛЮЧЕНО")
    print("   Все события будут выводиться в консоль")
    print("\nВАЖНО:")
    print("   Системное уведомление VK появляется когда:")
    print("   1. Пользователь открывает диалог")
    print("   2. Бот пытается отправить сообщение БЕЗ разрешения")
    print("   3. VK автоматически показывает уведомление с кнопками")
    print("\n" + "="*60 + "\n")
    try:
        bot.run_forever()
    except KeyboardInterrupt:
        print("\n\n⏹️ Бот остановлен пользователем")
    except Exception as e:
        print(f"\n\n❌ ОШИБКА ПОДКЛЮЧЕНИЯ: {e}")
        print("\nПроверьте:")
        print("1. Long Poll API включен в настройках сообщества")
        print("2. Включены события: 'Входящее сообщение' и 'Разрешение на получение'")
        print("3. Токен валиден и имеет права: 'сообщения сообщества'")
        print("4. Сообщения сообщества включены в настройках")
        import traceback
        traceback.print_exc()
