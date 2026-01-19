import requests
import json
import time
import logging
from datetime import datetime


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

TOKEN = "8234313919:AAH4COsuFFpAu9Vew0nFO7FhKQFxBXJQVg0"
ADMIN_ID = 287265398
OWNER_ID = 287265398
MODERATOR_ID = 7246838258
OWNER_USERNAME = "@tgzorf"
CHANNEL_USERNAME = "@NOOLSHY"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"


users = {}
applications = {}
moderation_apps = {}
cooperation_apps = {}
next_app_id = 1
next_mod_id = 1
next_coop_id = 1
pending_rejections = {}
scam_reports = {}
next_scam_id = 1


def send_message(chat_id, text, reply_markup=None, message_id=None):
    """Отправка сообщения"""
    try:
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        
        if reply_markup:
            payload['reply_markup'] = json.dumps(reply_markup)
        
        if message_id:
            payload['reply_to_message_id'] = message_id
        
        response = requests.post(
            f"{BASE_URL}/sendMessage",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Ошибка отправки: {response.status_code}, {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения: {e}")
        return None

def send_inline_keyboard(chat_id, text, buttons, message_id=None):
    """Отправка inline клавиатуры"""
    keyboard = {'inline_keyboard': buttons}
    return send_message(chat_id, text, keyboard, message_id)

def answer_callback(callback_id, text=None, show_alert=False):
    """Ответ на callback"""
    try:
        payload = {'callback_query_id': callback_id}
        if text:
            payload['text'] = text
            payload['show_alert'] = show_alert
        
        response = requests.post(
            f"{BASE_URL}/answerCallbackQuery",
            json=payload,
            timeout=5
        )
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Ошибка answer_callback: {e}")
        return False

def handle_start(user_id, first_name):
    """Обработка /start"""
    try:
        users[user_id] = {'step': 0}
        
        welcome = f"""<b>👋 Привет, {first_name}!</b>

🤖 <b>Бот для заявок в NoolShy Fame</b>

🎯 <b>Основные функции:</b>
• 📝 Подать заявку в фейм
• 🤝 Заявка на сотрудничество
• 👮 Заявка на модерацию
• 🚨 Отправить скамера

👑 <b>Владелец:</b> {OWNER_USERNAME}
🔗 <b>Канал:</b> {CHANNEL_USERNAME}"""
        
        keyboard = {
            'keyboard': [
                [{'text': '📝 Подать заявку'}, {'text': '🤝 Сотрудничество'}],
                [{'text': '👮 Модерация'}, {'text': '🚨 Отправить скамера'}],
                [{'text': '📋 Мои заявки'}, {'text': 'ℹ️ Информация'}],
                [{'text': '📜 Правила'}]
            ],
            'resize_keyboard': True
        }
        
        send_message(user_id, welcome, keyboard)
        logger.info(f"Пользователь {user_id} начал работу")
    except Exception as e:
        logger.error(f"Ошибка в handle_start: {e}")

def handle_info(user_id):
    """Информация о сообществе"""
    try:
        text = f"""<b>🎭 NoolShy Fame</b>

<b>Категории:</b>
• 📢 Медийки - известные личности
• 🔥 Высокий фейм - популярные в кругах
• ⚡ Средний фейм - активные участники
• 💫 Малый фейм - начинающие

<b>Виды сотрудничества:</b>
• 🏷️ Приписка
• 🛡️ Клан
• 👥 Состав
• 📋 Фейм-лист Telegram

<b>Контакты:</b>
• Владелец: {OWNER_USERNAME}
• Канал: {CHANNEL_USERNAME}

Для подачи заявки выберите нужную категорию"""
        
        send_message(user_id, text)
    except Exception as e:
        logger.error(f"Ошибка в handle_info: {e}")

def handle_rules(user_id):
    """Правила"""
    try:
        text = f"""<b>📜 Правила использования бота</b>

1. Запрещен спам и флуд
2. Информация должна быть достоверной
3. Одна заявка на человека
4. Соблюдение правил Telegram
5. Контент должен быть легальным

<b>👮 Для модераторов:</b>
• Обязательно изучение правил
• Работа только на добровольной основе
• Ответственность за свои действия

<b>🤝 Для сотрудничества:</b>
• Четкое определение целей
• Соблюдение договоренностей
• Уважительное отношение

<b>🚨 Отправка скамера:</b>
Используйте кнопку "🚨 Отправить скамера" для отправки информации о мошенниках

👑 <b>Администратор:</b> {OWNER_USERNAME}"""
        
        send_message(user_id, text)
    except Exception as e:
        logger.error(f"Ошибка в handle_rules: {e}")

def start_moderation_application(user_id):
    """Начало заявки на модерацию"""
    try:
        users[user_id] = {'step': 'mod_nickname', 'data': {}, 'type': 'moderation'}
        
        text = """<b>👮 ЗАЯВКА НА МОДЕРАЦИЮ</b>

<b>ШАГ 1 из 5: Введите ваш НИК</b>

💎 <b>Пример:</b> ZorF, Moderator Pro
<i>Ник должен быть от 2 до 20 символов</i>"""
        
        send_message(user_id, text)
    except Exception as e:
        logger.error(f"Ошибка в start_moderation_application: {e}")

def start_cooperation_application(user_id):
    """Начало заявки на сотрудничество"""
    try:
        users[user_id] = {'step': 'coop_type', 'data': {}, 'type': 'cooperation'}
        
        keyboard = {
            'keyboard': [
                [{'text': '🏷️ Приписка'}, {'text': '🛡️ Клан'}],
                [{'text': '👥 Состав'}, {'text': '📋 Фейм-лист ТГ'}],
                [{'text': '❌ Отменить'}]
            ],
            'resize_keyboard': True
        }
        
        text = """<b>🤝 ЗАЯВКА НА СОТРУДНИЧЕСТВО</b>

<b>ШАГ 1 из 4: Выберите тип сотрудничества</b>

• 🏷️ <b>Приписка</b> - упоминание в профиле
• 🛡️ <b>Клан</b> - вступление в группу/сообщество
• 👥 <b>Состав</b> - участие в составе
• 📋 <b>Фейм-лист ТГ</b> - включение в список известных

<i>Выберите один из вариантов:</i>"""
        
        send_message(user_id, text, keyboard)
    except Exception as e:
        logger.error(f"Ошибка в start_cooperation_application: {e}")

def start_scam_report(user_id):
    """Начало отправки скамера"""
    try:
        users[user_id] = {'step': 'scam_info'}
        
        text = """<b>🚨 Отправка информации о скамере</b>

<b>Пожалуйста, предоставьте следующую информацию:</b>

1. <b>Ник или юзернейм скамера</b>
2. <b>Описание ситуации</b>
3. <b>Доказательства (скриншоты, ссылки)</b>
4. <b>Ваши контакты для связи</b>

<i>Отправьте информацию одним сообщением</i>"""
        
        send_message(user_id, text)
    except Exception as e:
        logger.error(f"Ошибка в start_scam_report: {e}")

def process_moderation_step(user_id, text):
    """Обработка шагов заявки на модерацию"""
    try:
        if user_id not in users:
            return
        
        user_data = users[user_id]
        step = user_data.get('step')
        
        if step == 'mod_nickname':
            # ШАГ 1: Ник
            if len(text) < 2 or len(text) > 20:
                send_message(user_id, "❌ <b>Ник должен быть от 2 до 20 символов</b>\n\nПожалуйста, введите ник еще раз:")
                return
            
            user_data['data']['nickname'] = text
            user_data['step'] = 'mod_username'
            
            send_message(user_id, """<b>👮 ЗАЯВКА НА МОДЕРАЦИЮ</b>

<b>ШАГ 2 из 5: Введите ваш ЮЗЕРНЕЙМ</b>

👤 <b>Пример:</b> @username
<i>Юзернейм будет автоматически дополнен @ при необходимости</i>""")
        
        elif step == 'mod_username':
            # ШАГ 2: Юзернейм
            username = text.strip()
            if not username.startswith('@'):
                username = '@' + username
            
            user_data['data']['username'] = username
            user_data['step'] = 'mod_work_time'
            
            send_message(user_id, """<b>👮 ЗАЯВКА НА МОДЕРАЦИЮ</b>

<b>ШАГ 3 из 5: Сколько готов работать?</b>

⏰ <b>Укажите в свободной форме:</b>
• Количество часов в день/неделю
• График работы
• Предпочтительное время
• Срок сотрудничества

<i>Пример: "Готов работать 2-3 часа в день, в основном вечером"</i>""")
        
        elif step == 'mod_work_time':
            # ШАГ 3: Время работы
            user_data['data']['work_time'] = text
            user_data['step'] = 'mod_rules'
            
            keyboard = {
                'keyboard': [
                    [{'text': '✅ Да'}, {'text': '❌ Нет'}]
                ],
                'resize_keyboard': True
            }
            
            send_message(user_id, f"""<b>👮 ЗАЯВКА НА МОДЕРАЦИЮ</b>

<b>ШАГ 4 из 5: Изучили правила?</b>

📜 <b>Вопрос:</b> Вы изучили правила? (Попросить их можно у владельца {OWNER_USERNAME})

<i>Выберите ответ:</i>""", keyboard)
        
        elif step == 'mod_rules':
            # ШАГ 4: Изучение правил
            if text not in ['✅ Да', '❌ Нет']:
                send_message(user_id, "❌ <b>Пожалуйста, выберите вариант ответа</b>")
                return
            
            user_data['data']['rules_studied'] = 'Да' if text == '✅ Да' else 'Нет'
            user_data['step'] = 'mod_free_work'
            
            keyboard = {
                'keyboard': [
                    [{'text': '✅ Да'}, {'text': '❌ Нет'}]
                ],
                'resize_keyboard': True
            }
            
            send_message(user_id, """<b>👮 ЗАЯВКА НА МОДЕРАЦИЮ</b>

<b>ШАГ 5 из 5: Работать будешь бесплатно?</b>

💰 <b>Вопрос:</b> Работать ты будешь бесплатно?

<i>Модерация в нашем проекте - только на добровольной основе</i>""", keyboard)
        
        elif step == 'mod_free_work':
            # ШАГ 5: Бесплатная работа
            if text not in ['✅ Да', '❌ Нет']:
                send_message(user_id, "❌ <b>Пожалуйста, выберите вариант ответа</b>")
                return
            
            user_data['data']['free_work'] = 'Да' if text == '✅ Да' else 'Нет'
            show_moderation_preview(user_id, user_data['data'])
    
    except Exception as e:
        logger.error(f"Ошибка в process_moderation_step: {e}")

def process_cooperation_step(user_id, text):
    """Обработка шагов заявки на сотрудничество"""
    try:
        if user_id not in users:
            return
        
        user_data = users[user_id]
        step = user_data.get('step')
        
        if step == 'coop_type':
            # ШАГ 1: Тип сотрудничества
            if text not in ['🏷️ Приписка', '🛡️ Клан', '👥 Состав', '📋 Фейм-лист ТГ']:
                if text == '❌ Отменить':
                    if user_id in users:
                        del users[user_id]
                    send_message(user_id, "❌ Заявка отменена")
                    return
                send_message(user_id, "❌ <b>Пожалуйста, выберите тип сотрудничества из предложенных</b>")
                return
            
            user_data['data']['coop_type'] = text
            user_data['data']['coop_type_raw'] = text.replace('️', '').strip()
            user_data['step'] = 'coop_nickname'
            
            keyboard = {
                'keyboard': [
                    [{'text': '❌ Отменить'}]
                ],
                'resize_keyboard': True
            }
            
            send_message(user_id, f"""<b>🤝 ЗАЯВКА НА СОТРУДНИЧЕСТВО</b>

<b>ШАГ 2 из 4: Введите ваш НИК</b>

💎 <b>Пример:</b> ZorF, Business Partner
<i>Ник должен быть от 2 до 20 символов</i>""", keyboard)
        
        elif step == 'coop_nickname':
            # ШАГ 2: Ник
            if text == '❌ Отменить':
                if user_id in users:
                    del users[user_id]
                send_message(user_id, "❌ Заявка отменена")
                return
            
            if len(text) < 2 or len(text) > 20:
                send_message(user_id, "❌ <b>Ник должен быть от 2 до 20 символов</b>\n\nПожалуйста, введите ник еще раз:")
                return
            
            user_data['data']['nickname'] = text
            user_data['step'] = 'coop_username'
            
            send_message(user_id, """<b>🤝 ЗАЯВКА НА СОТРУДНИЧЕСТВО</b>

<b>ШАГ 3 из 4: Введите ваш ЮЗЕРНЕЙМ</b>

👤 <b>Пример:</b> @username
<i>Юзернейм будет автоматически дополнен @ при необходимости</i>""")
        
        elif step == 'coop_username':
            # ШАГ 3: Юзернейм
            username = text.strip()
            if not username.startswith('@'):
                username = '@' + username
            
            user_data['data']['username'] = username
            user_data['step'] = 'coop_rules'
            
            keyboard = {
                'keyboard': [
                    [{'text': '✅ Да'}, {'text': '❌ Нет'}]
                ],
                'resize_keyboard': True
            }
            
            send_message(user_id, f"""<b>🤝 ЗАЯВКА НА СОТРУДНИЧЕСТВО</b>

<b>ШАГ 4 из 4: Изучили правила?</b>

📜 <b>Вопрос:</b> Вы изучили правила? (Попросить их можно у владельца {OWNER_USERNAME})

<i>Выберите ответ:</i>""", keyboard)
        
        elif step == 'coop_rules':
            # ШАГ 4: Изучение правил
            if text not in ['✅ Да', '❌ Нет']:
                send_message(user_id, "❌ <b>Пожалуйста, выберите вариант ответа</b>")
                return
            
            user_data['data']['rules_studied'] = 'Да' if text == '✅ Да' else 'Нет'
            show_cooperation_preview(user_id, user_data['data'])
    
    except Exception as e:
        logger.error(f"Ошибка в process_cooperation_step: {e}")

def show_moderation_preview(user_id, data):
    """Показ предпросмотра заявки на модерацию"""
    try:
        preview = f"""<b>👮 ПРЕДПРОСМОТР ЗАЯВКИ НА МОДЕРАЦИЮ</b>

<b>1. Ник:</b> {data.get('nickname', 'Не указан')}
<b>2. Юзернейм:</b> {data.get('username', 'Не указан')}
<b>3. Готов работать:</b> {data.get('work_time', 'Не указано')}
<b>4. Изучил правила:</b> {data.get('rules_studied', 'Не указано')}
<b>5. Работа бесплатно:</b> {data.get('free_work', 'Не указано')}

<i>Всё верно? Подтвердите отправку на модерацию</i>"""
        
        keyboard = {
            'keyboard': [
                [{'text': '✅ ОТПРАВИТЬ НА МОДЕРАЦИЮ'}, {'text': '❌ Отменить'}]
            ],
            'resize_keyboard': True
        }
        
        send_message(user_id, preview, keyboard)
        users[user_id]['step'] = 'mod_confirm'
    except Exception as e:
        logger.error(f"Ошибка в show_moderation_preview: {e}")

def show_cooperation_preview(user_id, data):
    """Показ предпросмотра заявки на сотрудничество"""
    try:
        preview = f"""<b>🤝 ПРЕДПРОСМОТР ЗАЯВКИ НА СОТРУДНИЧЕСТВО</b>

<b>1. Тип сотрудничества:</b> {data.get('coop_type', 'Не указан')}
<b>2. Ник:</b> {data.get('nickname', 'Не указан')}
<b>3. Юзернейм:</b> {data.get('username', 'Не указан')}
<b>4. Изучили правила:</b> {data.get('rules_studied', 'Не указано')}

<i>Всё верно? Подтвердите отправку на модерацию</i>"""
        
        keyboard = {
            'keyboard': [
                [{'text': '✅ ОТПРАВИТЬ НА МОДЕРАЦИЮ'}, {'text': '❌ Отменить'}]
            ],
            'resize_keyboard': True
        }
        
        send_message(user_id, preview, keyboard)
        users[user_id]['step'] = 'coop_confirm'
    except Exception as e:
        logger.error(f"Ошибка в show_cooperation_preview: {e}")

def submit_moderation_application(user_id, username):
    """Отправка заявки на модерацию"""
    try:
        if user_id not in users or users[user_id].get('step') != 'mod_confirm':
            send_message(user_id, "❌ Нет данных для отправки")
            return
        
        global next_mod_id
        data = users[user_id]['data']
        
        if not username:
            username = f"user_{user_id}"
        
        moderation_apps[next_mod_id] = {
            'user_id': user_id,
            'username': username,
            'data': data,
            'status': 'pending',
            'time': datetime.now().strftime('%d.%m.%Y %H:%M'),
            'type': 'заявка на модерацию'
        }
        
        send_message(user_id, f"✅ <b>Заявка на модерацию #{next_mod_id} отправлена!</b>\n\nВладелец получил вашу заявку. Ожидайте ответа 1-3 дня.")
        
        send_moderation_to_admin(next_mod_id, data, user_id, username)
        
        if user_id in users:
            del users[user_id]
        
        next_mod_id += 1
    except Exception as e:
        logger.error(f"Ошибка в submit_moderation_application: {e}")

def submit_cooperation_application(user_id, username):
    """Отправка заявки на сотрудничество"""
    try:
        if user_id not in users or users[user_id].get('step') != 'coop_confirm':
            send_message(user_id, "❌ Нет данных для отправки")
            return
        
        global next_coop_id
        data = users[user_id]['data']
        
        if not username:
            username = f"user_{user_id}"
        
        cooperation_apps[next_coop_id] = {
            'user_id': user_id,
            'username': username,
            'data': data,
            'status': 'pending',
            'time': datetime.now().strftime('%d.%m.%Y %H:%M'),
            'type': 'заявка на сотрудничество'
        }
        
        send_message(user_id, f"✅ <b>Заявка на сотрудничество #{next_coop_id} отправлена!</b>\n\nВладелец получил вашу заявку. Ожидайте ответа 1-3 дня.")
        
        send_cooperation_to_admin(next_coop_id, data, user_id, username)
        
        if user_id in users:
            del users[user_id]
        
        next_coop_id += 1
    except Exception as e:
        logger.error(f"Ошибка в submit_cooperation_application: {e}")

def send_moderation_to_admin(app_id, data, user_id, username):
    """Отправка заявки на модерацию администратору"""
    try:
        admin_text = f"""<b>👮 НОВАЯ ЗАЯВКА НА МОДЕРАЦИЮ #{app_id}</b>

<b>1. Ник:</b> {data.get('nickname', 'Не указан')}
<b>2. Юзернейм:</b> {data.get('username', 'Не указан')}
<b>3. Готов работать:</b> {data.get('work_time', 'Не указано')}
<b>4. Изучил правила:</b> {data.get('rules_studied', 'Не указано')}
<b>5. Работа бесплатно:</b> {data.get('free_work', 'Не указано')}

<b>👤 Отправитель:</b> @{username}
<b>🆔 ID:</b> {user_id}
<b>⏰ Время:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}"""
        
        buttons = [[
            {'text': '✅ Принять', 'callback_data': f'accept_mod_{app_id}_{user_id}'},
            {'text': '❌ Отклонить', 'callback_data': f'reject_mod_{app_id}_{user_id}'},
            {'text': '👁️ Просмотр', 'callback_data': f'view_mod_{app_id}'}
        ]]
        
        send_inline_keyboard(ADMIN_ID, admin_text, buttons)
        logger.info(f"Заявка на модерацию #{app_id} отправлена админу")
    except Exception as e:
        logger.error(f"Ошибка в send_moderation_to_admin: {e}")

def send_cooperation_to_admin(app_id, data, user_id, username):
    """Отправка заявки на сотрудничество администратору"""
    try:
        admin_text = f"""<b>🤝 НОВАЯ ЗАЯВКА НА СОТРУДНИЧЕСТВО #{app_id}</b>

<b>1. Тип сотрудничества:</b> {data.get('coop_type', 'Не указан')}
<b>2. Ник:</b> {data.get('nickname', 'Не указан')}
<b>3. Юзернейм:</b> {data.get('username', 'Не указан')}
<b>4. Изучили правила:</b> {data.get('rules_studied', 'Не указано')}

<b>👤 Отправитель:</b> @{username}
<b>🆔 ID:</b> {user_id}
<b>⏰ Время:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}"""
        
        buttons = [[
            {'text': '✅ Принять', 'callback_data': f'accept_coop_{app_id}_{user_id}'},
            {'text': '❌ Отклонить', 'callback_data': f'reject_coop_{app_id}_{user_id}'},
            {'text': '👁️ Просмотр', 'callback_data': f'view_coop_{app_id}'}
        ]]
        
        send_inline_keyboard(ADMIN_ID, admin_text, buttons)
        logger.info(f"Заявка на сотрудничество #{app_id} отправлена админу")
    except Exception as e:
        logger.error(f"Ошибка в send_cooperation_to_admin: {e}")

# Существующие функции (сохранены из оригинального кода)
def start_application(user_id):
    """Начало заявки в фейм - ШАГ 1: Ник"""
    try:
        users[user_id] = {'step': 'app_nickname', 'data': {}, 'type': 'fame'}
        
        text = """<b>📝 ЗАЯВКА В NOOLSHY FAME</b>

<b>ШАГ 1 из 6: Введите ваш НИК</b>

💎 <b>Пример:</b> ZorF, Madonna Maniac
<i>Ник должен быть от 2 до 20 символов</i>"""
        
        send_message(user_id, text)
    except Exception as e:
        logger.error(f"Ошибка в start_application: {e}")

def process_application_step(user_id, text):
    """Обработка шагов заявки в фейм"""
    try:
        if user_id not in users:
            return
        
        user_data = users[user_id]
        step = user_data.get('step')
        
        if step == 'app_nickname':
            if len(text) < 2 or len(text) > 20:
                send_message(user_id, "❌ <b>Ник должен быть от 2 до 20 символов</b>\n\nПожалуйста, введите ник еще раз:")
                return
            
            if 'data' not in user_data:
                user_data['data'] = {}
            user_data['data']['nickname'] = text
            user_data['step'] = 'app_username'
            
            send_message(user_id, """<b>📝 ЗАЯВКА В NOOLSHY FAME</b>

<b>ШАГ 2 из 6: Введите ваш ЮЗЕРНЕЙМ</b>

👤 <b>Пример:</b> @username или просто username
<i>Юзернейм будет автоматически дополнен @ при необходимости</i>""")
        
        elif step == 'app_username':
            username = text.strip()
            if not username.startswith('@'):
                username = '@' + username
            
            user_data['data']['username'] = username
            user_data['step'] = 'app_about'
            
            send_message(user_id, """<b>📝 ЗАЯВКА В NOOLSHY FAME</b>

<b>ШАГ 3 из 6: Расскажите о себе</b>

📖 <b>Ответьте на все вопросы:</b>
• Как пришли в комьюнити?
• О всех своих проектах
• Связях с медиа/фейм личностями
• Как подняли свою популярность

<i>Напишите развернутый ответ (минимум 50 символов)</i>""")
        
        elif step == 'app_about':
            if len(text) < 50:
                send_message(user_id, "❌ <b>Пожалуйста, напишите более развернутый ответ (минимум 50 символов)</b>")
                return
            
            user_data['data']['about'] = text
            user_data['step'] = 'app_tiktok'
            
            keyboard = {
                'keyboard': [
                    [{'text': '➡️ Пропустить'}]
                ],
                'resize_keyboard': True
            }
            
            send_message(user_id, """<b>📝 ЗАЯВКА В NOOLSHY FAME</b>

<b>ШАГ 4 из 6: TikTok аккаунт</b>

🎵 <b>Отправьте ваш TikTok аккаунт (если имеется)</b>
<i>Пример: @tiktok_username или ссылка</i>

<i>Или нажмите "➡️ Пропустить"</i>""", keyboard)
        
        elif step == 'app_tiktok':
            if text == '➡️ Пропустить':
                user_data['data']['tiktok'] = 'Не указан'
            else:
                user_data['data']['tiktok'] = text
            
            user_data['step'] = 'app_project'
            
            send_message(user_id, """<b>📝 ЗАЯВКА В NOOLSHY FAME</b>

<b>ШАГ 5 из 6: Ссылка на проект</b>

🔗 <b>Ссылка на ваш проект (обязательно)</b>
<i>Пример: https://t.me/канал или @username</i>

<b>⚠️ Без проекта заявка не принимается!</b>""")
        
        elif step == 'app_project':
            if len(text) < 5:
                send_message(user_id, "❌ <b>Пожалуйста, укажите корректную ссылку на проект</b>")
                return
            
            user_data['data']['project'] = text
            user_data['step'] = 'app_extra'
            
            keyboard = {
                'keyboard': [
                    [{'text': '➕ Добавить ссылку'}, {'text': '➡️ Пропустить'}]
                ],
                'resize_keyboard': True
            }
            
            send_message(user_id, """<b>📝 ЗАЯВКА В NOOLSHY FAME</b>

<b>ШАГ 6 из 6: Дополнительные ссылки</b>

🔗 <b>Дополнительные ссылки (необязательно):</b>
<i>Можно добавить ссылки на другие проекты, соцсети и т.д.</i>

<i>Нажмите "➕ Добавить ссылку" или "➡️ Пропустить"</i>""", keyboard)
        
        elif step == 'app_extra':
            if text == '➕ Добавить ссылку':
                user_data['step'] = 'app_waiting_link'
                send_message(user_id, "🔗 <b>Введите ссылку:</b>\n<i>Пример: https://example.com или @username</i>")
            elif text == '➡️ Пропустить':
                user_data['data']['extra_links'] = []
                show_application_preview(user_id, user_data['data'])
        
        elif step == 'app_waiting_link':
            if 'extra_links' not in user_data['data']:
                user_data['data']['extra_links'] = []
            
            user_data['data']['extra_links'].append(text)
            user_data['step'] = 'app_add_more'
            
            keyboard = {
                'keyboard': [
                    [{'text': '➕ Добавить ещё'}, {'text': '✅ Готово'}]
                ],
                'resize_keyboard': True
            }
            
            links_count = len(user_data['data']['extra_links'])
            send_message(user_id, f"✅ <b>Ссылка добавлена!</b>\n\nВсего ссылок: {links_count}\n\nДобавить ещё или завершить?", keyboard)
        
        elif step == 'app_add_more':
            if text == '➕ Добавить ещё':
                user_data['step'] = 'app_waiting_link'
                send_message(user_id, "🔗 <b>Введите следующую ссылку:</b>")
            elif text == '✅ Готово':
                show_application_preview(user_id, user_data['data'])
    
    except Exception as e:
        logger.error(f"Ошибка в process_application_step: {e}")

def show_application_preview(user_id, data):
    """Показ предпросмотра заявки в фейм"""
    try:
        about_preview = data.get('about', '')[:200]
        if len(data.get('about', '')) > 200:
            about_preview += '... (текст сокращен)'
        
        preview = f"""<b>📋 ПРЕДПРОСМОТР ЗАЯВКИ В FAME</b>

<b>1. Ник:</b> {data.get('nickname', 'Не указан')}
<b>2. Юзернейм:</b> {data.get('username', 'Не указан')}
<b>3. О себе:</b>
{about_preview}
<b>4. TikTok:</b> {data.get('tiktok', 'Не указан')}
<b>5. Проект:</b> {data.get('project', 'Не указан')}"""
        
        extra_links = data.get('extra_links', [])
        if extra_links:
            preview += "\n\n<b>6. Доп. ссылки:</b>\n"
            for i, link in enumerate(extra_links, 1):
                preview += f"  {i}. {link}\n"
        
        preview += "\n\n<i>Всё верно? Подтвердите отправку на модерацию</i>"
        
        keyboard = {
            'keyboard': [
                [{'text': '✅ ОТПРАВИТЬ НА МОДЕРАЦИЮ'}, {'text': '❌ Отменить'}]
            ],
            'resize_keyboard': True
        }
        
        send_message(user_id, preview, keyboard)
        users[user_id] = {'step': 'app_confirm', 'data': data, 'type': 'fame'}
    except Exception as e:
        logger.error(f"Ошибка в show_application_preview: {e}")

def submit_application(user_id, username):
    """Отправка заявки в фейм на модерацию"""
    try:
        if user_id not in users or users[user_id].get('step') != 'app_confirm':
            send_message(user_id, "❌ Нет данных для отправки")
            return
        
        global next_app_id
        data = users[user_id]['data']
        
        if not username:
            username = f"user_{user_id}"
        
        applications[next_app_id] = {
            'user_id': user_id,
            'username': username,
            'data': data,
            'status': 'pending',
            'time': datetime.now().strftime('%d.%m.%Y %H:%M'),
            'type': 'заявка в NoolShy Fame'
        }
        
        send_message(user_id, f"✅ <b>Заявка #{next_app_id} отправлена на модерацию!</b>\n\nАдминистратор получил вашу заявку. Ожидайте ответа 1-3 дня.")
        
        send_to_admin_and_moderator(next_app_id, data, user_id, username)
        
        if user_id in users:
            del users[user_id]
        
        next_app_id += 1
    except Exception as e:
        logger.error(f"Ошибка в submit_application: {e}")

def send_to_admin_and_moderator(app_id, data, user_id, username):
    """Отправка заявки в фейм администратору и модератору"""
    try:
        about_preview = data.get('about', '')[:500]
        if len(data.get('about', '')) > 500:
            about_preview += '... (текст сокращен)'
        
        admin_text = f"""<b>📨 НОВАЯ ЗАЯВКА В FAME #{app_id}</b>

<b>1. Ник:</b> {data.get('nickname', 'Не указан')}
<b>2. Юзернейм:</b> {data.get('username', 'Не указан')}
<b>3. О себе:</b>
{about_preview}
<b>4. TikTok:</b> {data.get('tiktok', 'Не указан')}
<b>5. Проект:</b> {data.get('project', 'Не указан')}"""
        
        extra_links = data.get('extra_links', [])
        if extra_links:
            admin_text += "\n\n<b>6. Доп. ссылки:</b>\n"
            for i, link in enumerate(extra_links, 1):
                admin_text += f"  {i}. {link}\n"
        
        admin_text += f"\n<b>👤 Отправитель:</b> @{username}"
        admin_text += f"\n<b>🆔 ID:</b> {user_id}"
        admin_text += f"\n<b>⏰ Время:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        
        buttons = [[
            {'text': '✅ Принять', 'callback_data': f'accept_{app_id}_{user_id}'},
            {'text': '❌ Отклонить', 'callback_data': f'reject_{app_id}_{user_id}'}
        ]]
        
        send_inline_keyboard(ADMIN_ID, admin_text, buttons)
        
        moderator_about_preview = data.get('about', '')[:300]
        if len(data.get('about', '')) > 300:
            moderator_about_preview += '... (текст сокращен)'
        
        moderator_text = f"""<b>👀 НОВАЯ ЗАЯВКА В FAME #{app_id} (ТОЛЬКО ПРОСМОТР)</b>

<b>1. Ник:</b> {data.get('nickname', 'Не указан')}
<b>2. Юзернейм:</b> {data.get('username', 'Не указан')}
<b>3. О себе:</b>
{moderator_about_preview}
<b>4. TikTok:</b> {data.get('tiktok', 'Не указан')}
<b>5. Проект:</b> {data.get('project', 'Не указан')}
        
<b>👤 Отправитель:</b> @{username}
<b>🆔 ID:</b> {user_id}
<b>⏰ Время:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}

<i>Статус: ⏳ Ожидает решения владельца</i>"""
        
        moderator_buttons = [[
            {'text': '👁️ Просмотр полного текста', 'callback_data': f'view_{app_id}'}
        ]]
        
        send_inline_keyboard(MODERATOR_ID, moderator_text, moderator_buttons)
        
        logger.info(f"Заявка в фейм #{app_id} отправлена админу и модератору")
    except Exception as e:
        logger.error(f"Ошибка в send_to_admin_and_moderator: {e}")

def process_scam_report(user_id, username, text):
    """Обработка отчета о скамере"""
    try:
        if not username:
            username = f"user_{user_id}"
        
        global next_scam_id
        scam_reports[next_scam_id] = {
            'user_id': user_id,
            'username': username,
            'info': text,
            'time': datetime.now().strftime('%d.%m.%Y %H:%M'),
            'status': 'pending'
        }
        
        report_text = f"""<b>🚨 НОВЫЙ РЕПОРТ О СКАМЕРЕ #{next_scam_id}</b>

<b>Отправитель:</b> @{username}
<b>ID:</b> {user_id}
<b>Время:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}

<b>Информация:</b>
{text[:1500]}{'... (сообщение сокращено)' if len(text) > 1500 else ''}"""
        
        buttons = [[
            {'text': '📨 Отправить на модерацию', 'callback_data': f'send_moderation_{next_scam_id}'}
        ]]
        
        send_inline_keyboard(ADMIN_ID, report_text, buttons)
        
        send_message(user_id, "✅ <b>Ваш отчет отправлен администратору!</b>\n\nСпасибо за бдительность. Администратор рассмотрит ваш отчет.")
        
        if user_id in users:
            del users[user_id]
        
        next_scam_id += 1
        logger.info(f"Отчет о скамере #{next_scam_id-1} от {user_id}")
    except Exception as e:
        logger.error(f"Ошибка в process_scam_report: {e}")

def show_user_applications(user_id):
    """Показ всех заявок пользователя"""
    try:
        user_apps = []
        
        # Заявки в фейм
        for app_id, app in applications.items():
            if app.get('user_id') == user_id:
                status = app.get('status', 'неизвестно')
                status_emoji = '⏳' if status == 'pending' else '✅' if status == 'accepted' else '❌'
                app_type = app.get('type', 'заявка в фейм')
                app_time = app.get('time', 'неизвестно')
                user_apps.append(f"#{app_id} - {app_type} - {status_emoji} {status} - {app_time}")
        
        # Заявки на модерацию
        for app_id, app in moderation_apps.items():
            if app.get('user_id') == user_id:
                status = app.get('status', 'неизвестно')
                status_emoji = '⏳' if status == 'pending' else '✅' if status == 'accepted' else '❌'
                app_type = app.get('type', 'заявка на модерацию')
                app_time = app.get('time', 'неизвестно')
                user_apps.append(f"#{app_id} - {app_type} - {status_emoji} {status} - {app_time}")
        
        # Заявки на сотрудничество
        for app_id, app in cooperation_apps.items():
            if app.get('user_id') == user_id:
                status = app.get('status', 'неизвестно')
                status_emoji = '⏳' if status == 'pending' else '✅' if status == 'accepted' else '❌'
                app_type = app.get('type', 'заявка на сотрудничество')
                app_time = app.get('time', 'неизвестно')
                user_apps.append(f"#{app_id} - {app_type} - {status_emoji} {status} - {app_time}")
        
        if not user_apps:
            text = "📭 <b>У вас еще нет заявок</b>\n\nВыберите нужный тип заявки в главном меню"
        else:
            text = f"📋 <b>ВАШИ ЗАЯВКИ ({len(user_apps)})</b>\n\n"
            for app in user_apps:
                text += f"• {app}\n"
            text += f"\n⏳ - ожидает\n✅ - принята\n❌ - отклонена"
        
        send_message(user_id, text)
    except Exception as e:
        logger.error(f"Ошибка в show_user_applications: {e}")

def edit_message_text(chat_id, message_id, text, reply_markup=None):
    """Редактирование текста сообщения"""
    try:
        payload = {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        
        if reply_markup:
            payload['reply_markup'] = json.dumps(reply_markup)
        
        response = requests.post(
            f"{BASE_URL}/editMessageText",
            json=payload
        )
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Ошибка в edit_message_text: {e}")
        return False

def ask_rejection_reason(app_id, user_id, app_type):
    """Запрос причины отклонения у владельца"""
    try:
        pending_rejections[app_id] = {'user_id': user_id, 'type': app_type}
        
        text = f"❓ <b>Укажите причину отклонения заявки #{app_id} ({app_type}):</b>\n\n<i>Сообщение будет отправлено пользователю</i>"
        send_message(OWNER_ID, text)
    except Exception as e:
        logger.error(f"Ошибка в ask_rejection_reason: {e}")

def process_rejection_reason(app_id, reason_text):
    """Обработка причины отклонения"""
    try:
        if app_id not in pending_rejections:
            return False
        
        user_id = pending_rejections[app_id]['user_id']
        app_type = pending_rejections[app_id].get('type', 'заявка')
        
        # Определяем, в какой словарь сохранить
        if 'mod_' in str(app_id):
            if app_id in moderation_apps:
                moderation_apps[app_id]['status'] = 'rejected'
                moderation_apps[app_id]['reject_reason'] = reason_text
        elif 'coop_' in str(app_id):
            if app_id in cooperation_apps:
                cooperation_apps[app_id]['status'] = 'rejected'
                cooperation_apps[app_id]['reject_reason'] = reason_text
        else:
            if app_id in applications:
                applications[app_id]['status'] = 'rejected'
                applications[app_id]['reject_reason'] = reason_text
        
        send_message(user_id, f"""❌ <b>ВАША ЗАЯВКА #{app_id} ОТКЛОНЕНА</b>

<b>Тип:</b> {app_type}
<b>Причина:</b>
{reason_text}

<i>Если у вас есть вопросы, обратитесь к администратору: {OWNER_USERNAME}</i>""")
        
        if app_id in pending_rejections:
            del pending_rejections[app_id]
        
        send_message(OWNER_ID, f"✅ <b>Заявка #{app_id} отклонена</b>\n\nПричина отправлена пользователю.")
        
        return True
    except Exception as e:
        logger.error(f"Ошибка в process_rejection_reason: {e}")
        return False

def handle_callback(callback_id, user_id, data, message_id, chat_id):
    """Обработка callback от админа/модератора"""
    try:
        if not data:
            answer_callback(callback_id, "❌ Ошибка: пустые данные")
            return
            
        parts = data.split('_')
        
        # Обработка отправки скамера на модерацию
        if len(parts) >= 3 and parts[0] == 'send' and parts[1] == 'moderation':
            try:
                scam_id = int(parts[2])
            except ValueError:
                answer_callback(callback_id, "❌ Ошибка: неверный ID репорта")
                return
            
            if user_id != ADMIN_ID:
                answer_callback(callback_id, "❌ Нет прав администратора")
                return
            
            if scam_id in scam_reports:
                scam_reports[scam_id]['status'] = 'sent_to_moderation'
            
            edit_message_text(chat_id, message_id, 
                            f"✅ <b>Отчет #{scam_id} отправлен модератору</b>\n\nПользователь уведомлен.")
            
            if scam_id in scam_reports:
                target_user_id = scam_reports[scam_id]['user_id']
                send_message(target_user_id, "📨 <b>Ваш отчет о скамере отправлен на модерацию</b>\n\nСпасибо за вашу помощь в поддержании безопасности сообщества!")
            
            send_message(MODERATOR_ID, f"🔔 <b>Новый отчет о скамере #{scam_id} для проверки</b>\n\nПроверьте отчет в базе данных бота.")
            
            answer_callback(callback_id, "✅ Отчет отправлен модератору")
            return
        
        # Просмотр заявки в фейм (для модератора)
        elif len(parts) >= 2 and parts[0] == 'view':
            try:
                app_id = int(parts[1])
            except ValueError:
                answer_callback(callback_id, "❌ Ошибка: неверный ID заявки")
                return
            
            if user_id != MODERATOR_ID:
                answer_callback(callback_id, "❌ Нет прав модератора")
                return
            
            if app_id not in applications:
                answer_callback(callback_id, "❌ Заявка не найдена")
                return
            
            app = applications[app_id]
            app_data = app.get('data', {})
            
            view_text = f"""<b>👀 ПОЛНЫЙ ТЕКСТ ЗАЯВКИ В FAME #{app_id}</b>

<b>1. Ник:</b> {app_data.get('nickname', 'Не указан')}
<b>2. Юзернейм:</b> {app_data.get('username', 'Не указан')}
<b>3. О себе:</b>
{app_data.get('about', 'Не указано')}
<b>4. TikTok:</b> {app_data.get('tiktok', 'Не указан')}
<b>5. Проект:</b> {app_data.get('project', 'Не указан')}"""
            
            extra_links = app_data.get('extra_links', [])
            if extra_links:
                view_text += "\n\n<b>6. Доп. ссылки:</b>\n"
                for i, link in enumerate(extra_links, 1):
                    view_text += f"  {i}. {link}\n"
            
            view_text += f"\n<b>👤 Отправитель:</b> @{app.get('username', 'неизвестно')}"
            view_text += f"\n<b>🆔 ID:</b> {app.get('user_id', 'неизвестно')}"
            view_text += f"\n<b>⏰ Время:</b> {app.get('time', 'неизвестно')}"
            view_text += f"\n<b>📊 Статус:</b> {app.get('status', 'неизвестно')}"
            
            answer_callback(callback_id, "Загружаем заявку...")
            send_message(MODERATOR_ID, view_text)
            return
        
        # Просмотр заявки на модерацию
        elif len(parts) >= 3 and parts[0] == 'view' and parts[1] == 'mod':
            try:
                app_id = int(parts[2])
            except ValueError:
                answer_callback(callback_id, "❌ Ошибка: неверный ID заявки")
                return
            
            if app_id not in moderation_apps:
                answer_callback(callback_id, "❌ Заявка не найдена")
                return
            
            app = moderation_apps[app_id]
            app_data = app.get('data', {})
            
            view_text = f"""<b>👀 ПОЛНЫЙ ТЕКСТ ЗАЯВКИ НА МОДЕРАЦИЮ #{app_id}</b>

<b>1. Ник:</b> {app_data.get('nickname', 'Не указан')}
<b>2. Юзернейм:</b> {app_data.get('username', 'Не указан')}
<b>3. Готов работать:</b> {app_data.get('work_time', 'Не указано')}
<b>4. Изучил правила:</b> {app_data.get('rules_studied', 'Не указано')}
<b>5. Работа бесплатно:</b> {app_data.get('free_work', 'Не указано')}

<b>👤 Отправитель:</b> @{app.get('username', 'неизвестно')}
<b>🆔 ID:</b> {app.get('user_id', 'неизвестно')}
<b>⏰ Время:</b> {app.get('time', 'неизвестно')}
<b>📊 Статус:</b> {app.get('status', 'неизвестно')}"""
            
            answer_callback(callback_id, "Загружаем заявку...")
            send_message(user_id, view_text)
            return
        
        # Просмотр заявки на сотрудничество
        elif len(parts) >= 3 and parts[0] == 'view' and parts[1] == 'coop':
            try:
                app_id = int(parts[2])
            except ValueError:
                answer_callback(callback_id, "❌ Ошибка: неверный ID заявки")
                return
            
            if app_id not in cooperation_apps:
                answer_callback(callback_id, "❌ Заявка не найдена")
                return
            
            app = cooperation_apps[app_id]
            app_data = app.get('data', {})
            
            view_text = f"""<b>👀 ПОЛНЫЙ ТЕКСТ ЗАЯВКИ НА СОТРУДНИЧЕСТВО #{app_id}</b>

<b>1. Тип сотрудничества:</b> {app_data.get('coop_type', 'Не указан')}
<b>2. Ник:</b> {app_data.get('nickname', 'Не указан')}
<b>3. Юзернейм:</b> {app_data.get('username', 'Не указан')}
<b>4. Изучили правила:</b> {app_data.get('rules_studied', 'Не указано')}

<b>👤 Отправитель:</b> @{app.get('username', 'неизвестно')}
<b>🆔 ID:</b> {app.get('user_id', 'неизвестно')}
<b>⏰ Время:</b> {app.get('time', 'неизвестно')}
<b>📊 Статус:</b> {app.get('status', 'неизвестно')}"""
            
            answer_callback(callback_id, "Загружаем заявку...")
            send_message(user_id, view_text)
            return
        
        # Обработка принятия/отклонения заявок
        if len(parts) < 3:
            answer_callback(callback_id, "❌ Ошибка: неверный формат данных")
            return
        
        action = parts[0]
        
        try:
            app_id = int(parts[1])
            target_user_id = int(parts[2])
        except ValueError:
            answer_callback(callback_id, "❌ Ошибка: неверный ID")
            return
        
        # Определяем тип заявки
        app = None
        app_type = ""
        
        if 'accept_mod_' in data or 'reject_mod_' in data:
            if app_id not in moderation_apps:
                answer_callback(callback_id, "❌ Заявка на модерацию не найдена")
                return
            app = moderation_apps[app_id]
            app_type = "заявка на модерацию"
        elif 'accept_coop_' in data or 'reject_coop_' in data:
            if app_id not in cooperation_apps:
                answer_callback(callback_id, "❌ Заявка на сотрудничество не найдена")
                return
            app = cooperation_apps[app_id]
            app_type = "заявка на сотрудничество"
        else:
            if app_id not in applications:
                answer_callback(callback_id, "❌ Заявка не найдена")
                return
            app = applications[app_id]
            app_type = "заявка в фейм"
        
        if action == 'accept' or action == 'accept_mod' or action == 'accept_coop':
            if user_id != OWNER_ID:
                answer_callback(callback_id, "❌ Только владелец может принимать заявки", show_alert=True)
                return
            
            # Обновляем статус в соответствующем словаре
            if 'mod' in data:
                moderation_apps[app_id]['status'] = 'accepted'
            elif 'coop' in data:
                cooperation_apps[app_id]['status'] = 'accepted'
            else:
                applications[app_id]['status'] = 'accepted'
            
            # Отправляем сообщение пользователю
            send_message(target_user_id, f"""🎉 <b>ВАША {app_type.upper()} #{app_id} ПРИНЯТА!</b>

Поздравляем! Ваша заявка была одобрена.

Свяжитесь с администратором для получения дальнейших инструкций.""")
            
            # Обновляем сообщение у админа
            edit_message_text(chat_id, message_id, 
                            f"✅ <b>{app_type.upper()} #{app_id} ПРИНЯТА</b>\n\nПользователь @{app.get('username', 'неизвестно')} уведомлен.")
            
            # Уведомляем модератора (если это заявка в фейм)
            if 'mod' not in data and 'coop' not in data:
                send_message(MODERATOR_ID, f"""📝 <b>ЗАЯВКА В FAME #{app_id} ОБНОВЛЕНА</b>

<i>Статус: ✅ Принята владельцем</i>
<b>Пользователь:</b> @{app.get('username', 'неизвестно')}""")
            
            answer_callback(callback_id, f"✅ {app_type} принята")
            
        elif action == 'reject' or action == 'reject_mod' or action == 'reject_coop':
            if user_id != OWNER_ID:
                answer_callback(callback_id, "❌ Только владелец может отклонять заявки", show_alert=True)
                return
            
            ask_rejection_reason(app_id, target_user_id, app_type)
            answer_callback(callback_id, "📝 Укажите причину отклонения")
        else:
            answer_callback(callback_id, "❌ Неизвестное действие")
            
    except Exception as e:
        logger.error(f"Ошибка в handle_callback: {e}")
        answer_callback(callback_id, "❌ Произошла ошибка")

def main():
    """Главный цикл бота"""
    print("🤖 Запуск бота NoolShy Fame")
    print(f"👑 Владелец: {OWNER_USERNAME}")
    print(f"🆔 Admin ID: {ADMIN_ID}")
    print(f"👁️ Модератор ID: {MODERATOR_ID}")
    print("⏳ Ожидание обновлений...")
    
    offset = 0
    
    try:
        resp = requests.get(f"{BASE_URL}/getMe", timeout=10)
        if resp.status_code == 200:
            bot_info = resp.json()
            if bot_info.get('ok'):
                bot_name = bot_info['result']['first_name']
                print(f"✅ Бот '{bot_name}' запущен!")
            else:
                print(f"❌ Ошибка: {bot_info}")
                return
        else:
            print(f"❌ Ошибка подключения: {resp.status_code}")
            return
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return
    
    while True:
        try:
            response = requests.get(
                f"{BASE_URL}/getUpdates",
                params={'offset': offset, 'timeout': 30, 'allowed_updates': ['message', 'callback_query']},
                timeout=35
            )
            
            if response.status_code == 409:
                offset = 0
                print("⚠️ Конфликт: сброс offset")
                continue
            elif response.status_code != 200:
                print(f"❌ Ошибка HTTP: {response.status_code}")
                time.sleep(1)
                continue
            
            updates = response.json()
            
            if not updates.get('ok'):
                print(f"❌ Ответ не ok: {updates}")
                time.sleep(1)
                continue
            
            result = updates.get('result', [])
            
            for update in result:
                offset = update['update_id'] + 1
                
                if 'callback_query' in update:
                    callback = update['callback_query']
                    callback_id = callback['id']
                    user_id = callback['from']['id']
                    data = callback.get('data', '')
                    message = callback.get('message', {})
                    message_id = message.get('message_id')
                    chat_id = message.get('chat', {}).get('id')
                    
                    handle_callback(callback_id, user_id, data, message_id, chat_id)
                    continue
                
                if 'message' not in update:
                    continue
                
                message = update['message']
                user_id = message['from']['id']
                username = message['from'].get('username', '')
                first_name = message['from'].get('first_name', '')
                
                if 'text' in message:
                    text = message['text']
                    
                    if text.startswith('/start'):
                        handle_start(user_id, first_name)
                        continue
                    
                    # Основные команды
                    if text == '📝 Подать заявку':
                        start_application(user_id)
                        continue
                    
                    elif text == '👮 Модерация':
                        start_moderation_application(user_id)
                        continue
                    
                    elif text == '🤝 Сотрудничество':
                        start_cooperation_application(user_id)
                        continue
                    
                    elif text == '🚨 Отправить скамера':
                        start_scam_report(user_id)
                        continue
                    
                    elif text == '📋 Мои заявки':
                        show_user_applications(user_id)
                        continue
                    
                    elif text == 'ℹ️ Информация':
                        handle_info(user_id)
                        continue
                    
                    elif text == '📜 Правила':
                        handle_rules(user_id)
                        continue
                    
                    # Подтверждение отправки
                    elif text == '✅ ОТПРАВИТЬ НА МОДЕРАЦИЮ':
                        if user_id in users:
                            user_data = users[user_id]
                            app_type = user_data.get('type', '')
                            
                            if app_type == 'fame':
                                submit_application(user_id, username)
                            elif app_type == 'moderation':
                                submit_moderation_application(user_id, username)
                            elif app_type == 'cooperation':
                                submit_cooperation_application(user_id, username)
                        continue
                    
                    elif text == '❌ Отменить':
                        if user_id in users:
                            del users[user_id]
                        send_message(user_id, "❌ Заявка отменена")
                        continue
                    
                    # Специальные команды для шагов
                    elif text in ['➡️ Пропустить', '➕ Добавить ссылку', '✅ Готово', '➕ Добавить ещё', 
                                '✅ Да', '❌ Нет', '➕ Добавить ещё', '✅ Готово',
                                '🏷️ Приписка', '🛡️ Клан', '👥 Состав', '📋 Фейм-лист ТГ']:
                        if user_id in users:
                            user_data = users[user_id]
                            app_type = user_data.get('type', '')
                            
                            if app_type == 'fame':
                                process_application_step(user_id, text)
                            elif app_type == 'moderation':
                                process_moderation_step(user_id, text)
                            elif app_type == 'cooperation':
                                process_cooperation_step(user_id, text)
                        continue
                    
                    # Обработка причины отклонения от владельца
                    if user_id == OWNER_ID:
                        processed = False
                        for app_id in list(pending_rejections.keys()):
                            if process_rejection_reason(app_id, text):
                                processed = True
                                break
                        if processed:
                            continue
                    
                    # Обработка текстовых ответов пользователя
                    if user_id in users:
                        user_data = users[user_id]
                        step = user_data.get('step', '')
                        app_type = user_data.get('type', '')
                        
                        if step == 'scam_info':
                            process_scam_report(user_id, username, text)
                            continue
                        
                        elif step and step.startswith('app_') and app_type == 'fame':
                            process_application_step(user_id, text)
                            continue
                        
                        elif step and step.startswith('mod_') and app_type == 'moderation':
                            process_moderation_step(user_id, text)
                            continue
                        
                        elif step and step.startswith('coop_') and app_type == 'cooperation':
                            process_cooperation_step(user_id, text)
                            continue
                    
        except requests.exceptions.Timeout:
            continue
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Ошибка сети: {e}")
            time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Бот остановлен")
            break
        except Exception as e:
            print(f"💥 Критическая ошибка: {type(e).__name__}: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()