import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
import json
import os
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

# ========== ТОКЕН БОТА ==========
TOKEN = "8700545809:AAH6FyZB7Hdv5l_-CpIiFzshct7SdlOPo_k"
bot = telebot.TeleBot(TOKEN)

# ========== АДМІНИ (з Render Environment Variables) ==========
ADMIN_IDS = [int(id.strip()) for id in os.getenv("ADMIN_IDS", "").split(",") if id.strip()]
if not ADMIN_IDS:
    print("⚠️ Увага! Жодного адміна не налаштовано. Додайте змінну ADMIN_IDS.")

# ========== ФАЙЛ НОВИН ==========
NEWS_FILE = "news.json"

def load_news():
    if not os.path.exists(NEWS_FILE):
        return []
    with open(NEWS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return []

def save_news(news_list):
    with open(NEWS_FILE, "w", encoding="utf-8") as f:
        json.dump(news_list, f, ensure_ascii=False, indent=2)

def add_news(text):
    news = load_news()
    new_id = max([n["id"] for n in news], default=0) + 1
    news.append({
        "id": new_id,
        "text": text,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    save_news(news)
    return new_id

def delete_news(news_id):
    news = load_news()
    new_list = [n for n in news if n["id"] != news_id]
    if len(new_list) == len(news):
        return False
    save_news(new_list)
    return True

# ========== ЧАС УРОКІВ ==========
time_slots = {
    1: "8:30-9:15",
    2: "9:25-10:10",
    3: "10:30-11:15",
    4: "11:35-12:20",
    5: "12:30-13:15",
    6: "13:25-14:10",
    7: "14:20-15:05",
    8: "15:15-16:00"
}

# ========== РОЗКЛАД (скорочено для прикладу, але повний з вашого коду) ==========
schedule = {
    5: {
        1: ["англійська мова", "українська мова", "мистецтво", "математика", "фізична культура", "українська література"],
        2: ["етика", "англійська мова", "українська мова", "математика", "історія", "мистецтво"],
        3: ["інформатика(І)", "англійська мова", "математика", "українська мова", "технології", "фізична культура", "інформатика(ІІ)"],
        4: ["пізнаємо природу", "українська мова", "математика", "українська література", "фізична культура"],
        5: ["здоров'я, безпека і добробут", "математика", "пізнаємо природу", "зарубіжна література", "англійська мова"]
    },
    6: {
        1: ["математика", "англійська мова", "фізична культура", "українська мова", "українська література", "мистецтво", "інформатика(І)"],
        2: ["фізична культура", "українська мова", "технології", "англійська мова", "математика", "історія"],
        3: ["зарубіжна література", "етика", "українська література", "математика", "географія", "пізнаємо природу"],
        4: ["українська мова", "математика", "фізична культура", "здоров'я, безпека і добробут", "англійська мова", "мистецтво"],
        5: ["англійська мова", "математика", "пізнаємо природу", "історія України", "географія", "математика", "інформатика(ІІ)"]
    },
    7: {
        1: ["українська мова", "інформатика", "англійська мова", "фізична культура", "алгебра", "громадянська освіта", "здоров'я, безпека і добробут"],
        2: ["українська література", "всесвітня історія", "англійська мова", "біологія", "геометрія", "фізика", "технології"],
        3: ["українська мова", "всесвітня історія", "інформатика", "фізика", "біологія", "алгебра", "хімія/осн. христ. етики"],
        4: ["англійська мова", "геометрія", "історія України", "фізична культура", "географія", "зарубіжна література", "мистецтво"],
        5: ["алгебра", "хімія", "українська мова", "географія", "англійська мова", "українська література", "мистецтво"]
    },
    8: {
        1: ["фізична культура", "алгебра", "фізика", "інформатика", "англійська мова", "підпр. і фін. грамотність", "здоров'я, безпека і добробут"],
        2: ["англійська мова", "технології", "біологія", "фізика", "фізична культура", "геометрія/осн. христ. етики", "мистецтво"],
        3: ["алгебра", "хімія", "історія України", "українська мова", "інформатика", "німецька мова", "українська література"],
        4: ["геометрія", "фізична культура", "зарубіжна література", "громадянська освіта", "українська мова", "географія", "українська література"],
        5: ["алгебра", "українська мова", "біологія", "англійська мова", "хімія", "всесвітня історія", "географія"]
    },
    9: {
        1: ["укр. мова(І)/англ. мова(ІІ)", "англ. мова(І)/укр. мова(ІІ)", "алгебра", "біологія", "інформатика", "географія", "фізика"],
        2: ["всесвітня історія", "хімія", "геометрія", "укр. мова(І)/англ. мова(ІІ)", "англ. мова(І)/укр. мова(ІІ)", "фізична культура", "зарубіжна література", "мистецтво"],
        3: ["трудове навчання (д.)", "німецька мова", "алгебра", "інформатика", "фізична культура", "осн. христ. етики", "фізика", "трудове навчання (хл.)"],
        4: ["історія України", "фізика", "геометрія", "українська література", "зарубіжна література", "основи здоров'я", "географія/історія України"],
        5: ["біологія", "укр. мова(І)/англ. мова(ІІ)", "англ. мова(І)/укр. мова(ІІ)", "українська література", "основи правознавства", "хімія", "фізична культура"]
    },
    10: {
        1: ["географія", "українська мова", "математика", "фізика", "українська література", "біологія", "ЗУ(Ліцей - ІІ тиждень)"],
        2: ["хімія", "інформатика", "історія", "технології", "англійська мова", "математика", "фізична культура"],
        3: ["біологія", "математика", "англійська мова", "фізична культура", "фізика", "українська мова", "географія/німецька мова", "хімія/---"],
        4: ["фізична культура", "українська мова", "фізика", "українська література", "математика", "історія", "громадянська освіта"],
        5: ["українська мова", "історія", "інформатика", "українська література", "зарубіжна література", "англійська мова", "громадянська освіта"]
    },
    11: {
        1: ["українська мова", "фізична культура", "історія", "українська література", "географія", "фізика", "хімія"],
        2: ["технології", "англійська мова", "фізика", "математика", "біологія", "ЗУ(Ліцей - ІІ тиждень)"],
        3: ["фізична культура", "українська мова", "українська література", "історія", "математика", "астрономія", "технології", "---/німецька мова"],
        4: ["українська мова", "англійська мова", "українська література", "фізика", "математика", "фізична культура", "зарубіжна література"],
        5: ["історія", "математика", "українська мова", "біологія", "інформатика", "англійська мова", "хімія"]
    }
}

days_ua = {
    1: "📅 Понеділок",
    2: "📅 Вівторок", 
    3: "📅 Середа",
    4: "📅 Четвер",
    5: "📅 П'ятниця"
}

def get_current_day():
    today = datetime.now().weekday()
    if today < 5:
        return today + 1
    return None

# ========== КНОПКИ ==========
def main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = [InlineKeyboardButton(f"{cls} клас", callback_data=f"class_{cls}") for cls in [5,6,7,8,9,10,11]]
    markup.add(*buttons)
    markup.add(InlineKeyboardButton("📰 Новини", callback_data="news"))
    return markup

def day_menu(cls):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📅 Сьогодні", callback_data=f"today_{cls}"),
        InlineKeyboardButton("➡️ Завтра", callback_data=f"tomorrow_{cls}")
    )
    markup.add(
        InlineKeyboardButton("Понеділок", callback_data=f"day_{cls}_1"),
        InlineKeyboardButton("Вівторок", callback_data=f"day_{cls}_2"),
        InlineKeyboardButton("Середа", callback_data=f"day_{cls}_3"),
        InlineKeyboardButton("Четвер", callback_data=f"day_{cls}_4"),
        InlineKeyboardButton("П'ятниця", callback_data=f"day_{cls}_5")
    )
    markup.add(InlineKeyboardButton("🔙 На головну", callback_data="main_menu"))
    return markup

def show_schedule(chat_id, message_id, cls, day, is_edit=True):
    lessons = schedule.get(cls, {}).get(day, [])
    if not lessons:
        text = f"❌ <b>Немає розкладу</b>\n\n{cls} клас, {days_ua[day]}"
    else:
        lesson_lines = []
        for i, lesson in enumerate(lessons, start=1):
            time_str = time_slots.get(i, "час невідомий")
            lesson_lines.append(f"{i}. {time_str} : {lesson}")
        lesson_list = "\n".join(lesson_lines)
        text = f"📚 <b>{cls} клас</b>\n{days_ua[day]}\n\n📖 <b>Розклад:</b>\n{lesson_list}"
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙 Назад", callback_data=f"class_{cls}"))
    markup.add(InlineKeyboardButton("🏠 Головне меню", callback_data="main_menu"))
    
    if is_edit:
        bot.edit_message_text(text, chat_id, message_id, parse_mode="HTML", reply_markup=markup)
    else:
        bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)

def show_news(chat_id, message_id, is_edit=True):
    news_list = load_news()
    if not news_list:
        text = "📰 <b>Новини</b>\n\n😔 Немає новин."
    else:
        text = "📰 <b>Новини</b>\n\n"
        for n in news_list:
            text += f"🆔 <b>{n['id']}</b> | {n['date']}\n{n['text']}\n\n"
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙 На головну", callback_data="main_menu"))
    if is_edit:
        bot.edit_message_text(text, chat_id, message_id, parse_mode="HTML", reply_markup=markup)
    else:
        bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)

# ========== АДМІН КОМАНДИ ==========
def is_admin(user_id):
    return user_id in ADMIN_IDS

@bot.message_handler(commands=['addnews'])
def add_news_command(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ У вас немає прав адміністратора.")
        return
    text = message.text.replace('/addnews', '', 1).strip()
    if not text:
        bot.reply_to(message, "✏️ Напишіть текст новини після команди: `/addnews Текст новини`", parse_mode="Markdown")
        return
    new_id = add_news(text)
    bot.reply_to(message, f"✅ Новину додано! ID: {new_id}")

@bot.message_handler(commands=['deletenews'])
def delete_news_command(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ У вас немає прав адміністратора.")
        return
    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        bot.reply_to(message, "❌ Використання: `/deletenews ID`", parse_mode="Markdown")
        return
    news_id = int(parts[1])
    if delete_news(news_id):
        bot.reply_to(message, f"🗑 Новину з ID {news_id} видалено.")
    else:
        bot.reply_to(message, f"⚠️ Новину з ID {news_id} не знайдено.")

@bot.message_handler(commands=['listnews'])
def list_news_command(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ У вас немає прав адміністратора.")
        return
    news = load_news()
    if not news:
        bot.reply_to(message, "📭 Новини відсутні.")
        return
    text = "📋 <b>Список новин</b>\n\n"
    for n in news:
        text += f"🆔 {n['id']} | {n['date']}\n{n['text']}\n\n"
    bot.send_message(message.chat.id, text, parse_mode="HTML")

# ========== ОСНОВНІ ОБРОБНИКИ ==========
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🎓 <b>Вітаю в боті розкладу!</b>\n\n"
        "📌 Розклад на <b>понеділок - п'ятницю</b>\n"
        "📌 Доступні класи: <b>5-11</b>\n\n"
        "Оберіть клас:",
        parse_mode="HTML",
        reply_markup=main_menu()
    )

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(
        message.chat.id,
        "📖 <b>Інструкція:</b>\n\n"
        "1️⃣ Натисніть на клас\n"
        "2️⃣ Оберіть день тижня\n"
        "3️⃣ Отримайте розклад\n\n"
        "⚡ <b>Швидкі кнопки:</b>\n"
        "• <b>Сьогодні</b> - розклад на поточний день\n"
        "• <b>Завтра</b> - розклад на наступний день\n\n"
        "📰 <b>Новини</b> – останні повідомлення адміністрації\n\n"
        "🔄 Для повернення натисніть 'На головну'",
        parse_mode="HTML"
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == "main_menu":
        bot.edit_message_text(
            "🎓 <b>Оберіть клас:</b>",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=main_menu()
        )
        return
    if call.data == "news":
        show_news(call.message.chat.id, call.message.message_id, is_edit=True)
        return
    if call.data.startswith("class_"):
        cls = int(call.data.split("_")[1])
        bot.edit_message_text(
            f"📚 <b>{cls} клас</b>\n\nОберіть день:",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=day_menu(cls)
        )
        return
    if call.data.startswith("day_"):
        _, cls, day = call.data.split("_")
        cls, day = int(cls), int(day)
        show_schedule(call.message.chat.id, call.message.message_id, cls, day, is_edit=True)
        return
    if call.data.startswith("today_"):
        cls = int(call.data.split("_")[1])
        day = get_current_day()
        if day is None:
            bot.answer_callback_query(call.id, "Сьогодні вихідний! Оберіть інший день.", show_alert=True)
            return
        show_schedule(call.message.chat.id, call.message.message_id, cls, day, is_edit=True)
        return
    if call.data.startswith("tomorrow_"):
        cls = int(call.data.split("_")[1])
        today_num = datetime.now().weekday()
        if today_num >= 4:
            bot.answer_callback_query(call.id, "Завтра вихідний! Оберіть інший день.", show_alert=True)
            return
        tomorrow_day = today_num + 2
        show_schedule(call.message.chat.id, call.message.message_id, cls, tomorrow_day, is_edit=True)
        return

# ========== ФОН: ОПІВНІЧНЕ ОНОВЛЕННЯ ==========
def midnight_updater():
    while True:
        now = datetime.now()
        next_midnight = datetime(now.year, now.month, now.day) + timedelta(days=1)
        seconds_to_sleep = (next_midnight - now).total_seconds()
        time.sleep(seconds_to_sleep)
        print("🕛 [MIDNIGHT] Оновлення дати – кеш скинуто (актуальний розклад)")

# ========== HTTP-СЕРВЕР ДЛЯ RENDER HEALTH CHECK ==========
PORT = int(os.environ.get("PORT", 8000))

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health" or self.path == "/":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        else:
            self.send_response(404)
            self.end_headers()
    def log_message(self, format, *args):
        # Не засмічуємо логи
        pass

def run_http_server():
    server = HTTPServer(("0.0.0.0", PORT), HealthHandler)
    print(f"🌐 HTTP сервер запущено на порту {PORT} для health check")
    server.serve_forever()

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    print("✅ Бот розкладу запущений!")
    print("📋 Доступні класи: 5, 6, 7, 8, 9, 10, 11")
    print("👑 Адміни:", ADMIN_IDS if ADMIN_IDS else "не налаштовано")
    
    # Запускаємо потік опівнічного оновлення
    threading.Thread(target=midnight_updater, daemon=True).start()
    
    # Запускаємо HTTP-сервер в окремому потоці
    threading.Thread(target=run_http_server, daemon=True).start()
    
    # Основний потік – polling бота
    print("🤖 Бот починає опитування...")
    bot.infinity_polling()
