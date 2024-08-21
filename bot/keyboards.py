from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("My Servers", callback_data="servers"),
            InlineKeyboardButton("Buy Server", callback_data="buy_server"),
        ],
        [InlineKeyboardButton("Profile", callback_data="profile")],
    ]
    return InlineKeyboardMarkup(keyboard)


def server_list_keyboard(servers):
    keyboard = [[InlineKeyboardButton(server.name, callback_data=f"server_{server.id}")] for server in servers]
    keyboard.append([InlineKeyboardButton("Back", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard)


def country_keyboard():
    countries = ["Germany", "Finland", "USA"]
    keyboard = [[InlineKeyboardButton(country, callback_data=f"country_{country}")] for country in countries]
    keyboard.append([InlineKeyboardButton("Back", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard)


def os_selection_keyboard(server_id):
    os_options = ["Ubuntu 20.04", "Debian 10", "CentOS 7", "Arch Linux"]
    keyboard = [[InlineKeyboardButton(os, callback_data=f"change_os_{server_id}_{os}")] for os in os_options]
    keyboard.append([InlineKeyboardButton("Back", callback_data=f"server_{server_id}")])
    return InlineKeyboardMarkup(keyboard)


def server_actions_keyboard(server_id):
    keyboard = [
        [InlineKeyboardButton("Power Off", callback_data=f"power_off_{server_id}")],
        [InlineKeyboardButton("Reboot", callback_data=f"reboot_{server_id}")],
        [InlineKeyboardButton("Delete", callback_data=f"delete_{server_id}")],
        [InlineKeyboardButton("Change Password", callback_data=f"change_password_{server_id}")],
        [InlineKeyboardButton("Change OS", callback_data=f"change_os_{server_id}")],
        [InlineKeyboardButton("Back", callback_data="servers")],
    ]
    return InlineKeyboardMarkup(keyboard)


def profile_keyboard():
    keyboard = [
        [InlineKeyboardButton("Financial", callback_data="financial")],
        [InlineKeyboardButton("Invited Users", callback_data="invited_users")],
        [InlineKeyboardButton("Increase Balance", callback_data="increase_balance")],
        [InlineKeyboardButton("Back", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


def payment_method_keyboard():
    keyboard = [
        [InlineKeyboardButton("Zarinpal", callback_data="pay_zarinpal")],
        [InlineKeyboardButton("Zibal", callback_data="pay_zibal")],
        [InlineKeyboardButton("Cryptocurrency", callback_data="pay_crypto")],
        [InlineKeyboardButton("Back", callback_data="profile")],
    ]
    return InlineKeyboardMarkup(keyboard)
