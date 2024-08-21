# bot/handlers.py
from services.crypto_gateway import CryptoGateway

async def increase_balance_crypto(update: Update, context: ContextTypes.DEFAULT_TYPE, amount: float):
    query = update.callback_query
    await query.answer()

    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()

    crypto_gateway = CryptoGateway()
    crypto_payment_info = crypto_gateway.create_crypto_payment(user, amount)

    crypto_payment_instructions = (
        f"Please send {amount} EUR worth of cryptocurrency to the following address:\n\n"
        f"Bitcoin (BTC): {crypto_payment_info['address']}\n"
        f"The payment must be made within {crypto_payment_info['expires_in']} seconds."
    )

    await query.edit_message_text(
        crypto_payment_instructions,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("I've paid", callback_data=f"increase_balance_crypto_confirm_{amount}")]])
    )

async def increase_balance_crypto_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()

    # Get the amount from the callback data
    amount = float(query.data.split("_")[3])

    crypto_gateway = CryptoGateway()
    if crypto_gateway.confirm_crypto_payment(user, amount):
        user.balance += amount
        db.add(Transaction(user_id=user.id, amount=amount, type="payment", timestamp=datetime.utcnow()))
        db.commit()

        await query.edit_message_text(
            f"Balance increased by {amount} EUR. Your new balance is {user.balance} EUR.",
            reply_markup=main_menu_keyboard()
        )
    else:
        await query.edit_message_text(
            "Failed to confirm the crypto payment. Please try again.",
            reply_markup=main_menu_keyboard()
        )