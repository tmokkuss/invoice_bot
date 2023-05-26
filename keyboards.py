import aiogram
from aiogram.types import KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup


async def pay_markup_ru():
    markup = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
    crypto = InlineKeyboardButton(callback_data="crypto", text='Крипта')
    card = InlineKeyboardButton(callback_data="card_ru", text='По карте')
    markup.add(card, crypto)
    return markup


async def pay_markup_ua():
    markup = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
    crypto = InlineKeyboardButton(callback_data="crypto", text='Крипта')
    card = InlineKeyboardButton(callback_data="card_ua", text='По карте')
    markup.add(card, crypto)
    return markup


async def pay_markup_other():
    markup = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
    crypto = InlineKeyboardButton(callback_data="crypto", text='Крипта')
    card = InlineKeyboardButton(callback_data="card_ot", text='По карте')
    markup.add(card, crypto)
    return markup


async def pay_markup_before():
    markup = InlineKeyboardMarkup(resize_keyboard=True)
    pay = InlineKeyboardButton(callback_data="pay_before", text='Оплатить')
    markup.add(pay)
    return markup
