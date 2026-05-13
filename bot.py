import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
import os
import threading
import time
from flask import Flask, request
import json

# ========== ТОКЕН БОТА ==========
TOKEN = "8700545809:AAH6FyZB7Hdv5l_-CpIiFzshct7SdlOPo_k"
bot = telebot.TeleBot(TOKEN)

# ========== АДМІНИ (з Render) ==========
ADMIN_IDS = [int(id.strip()) for id in os.getenv("ADMIN_IDS", "").split(",") if id.strip()]
if not ADMIN_IDS:
    print("⚠️ Увага! Жодного адміна не налаштовано. Додайте змінну ADMIN_IDS.")

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

# ========== РОЗКЛАД ВЧИТЕЛІВ ==========
teachers_schedule = {
    "Баглай О.Д.": {
        1: {2: ["7"], 4: ["8"], 5: ["9"]},
        2: {4: ["10"]},
        3: {3: ["7"], 4: ["9"], 5: ["8"]},
        5: {4: ["10"]}
    },
    "Белей О.Є.": {
        1: {1: ["6"], 2: ["8а"], 3: ["9а"]},
        2: {3: ["9а"], 4: ["11"], 5: ["6"], 6: ["8а"]},
        3: {3: ["9а"], 4: ["11"], 5: ["6"]},
        4: {1: ["8а"], 2: ["6"], 3: ["9а"], 5: ["11"]},
        5: {1: ["8а"], 2: ["11"], 5: ["11"], 6: ["6"]}
    },
    "Боднар М.Р.": {
        1: {1: ["3"], 2: ["7"], 4: ["8"], 5: ["9"], 6: ["3"], 7: ["6"]},
        2: {1: ["4"], 2: ["10"]},
        3: {1: ["5"], 3: ["7"], 4: ["9"], 5: ["8"], 6: ["4"], 7: ["5"]},
        5: {1: ["2"], 3: ["10"], 5: ["11"], 6: ["2"], 7: ["6"]}
    },
    "Ванярх Ю.М.": {
        1: {1: ["8"], 2: ["11"], 3: ["6"], 4: ["7"], 5: ["5"]},
        2: {1: ["6"], 2: ["7"], 5: ["8"], 7: ["10"]},
        3: {1: ["11"], 4: ["10"], 6: ["5"]},
        4: {1: ["10"], 2: ["8"], 3: ["6"], 4: ["7"], 5: ["5"], 6: ["11"]}
    },
    "Горбачевська У.А.": {
        1: {1: ["7м"], 2: ["5м"], 4: ["6м"], 5: ["6л"], 6: ["5л"]},
        2: {1: ["7л"], 2: ["6м"], 3: ["5м"]},
        3: {1: ["7м"], 3: ["6л"], 4: ["5м"]},
        4: {1: ["6м"], 2: ["5м"], 4: ["8д"], 5: ["5л"]},
        5: {5: ["6м"], 6: ["7м"], 7: ["5д"], 8: ["7л"]}
    },
    "Григорчук С.Р.": {
        1: {6: ["3ін"]},
        2: {4: ["1ін"], 5: ["2ін"]},
        4: {6: ["2"]},
        5: {6: ["3"], 8: ["4"]}
    },
    "Гудима О.Р.": {
        1: {3: ["10"], 4: ["5"], 5: ["7а"]},
        2: {4: ["5"], 5: ["7а"], 6: ["10"]},
        3: {2: ["10"], 3: ["5"], 6: ["7а"]},
        4: {3: ["7а"], 4: ["2"], 5: ["5"]},
        5: {1: ["7а"], 2: ["5"]}
    },
    "Гуменний Р.Є.": {
        1: {3: ["5м"], 6: ["6н"]},
        2: {3: ["8т"], 4: ["6т"], 5: ["10т"], 7: ["5м"], 8: ["8н"]},
        3: {1: ["9м"], 2: ["9к"], 6: ["5т"], 8: ["9м"]},
        4: {6: ["6н"], 7: ["7м"]},
        5: {8: ["7м"]}
    },
    "Івахів Б.І.": {
        2: {1: ["11"], 6: ["7"]},
        3: {7: ["11"]},
        5: {5: ["9м"], 6: ["9к"], 7: ["9л"], 8: ["10д"]}
    },
    "Іськів Т.М.": {
        1: {1: ["9м"], 2: ["9м"]},
        2: {4: ["9м"], 5: ["9м"], 7: ["9"]},
        4: {6: ["6"]},
        5: {6: ["6"], 8: ["9м"]}
    },
    "Клапко М.-М.О.": {
        4: {1: ["9у"], 4: ["6 зб"], 6: ["9о"], 7: ["7п"]},
        5: {1: ["5 зб"], 8: ["10п"]}
    },
    "Корда Г.З.": {
        1: {6: ["8п"], 7: ["7зб"]},
        2: {1: ["9б"]},
        3: {5: ["7"], 6: ["10"], 7: ["11а"], 8: ["9"]},
        4: {2: ["9"], 3: ["10"], 4: ["11"]}
    },
    "Кусьнеж О.Я.": {
        1: {3: ["8"], 4: ["10"], 6: ["11"], 7: ["9"]},
        2: {4: ["11"], 5: ["8"], 7: ["7"]}
    },
    "Москалюк У.І.": {
        3: {4: ["9"], 7: ["8"], 8: ["10/11"]},
        5: {6: ["2"], 7: ["3"], 8: ["9"]}
    },
    "Олексин О.В.": {
        2: {3: ["3"], 4: ["2"], 7: ["9"]},
        3: {3: ["3"], 4: ["2"], 6: ["9"]},
        5: {5: ["5н"], 6: ["7"], 7: ["6"], 8: ["8"]}
    },
    "Пастух А.М.": {
        1: {1: ["10"], 6: ["11"], 7: ["9"]},
        3: {6: ["6"], 7: ["10"], 8: ["5"]},
        4: {1: ["5н"], 5: ["7"], 6: ["8"], 7: ["9"]},
        5: {5: ["5н"]}
    },
    "Пекарська О.А.": {
        1: {1: ["9"], 2: ["6"], 3: ["7"], 4: ["2"]},
        2: {2: ["3"], 3: ["11"], 4: ["7"], 5: ["6"], 6: ["9"]},
        4: {1: ["7"], 2: ["11"], 5: ["3"], 6: ["6"]},
        5: {1: ["6"], 2: ["2"], 3: ["9"], 4: ["3"], 5: ["7"], 6: ["11"]}
    },
    "Сабадашка Н.Д.": {
        1: {1: ["5"], 2: ["9"], 3: ["4"], 4: ["2"], 6: ["8"]},
        2: {1: ["8"], 2: ["5"], 3: ["4"], 5: ["9"], 6: ["10"]},
        3: {2: ["6"], 3: ["5"], 4: ["10"], 5: ["2"]},
        5: {1: ["4"], 2: ["9"], 3: ["2"], 4: ["8"], 5: ["5"], 6: ["10"]}
    },
    "Савостьянов Р.В.": {
        2: {1: ["5"], 2: ["3"], 3: ["2"], 7: ["8"]},
        3: {4: ["6"], 6: ["4"], 7: ["9"], 8: ["2"]}
    },
    "Стегній М.М.": {
        1: {4: ["11"], 7: ["10"], 8: ["3б"]},
        2: {4: ["10"], 6: ["5"], 7: ["6"]},
        3: {3: ["7б"], 4: ["8б"], 5: ["11"]},
        4: {4: ["7б"], 5: ["8го"], 7: ["10"], 8: ["10б"]},
        5: {1: ["11"], 2: ["10"], 5: ["6"], 7: ["8б"], 8: ["10г"]}
    },
    "Федишин М.Т.": {
        1: {1: ["11м"], 2: ["10м"], 4: ["11л"], 5: ["10л"]},
        3: {3: ["11л"], 4: ["11м"], 5: ["8м"], 7: ["10л"], 8: ["8л"]},
        4: {1: ["11л"], 2: ["10м"], 3: ["11л"], 4: ["10л"], 5: ["8м"], 8: ["8л"]},
        5: {1: ["10л"], 2: ["8м"], 3: ["11м"], 4: ["10м"]}
    },
    "Цибульська Н.М.": {
        1: {4: ["9б"], 6: ["10б"], 7: ["11к"]},
        2: {1: ["10к"], 2: ["9к"], 3: ["8б"], 4: ["7б"], 5: ["11б"]},
        3: {1: ["10г"], 2: ["8к"], 6: ["7б"], 7: ["11"], 8: ["11"]},
        5: {1: ["9б"], 2: ["7к"], 3: ["8б"], 4: ["11б"], 5: ["8к"], 6: ["9к"], 7: ["11к"]}
    },
    "Ліцей ЗУ": {
        1: {7: ["10"], 8: ["10"]},
        2: {6: ["11"], 7: ["11"]},
        3: {7: ["11"], 8: ["11"]}
    }
}

teachers_list = sorted(teachers_schedule.keys())

# ========== РОЗКЛАД ==========
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
    markup.add(InlineKeyboardButton("👨‍🏫 Розклад вчителів", callback_data="teachers"))
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

def teachers_menu(page=0):
    """Створює меню з вчителями з пагінацією"""
    markup = InlineKeyboardMarkup(row_width=1)
    
    items_per_page = 8
    start_idx = page * items_per_page
    end_idx = min(start_idx + items_per_page, len(teachers_list))
    
    for i in range(start_idx, end_idx):
        teacher = teachers_list[i]
        markup.add(InlineKeyboardButton(teacher, callback_data=f"teacher_{i}"))
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"teachers_page_{page-1}"))
    if end_idx < len(teachers_list):
        nav_buttons.append(InlineKeyboardButton("Вперед ➡️", callback_data=f"teachers_page_{page+1}"))
    
    if nav_buttons:
        markup.add(*nav_buttons)
    
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

def show_teacher_schedule(chat_id, message_id, teacher_name, is_edit=True):
    schedule_data = teachers_schedule.get(teacher_name, {})
    
    if not schedule_data:
        text = f"👨‍🏫 <b>{teacher_name}</b>\n\n❌ Розклад відсутній"
    else:
        text = f"👨‍🏫 <b>{teacher_name}</b>\n\n"
        
        for day_num in [1, 2, 3, 4, 5]:
            if day_num in schedule_data:
                day_lessons = schedule_data[day_num]
                text += f"{days_ua[day_num]}:\n"
                
                sorted_lessons = sorted(day_lessons.items())
                for lesson_num, classes in sorted_lessons:
                    time_str = time_slots.get(lesson_num, "???")
                    classes_str = ", ".join(classes)
                    text += f"  {lesson_num}. {time_str} - {classes_str} кл.\n"
                text += "\n"
            else:
                text += f"{days_ua[day_num]}:\n  —\n\n"
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙 До списку вчителів", callback_data="teachers"))
    markup.add(InlineKeyboardButton("🏠 Головне меню", callback_data="main_menu"))
    
    if is_edit:
        bot.edit_message_text(text, chat_id, message_id, parse_mode="HTML", reply_markup=markup)
    else:
        bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)

# ========== ОСНОВНІ ОБРОБНИКИ ==========
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🎓 <b>Вітаю в боті розкладу!</b>\n\n"
        "📌 Розклад на <b>понеділок - п'ятницю</b>\n"
        "📌 Доступні класи: <b>5-11</b>\n"
        "📌 Розклад вчителів\n\n"
        "Оберіть потрібний розділ:",
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
        "👨‍🏫 <b>Розклад вчителів</b> – перегляд розкладу викладачів\n\n"
        "🔄 Для повернення натисніть 'На головну'",
        parse_mode="HTML"
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    # Головне меню
    if call.data == "main_menu":
        bot.edit_message_text(
            "🎓 <b>Оберіть розділ:</b>",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=main_menu()
        )
        return

    # Розклад вчителів (список)
    if call.data == "teachers":
        bot.edit_message_text(
            "👨‍🏫 <b>Оберіть вчителя:</b>",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=teachers_menu(page=0)
        )
        return

    # Пагінація вчителів
    if call.data.startswith("teachers_page_"):
        page = int(call.data.split("_")[2])
        bot.edit_message_text(
            "👨‍🏫 <b>Оберіть вчителя:</b>",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=teachers_menu(page)
        )
        return

    # Конкретний вчитель
    if call.data.startswith("teacher_"):
        index = int(call.data.split("_")[1])
        if 0 <= index < len(teachers_list):
            teacher = teachers_list[index]
            show_teacher_schedule(call.message.chat.id, call.message.message_id, teacher, is_edit=True)
        else:
            bot.answer_callback_query(call.id, "Вчителя не знайдено", show_alert=True)
        return

    # Клас
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

    # День
    if call.data.startswith("day_"):
        _, cls, day = call.data.split("_")
        cls, day = int(cls), int(day)
        show_schedule(call.message.chat.id, call.message.message_id, cls, day, is_edit=True)
        return

    # Сьогодні
    if call.data.startswith("today_"):
        cls = int(call.data.split("_")[1])
        day = get_current_day()
        if day is None:
            bot.answer_callback_query(call.id, "Сьогодні вихідний! Оберіть інший день.", show_alert=True)
            return
        show_schedule(call.message.chat.id, call.message.message_id, cls, day, is_edit=True)
        return

    # Завтра
    if call.data.startswith("tomorrow_"):
        cls = int(call.data.split("_")[1])
        today_num = datetime.now().weekday()
        if today_num >= 4:
            bot.answer_callback_query(call.id, "Завтра вихідний! Оберіть інший день.", show_alert=True)
            return
        tomorrow_day = today_num + 2
        show_schedule(call.message.chat.id, call.message.message_id, cls, tomorrow_day, is_edit=True)
        return

# ========== FLASK + WEBHOOK ==========
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        if request.headers.get('content-type') == 'application/json':
            data = request.get_json()
            print(f"DEBUG: отримано update_id: {data.get('update_id')}")
            update = telebot.types.Update.de_json(data)
            if update:
                bot.process_new_updates([update])
                print("DEBUG: обробка успішна")
            else:
                print("DEBUG: не вдалося створити Update")
            return '', 200
        return '', 403
    except Exception as e:
        print(f"ERROR in webhook: {e}")
        return '', 500

@app.route('/health', methods=['GET'])
def health():
    return 'OK', 200

@app.route('/')
def index():
    return 'OK', 200

# ========== ЗАПУСК ==========
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    
    render_url = os.environ.get('RENDER_EXTERNAL_URL')
    if render_url:
        webhook_url = f"{render_url}/webhook"
        bot.remove_webhook()
        bot.set_webhook(url=webhook_url)
        print(f"✅ Вебхук встановлено: {webhook_url}")
    else:
        print("⚠️ RENDER_EXTERNAL_URL не знайдено, вебхук не встановлено.")
    
    print("✅ Бот запущено в режимі вебхука (Flask)")
    print(f"🌐 Слухаємо на порту {port}")
    app.run(host='0.0.0.0', port=port)
