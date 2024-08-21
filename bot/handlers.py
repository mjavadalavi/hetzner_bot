from datetime import datetime
import pandas as pd
from io import BytesIO
from telegram import InputFile
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db_utils import get_db
from database.models import User, Server, PaymentGateway, Transaction
from services.hetzner_api import get_server_list, create_server, delete_server, reboot_server, change_server_password, \
    get_server_details, change_server_os
from services.payment_gateway import create_payment
from .keyboards import main_menu_keyboard, server_list_keyboard, country_keyboard, server_actions_keyboard, \
    profile_keyboard, os_selection_keyboard
from sqlalchemy import func
from services.payment_gateway import process_payment


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db = next(get_db())

    db_user = db.query(User).filter(User.telegram_id == user.id).first()
    if not db_user:
        db_user = User(telegram_id=user.id, username=user.username)
        db.add(db_user)
        db.commit()

    total_expenses = sum([t.amount for t in db_user.transactions if t.type == "usage"])
    total_balance = db_user.balance
    server_stats = f"Active servers: {len([s for s in db_user.servers if s.status == 'active'])}"

    welcome_message = (
        f"Welcome, {user.first_name}!\n\n"
        f"Total expenses: ${total_expenses:.2f}\n"
        f"Current balance: ${total_balance:.2f}\n"
        f"{server_stats}"
    )

    await update.message.reply_text(welcome_message, reply_markup=main_menu_keyboard())


async def servers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()

    server_list = db.query(Server).filter(Server.user_id == user.id).all()

    await query.edit_message_text(
        "Your servers:",
        reply_markup=server_list_keyboard(server_list)
    )


async def buy_server(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "Select a country:",
        reply_markup=country_keyboard()
    )


async def select_server(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    country = query.data.split("_")[1]

    server_list = get_server_list(country)

    keyboard = []
    for server in server_list:
        button_text = f"{server['name']} - {server['specs']} - ${server['hourly_cost']}/hour"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"confirm_server_{server['id']}")])
    keyboard.append([InlineKeyboardButton("Back", callback_data="buy_server")])

    await query.edit_message_text(
        f"Available servers in {country}:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def confirm_server(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    server_id = query.data.split("_")[2]

    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()

    server = get_server_details(server_id)

    if user.balance < server['hourly_cost'] * 24:
        payment_url = create_payment(user.id, server['hourly_cost'] * 24, PaymentGateway.ZARINPAL)
        await query.edit_message_text(
            "Insufficient balance. Please add funds:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Pay", url=payment_url)]])
        )
    else:
        new_server = create_server(user, server)
        db.add(new_server)
        db.commit()

        await query.edit_message_text(
            f"Server created successfully!\nServer ID: {new_server.hetzner_id}",
            reply_markup=main_menu_keyboard()
        )


async def server_actions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    server_id = query.data.split("_")[1]

    await query.edit_message_text(
        f"Select an action for server {server_id}:",
        reply_markup=server_actions_keyboard(server_id)
    )


async def power_off_server(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    server_id = query.data.split("_")[2]

    # Implement power off logic

    await query.edit_message_text(
        f"Server {server_id} powered off successfully.",
        reply_markup=main_menu_keyboard()
    )


async def reboot_server(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    server_id = query.data.split("_")[2]

    await reboot_server(server_id)

    await query.edit_message_text(
        f"Server {server_id} is rebooting.",
        reply_markup=main_menu_keyboard()
    )


async def delete_server(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    server_id = query.data.split("_")[2]

    await delete_server(server_id)

    db = next(get_db())
    db.query(Server).filter(Server.id == server_id).delete()
    db.commit()

    await query.edit_message_text(
        f"Server {server_id} has been deleted.",
        reply_markup=main_menu_keyboard()
    )


async def change_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    server_id = query.data.split("_")[2]

    # Implement change password logic
    new_password = change_server_password(server_id)

    await query.edit_message_text(
        f"Password for server {server_id} has been changed. New password: {new_password}",
        reply_markup=main_menu_keyboard()
    )


async def change_os(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    server_id = query.data.split("_")[2]

    await query.edit_message_text(
        f"Select new OS for server {server_id}:",
        reply_markup=os_selection_keyboard(server_id)
    )


async def confirm_os_change(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    server_id = query.data.split("_")[2]
    new_os = query.data.split("_")[3]

    # Implement the logic to change the OS of the server
    change_server_os(server_id, new_os)

    await query.edit_message_text(
        f"OS for server {server_id} has been changed to {new_os}.",
        reply_markup=main_menu_keyboard()
    )


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "Profile options:",
        reply_markup=profile_keyboard()
    )


def calculate_total_expenses(db, user):
    total_expenses = db.query(func.sum(Transaction.amount)).filter(Transaction.user_id == user.id,
                                                                   Transaction.type == "usage").scalar() or 0
    return total_expenses


async def financial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()

    total_expenses = calculate_total_expenses(db, user)
    balance = user.balance

    financial_message = (
        f"Your financial summary:\n\n"
        f"Total expenses: {total_expenses:.2f} EUR\n"
        f"Current balance: {balance:.2f} EUR\n\n"
        "What would you like to do?"
    )

    keyboard = [
        [
            InlineKeyboardButton("Pay Bill", callback_data="pay_bill"),
            InlineKeyboardButton("Download Statement", callback_data="download_statement"),
        ],
        [
            InlineKeyboardButton("Increase Balance", callback_data="increase_balance"),
            InlineKeyboardButton("Back", callback_data="main_menu"),
        ],
    ]

    await query.edit_message_text(financial_message, reply_markup=InlineKeyboardMarkup(keyboard))


async def pay_bill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()

    if user.balance < user.get_daily_cost():
        payment_url = process_payment(user, user.get_daily_cost())
        await query.edit_message_text(
            "Insufficient balance. Please add funds:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Pay", url=payment_url)]])
        )
    else:
        user.balance -= user.get_daily_cost()
        db.add(Transaction(user_id=user.id, amount=-user.get_daily_cost(), type="usage", timestamp=datetime.utcnow()))
        db.commit()
        await query.edit_message_text(
            "Bill paid successfully!",
            reply_markup=main_menu_keyboard()
        )


async def download_statement(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()

    transactions = db.query(Transaction).filter(Transaction.user_id == user.id).order_by(
        Transaction.timestamp.desc()).all()

    generate_and_send_statement(user, transactions)

    await query.edit_message_text(
        "Your financial statement has been sent to you.",
        reply_markup=main_menu_keyboard()
    )


def generate_and_send_statement(user, transactions, context):
    # Create a DataFrame from the transactions
    df = pd.DataFrame([
        {
            "Timestamp": transaction.timestamp,
            "Amount": transaction.amount,
            "Type": transaction.type
        }
        for transaction in transactions
    ])

    # Format the DataFrame
    df["Timestamp"] = df["Timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df["Amount"] = df["Amount"].apply(lambda x: f"{x:.2f} EUR")

    # Generate the Excel file
    buffer = BytesIO()
    df.to_excel(buffer, index=False, sheet_name="Transactions")
    buffer.seek(0)

    # Send the Excel file to the user
    file_name = f"{user.username}_financial_statement_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
    await context.bot.send_document(
        chat_id=context.update.effective_user.id,
        document=InputFile(buffer, filename=file_name),
        caption="Here is your financial statement."
    )


# bot/handlers.py
async def increase_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("Pay with Zipal/Zarinpal", callback_data="increase_balance_payment")],
        [InlineKeyboardButton("Pay with Crypto", callback_data="increase_balance_crypto")],
        [InlineKeyboardButton("Back", callback_data="financial")],
    ]

    await query.edit_message_text(
        "How would you like to increase your balance?\n\nPlease enter the amount you want to add:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    # Wait for the user to enter the amount
    amount = await wait_for_amount(update, context)
    if amount is None:
        return

    # Continue with the payment options
    if query.data == "increase_balance_payment":
        await increase_balance_payment(update, context, amount)
    elif query.data == "increase_balance_crypto":
        await increase_balance_crypto(update, context, amount)


async def wait_for_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Wait for the user to enter the amount
    user_input = await context.bot.wait_for('message', timeout=60, chat_id=update.effective_user.id)
    try:
        amount = float(user_input.text)
        if amount <= 0:
            await update.message.reply_text("Please enter a valid positive amount.")
            return None
        return amount
    except ValueError:
        await update.message.reply_text("Please enter a valid number.")
        return None


async def increase_balance_payment(update: Update, context: ContextTypes.DEFAULT_TYPE, amount: float):
    query = update.callback_query
    await query.answer()

    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()

    payment_url = process_payment(user, amount)
    await query.edit_message_text(
        f"Please complete the payment to add {amount} EUR to your balance:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Pay", url=payment_url)]])
    )


async def increase_balance_crypto(update: Update, context: ContextTypes.DEFAULT_TYPE, amount: float):
    query = update.callback_query
    await query.answer()

    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()

    crypto_payment_instructions = (
        f"Please send {amount} EUR worth of cryptocurrency to the following address:\n\n"
        "Bitcoin (BTC): 1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2\n"
        "Ethereum (ETH): 0xde0b295669a9FD93d5F28D9Ec85E40f4cb697BAe\n"
        "Once the payment is confirmed, your balance will be updated automatically."
    )

    await query.edit_message_text(
        crypto_payment_instructions,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("I've paid", callback_data=f"increase_balance_crypto_confirm_{amount}")]])
    )


async def increase_balance_crypto_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()

    # Get the amount from the callback data
    amount = float(query.data.split("_")[3])

    # Verify the crypto payment and update the user's balance
    user.balance += amount
    db.add(Transaction(user_id=user.id, amount=amount, type="payment", timestamp=datetime.utcnow()))
    db.commit()

    await query.edit_message_text(
        f"Balance increased by {amount} EUR. Your new balance is {user.balance} EUR.",
        reply_markup=main_menu_keyboard()
    )
