from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, CallbackContext

TOKEN = "7741982658:AAGD-o2oXnDnJLZtXfUjF5jZWuhLvVaBUso"

# In-memory storage
customers = {}
orders = {}

# Branch locations info
BRANCHES = {
    "📍 Tashkent City Mall": {
        "phone": "+998722160611",
        "hours": "11:00AM - 11:30PM",
        "maps_link": "https://maps.google.com/?q=41.311081,69.240562"
    },
    "📍 Compass Mall": {
        "phone": "+998722160612", 
        "hours": "11:00AM - 11:30PM",
        "maps_link": "https://maps.google.com/?q=41.338896,69.334247"
    },
    "📍 Samarkand Darvoza": {
        "phone": "+998722160613",
        "hours": "11:00AM - 11:30PM", 
        "maps_link": "https://maps.google.com/?q=41.285529,69.204406"
    },
    "📍 Parkent Mall": {
        "phone": "+998722160614",
        "hours": "11:00AM - 11:30PM",
        "maps_link": "https://maps.google.com/?q=41.325562,69.344947"
    }
}

# Product categories and items with descriptions and prices
MENU = {
    "Fruit_Desserts": {
        "Fresh Fruit Cake": {
            "description": "Colorful cake with raspberry, strawberry, kiwi, and mango",
            "price": "$8.99"
        },
        "Apple Pie": {
            "description": "Traditional pie with cinnamon-spiced apples and golden crust",
            "price": "$7.99"
        },
        "Peach Cheesecake": {
            "description": "Smooth cheesecake topped with sweet peach slices",
            "price": "$9.99"
        },
        "Banana Cake": {
            "description": "Soft cake bursting with ripe banana flavor",
            "price": "$6.99"
        },
        "Strawberry Napoleon": {
            "description": "Flaky pastry layered with strawberries and whipped cream",
            "price": "$8.99"
        }
    },
    "Chocolate_Cakes": {
        "Sachertorte": {
            "description": "Austrian chocolate cake with apricot jam",
            "price": "$8.99"
        },
        "Prague Cake": {
            "description": "One of the Russian desserts, with chocolate cream and glaze",
            "price": "$7.99"
        },
        "Brownie Cake": {
            "description": "Made with a moist chocolate sponge cake",
            "price": "$6.99"
        },
        "Black Forest Cake": {
            "description": "Chocolate sponge cake with cherries and cream",
            "price": "$9.99"
        },
        "Mud Cake": {
            "description": "Very moist and rich chocolate cake",
            "price": "$7.99"
        }
    }
}

# Start command
async def start(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    contact_keyboard = [[KeyboardButton("Share Phone Number", request_contact=True)]]
    
    reply_markup = ReplyKeyboardMarkup(
        contact_keyboard,
        resize_keyboard=True
    )
    await update.message.reply_text("Assalomu aleykum\n\nOdellasweet bot makes ordering sweets simple! View our menu, place an order, and get delivery info in seconds.\n\nPlease share your phone number to continue.", reply_markup=reply_markup)

# Handle phone number
async def phone_handler(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    phone = update.message.contact.phone_number
    
    customers[user_id] = phone
    orders[user_id] = []
    
    menu_keyboard = [
        ["🍓 Fruit Desserts", "🍰 Chocolate Cakes"],
        ["🛒 View Order"],["🏢Our branches","📞Support"]
    ]
    reply_markup = ReplyKeyboardMarkup(
        menu_keyboard,
        resize_keyboard=True
    )
    
    # Remove the contact keyboard and show menu keyboard
    await update.message.reply_text("Thank you! You can now use the menu buttons to place your order.", reply_markup=reply_markup)

# Handle text messages for menu selections
async def message_handler(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    user_id = update.message.from_user.id

    if text == "🍓 Fruit Desserts":
        keyboard = [
            [InlineKeyboardButton(dessert, callback_data=f"fruit_{dessert}")]
            for dessert in MENU["Fruit_Desserts"].keys()
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Select a dessert:", reply_markup=reply_markup)
    
    elif text == "🍰 Chocolate Cakes":
        keyboard = [
            [InlineKeyboardButton(cake, callback_data=f"cake_{cake}")]
            for cake in MENU["Chocolate_Cakes"].keys()
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Select a cake:", reply_markup=reply_markup)
    
    elif text == "🛒 View Order":
        if user_id in orders and orders[user_id]:
            # Create a dictionary to count items and calculate total price
            order_summary = {}
            total_price = 0
            
            for order in orders[user_id]:
                item_name = order.split(" x")[0]
                quantity = int(order.split("x")[1].split(" ")[0])
                price = float(order.split("$")[1].strip(")"))
                
                if item_name in order_summary:
                    order_summary[item_name]["qty"] += quantity
                else:
                    order_summary[item_name] = {
                        "qty": quantity,
                        "price": price
                    }
                total_price += quantity * price
            
            # Format the order summary
            order_list = []
            for item, details in order_summary.items():
                order_list.append(f"{item} x{details['qty']} (${details['price']})")
            
            order_text = "\n".join(order_list)
            order_text += f"\n\nTotal: ${total_price:.2f}"
            
            # Create inline keyboard with view more buttons
            keyboard = [
                [InlineKeyboardButton("🍓 View More Desserts", callback_data="back_to_fruit"),
                 InlineKeyboardButton("🍰 View More Cakes", callback_data="back_to_cakes")],
                [InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(f"Your order:\n{order_text}", reply_markup=reply_markup)
        else:
            # Show empty cart message with view more buttons
            keyboard = [
                [InlineKeyboardButton("🍓 View More Desserts", callback_data="back_to_fruit"),
                 InlineKeyboardButton("🍰 View More Cakes", callback_data="back_to_cakes")],
                [InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("Your order is empty.", reply_markup=reply_markup)
    
    elif text == "🍓 View More Desserts" or (update.callback_query and update.callback_query.data == "view_more_desserts"):
        keyboard = [
            [InlineKeyboardButton(dessert, callback_data=f"fruit_{dessert}")]
            for dessert in MENU["Fruit_Desserts"].keys()
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Select a dessert:", reply_markup=reply_markup)

    elif text == "🍰 View More Cakes" or (update.callback_query and update.callback_query.data == "view_more_cakes"):
        keyboard = [
            [InlineKeyboardButton(cake, callback_data=f"cake_{cake}")]
            for cake in MENU["Chocolate_Cakes"].keys()
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Select a cake:", reply_markup=reply_markup)
    elif text == "🏢Our branches":
        locations_keyboard = [
            ["📍 Tashkent City Mall", "📍 Samarkand Darvoza"],
            ["📍 Compass Mall", "📍 Parkent Mall"],
            ["⬅️ Back to Menu"]
        ]
        reply_markup = ReplyKeyboardMarkup(
            locations_keyboard,
            resize_keyboard=True
        )
        await update.message.reply_text("Select a branch location:", reply_markup=reply_markup)
    elif text in BRANCHES:
        branch_info = BRANCHES[text]
        info_text = (
            f"Branch: {text}\n"
            f"Working Hours: {branch_info['hours']}\n"
            f"Phone: {branch_info['phone']}\n"
            f"Location: {branch_info['maps_link']}"
        )
        await update.message.reply_text(info_text)
    elif text=="📞Support":
        support_text = (
            "Contact us:\n\n"
            "Telegram: @odellasweetadmin\n"
            "Phone: +998722160606\n" 
            "E-mail: odellasweet@gmail.com"
        )
        await update.message.reply_text(support_text)
        
    elif text == "⬅️ Back to Menu":
        menu_keyboard = [
            ["🍓 Fruit Desserts", "🍰 Chocolate Cakes"],
            ["🛒 View Order"],["🏢Our branches","📞Support"]
        ]
        reply_markup = ReplyKeyboardMarkup(
            menu_keyboard,
            resize_keyboard=True
        )
        await update.message.reply_text("Main Menu:", reply_markup=reply_markup)

# Handle product selection
async def button_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    selection = query.data
    
    if selection.startswith("fruit_"):
        dessert = selection.replace("fruit_", "")
        dessert_info = MENU["Fruit_Desserts"][dessert]
        keyboard = [
            [InlineKeyboardButton("🛒 Order", callback_data=f"order_fruit_{dessert}")],
            [InlineKeyboardButton("⬅️ Back to Desserts", callback_data="back_to_fruit")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"🍓 {dessert}\n\n"
            f"Description: {dessert_info['description']}\n"
            f"Price: {dessert_info['price']}\n\n"
            f"Would you like to order this dessert?",
            reply_markup=reply_markup
        )
    elif selection.startswith("order_fruit_"):
        dessert = selection.replace("order_fruit_", "")
        keyboard = []
        # Create rows of 3 buttons each for numbers 1-9
        for i in range(0, 9, 3):
            row = []
            for j in range(1, 4):
                if i + j <= 9:
                    row.append(InlineKeyboardButton(str(i + j), callback_data=f"qty_fruit_{dessert}_{i+j}"))
            keyboard.append(row)
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data=f"fruit_{dessert}")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Please select quantity:", reply_markup=reply_markup)
    elif selection.startswith("qty_fruit_"):
        _, _, dessert, qty = selection.split("_")
        dessert_info = MENU["Fruit_Desserts"][dessert]
        orders[user_id].append(f"{dessert} x{qty} ({dessert_info['price']})")
        keyboard = [
            [InlineKeyboardButton("🛒 View Order", callback_data="view_order")],
            [InlineKeyboardButton("🍓 More Fruit Desserts", callback_data="back_to_fruit")],
            [InlineKeyboardButton("🍰 View Chocolate Cakes", callback_data="back_to_cakes")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(f"Added {qty}x {dessert} to your order!", reply_markup=reply_markup)
    elif selection.startswith("cake_"):
        cake = selection.replace("cake_", "")
        cake_info = MENU["Chocolate_Cakes"][cake]
        keyboard = [
            [InlineKeyboardButton("🛒 Order", callback_data=f"order_cake_{cake}")],
            [InlineKeyboardButton("⬅️ Back to Cakes", callback_data="back_to_cakes")]
            
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"🍰 {cake}\n\n"
            f"Description: {cake_info['description']}\n"
            f"Price: {cake_info['price']}\n\n"
            f"Would you like to order this cake?",
            reply_markup=reply_markup
        )
    elif selection.startswith("order_cake_"):
        cake = selection.replace("order_cake_", "")
        keyboard = []
        # Create rows of 3 buttons each for numbers 1-9
        for i in range(0, 9, 3):
            row = []
            for j in range(1, 4):
                if i + j <= 9:
                    row.append(InlineKeyboardButton(str(i + j), callback_data=f"qty_cake_{cake}_{i+j}"))
            keyboard.append(row)
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data=f"cake_{cake}")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Please select quantity:", reply_markup=reply_markup)
    elif selection.startswith("qty_cake_"):
        _, _, cake, qty = selection.split("_")
        cake_info = MENU["Chocolate_Cakes"][cake]
        orders[user_id].append(f"{cake} x{qty} ({cake_info['price']})")
        keyboard = [
            [InlineKeyboardButton("🛒 View Order", callback_data="view_order")],
            [InlineKeyboardButton("🍰 More Chocolate Cakes", callback_data="back_to_cakes")],
            [InlineKeyboardButton("🍓 View Fruit Desserts", callback_data="back_to_fruit")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(f"Added {qty}x {cake} to your order!", reply_markup=reply_markup)
    elif selection == "back_to_fruit":
        keyboard = [
            [InlineKeyboardButton(dessert, callback_data=f"fruit_{dessert}")]
            for dessert in MENU["Fruit_Desserts"].keys()
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Select a dessert:", reply_markup=reply_markup)
    elif selection == "back_to_cakes":
        keyboard = [
            [InlineKeyboardButton(cake, callback_data=f"cake_{cake}")]
            for cake in MENU["Chocolate_Cakes"].keys()
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Select a cake:", reply_markup=reply_markup)
    elif selection == "back":
        await query.message.delete()
    elif selection == "view_order":
        if user_id in orders and orders[user_id]:
            order_summary = {}
            total_price = 0
            
            for order in orders[user_id]:
                item_name = order.split(" x")[0]
                quantity = int(order.split("x")[1].split(" ")[0])
                price = float(order.split("$")[1].strip(")"))
                
                if item_name in order_summary:
                    order_summary[item_name]["qty"] += quantity
                else:
                    order_summary[item_name] = {
                        "qty": quantity,
                        "price": price
                    }
                total_price += quantity * price
            
            order_list = []
            for item, details in order_summary.items():
                order_list.append(f"{item} x{details['qty']} (${details['price']})")
            
            order_text = "\n".join(order_list)
            order_text += f"\n\nTotal: ${total_price:.2f}"
            
            keyboard = [
                [InlineKeyboardButton("🍓 More Fruit Desserts", callback_data="back_to_fruit")],
                [InlineKeyboardButton("🍰 View Chocolate Cakes", callback_data="back_to_cakes")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(f"Your order:\n{order_text}", reply_markup=reply_markup)
        else:
            keyboard = [
                [InlineKeyboardButton("🍓 More Fruit Desserts", callback_data="back_to_fruit")],
                [InlineKeyboardButton("🍰 View Chocolate Cakes", callback_data="back_to_cakes")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("Your order is empty.", reply_markup=reply_markup)

# Main function
def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.CONTACT, phone_handler))
    app.add_handler(MessageHandler(filters.TEXT, message_handler))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    app.run_polling()

if __name__ == "__main__":
    main()
