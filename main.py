import datetime
import re
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InputMediaPhoto
import config
import logging
import pygsheets
import asyncio
from aiogram import Bot, Dispatcher, executor, types
import keyboards
import queries

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
gs = pygsheets.authorize(service_file='green-webbing-377413-45aa6ca00d62.json')

TELEGRAM_PAY_CHAT_ID = -912201348

message_start = "Привет! Этот бот предназначен для оплаты и автоматических напоминаний по платежу курса Alice K."
message_start_for_new_users = "Привет! Этот бот предназначен для оплаты и автоматических напоминаний по платежу курса " \
                              "Alice K.\n" \
                              "Пожалуйста, пришлите фамилию и имя, а также email, в таком формате:\n" \
                              "<code>Фамилия и Имя:</code>\n<code>Email:</code>"

message_for_today_pay = "Ваш платеж ожидается сегодня.\nСумма платежа: "
message_for_crypto = "Для оплаты USDT в сети TRC20 используйте следующий адрес: <code>TEdpbqrdYZx7DryonmhhHVVCjtDyUaZAXR</code>\n" \
                     "После перевода монет — сделайте скриншот и пришлите его сюда\n" \
                     "Cумма платежа:"
message_for_card_ru = "Реквизиты для перевода: <code>5536 9140 6508 5940</code>\n" \
                      "После перевода — сделайте скриншот перевода и перешлите его сюда\n" \
                      "Cумма платежа:"
message_for_card_ua = "Реквизиты для перевода: <code>5536 9140 6508 5940</code>\n" \
                      "После перевода  — сделайте скриншот перевода и перешлите его сюда\n" \
                      "Cумма платежа:"
message_thanks = "Мы получили ваш скриншот, спасибо за платеж"
message_email_error = "Пожалуйста, введите правильный формат email"
message_user_not_found = "Пожалуйста, перепроверьте почту, эту ли вы использовали при регистрации на курс, если да, " \
                         "то напишите сюда:"
message_for_before_pay = "Сумма платежа: "
sh = gs.open('AliceK Pay')
wk1 = sh.sheet1

today = datetime.datetime.now().strftime("%d.%m.%Y")


class PayScreen(StatesGroup):
    screen = State()


class Registration(StatesGroup):
    check_email_in_sheets = State()


async def get_the_date_after():
    moscow_time = datetime.datetime.now()
    markup_before = await keyboards.pay_markup_before()
    markup_ua = await keyboards.pay_markup_ua()
    markup_ru = await keyboards.pay_markup_ru()
    markup_ot = await keyboards.pay_markup_other()
    for row_index, row in enumerate(wk1.get_all_records(), start=2):
        cell_index_row = f'A{row_index}'
        cell = wk1.cell(cell_index_row)
        color = cell.color
        if color == (0.5764706, 0.76862746, 0.49019608, 0):
            continue
        else:
            timestamp = row['DATЕ: ']
            time = datetime.datetime.strptime(timestamp, '%d.%m.%Y')
            delta = moscow_time - time
            if row['COUNTRY:'] == 'Ukraine':
                if delta.days == -3:
                    await bot.send_message(row['USER_ID:'], f"Добрый день! Ваш платеж ожидается через 3 дня\n\n"
                                                            f"Сумма платежа: <b>{row['SUM:']} {row['CURRENCY:']}</b>",
                                           reply_markup=markup_before)
                elif delta.days == 0:
                    await bot.send_message(row['USER_ID:'], f"Добрый день! Ваш платеж ожидается сегодня\n\n"
                                                            f"Сумма платежа: <b>{row['SUM:']} {row['CURRENCY:']}</b>",
                                           reply_markup=markup_ua)
                elif delta.days == 1:
                    await bot.send_message(row['USER_ID:'], "Добрый день! Вы просрочили платеж на 1 день\n"
                                                            "Пожалуйста оплатите свой счет, "
                                                            "иначе доступ к курсу будет заблокирован\n\n"
                                                            f"Сумма платежа: <b>{row['SUM:']} {row['CURRENCY:']}</b>",
                                           reply_markup=markup_ua)
                elif delta.days == 3:
                    await bot.send_message(row['USER_ID:'], "Добрый день! Вы просрочили платеж на 3 дня\n"
                                                            "Пожалуйста оплатите свой счет, "
                                                            "иначе доступ к курсу будет заблокирован\n\n"
                                                            f"Сумма платежа: <b>{row['SUM:']} {row['CURRENCY:']}</b>",
                                           reply_markup=markup_ua)
                elif delta.days == 7:
                    await bot.send_message(row['USER_ID:'], "Добрый день! Вы просрочили платеж на неделю\n"
                                                            "Пожалуйста оплатите свой счет, "
                                                            "иначе доступ к курсу будет заблокирован\n\n"
                                                            f"Сумма платежа: <b>{row['SUM:']} {row['CURRENCY:']}</b>",
                                           reply_markup=markup_ua)
                    await bot.send_message(TELEGRAM_PAY_CHAT_ID, f"‼️‼️<b>НАПИСАТЬ ЧЕЛОВЕКУ</b>‼️‼️\n"
                                                                 f"username: @{row['USERNAME:']}\n"
                                                                 f"Сумма платежа: <b>{row['SUM:']} {row['CURRENCY:']}</b>\n"
                                                                 f"Дата платежа: <b>{row['DATЕ: ']}</b>")
                elif delta.days == 14:
                    await bot.send_message(row['USER_ID:'], "Добрый день! Вы просрочили платеж на 2 недели\n"
                                                            "Пожалуйста оплатите свой счет, "
                                                            "иначе доступ к курсу будет заблокирован\n\n"
                                                            f"Сумма платежа: <b>{row['SUM:']} {row['CURRENCY:']}</b>",
                                           reply_markup=markup_ua)
                    await bot.send_message(TELEGRAM_PAY_CHAT_ID, f"‼️‼️<b>НАПИСАТЬ ЧЕЛОВЕКУ</b>‼️‼️\n"
                                                                 f"username: @{row['USERNAME:']}\n"
                                                                 f"Сумма платежа: <b>{row['SUM:']} {row['CURRENCY:']}</b>\n"
                                                                 f"Дата платежа: <b>{row['DATЕ: ']}</b>")
                elif delta.days == 30:
                    await bot.send_message(row['USER_ID:'], "Добрый день! Вы просрочили платеж на месяц\n"
                                                            "Пожалуйста оплатите свой счет, "
                                                            "иначе доступ к курсу будет заблокирован\n\n"
                                                            f"Сумма платежа: <b>{row['SUM:']} {row['CURRENCY:']}</b>",
                                           reply_markup=markup_ua)
                    await bot.send_message(TELEGRAM_PAY_CHAT_ID, f"‼️‼️<b>НАПИСАТЬ ЧЕЛОВЕКУ</b>‼️‼️\n"
                                                                 f"username: @{row['USERNAME:']}\n"
                                                                 f"Сумма платежа: <b>{row['SUM:']} {row['CURRENCY:']}</b>\n"
                                                                 f"Дата платежа: <b>{row['DATЕ: ']}</b>")
            elif row['COUNTRY:'] == 'Russia':
                if delta.days == -3:
                    await bot.send_message(row['USER_ID:'], f"Добрый день! Ваш платеж ожидается через 3 дня\n\n"
                                                            f"Сумма платежа: <b>{row['SUM:']} {row['CURRENCY:']}</b>",
                                           reply_markup=markup_before)
                elif delta.days == 0:
                    await bot.send_message(row['USER_ID:'], f"Добрый день! Ваш платеж ожидается сегодня\n\n"
                                                            f"Сумма платежа: <b>{row['SUM:']} {row['CURRENCY:']}</b>",
                                           reply_markup=markup_ru)
                elif delta.days == 1:
                    await bot.send_message(row['USER_ID:'], "Добрый день! Вы просрочили платеж на 1 день\n"
                                                            "Пожалуйста оплатите свой счет, "
                                                            "иначе доступ к курсу будет заблокирован\n\n"
                                                            f"Сумма платежа: <b>{row['SUM:']} {row['CURRENCY:']}</b>",
                                           reply_markup=markup_ru)
                elif delta.days == 3:
                    await bot.send_message(row['USER_ID:'], "Добрый день! Вы просрочили платеж на 3 дня\n"
                                                            "Пожалуйста оплатите свой счет, "
                                                            "иначе доступ к курсу будет заблокирован\n\n"
                                                            f"Сумма платежа: <b>{row['SUM:']} {row['CURRENCY:']}</b>",
                                           reply_markup=markup_ru)
                elif delta.days == 7:
                    await bot.send_message(row['USER_ID:'], "Добрый день! Вы просрочили платеж на неделю\n"
                                                            "Пожалуйста оплатите свой счет, "
                                                            "иначе доступ к курсу будет заблокирован\n\n"
                                                            f"Сумма платежа: <b>{row['SUM:']} {row['CURRENCY:']}</b>",
                                           reply_markup=markup_ru)
                    await bot.send_message(TELEGRAM_PAY_CHAT_ID, f"‼️‼️<b>НАПИСАТЬ ЧЕЛОВЕКУ</b>‼️‼️\n"
                                                                 f"username: @{row['USERNAME:']}\n"
                                                                 f"Сумма платежа: <b>{row['SUM:']} {row['CURRENCY:']}</b>\n"
                                                                 f"Дата платежа: <b>{row['DATЕ: ']}</b>")
                elif delta.days == 14:
                    await bot.send_message(row['USER_ID:'], "Добрый день! Вы просрочили платеж на 2 недели\n"
                                                            "Пожалуйста оплатите свой счет, "
                                                            "иначе доступ к курсу будет заблокирован\n\n"
                                                            f"Сумма платежа: <b>{row['SUM:']} {row['CURRENCY:']}</b>",
                                           reply_markup=markup_ru)
                    await bot.send_message(TELEGRAM_PAY_CHAT_ID, f"‼️‼️<b>НАПИСАТЬ ЧЕЛОВЕКУ</b>‼️‼️\n"
                                                                 f"username: @{row['USERNAME:']}\n"
                                                                 f"Сумма платежа: <b>{row['SUM:']} {row['CURRENCY:']}</b>\n"
                                                                 f"Дата платежа: <b>{row['DATЕ: ']}</b>")
                elif delta.days == 30:
                    await bot.send_message(row['USER_ID:'], "Добрый день! Вы просрочили платеж на месяц\n"
                                                            "Пожалуйста оплатите свой счет, "
                                                            "иначе доступ к курсу будет заблокирован\n\n"
                                                            f"Сумма платежа: <b>{row['SUM:']} {row['CURRENCY:']}</b>",
                                           reply_markup=markup_ru)
                    await bot.send_message(TELEGRAM_PAY_CHAT_ID, f"‼️‼️<b>НАПИСАТЬ ЧЕЛОВЕКУ</b>‼️‼️\n"
                                                                 f"username: @{row['USERNAME:']}\n"
                                                                 f"Сумма платежа: <b>{row['SUM:']} {row['CURRENCY:']}</b>\n"
                                                                 f"Дата платежа: <b>{row['DATЕ: ']}</b>")
            elif row['COUNTRY:'] == 'Other':
                if delta.days == -3:
                    await bot.send_message(row['USER_ID:'], f"Добрый день! Ваш платеж ожидается через 3 дня\n\n"
                                                            f"Сумма платежа: <b>{row['SUM:']} {row['CURRENCY:']}</b>",
                                           reply_markup=markup_before)
                elif delta.days == 0:
                    await bot.send_message(row['USER_ID:'], f"Добрый день! Ваш платеж ожидается сегодня\n\n"
                                                            f"Сумма платежа: <b>{row['SUM:']} {row['CURRENCY:']}</b>",
                                           reply_markup=markup_ot)
                elif delta.days == 1:
                    await bot.send_message(row['USER_ID:'], f"Добрый день! Вы просрочили платеж на 1 день\n"
                                                            f"Пожалуйста оплатите свой счет, "
                                                            f"иначе доступ к курсу будет заблокирован\n\n"
                                                            f"Сумма платежа: <b>{row['SUM:']} {row['CURRENCY:']}</b>",
                                           reply_markup=markup_ot)
                elif delta.days == 3:
                    await bot.send_message(row['USER_ID:'], "Добрый день! Вы просрочили платеж на 3 дня\n"
                                                            "Пожалуйста оплатите свой счет, "
                                                            "иначе доступ к курсу будет заблокирован\n\n"
                                                            f"Сумма платежа: <b>{row['SUM:']} {row['CURRENCY:']}</b>",
                                           reply_markup=markup_ot)
                elif delta.days == 7:
                    await bot.send_message(row['USER_ID:'], "Добрый день! Вы просрочили платеж на неделю\n"
                                                            "Пожалуйста оплатите свой счет, "
                                                            "иначе доступ к курсу будет заблокирован\n\n"
                                                            f"Сумма платежа: <b>{row['SUM:']} {row['CURRENCY:']}</b>",
                                           reply_markup=markup_ot)
                    await bot.send_message(TELEGRAM_PAY_CHAT_ID, f"‼️‼️<b>НАПИСАТЬ ЧЕЛОВЕКУ</b>‼️‼️\n"
                                                                 f"username: @{row['USERNAME:']}\n"
                                                                 f"Сумма платежа: <b>{row['SUM:']} {row['CURRENCY:']}\n"
                                                                 f"Дата платежа: <b>{row['DATЕ: ']}")
                elif delta.days == 14:
                    await bot.send_message(row['USER_ID:'], "Добрый день! Вы просрочили платеж на 2 недели\n"
                                                            "Пожалуйста оплатите свой счет, "
                                                            "иначе доступ к курсу будет заблокирован\n\n"
                                                            f"Сумма платежа: <b>{row['SUM:']} {row['CURRENCY:']}</b>",
                                           reply_markup=markup_ot)
                    await bot.send_message(TELEGRAM_PAY_CHAT_ID, f"‼️‼️<b>НАПИСАТЬ ЧЕЛОВЕКУ</b>‼️‼️\n"
                                                                 f"username: @{row['USERNAME:']}\n"
                                                                 f"Сумма платежа: <b>{row['SUM:']} {row['CURRENCY:']}\n"
                                                                 f"Дата платежа: <b>{row['DATЕ: ']}")
                elif delta.days == 30:
                    await bot.send_message(row['USER_ID:'], "Добрый день! Вы просрочили платеж на месяц\n"
                                                            "Пожалуйста оплатите свой счет, "
                                                            "иначе доступ к курсу будет заблокирован\n\n"
                                                            f"Сумма платежа: <b>{row['SUM:']} {row['CURRENCY:']}</b>",
                                           reply_markup=markup_ot)
                    await bot.send_message(TELEGRAM_PAY_CHAT_ID, f"‼️‼️<b>НАПИСАТЬ ЧЕЛОВЕКУ</b>‼️‼️\n"
                                                                 f"username: @{row['USERNAME:']}\n"
                                                                 f"Сумма платежа: <b>{row['SUM:']} {row['CURRENCY:']}\n"
                                                                 f"Дата платежа: <b>{row['DATЕ: ']}")


async def get_the_birth():
    today = datetime.date.today()
    fake_year = today.year

    for row_index, row in enumerate(wk1.get_all_records(), start=2):
        timestamp = row['ДР:']
        time_str = str(timestamp)
        print(time_str)
        time = datetime.datetime.strptime(time_str, '%d.%m').date()
        time = time.replace(year=fake_year)
        delta = today - time
        print(delta.days)
        if delta.days == 0:
            await bot.send_message(TELEGRAM_PAY_CHAT_ID, f"🎁 <b>Сегодня день рождения у </b>🎁\n"
                                                         f"username: @{row['USERNAME:']}\n")
        else:
            continue

async def check_users():
    while True:
        asyncio.create_task(get_the_date_after())
        asyncio.create_task(get_the_birth())
        await asyncio.sleep(60*60*60)


@dp.message_handler(commands=['start'], state='*')
async def start(message: types.Message):
    if message.from_user.id in await queries.get_the_users():
        list_data = await queries.get_the_date(message)
        await bot.send_message(message.chat.id, message_start)
        markup_ru = await keyboards.pay_markup_ru()
        markup_ua = await keyboards.pay_markup_ua()
        markup_ot = await keyboards.pay_markup_other()
        markup_before = await keyboards.pay_markup_before()
        if list_data[0] == today:
            if list_data[5] == 'Russia':
                await bot.send_message(message.chat.id, text=message_for_today_pay + f'<b>{list_data[3]} {list_data[4]}</b>',
                                       reply_markup=markup_ru)
            elif list_data[5] == 'Ukraine':
                await bot.send_message(message.chat.id, text=message_for_today_pay + f'<b>{list_data[3]} {list_data[4]}</b>',
                                       reply_markup=markup_ua)
            else:
                await bot.send_message(message.chat.id, text=message_for_today_pay + f'<b>{list_data[3]} {list_data[4]}</b>',
                                       reply_markup=markup_ot)
        elif list_data[0] > today:
            if list_data[5] == 'Russia':
                await bot.send_message(message.chat.id, text=f'Ваш ближайший платеж: <b>{list_data[0]}</b>\n\n'
                                                             f'Сумма платежа: <b>{list_data[3]}</b> {list_data[4]}\n'
                                                             f'Но вы можете оплатить раньше, для этого нажмите '
                                                             f'на кнопку',
                                       reply_markup=markup_before)
            elif list_data[5] == 'Ukraine':
                await bot.send_message(message.chat.id, text=f'Ваш ближайший платеж: <b>{list_data[0]}</b>\n\n'
                                                             f'Сумма платежа: <b>{list_data[3]}</b> {list_data[4]}\n'
                                                             f'Но вы можете оплатить раньше, для этого нажмите '
                                                             f'на кнопку',
                                       reply_markup=markup_before)
            else:
                await bot.send_message(message.chat.id, text=f'Ваш ближайший платеж: <b>{list_data[0]}</b>\n\n'
                                                             f'Сумма платежа: <b>{list_data[3]}</b> {list_data[4]}\n'
                                                             f'Но вы можете оплатить раньше, для этого нажмите '
                                                             f'на кнопку',
                                       reply_markup=markup_before)
        elif list_data[0] < today:
            if list_data[5] == 'Russia':
                await bot.send_message(message.chat.id,
                                       text=f'Ваш ближайший платеж должен был быть: <b>{list_data[0]}</b>\n\n'
                                            f'Сумма платежа: <b>{list_data[3]} {list_data[4]}</b>\n\n'
                                            f'Пожалуйста оплатите свой счет, иначе доступ к курсу'
                                            f' будет заблокирован', reply_markup=markup_ru)
            elif list_data[5] == 'Ukraine':
                await bot.send_message(message.chat.id,
                                       text=f'Ваш ближайший платеж должен был быть: <b>{list_data[0]}</b>\n\n'
                                            f'Сумма платежа: <b>{list_data[3]} {list_data[4]}</b>\n\n'
                                            f'Пожалуйста оплатите свой счет, иначе доступ к курсу'
                                            f' будет заблокирован', reply_markup=markup_ua)
            else:
                await bot.send_message(message.chat.id,
                                       text=f'Ваш ближайший платеж должен был быть: <b>{list_data[0]}</b>\n\n'
                                            f'Сумма платежа: <b>{list_data[3]} {list_data[4]}</b>\n\n'
                                            f'Пожалуйста оплатите свой счет, иначе доступ к курсу'
                                            f' будет заблокирован', reply_markup=markup_ot)
    else:
        await bot.send_message(message.chat.id, message_start_for_new_users)
        await Registration.check_email_in_sheets.set()


@dp.message_handler(state=Registration.check_email_in_sheets)
async def registration(message: types.Message, state: FSMContext):
    text = message.text
    pattern = r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+'
    match = re.search(pattern, text)
    if match:
        email = match.group()
        if wk1.find(f'{email}'):
            for i in wk1.find(f'{email}'):
                pattern_name = r'Фамилия и Имя:\s+([\w\s]+)\s'
                match_name = re.search(pattern_name, text)
                name = match_name.group(1)
                name_address = i.address + (0, -1)
                id_address = i.address + (0, -4)
                wk1.update_value(addr=id_address.label, val=message.chat.id)
                wk1.update_value(addr=name_address.label, val=name)
                markup = types.InlineKeyboardMarkup(resize_keyboard=True)
                start_re = types.InlineKeyboardButton(text='Посмотреть оплату', callback_data='start_re')
                markup.add(start_re)
                await state.finish()
                await bot.send_message(message.chat.id, text="Нажмите на кнопку ниже", reply_markup=markup)

        else:
            markup = types.InlineKeyboardMarkup(resize_keyboard=True)
            chat_with_oleg = types.InlineKeyboardButton(text="Написать", url="https://t.me/AliceKdesign")
            markup.add(chat_with_oleg)
            await bot.send_message(message.chat.id, text=message_user_not_found, reply_markup=markup)
    else:
        await bot.send_message(message.chat.id, text=message_email_error)


@dp.callback_query_handler(text='start_re', state='*')
async def start_after_registration(callback: types.CallbackQuery):
    if callback.from_user.id in await queries.get_the_users():
        list_data = await queries.get_the_date_after_call(callback)
        markup_ru = await keyboards.pay_markup_ru()
        markup_ua = await keyboards.pay_markup_ua()
        markup_ot = await keyboards.pay_markup_other()
        markup_before = await keyboards.pay_markup_before()
        if list_data[0] == today:
            if list_data[5] == 'Russia':
                await bot.send_message(callback.message.chat.id, text=message_for_today_pay + f'<b>{list_data[3]} {list_data[4]}</b>',
                                       reply_markup=markup_ru)
            elif list_data[5] == 'Ukraine':
                await bot.send_message(callback.message.chat.id, text=message_for_today_pay + f'<b>{list_data[3]} {list_data[4]}</b>',
                                       reply_markup=markup_ua)
            else:
                await bot.send_message(callback.message.chat.id, text=message_for_today_pay + f'<b>{list_data[3]} {list_data[4]}</b>',
                                       reply_markup=markup_ot)

        elif list_data[0] > today:
            if list_data[5] == 'Russia':
                await bot.send_message(callback.message.chat.id, text=f'Ваш ближайший платеж {list_data[0]}\n'
                                                                      f'Сумма платежа: <b>{list_data[3]} {list_data[4]}</b>\n'
                                                                      f'Но вы можете оплатить заранее, для этого нажмите '
                                                                      f'на кнопку',
                                       reply_markup=markup_before)
            elif list_data[5] == 'Ukraine':
                await bot.send_message(callback.message.chat.id, text=f'Ваш ближайший платеж {list_data[0]}\n'
                                                                      f'Сумма платежа: <b>{list_data[3]} {list_data[4]}</b>\n'
                                                                      f'Но вы можете оплатить заранее, для этого нажмите '
                                                                      f'на кнопку',
                                       reply_markup=markup_before)
            else:
                await bot.send_message(callback.message.chat.id, text=f'Ваш ближайший платеж {list_data[0]}\n'
                                                                      f'Сумма платежа: <b>{list_data[3]} {list_data[4]}</b>\n'
                                                                      f'Но вы можете оплатить заранее, для этого нажмите '
                                                                      f'на кнопку',
                                       reply_markup=markup_before)
        elif list_data[0] < today:
            if list_data[5] == 'Russia':
                await bot.send_message(callback.message.chat.id,
                                       text=f'Ваш ближайший платеж должен был быть {list_data[0]}\n\n'
                                            f'Сумма платежа: <b>{list_data[3]} {list_data[4]}</b>\n'
                                            f'Пожалуйста оплатите свой счет, иначе доступ к курсу'
                                            f' будет заблокирован',
                                       reply_markup=markup_ua)
            elif list_data[5] == 'Ukraine':
                await bot.send_message(callback.message.chat.id,
                                       text=f'Ваш ближайший платеж должен был быть {list_data[0]}\n\n'
                                            f'Сумма платежа: <b>{list_data[3]} {list_data[4]}</b>\n'
                                            f'Пожалуйста оплатите свой счет, иначе доступ к курсу'
                                            f' будет заблокирован',
                                       reply_markup=markup_ru)
            else:
                await bot.send_message(callback.message.chat.id,
                                       text=f'Ваш ближайший платеж должен был быть {list_data[0]}\n\n'
                                            f'Сумма платежа: <b>{list_data[3]} {list_data[4]}</b>\n'
                                            f'Пожалуйста оплатите свой счет, иначе доступ к курсу'
                                            f' будет заблокирован',
                                       reply_markup=markup_ot)
    else:
        await bot.send_message(callback.message.chat.id, message_start_for_new_users)
        await Registration.check_email_in_sheets.set()


@dp.callback_query_handler(text='pay_before', state='*')
async def pay_before(callback: types.CallbackQuery):
    if callback.from_user.id in await queries.get_the_users():
        list_data = await queries.get_the_date_after_call(callback)
        markup_ru = await keyboards.pay_markup_ru()
        markup_ua = await keyboards.pay_markup_ua()
        markup_ot = await keyboards.pay_markup_other()
        if list_data[5] == 'Russia':
            await bot.send_message(callback.message.chat.id, text=message_for_today_pay + f'<b>{list_data[3]} {list_data[4]}</b>',
                                   reply_markup=markup_ru)
        elif list_data[5] == 'Ukraine':
            await bot.send_message(callback.message.chat.id, text=message_for_today_pay + f'<b>{list_data[3]} {list_data[4]}</b>',
                                   reply_markup=markup_ua)
        else:
            await bot.send_message(callback.message.chat.id, text=message_for_today_pay + f'<b>{list_data[3]} {list_data[4]}</b>',
                                   reply_markup=markup_ot)


@dp.callback_query_handler(text='crypto', state='*')
async def crypto_pay(callback: types.CallbackQuery, state: FSMContext):
    list_data = await queries.get_the_date_after_call(callback)
    if list_data[5] == 'Russia':
        await bot.send_message(callback.message.chat.id, text=message_for_crypto + f' <code>{list_data[3]} {list_data[4]}</code>')
        async with state.proxy() as data:
            data["screen"] = callback.data
        await PayScreen.screen.set()
    elif list_data[5] == 'Ukraine':
        await bot.send_message(callback.message.chat.id, text=message_for_crypto + f' <code>{list_data[3]} {list_data[4]}</code>')
        async with state.proxy() as data:
            data["screen"] = callback.data
        await PayScreen.screen.set()
    else:
        await bot.send_message(callback.message.chat.id, text=message_for_crypto + f' <code>{list_data[3]} {list_data[4]}</code>')
        async with state.proxy() as data:
            data["screen"] = callback.data
        await PayScreen.screen.set()


@dp.callback_query_handler(text='card_ru', state='*')
async def card_ru_pay(callback: types.CallbackQuery, state: FSMContext):
    list_data = await queries.get_the_date_after_call(callback)
    await bot.send_message(callback.message.chat.id, text=message_for_card_ru + f' <code>{list_data[3]} {list_data[4]}</code>')
    async with state.proxy() as data:
        data["screen"] = callback.data
    await PayScreen.screen.set()


@dp.callback_query_handler(text='card_ua', state='*')
async def card_ru_pay(callback: types.CallbackQuery, state: FSMContext):
    list_data = await queries.get_the_date_after_call(callback)
    await bot.send_message(callback.message.chat.id, text=message_for_card_ua + f' <code>{list_data[3]} {list_data[4]}</code>')
    async with state.proxy() as data:
        data["screen"] = callback.data
    await PayScreen.screen.set()


@dp.callback_query_handler(text='card_ot', state='*')
async def card_ot_pay(callback: types.CallbackQuery, state: FSMContext):
    list_data = await queries.get_the_date_after_call(callback)
    await bot.send_message(callback.message.chat.id, text=message_for_card_ua + f' <code>{list_data[3]} {list_data[4]}</code>')
    async with state.proxy() as data:
        data["screen"] = callback.data
    await PayScreen.screen.set()


@dp.message_handler(content_types=['photo'], state=PayScreen.screen)
async def wait_for_screen(message: types.Message, state: FSMContext):
    list_data = await queries.get_the_date(message)
    data = await state.get_data()
    if data['screen'] == 'crypto':
        payment_type = 'Крипта'
    elif data['screen'] == 'card_ua':
        payment_type = 'Оплата по карте UA'
    elif data['screen'] == 'card_ot':
        payment_type = 'Оплата по карте RU'
    else:
        payment_type = 'Оплата по карте других стран'
    user_id = list_data[2]
    price = list_data[3]
    currency = list_data[4]
    name_and_surname = list_data[6]
    email = list_data[7]
    photo = message.photo[-1].file_id
    media = [InputMediaPhoto(photo, caption=f'💸 <b>ПРОВЕРИТЬ ПЛАТЕЖ</b>\n'
                                            f'<b>ФАМИЛИЯ ИМЯ:</b> {name_and_surname}\n'
                                            f'<b>username:</b> @{message.from_user.username}\n'
                                            f'<b>Способ оплаты:</b> {payment_type} \n'
                                            f'<b>Сумма:</b> {price} {currency}\n'
                                            f'<b>USER_ID:</b> {user_id}\n'
                                            f'<b>E-mail:</b> {email}\n')]
    await bot.send_media_group(TELEGRAM_PAY_CHAT_ID, media=media)
    await bot.send_message(message.chat.id, text=message_thanks)
    await state.finish()
    for i in wk1.find(email):
        list_data = [data for data in wk1.get_row(i.address[0], returnas='cells')]
        for cell in list_data:
            if cell.value != '':
                cell.color = (0.5764706, 0.76862746, 0.49019608, 0)


async def main():
    asyncio.create_task(get_the_date_after())
    await check_users()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    executor.start_polling(dp, skip_updates=False)
