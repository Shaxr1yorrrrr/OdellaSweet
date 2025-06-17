from telethon import TelegramClient, events, Button

API_ID = 12345
API_HASH = "0123456789abcdef0123456789abcdef"
BOT_TOKEN = "7741982658:AAGD-o2oXnDnJLZtXfUjF5jZWuhLvVaBUso"

# In‑memory storage
customers = {}
orders = {}

# Your branch and menu data...
BRANCHES = { ... }  # same as before
MENU = { ... }      # same as before

# Initialize bot client
bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    reply = "Assalomu aleykum!\nShare your phone number to start."
    buttons = [[Button.request_phone("Share Phone")]]
    await event.respond(reply, buttons=buttons)

@bot.on(events.NewMessage(func=lambda e: e.message.phone))
async def phone_handler(event):
    user_id = event.sender_id
    customers[user_id] = event.message.phone
    orders[user_id] = []
    kb = [
        [Button.text("🍓 Fruit Desserts"), Button.text("🍰 Chocolate Cakes")],
        [Button.text("🛒 View Order")],
        [Button.text("🏢 Our branches"), Button.text("📞 Support")]
    ]
    await event.respond("Thank you! Here's the menu:", buttons=kb)

@bot.on(events.NewMessage())
async def menu_handler(event):
    text = event.message.text
    user_id = event.sender_id

    if text in ["🍓 Fruit Desserts", "🍰 Chocolate Cakes"]:
        category = "Fruit_Desserts" if "Fruit" in text else "Chocolate_Cakes"
        buttons = [[Button.inline(item, f"{category}|{item}")] for item in MENU[category]]
        await event.respond("Choose item:", buttons=buttons)

    elif text == "🛒 View Order":
        # Summarize orders as before (string logic)
        summary, kb = build_order_summary(orders.get(user_id, []))
        await event.respond(summary, buttons=kb)

    elif text == "🏢 Our branches":
        kb = [[Button.text(name)] for name in BRANCHES]
        await event.respond("Choose branch:", buttons=kb)

    elif text in BRANCHES:
        info = BRANCHES[text]
        await event.respond(
            f"{text}\nHours: {info['hours']}\nPhone: {info['phone']}\n{info['maps_link']}"
        )

    elif text == "📞 Support":
        await event.respond("Contact us:\nTelegram: @odellasweetadmin\nPhone: +998722160606")

@bot.on(events.CallbackQuery)
async def callback_handler(event):
    data = event.data.decode()
    user_id = event.sender_id

    if "|" in data:
        category, item = data.split("|")
        await event.respond(f"{item}: {MENU[category][item]['description']} — {MENU[category][item]['price']}",
                            buttons=[
                                [Button.inline("🛒 Order", f"order|{category}|{item}")],
                                [Button.inline("⬅️ Back", f"back|{category}")]
                            ])

    elif data.startswith("order|"):
        _, category, item = data.split("|")
        buttons = [ [Button.inline(str(i), f"qty|{category}|{item}|{i}") for i in [1,2,3]] ]
        await event.respond("Select quantity:", buttons=buttons)

    elif data.startswith("qty|"):
        _, category, item, qty = data.split("|")
        orders.setdefault(user_id, []).append(f"{item} x{qty} ({MENU[category][item]['price']})")
        await event.respond(f"Added {qty}x {item} to your order!",
                            buttons=[[Button.inline("🛒 View Order", "view_order")]])

    elif data == "view_order":
        summary, kb = build_order_summary(orders.get(user_id, []))
        await event.respond(summary, buttons=kb)

    elif data.startswith("back|"):
        _, category = data.split("|")
        buttons = [[Button.inline(it, f"{category}|{it}")] for it in MENU[category]]
        await event.respond("Back to items:", buttons=buttons)

def build_order_summary(item_list):
    if not item_list:
        return "Your order is empty.", [[Button.inline("🍓 Fruit Desserts", "back|Fruit_Desserts"),
                                         Button.inline("🍰 Chocolate Cakes", "back|Chocolate_Cakes")]]
    summary, total = "", 0
    counts = {}
    for entry in item_list:
        name, rest = entry.split(" x")
        qty = int(rest.split(" ")[0])
        price = float(rest.split("$")[1].strip(")"))
        counts.setdefault(name, [0, price])[0] += qty
        total += qty * price
    for name,(qty, price) in counts.items():
        summary += f"{name} x{qty} (${price})\n"
    summary += f"\nTotal: ${total:.2f}"
    kb = [[Button.inline("🍓 Fruit Desserts", "back|Fruit_Desserts"),
           Button.inline("🍰 Chocolate Cakes", "back|Chocolate_Cakes")]]
    return summary, kb

if __name__ == "__main__":
    print("Bot started!")
    bot.run_until_disconnected()
