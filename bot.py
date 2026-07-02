from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
    FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
)
import asyncio
import os

TOKEN = "8898446620:AAFTw6J8f9ry0_sIWl55cyy2Ta439h8d8qk"
ADMIN_ID = 1107552133

bot = Bot(token=TOKEN)
dp = Dispatcher()

PHOTOS_DIR = r"C:\BlankBot\photos"

users = {}
orders_db = {}
order_counter = 1000

READY_PRODUCTS = {
    "Sakura Black": {"price": 799, "photo": "sakura_black.jpg.jpeg"},
    "No Win Black": {"price": 799, "photo": "no_win_black.jpg.png"},
    "Stussy White": {"price": 799, "photo": "stussy_white.jpg.PNG"},
    "Katana Black": {"price": 799, "photo": "katana_black.jpg.png"},
    "God White": {"price": 799, "photo": "god_white.jpg.png"},
}

CUSTOM_TSHIRTS = {
    "Classic Black 100%": 249,
    "Classic White 100%": 249,
    "Classic Black 95/5": 549,
    "Classic White 95/5": 549,
}

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👕 Каталог футболок")],
        [KeyboardButton(text="🎨 Свой дизайн")],
        [KeyboardButton(text="🛒 Корзина")],
        [KeyboardButton(text="🖨 Услуги печати")],
        [KeyboardButton(text="📞 Связаться с нами")]
    ],
    resize_keyboard=True
)

ready_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Sakura Black"), KeyboardButton(text="No Win Black")],
        [KeyboardButton(text="Stussy White"), KeyboardButton(text="Katana Black")],
        [KeyboardButton(text="God White")],
        [KeyboardButton(text="🛒 Корзина"), KeyboardButton(text="⬅️ Назад")]
    ],
    resize_keyboard=True
)

product_action_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Добавить в корзину")],
        [KeyboardButton(text="👕 Каталог футболок"), KeyboardButton(text="🛒 Корзина")],
        [KeyboardButton(text="⬅️ Назад")]
    ],
    resize_keyboard=True
)

custom_tshirt_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Classic Black 100%")],
        [KeyboardButton(text="Classic White 100%")],
        [KeyboardButton(text="Classic Black 95/5")],
        [KeyboardButton(text="Classic White 95/5")],
        [KeyboardButton(text="⬅️ Назад")]
    ],
    resize_keyboard=True
)

size_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="S"), KeyboardButton(text="M")],
        [KeyboardButton(text="L"), KeyboardButton(text="XL")],
        [KeyboardButton(text="⬅️ Назад")]
    ],
    resize_keyboard=True
)

quantity_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="1"), KeyboardButton(text="2"), KeyboardButton(text="3")],
        [KeyboardButton(text="4"), KeyboardButton(text="5")],
        [KeyboardButton(text="⬅️ Назад")]
    ],
    resize_keyboard=True
)

cart_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Оформить заказ")],
        [KeyboardButton(text="🗑 Очистить корзину")],
        [KeyboardButton(text="👕 Продолжить покупки")],
        [KeyboardButton(text="⬅️ Назад")]
    ],
    resize_keyboard=True
)

phone_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📱 Отправить номер", request_contact=True)],
        [KeyboardButton(text="⬅️ Назад")]
    ],
    resize_keyboard=True
)

confirm_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Подтвердить заказ")],
        [KeyboardButton(text="✏️ Изменить заказ")]
    ],
    resize_keyboard=True
)

services_text = """
🖨 Услуги печати

Цены указаны только за печать макета, без стоимости футболки.

🔹 Мини-принт до 5×5 см — 30 грн
🔹 Малый принт до 10×10 см — 50 грн
🔹 Средний принт до 15×15 см — 80 грн
🔹 Большой принт до 20×20 см — 120 грн
🔹 Формат A4 до 21×30 см — 180 грн
🔹 Формат A3 до 30×42 см — 300 грн
🔹 Принт на грудь или спину до 40×50 см — 450 грн
🔹 Макси-принт до 50×58 см — 650 грн
🔹 Полный принт до 58×58 см — 800 грн

✅ Разработка макета входит в цену.
📦 Также выполняем оптовый DTF-друк.
"""

def get_user(user_id):
    if user_id not in users:
        users[user_id] = {
            "cart": [],
            "draft": {},
            "checkout": {}
        }
    return users[user_id]

def user_info(message: Message):
    username = message.from_user.username
    return f"@{username}" if username else "не указан"

def cart_text(cart):
    if not cart:
        return "🛒 Ваша корзина пуста."

    total = 0
    text = "🛒 Ваша корзина:\n\n"

    for i, item in enumerate(cart, 1):
        item_total = item["price"] * int(item["quantity"])
        total += item_total

        text += (
            f"{i}. {item['product']}\n"
            f"📏 Размер: {item['size']}\n"
            f"🔢 Количество: {item['quantity']}\n"
            f"💰 Сумма: {item_total} грн\n\n"
        )

    text += f"────────────\n💵 Итого: {total} грн"
    return text

def admin_status_keyboard(order_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🟡 В обработке", callback_data=f"status:{order_id}:В обработке")],
            [InlineKeyboardButton(text="🟠 Печатается", callback_data=f"status:{order_id}:Печатается")],
            [InlineKeyboardButton(text="🔵 Готов", callback_data=f"status:{order_id}:Готов")],
            [InlineKeyboardButton(text="🚚 Отправлен", callback_data=f"status:{order_id}:Отправлен")]
        ]
    )

@dp.message(Command("start"))
async def start(message: Message):
    user = get_user(message.from_user.id)
    user["draft"] = {}
    user["checkout"] = {}

    await message.answer(
        "👋 Добро пожаловать в BLANK PRINT\n\nВыберите действие:",
        reply_markup=main_menu
    )

@dp.message(lambda m: m.text == "⬅️ Назад")
async def back(message: Message):
    user = get_user(message.from_user.id)
    user["draft"] = {}
    user["checkout"] = {}

    await message.answer("Главное меню:", reply_markup=main_menu)

@dp.message(lambda m: m.text == "👕 Продолжить покупки")
async def continue_shopping(message: Message):
    await catalog(message)

@dp.message(lambda m: m.text == "👕 Каталог футболок")
async def catalog(message: Message):
    text = "👕 Готовые футболки BLANK PRINT:\n\n"

    for name, data in READY_PRODUCTS.items():
        text += f"• {name} — {data['price']} грн\n"

    text += "\nВыберите модель ниже:"
    await message.answer(text, reply_markup=ready_menu)

@dp.message(lambda m: m.text in READY_PRODUCTS)
async def show_ready_product(message: Message):
    user = get_user(message.from_user.id)
    product_name = message.text
    product = READY_PRODUCTS[product_name]

    user["draft"] = {
        "type": "ready",
        "product": product_name,
        "price": product["price"],
        "photo": product["photo"],
        "step": "product_selected"
    }

    photo_path = os.path.join(PHOTOS_DIR, product["photo"])

    caption = f"""
👕 {product_name}

💰 Цена: {product['price']} грн

Нажмите «➕ Добавить в корзину».
"""

    if os.path.exists(photo_path):
        await message.answer_photo(
            photo=FSInputFile(photo_path),
            caption=caption,
            reply_markup=product_action_menu
        )
    else:
        await message.answer(
            f"{caption}\n⚠️ Фото не найдено:\n{photo_path}",
            reply_markup=product_action_menu
        )

@dp.message(lambda m: m.text == "➕ Добавить в корзину")
async def add_ready_start(message: Message):
    user = get_user(message.from_user.id)

    if not user["draft"]:
        await message.answer("Сначала выберите футболку.", reply_markup=ready_menu)
        return

    user["draft"]["step"] = "size"
    await message.answer("Выберите размер:", reply_markup=size_menu)

@dp.message(lambda m: m.text == "🎨 Свой дизайн")
async def custom_design(message: Message):
    user = get_user(message.from_user.id)
    user["draft"] = {
        "type": "custom",
        "step": "waiting_mockup"
    }

    await message.answer(
        "🎨 Заказ со своим дизайном\n\n"
        "Отправьте картинку, фото или файл с макетом.",
        reply_markup=ReplyKeyboardRemove()
    )

@dp.message(lambda m: m.photo or m.document)
async def get_mockup(message: Message):
    user = get_user(message.from_user.id)
    draft = user["draft"]

    if draft.get("step") != "waiting_mockup":
        return

    draft["mockup_message_id"] = message.message_id
    draft["step"] = "custom_tshirt"

    await message.answer(
        "✅ Макет получен.\n\nТеперь выберите футболку:",
        reply_markup=custom_tshirt_menu
    )

@dp.message(lambda m: m.text in CUSTOM_TSHIRTS)
async def choose_custom_tshirt(message: Message):
    user = get_user(message.from_user.id)
    draft = user["draft"]

    if not draft or draft.get("type") != "custom":
        return

    draft["product"] = message.text
    draft["price"] = CUSTOM_TSHIRTS[message.text]
    draft["step"] = "size"

    await message.answer("Выберите размер:", reply_markup=size_menu)

@dp.message(lambda m: m.text in ["S", "M", "L", "XL"])
async def choose_size(message: Message):
    user = get_user(message.from_user.id)
    draft = user["draft"]

    if not draft:
        await message.answer("Сначала выберите товар.", reply_markup=main_menu)
        return

    draft["size"] = message.text
    draft["step"] = "quantity"

    await message.answer("Выберите количество:", reply_markup=quantity_menu)

@dp.message(lambda m: m.text in ["1", "2", "3", "4", "5"])
async def choose_quantity(message: Message):
    user = get_user(message.from_user.id)
    draft = user["draft"]

    if not draft:
        return

    draft["quantity"] = message.text

    if draft["type"] == "custom":
        draft["step"] = "comment"
        await message.answer(
            "Напишите комментарий к макету.\n\nНапример: где разместить принт, размер печати, пожелания.",
            reply_markup=ReplyKeyboardRemove()
        )
        return

    user["cart"].append(draft.copy())
    user["draft"] = {}

    await message.answer(
        "✅ Товар добавлен в корзину.",
        reply_markup=cart_menu
    )
    await message.answer(cart_text(user["cart"]), reply_markup=cart_menu)

@dp.message(lambda m: m.text == "🛒 Корзина")
async def show_cart(message: Message):
    user = get_user(message.from_user.id)
    await message.answer(cart_text(user["cart"]), reply_markup=cart_menu)

@dp.message(lambda m: m.text == "🗑 Очистить корзину")
async def clear_cart(message: Message):
    user = get_user(message.from_user.id)
    user["cart"] = []
    user["draft"] = {}
    user["checkout"] = {}

    await message.answer("🗑 Корзина очищена.", reply_markup=main_menu)

@dp.message(lambda m: m.text == "✅ Оформить заказ")
async def checkout_start(message: Message):
    user = get_user(message.from_user.id)

    if not user["cart"]:
        await message.answer("Корзина пустая.", reply_markup=main_menu)
        return

    user["checkout"] = {"step": "name"}

    await message.answer("Введите имя:", reply_markup=ReplyKeyboardRemove())

@dp.message(lambda m: m.contact)
async def get_contact(message: Message):
    user = get_user(message.from_user.id)
    checkout = user["checkout"]

    if checkout.get("step") != "phone":
        return

    checkout["phone"] = message.contact.phone_number
    checkout["step"] = "confirm"

    await message.answer(
        make_confirm_text(user["cart"], checkout),
        reply_markup=confirm_menu
    )

def make_confirm_text(cart, checkout):
    total = sum(item["price"] * int(item["quantity"]) for item in cart)

    text = "📋 Проверьте заказ\n\n"
    text += cart_text(cart)
    text += f"""

👤 Имя: {checkout.get('name')}
📱 Телефон: {checkout.get('phone')}

✅ Если всё верно, подтвердите заказ.
"""
    return text

@dp.message(lambda m: m.text == "✅ Подтвердить заказ")
async def confirm_order(message: Message):
    user = get_user(message.from_user.id)

    if not user["cart"] or user["checkout"].get("step") != "confirm":
        await message.answer("Заказ не найден. Начните заново.", reply_markup=main_menu)
        return

    global order_counter
    order_counter += 1
    order_id = order_counter

    total = sum(item["price"] * int(item["quantity"]) for item in user["cart"])

    orders_db[order_id] = {
        "client_id": message.from_user.id,
        "cart": user["cart"].copy(),
        "name": user["checkout"]["name"],
        "phone": user["checkout"]["phone"],
        "total": total,
        "status": "Принят"
    }

    text = f"""
🔥 Новый заказ BLANK PRINT

🧾 Номер заказа: #{order_id}

{cart_text(user["cart"])}

👤 Имя: {user["checkout"]["name"]}
📱 Телефон: {user["checkout"]["phone"]}
💬 Telegram: {user_info(message)}
🆔 ID клиента: {message.from_user.id}

Статус: 🟡 Принят
"""

    await bot.send_message(
        ADMIN_ID,
        text,
        reply_markup=admin_status_keyboard(order_id)
    )

    for item in user["cart"]:
        if item.get("type") == "custom" and item.get("mockup_message_id"):
            await bot.copy_message(
                chat_id=ADMIN_ID,
                from_chat_id=message.from_user.id,
                message_id=item["mockup_message_id"]
            )

    await message.answer(
        f"✅ Заказ №{order_id} принят!\n\nСтатус: 🟡 В обработке\n\nМы скоро свяжемся с вами.",
        reply_markup=main_menu
    )

    user["cart"] = []
    user["draft"] = {}
    user["checkout"] = {}

@dp.message(lambda m: m.text == "✏️ Изменить заказ")
async def edit_order(message: Message):
    user = get_user(message.from_user.id)
    user["checkout"] = {}

    await message.answer("Можете изменить корзину или продолжить покупки.", reply_markup=cart_menu)

@dp.message(lambda m: m.text == "🖨 Услуги печати")
async def print_services(message: Message):
    await message.answer(services_text, reply_markup=main_menu)

@dp.message(lambda m: m.text == "📞 Связаться с нами")
async def contact_us(message: Message):
    user = get_user(message.from_user.id)
    user["draft"] = {"type": "contact", "step": "message"}

    await message.answer(
        "📞 Напишите ваше сообщение.\n\nОно сразу придёт менеджеру.",
        reply_markup=ReplyKeyboardRemove()
    )

@dp.callback_query(F.data.startswith("status:"))
async def change_status(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа.")
        return

    _, order_id_text, status = callback.data.split(":")
    order_id = int(order_id_text)

    if order_id not in orders_db:
        await callback.answer("Заказ не найден.")
        return

    orders_db[order_id]["status"] = status
    client_id = orders_db[order_id]["client_id"]

    await bot.send_message(
        client_id,
        f"🔔 Статус заказа #{order_id} обновлён:\n\n{status}"
    )

    await callback.answer("Статус обновлён.")

@dp.message()
async def process_text(message: Message):
    user = get_user(message.from_user.id)
    draft = user["draft"]
    checkout = user["checkout"]

    if draft.get("type") == "contact":
        text = f"""
💬 Новое сообщение от клиента

Сообщение:
{message.text}

Telegram: {user_info(message)}
ID клиента: {message.from_user.id}
"""
        await bot.send_message(ADMIN_ID, text)
        await message.answer("✅ Сообщение отправлено менеджеру.", reply_markup=main_menu)
        user["draft"] = {}
        return

    if draft.get("step") == "comment":
        draft["comment"] = message.text
        user["cart"].append(draft.copy())
        user["draft"] = {}

        await message.answer("✅ Заказ со своим дизайном добавлен в корзину.", reply_markup=cart_menu)
        await message.answer(cart_text(user["cart"]), reply_markup=cart_menu)
        return

    if checkout.get("step") == "name":
        checkout["name"] = message.text
        checkout["step"] = "phone"

        await message.answer("Отправьте телефон:", reply_markup=phone_menu)
        return

    if checkout.get("step") == "phone":
        checkout["phone"] = message.text
        checkout["step"] = "confirm"

        await message.answer(
            make_confirm_text(user["cart"], checkout),
            reply_markup=confirm_menu
        )
        return

    await message.answer("Выберите действие в меню:", reply_markup=main_menu)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())