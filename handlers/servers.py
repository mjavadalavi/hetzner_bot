from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackQueryHandler
from database.models import User, Server
from database.db_session import SessionLocal
from services.hetzner_service import HetznerService
from services.payment_service import PaymentService


hetzner_service = HetznerService()


def list_servers(update: Update, context):
    query = update.callback_query
    user = query.from_user
    session = SessionLocal()

    db_user = session.query(User).filter_by(username=user.username).first()
    if db_user:
        servers = db_user.servers
        keyboard = []
        for server in servers:
            keyboard.append([InlineKeyboardButton(f"Server {server.id}", callback_data=f'server_{server.id}')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="Select a server:", reply_markup=reply_markup)
    else:
        query.edit_message_text(text="You have no servers.")


def server_operations(update: Update, context):
    query = update.callback_query
    server_id = query.data.split('_')[1]
    keyboard = [
        [InlineKeyboardButton("Turn Off", callback_data=f'turn_off_{server_id}')],
        [InlineKeyboardButton("Reboot", callback_data=f'reboot_{server_id}')],
        [InlineKeyboardButton("Change OS", callback_data=f'change_os_{server_id}')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=f"Server {server_id} operations:", reply_markup=reply_markup)


def handle_turn_off(update: Update, context):
    query = update.callback_query
    server_id = query.data.split('_')[2]
    response = hetzner_service.power_off_server(server_id)
    query.edit_message_text(text=f"Server {server_id} turned off. Response: {response}")


def handle_reboot(update: Update, context):
    query = update.callback_query
    server_id = query.data.split('_')[2]
    response = hetzner_service.reboot_server(server_id)
    query.edit_message_text(text=f"Server {server_id} rebooted. Response: {response}")


def handle_change_os(update: Update, context):
    query = update.callback_query
    server_id = query.data.split('_')[2]
    # List available OS images (this should be fetched from Hetzner API)
    os_images = ["ubuntu-20.04", "debian-10", "centos-8"]
    keyboard = [[InlineKeyboardButton(os_image, callback_data=f'change_os_{server_id}_{os_image}')] for os_image in
                os_images]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Select an OS:", reply_markup=reply_markup)


def handle_os_selection(update: Update, context):
    query = update.callback_query
    data = query.data.split('_')
    server_id = data[2]
    os_image = data[3]
    response = hetzner_service.change_os(server_id,)
    query.edit_message_text(text=f"Server {server_id} OS changed to {os_image}. Response: {response}")


def setup_dispatcher(dispatcher):
    dispatcher.add_handler(CallbackQueryHandler(list_servers, pattern='my_servers'))
    dispatcher.add_handler(CallbackQueryHandler(server_operations, pattern='server_'))
    dispatcher.add_handler(CallbackQueryHandler(handle_turn_off, pattern='turn_off_'))
    dispatcher.add_handler(CallbackQueryHandler(handle_reboot, pattern='reboot_'))
    dispatcher.add_handler(CallbackQueryHandler(handle_change_os, pattern='change_os_'))
    dispatcher.add_handler(CallbackQueryHandler(handle_os_selection, pattern='change_os_'))
