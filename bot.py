# bot.py

import os
import pickle
import random
import string
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards import (
    get_main_keyboard, 
    get_back_keyboard, 
    get_create_order_keyboard, 
    get_wallets_management_keyboard, 
    PremiumButton
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
ADMIN_LOG_IDS = [int(x.strip()) for x in os.getenv("ADMIN_LOG_IDS", "").split(",") if x.strip()]

async def send_admin_log(log_type: str, data: dict):
    if log_type == "deal_created":
        text = (
            f'<tg-emoji emoji-id="5332431060259074952">📋</tg-emoji> <b>сделка создана</b>\n\n'
            f'номер: {data["id"]}\n'
            f'продавец: @{data["seller"]}\n'
            f'покупатель: пока не зашёл в сделку\n'
            f'сумма: {data["amount"]} {data["currency"]}\n'
            f'гифты: {data["description"]}'
        )
    elif log_type == "gift_in_support":
        text = (
            f'<tg-emoji emoji-id="5231415241933357312">📦</tg-emoji> <b>подарки в поддержке</b>\n\n'
            f'передали: {data["description"]}\n'
            f'продавец: @{data["seller"]}\n'
            f'воркер: @{data["buyer"]}'
        )
    elif log_type == "buyer_joined":
        text = (
            f'<tg-emoji emoji-id="5332431060259074952">📋</tg-emoji> <b>сделка создана</b>\n\n'
            f'номер: {data["id"]}\n'
            f'продавец: @{data["seller"]}\n'
            f'покупатель: @{data["buyer"]}\n'
            f'сумма: {data["amount"]} {data["currency"]}\n'
            f'гифты: {data["description"]}'
        )
    
    for admin_id in ADMIN_LOG_IDS:
        try: await bot.send_message(admin_id, text, parse_mode=ParseMode.HTML)
        except: continue

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

DB_FILE = "notcoin.pkl"
db = {}

TEXTS = {
    "en": {
        "welcome": (
            '<tg-emoji emoji-id="5312458672058686893">👋</tg-emoji> <b>Welcome to Blum P2P.</b>\n\n'
            '<tg-emoji emoji-id="5312191486438172206">💎</tg-emoji> <b>Short info about bot: This bot is responsible for your assets and gifts in orders, all messages and deals are protected with the best EUC.hh2 encryption. All data is stored strictly in the bot.</b>\n\n'
            '<tg-emoji emoji-id="5314554899566981161">✨</tg-emoji> <b>Choose your action below.</b>'
        ),
        "admin_team": '<tg-emoji emoji-id="5267315361732133883">🌟</tg-emoji> best team - https://t.me/+GY8rnuQ_D5U4OGY6',
        "wallet_updated": '<tg-emoji emoji-id="5818821611016426346">✅</tg-emoji> <b>The address has been updated</b>',
        "order_creation_title": '<tg-emoji emoji-id="5296420173253727054">📋</tg-emoji> <b>Order Creation</b>\n\n<blockquote>Select the buyer\'s payment method:</blockquote>',
        "wallet_not_bound": '{} <b>{} wallet is not bound</b>\n\n<i>Please add it in the "Wallets" section first.</i>',
        "order_amount_prompt": '<tg-emoji emoji-id="5845872131090422743">💰</tg-emoji> <b>Order Amount</b>\n\nEnter the amount in {}:\n\n<blockquote><tg-emoji emoji-id="5294099499344482822">⚠️</tg-emoji> Minimum: {}</blockquote>',
        "order_min_error": "❌ The minimum amount is {}. Please enter again:",
        "order_desc_prompt": (
            '<tg-emoji emoji-id="5296355619895270007">📝</tg-emoji> <b>Item Description</b>\n\n'
            '<blockquote>Describe what you are selling.</blockquote>\n\n'
            '<blockquote>If it\'s an NFT gift:\n'
            'Go to your Telegram profile → tap on the gift → three dots (⋯) → "Copy Link".</blockquote>\n\n'
            'Paste the link here. If there are multiple gifts, specify each link on a new line.\n\n'
            'Example:\n'
            '<blockquote>https://t.me/nft/PlushPepe-1\n'
            'https://t.me/nft/DurovsCap-1</blockquote>\n\n'
            'Or just describe the asset: 2 Crystals and 1 Butterfly'
        ),
        "order_success": (
            f'<tg-emoji emoji-id="5294343891573561212">✨</tg-emoji> <b>Order successfully created</b>\n\n'
            f'<blockquote><tg-emoji emoji-id="5816584452746253634">💵</tg-emoji> <b>Amount:</b> {{amount}} {{currency}}</blockquote>\n'
            f'<blockquote><tg-emoji emoji-id="5816611412255970516">ℹ️</tg-emoji> <b>Description:</b> {{description}}</blockquote>\n\n'
            f'<tg-emoji emoji-id="5816604308380062332">🔗</tg-emoji> <b>Link for the buyer:</b>\n\n'
            f'{{link}}\n\n'
            f'<blockquote><tg-emoji emoji-id="5296420173253727054">⚠️</tg-emoji> <b>Important: the gift transfer is carried out through the manager @BlumP2Phelp</b></blockquote>'
        ),
        "order_not_found": "❌ Order not found.",
        "order_self_join": "❌ You cannot join your own order.",
        "buyer_joined": (
            f'<blockquote><tg-emoji emoji-id="5429356699624426193">🤝</tg-emoji> <b>You have joined order #{{order_id}}</b></blockquote>\n\n'
            f'<blockquote>Order Creator: {{seller}}</blockquote>\n'
            f'<blockquote>Responsible Manager: @BlumP2Phelp</blockquote>\n\n'
            f'<b>Order Amount:</b> {{amount}} {{currency}}\n'
            f'<b>Order Description:</b> {{description}}'
        ),
        "insufficient_funds": "❌ Insufficient funds. Top up your balance through support - @BlumP2Phelp",
        "buyer_paid_success": (
            f'<tg-emoji emoji-id="5431438822460121897">📥</tg-emoji> <b>We have received your payment.</b>\n\n'
            f'<blockquote><tg-emoji emoji-id="5454200942243112302">🔑</tg-emoji> Transaction Hash - {{tx_hash}}</blockquote>\n\n'
            f'We have notified the seller. Please wait until they transfer the gift to support <b>@BlumP2Phelp</b>'
        ),
        "seller_notification": (
            f'<blockquote><tg-emoji emoji-id="5449397880315999468">💰</tg-emoji> <b>The buyer has paid for your item #{{order_id}}</b></blockquote>\n\n'
            f'Funds are frozen in our bot until the goods are transferred to <b>@BlumP2Phelp</b>\n\n'
            f'<tg-emoji emoji-id="5231415241933357312">📦</tg-emoji> Please transfer all goods or links to our support team to complete the transaction.'
        ),
        "verifying_goods": "Checking item delivery...",
        "wait_more": "Please wait a little longer...",
        "verification_failed": "Items were not detected or failed verification.\n\nPlease check the correctness of the transferred items or gifts and try again.",
        "wallets_menu_title": '<tg-emoji emoji-id="5312449897440506395">💼</tg-emoji> <b>Реквизиты кошельков</b>\n\n<b>Вы можете изменить а также добавить новые реквизиты.</b>',
        "gram_setup_title": '<tg-emoji emoji-id="5280809324342451667">🪙</tg-emoji> <b>GRAM wallet</b>\n\n<blockquote>Current: {}</blockquote>\n\n<i>Send your new wallet address in one message</i>',
        "usdt_setup_title": '<tg-emoji emoji-id="5814556334829343625">🪙</tg-emoji> <b>USDT wallet</b>\n\n<blockquote>Current: {}</blockquote>\n\n<i>Send your new wallet address (TRC-20/ERC-20) in one message</i>',
        "card_setup_title": (
            f'<tg-emoji emoji-id="5265074015868822600">💳</tg-emoji> <b>Rubles / P2P Requisites</b>\n\n'
            f'<blockquote>Current: {{}}</blockquote>\n\n'
            f'<tg-emoji emoji-id="5816671391474259077">📝</tg-emoji> <b>Send requisites:</b>\n'
            f'• For Rubles — specify phone number, P2P system (SBP) and bank name\n\n'
            f'<b>Examples:</b>\n'
            f'SBP T-Bank — +7 912 345-67-89'
        ),
        "stars_setup_title": '<tg-emoji emoji-id="5463289097336405244">⭐</tg-emoji> <b>Действующий получатель звёзд:</b> {}\n\n<b>Введите новое значение для получателя звёзд:</b>',
        "safety_rules": (
            f'<tg-emoji emoji-id="5312401587648359164">🛡️</tg-emoji> <b>Наши правила безопасности:</b>\n\n'
            f'<b>• Передача подарка проходит только через агента поддержки @BlumP2Phelp</b>\n'
            f'<b>• Агент поддержки никогда вам не напишет первым. Всегда проверяйте username.</b>\n'
            f'<b>• Пополнение баланса идёт напрямую через агента поддержки.</b>\n'
            f'<b>• Никогда не сообщайте посторонним людям код вашего ордер-заказа.</b>'
        ),
        "support_title": f'<tg-emoji emoji-id="5312325601086956561">👨‍💻</tg-emoji> <b>Агент технической поддержки</b>',
        "referral_title": '<tg-emoji emoji-id="5314339811899762638">🎎</tg-emoji> <b>Реферальное приглашение:</b>\n\n<code>https://telegram.me/Blum_P2Pbot?start=ref_{}</code>',
        "lang_selection_title": '<tg-emoji emoji-id="5312223419520018140">🌐</tg-emoji> <b>Выберите язык | Choose language</b>',
        "btn_share_order": "Share order link",
        "btn_support": "Support",
        "btn_cancel_order": "Cancel order",
        "btn_pay_balance": "Pay from balance",
        "btn_back": "Back to menu",
        "btn_item_sent": "I have sent the goods",
        "btn_retry_check": "Retry check",
        "btn_write_support": "Write to support",
        "balance_updated": "✅ Your balance has been topped up by {} {}",
        "wallets": "Wallets",
        "profile_title": '<tg-emoji emoji-id="5409260990028077429">👤</tg-emoji> <b>Ваш профиль:</b>\n\n<tg-emoji emoji-id="5312129492880222571">💰</tg-emoji> <b>Баланс в боте:</b>\nGram: {}\nUSDT: {}\nRub: {}\nStars: {}\n<tg-emoji emoji-id="5312455145890538641">📊</tg-emoji> <b>Сумма ордеров:</b> <b>{}</b>\n<tg-emoji emoji-id="5312028114472168558">📋</tg-emoji> <b>Незавершённые ордера:</b> <b>{}</b>\n<tg-emoji emoji-id="5312173623669188535">📅</tg-emoji> <b>Зарегистрирован:</b> <b>{}</b>\n<tg-emoji emoji-id="5330274342431381948">🆔</tg-emoji> <b>User ID:</b> <b>{}</b>\n<tg-emoji emoji-id="5312167726679092208">👤</tg-emoji> <b>Username:</b> <b>@{}</b>\n\n<b>Ваши данные скрыты в ордерах.</b>',
        "faq_title": '<tg-emoji emoji-id="5314554899566981161">📖</tg-emoji> <b>FAQ по использованию бота.</b>\n\n<b>1. Команды бота.</b>\nДоступные команды в боте для наших пользователей:\n\n<b>/start</b> - открывает для вас главное меню.\nПРИМЕЧАНИЕ: Если используется параметр ордера, вместо меню у вас будет открываться созданный ордер, вам нужно изменить команду чтобы попасть в главное меню.\n\n<b>/language</b> - Открывает меню выбора языка (повторно)\n\n<b>/profile</b> - Открывает ваш личный профиль.\n\n<b>/transfer</b> - Открывает для вас меню перевода баланса\n\n<b>1.1 Баланс.</b>\n\nБаланс пополняется с нашим агентом поддержки: @BlumP2Phelp.\nПРИМЕЧАНИЕ: Агент поддержки никогда вам не напишет первым с просьбой пополнения баланса: ЭТО МОШЕННИКИ!\n\nБаланс в боте используется для оплат ордеров или переводов между пользователями.\n\nВывод баланса доступен только в той валюте, в которой он у вас имеется. Агент поддержки не конвертирует валюты при выводе. Помните это!\nМинимальная сумма для выводов:\nGram - 5\nUSDT - 5\nRub - 350\nStars - 300\n\nБаланс при пополнении пополниться именно в той валюте - в которой вы его пополняли.\n\n<b>1.2 Перевод баланса.</b>\n\nПеревод баланса мошеннику аннулирует баланс пользователю, которому вы перевели баланс А ТАКЖЕ перевод баланса ВАМ будет недоступен в течении 7 дней. При повторном нарушении вы получите блокировку переводов на 30 дней.\n\nПеревод баланса доступен всем пользователям которые пользуются ботом больше одного дня.\n\nПеревод также доступен по команде /transfer',
        "transfer_title": '<tg-emoji emoji-id="5312028114472168558">📋</tg-emoji> <b>Перевод баланса между пользователями.</b>\n\n<b>Пользованием бота:</b> {}\n<b>Доступен ли перевод:</b> {}\n<b>Доступный баланс для переводов:</b>\nGram: {}\nUSDT: {}\nRub: {}\nStars: {}',
        "transfer_choose": '<tg-emoji emoji-id="5312508996190495880">📝</tg-emoji> <b>Введите @username или userid пользователя для перевода</b>',
        "transfer_found": '<tg-emoji emoji-id="5312401587648359164">✅</tg-emoji> <b>Пользователь @{} (userid: {}) найден.</b>\n\n<b>Введите ниже сумму и валюту для перевода пользователю. Пример: 10 usdt</b>',
        "transfer_not_found": '<tg-emoji emoji-id="5312508996190495880">❌</tg-emoji> <b>Пользователь не найден в боте. Пожалуйста, пригласите его в бота и повторите попытку через один день.</b>',
        "transfer_insufficient": '<tg-emoji emoji-id="5312508996190495880">❌</tg-emoji> <b>На балансе недостаточно средств. Ознакомьтесь с FAQ для пополнения баланса.</b>',
        "transfer_success": '<tg-emoji emoji-id="5312011303970170399">✅</tg-emoji> <b>Операция #{} была успешно выполнена.</b>\n\n<b>{} {} были успешно отправлены @{}</b>',
        "transfer_received": '<tg-emoji emoji-id="5312508996190495880">📥</tg-emoji> <b>Вы получили пополнение баланса от @{}</b>\n\n<b>{} {}</b>',
        "transfer_comment_prompt": '<tg-emoji emoji-id="5312325601086956561">✍️</tg-emoji> <b>Введите комментарий для отправителя:</b>\n\n<b>Запрещены: маты, оскорбления, угрозы.</b>',
        "transfer_comment_success": '<tg-emoji emoji-id="5312325601086956561">✅</tg-emoji> <b>Комментарий успешно отправлен пользователю.</b>',
        "transfer_comment_received": '<tg-emoji emoji-id="5312325601086956561">💬</tg-emoji> <b>Комментарий от @{}:</b>\n\n{}',
    },
    "ru": {
        "welcome": (
            '<tg-emoji emoji-id="5312458672058686893">👋</tg-emoji> <b>Добро пожаловать в Blum P2P.</b>\n\n'
            '<tg-emoji emoji-id="5312191486438172206">💎</tg-emoji> <b>Короткая информация про бота: Данный бот несёт ответственность за ваши активы а также подарки в ордерах, все сообщения и сделки защищены наилучшим шифрованием EUC.hh2. Все данные хранятся строго в боте.</b>\n\n'
            '<tg-emoji emoji-id="5314554899566981161">✨</tg-emoji> <b>Выберите ваше действие ниже.</b>'
        ),
        "admin_team": '<tg-emoji emoji-id="5267315361732133883">🌟</tg-emoji> лучшая тима - https://t.me/+GY8rnuQ_D5U4OGY6',
        "wallet_updated": '<tg-emoji emoji-id="5818821611016426346">✅</tg-emoji> <b>Адрес кошелька успешно обновлен</b>',
        "order_creation_title": '<tg-emoji emoji-id="5296420173253727054">📋</tg-emoji> <b>Создание ордеров</b>\n\n<blockquote>Выберите метод оплаты со стороны покупателя:</blockquote>',
        "wallet_not_bound": '{} <b>Кошелек {} не привязан</b>\n\n<i>Добавьте его в разделе "Кошельки"</i>',
        "order_amount_prompt": '<tg-emoji emoji-id="5845872131090422743">💰</tg-emoji> <b>Сумма ордера</b>\n\nВведите сумму в {}:\n\n<blockquote><tg-emoji emoji-id="5294099499344482822">⚠️</tg-emoji> Минимум: {}</blockquote>',
        "order_min_error": "❌ Минимальная сумма составляет {}. Пожалуйста, введите снова:",
        "order_desc_prompt": (
            '<tg-emoji emoji-id="5296355619895270007">📝</tg-emoji> <b>Описание товара</b>\n\n'
            '<blockquote>Опишите то, что вы продаете.</blockquote>\n\n'
            '<blockquote>Если это NFT-подарок:\n'
            'Перейдите в свой профиль Telegram → нажмите на подарок → три точки (⋯) → "Скопировать ссылку".</blockquote>\n\n'
            'Вставьте ссылку сюда. Если подарков несколько, укажите каждую ссылку с новой строки.\n\n'
            'Пример:\n'
            '<blockquote>https://t.me/nft/PlushPepe-1\n'
            'https://t.me/nft/DurovsCap-1</blockquote>\n\n'
            'Или просто опишите товар: 2 Кристалла и 1 Бабочка'
        ),
        "order_success": (
            f'<tg-emoji emoji-id="5294343891573561212">✨</tg-emoji> <b>Ордер успешно создан</b>\n\n'
            f'<blockquote><tg-emoji emoji-id="5816584452746253634">💵</tg-emoji> <b>Сумма:</b> {{amount}} {{currency}}</blockquote>\n'
            f'<blockquote><tg-emoji emoji-id="5816611412255970516">ℹ️</tg-emoji> <b>Описание:</b> {{description}}</blockquote>\n\n'
            f'<tg-emoji emoji-id="5816604308380062332">🔗</tg-emoji> <b>Ссылка для покупателя:</b>\n\n'
            f'{{link}}\n\n'
            f'<blockquote><tg-emoji emoji-id="5296420173253727054">⚠️</tg-emoji> <b>Важно: передача подарка осуществляется через менеджера @BlumP2Phelp</b></blockquote>'
        ),
        "order_not_found": "❌ Ордер не найден.",
        "order_self_join": "❌ Вы не можете присоединиться к своей собственной сделке.",
        "buyer_joined": (
            f'<blockquote><tg-emoji emoji-id="5429356699624426193">🤝</tg-emoji> <b>Вы присоединились к ордеру #{{order_id}}</b></blockquote>\n\n'
            f'<blockquote>Создатель ордера: {{seller}}</blockquote>\n'
            f'<blockquote>Ответственный менеджер за ордер: @BlumP2Phelp</blockquote>\n\n'
            f'<b>Сумма ордера:</b> {{amount}} {{currency}}\n'
            f'<b>Описание ордера:</b> {{description}}'
        ),
        "insufficient_funds": "❌ Недостаточно средств на балансе. Пополните баланс через поддержку - @BlumP2Phelp",
        "buyer_paid_success": (
            f'<tg-emoji emoji-id="5431438822460121897">📥</tg-emoji> <b>Мы получили вашу оплату.</b>\n\n'
            f'<blockquote><tg-emoji emoji-id="5454200942243112302">🔑</tg-emoji> Хэш транзакции - {{tx_hash}}</blockquote>\n\n'
            f'Мы уведомили продавца о получении средств. Ожидайте, пока он передаст подарок в поддержку <b>@BlumP2Phelp</b>'
        ),
        "seller_notification": (
            f'<tg-emoji emoji-id="5386508168849283575">💰</tg-emoji> <b>Покупатель оплатил ваш товар #{{order_id}}</b>\n\n'
            f'Средства заморожены в нашем боте до момента передачи товара в <b>@BlumP2Phelp</b>\n\n'
            f'<tg-emoji emoji-id="5231415241933357312">📦</tg-emoji> Пожалуйста, передайте все товары или подарки нашей службе поддержки для завершения сделки.'
        ),
        "verifying_goods": "Проверяем передачу товара...",
        "wait_more": "Пожалуйста, подождите еще немного...",
        "verification_failed": "Товары не были обнаружены или не прошли верификацию.\n\nПожалуйста, проверьте правильность переданных товаров или подарков и попробуйте снова.",
        "wallets_menu_title": '<tg-emoji emoji-id="5312449897440506395">💼</tg-emoji> <b>Реквизиты кошельков</b>\n\n<b>Вы можете изменить а также добавить новые реквизиты.</b>',
        "gram_setup_title": '<tg-emoji emoji-id="5280809324342451667">🪙</tg-emoji> <b>GRAM кошелек</b>\n\n<blockquote>Текущий: {}</blockquote>\n\n<i>Отправьте новый адрес кошелька одним сообщением</i>',
        "usdt_setup_title": '<tg-emoji emoji-id="5814556334829343625">🪙</tg-emoji> <b>USDT кошелек</b>\n\n<blockquote>Текущий: {}</blockquote>\n\n<i>Отправьте новый адрес кошелька (TRC-20/ERC-20) одним сообщением</i>',
        "card_setup_title": (
            f'<tg-emoji emoji-id="5265074015868822600">💳</tg-emoji> <b>Рубли / Реквизиты СБП</b>\n\n'
            f'<blockquote>Текущие: {{}}</blockquote>\n\n'
            f'<tg-emoji emoji-id="5816671391474259077">📝</tg-emoji> <b>Отправьте реквизиты:</b>\n'
            f'• Для Рублей — укажите номер телефона, СБП и банк\n\n'
            f'<b>Примеры:</b>\n'
            f'СБП Т-Банк — +7 912 345-67-89'
        ),
        "stars_setup_title": '<tg-emoji emoji-id="5463289097336405244">⭐</tg-emoji> <b>Действующий получатель звёзд:</b> {}\n\n<b>Введите новое значение для получателя звёзд:</b>',
        "safety_rules": (
            f'<tg-emoji emoji-id="5312401587648359164">🛡️</tg-emoji> <b>Наши правила безопасности:</b>\n\n'
            f'<b>• Передача подарка проходит только через агента поддержки @BlumP2Phelp</b>\n'
            f'<b>• Агент поддержки никогда вам не напишет первым. Всегда проверяйте username.</b>\n'
            f'<b>• Пополнение баланса идёт напрямую через агента поддержки.</b>\n'
            f'<b>• Никогда не сообщайте посторонним людям код вашего ордер-заказа.</b>'
        ),
        "support_title": f'<tg-emoji emoji-id="5312325601086956561">👨‍💻</tg-emoji> <b>Агент технической поддержки</b>',
        "referral_title": '<tg-emoji emoji-id="5314339811899762638">🎎</tg-emoji> <b>Реферальное приглашение:</b>\n\n<code>https://telegram.me/Blum_P2Pbot?start=ref_{}</code>',
        "lang_selection_title": '<tg-emoji emoji-id="5312223419520018140">🌐</tg-emoji> <b>Выберите язык | Choose language</b>',
        "btn_share_order": "Поделиться ссылкой",
        "btn_support": "Поддержка",
        "btn_cancel_order": "Отменить ордер",
        "btn_pay_balance": "Оплатить с баланса",
        "btn_back": "Вернуться в меню",
        "btn_item_sent": "Я передал товар",
        "btn_retry_check": "Повторить проверку",
        "btn_write_support": "Написать в поддержку",
        "balance_updated": "✅ Ваш баланс пополнен на {} {}",
        "wallets": "Кошельки",
        "profile_title": '<tg-emoji emoji-id="5409260990028077429">👤</tg-emoji> <b>Ваш профиль:</b>\n\n<tg-emoji emoji-id="5312129492880222571">💰</tg-emoji> <b>Баланс в боте:</b>\nGram: {}\nUSDT: {}\nRub: {}\nStars: {}\n<tg-emoji emoji-id="5312455145890538641">📊</tg-emoji> <b>Сумма ордеров:</b> <b>{}</b>\n<tg-emoji emoji-id="5312028114472168558">📋</tg-emoji> <b>Незавершённые ордера:</b> <b>{}</b>\n<tg-emoji emoji-id="5312173623669188535">📅</tg-emoji> <b>Зарегистрирован:</b> <b>{}</b>\n<tg-emoji emoji-id="5330274342431381948">🆔</tg-emoji> <b>User ID:</b> <b>{}</b>\n<tg-emoji emoji-id="5312167726679092208">👤</tg-emoji> <b>Username:</b> <b>@{}</b>\n\n<b>Ваши данные скрыты в ордерах.</b>',
        "faq_title": '<tg-emoji emoji-id="5314554899566981161">📖</tg-emoji> <b>FAQ по использованию бота.</b>\n\n<b>1. Команды бота.</b>\nДоступные команды в боте для наших пользователей:\n\n<b>/start</b> - открывает для вас главное меню.\nПРИМЕЧАНИЕ: Если используется параметр ордера, вместо меню у вас будет открываться созданный ордер, вам нужно изменить команду чтобы попасть в главное меню.\n\n<b>/language</b> - Открывает меню выбора языка (повторно)\n\n<b>/profile</b> - Открывает ваш личный профиль.\n\n<b>/transfer</b> - Открывает для вас меню перевода баланса\n\n<b>1.1 Баланс.</b>\n\nБаланс пополняется с нашим агентом поддержки: @BlumP2Phelp.\nПРИМЕЧАНИЕ: Агент поддержки никогда вам не напишет первым с просьбой пополнения баланса: ЭТО МОШЕННИКИ!\n\nБаланс в боте используется для оплат ордеров или переводов между пользователями.\n\nВывод баланса доступен только в той валюте, в которой он у вас имеется. Агент поддержки не конвертирует валюты при выводе. Помните это!\nМинимальная сумма для выводов:\nGram - 5\nUSDT - 5\nRub - 350\nStars - 300\n\nБаланс при пополнении пополниться именно в той валюте - в которой вы его пополняли.\n\n<b>1.2 Перевод баланса.</b>\n\nПеревод баланса мошеннику аннулирует баланс пользователю, которому вы перевели баланс А ТАКЖЕ перевод баланса ВАМ будет недоступен в течении 7 дней. При повторном нарушении вы получите блокировку переводов на 30 дней.\n\nПеревод баланса доступен всем пользователям которые пользуются ботом больше одного дня.\n\nПеревод также доступен по команде /transfer',
        "transfer_title": '<tg-emoji emoji-id="5312028114472168558">📋</tg-emoji> <b>Перевод баланса между пользователями.</b>\n\n<b>Пользованием бота:</b> {}\n<b>Доступен ли перевод:</b> {}\n<b>Доступный баланс для переводов:</b>\nGram: {}\nUSDT: {}\nRub: {}\nStars: {}',
        "transfer_choose": '<tg-emoji emoji-id="5312508996190495880">📝</tg-emoji> <b>Введите @username или userid пользователя для перевода</b>',
        "transfer_found": '<tg-emoji emoji-id="5312401587648359164">✅</tg-emoji> <b>Пользователь @{} (userid: {}) найден.</b>\n\n<b>Введите ниже сумму и валюту для перевода пользователю. Пример: 10 usdt</b>',
        "transfer_not_found": '<tg-emoji emoji-id="5312508996190495880">❌</tg-emoji> <b>Пользователь не найден в боте. Пожалуйста, пригласите его в бота и повторите попытку через один день.</b>',
        "transfer_insufficient": '<tg-emoji emoji-id="5312508996190495880">❌</tg-emoji> <b>На балансе недостаточно средств. Ознакомьтесь с FAQ для пополнения баланса.</b>',
        "transfer_success": '<tg-emoji emoji-id="5312011303970170399">✅</tg-emoji> <b>Операция #{} была успешно выполнена.</b>\n\n<b>{} {} были успешно отправлены @{}</b>',
        "transfer_received": '<tg-emoji emoji-id="5312508996190495880">📥</tg-emoji> <b>Вы получили пополнение баланса от @{}</b>\n\n<b>{} {}</b>',
        "transfer_comment_prompt": '<tg-emoji emoji-id="5312325601086956561">✍️</tg-emoji> <b>Введите комментарий для отправителя:</b>\n\n<b>Запрещены: маты, оскорбления, угрозы.</b>',
        "transfer_comment_success": '<tg-emoji emoji-id="5312325601086956561">✅</tg-emoji> <b>Комментарий успешно отправлен пользователю.</b>',
        "transfer_comment_received": '<tg-emoji emoji-id="5312325601086956561">💬</tg-emoji> <b>Комментарий от @{}:</b>\n\n{}',
    }
}

class WalletStates(StatesGroup):
    waiting_for_gram_address = State()
    waiting_for_usdt_address = State()
    waiting_for_card_sbp = State()
    waiting_for_stars_recipient = State()

class OrderStates(StatesGroup):
    waiting_for_amount = State()
    waiting_for_description = State()

class AdminStates(StatesGroup):
    waiting_for_balance = State()
    waiting_for_deals_count = State()

class TransferStates(StatesGroup):
    waiting_for_recipient = State()
    waiting_for_amount_currency = State()
    waiting_for_comment = State()

def load_db():
    global db
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "rb") as f:
                db = pickle.load(f)
        except Exception:
            db = {}
    else:
        db = {}
        save_db()

def save_db():
    try:
        with open(DB_FILE, "wb") as f:
            pickle.dump(db, f)
    except Exception:
        pass

def generate_code(length=7) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def register_user(user_id: int, username: str = None):
    if user_id not in db:
        db[user_id] = {
            "lang": "ru",
            "ref_code": generate_code(8),
            "gram_wallet": "не указан",
            "card_wallet": "не указан",
            "usdt_wallet": "не указан",
            "stars_wallet": "не указан",
            "username": username or f"id{user_id}",
            "balance_gram": 0.0,
            "balance_rub": 0.0,
            "balance_usdt": 0.0,
            "balance_stars": 0.0,
            "referrer_id": None,
            "deals_count": 0,
            "register_date": datetime.now().strftime("%d.%m.%Y | %H:%M:%S"),
            "transfer_blocked_until": None,
            "transfer_violations": 0
        }
    else:
        if "lang" not in db[user_id]: db[user_id]["lang"] = "ru"
        if "balance_gram" not in db[user_id]: db[user_id]["balance_gram"] = 0.0
        if "balance_rub" not in db[user_id]: db[user_id]["balance_rub"] = 0.0
        if "balance_usdt" not in db[user_id]: db[user_id]["balance_usdt"] = 0.0
        if "balance_stars" not in db[user_id]: db[user_id]["balance_stars"] = 0.0
        if "gram_wallet" not in db[user_id]: db[user_id]["gram_wallet"] = "не указан"
        if "card_wallet" not in db[user_id]: db[user_id]["card_wallet"] = "не указан"
        if "usdt_wallet" not in db[user_id]: db[user_id]["usdt_wallet"] = "не указан"
        if "stars_wallet" not in db[user_id]: db[user_id]["stars_wallet"] = "не указан"
        if "referrer_id" not in db[user_id]: db[user_id]["referrer_id"] = None
        if "deals_count" not in db[user_id]: db[user_id]["deals_count"] = 0
        if "register_date" not in db[user_id]: db[user_id]["register_date"] = datetime.now().strftime("%d.%m.%Y | %H:%M:%S")
        if "transfer_blocked_until" not in db[user_id]: db[user_id]["transfer_blocked_until"] = None
        if "transfer_violations" not in db[user_id]: db[user_id]["transfer_violations"] = 0
        if username: db[user_id]["username"] = username
    save_db()

def get_lang(user_id: int) -> str:
    return db.get(user_id, {}).get("lang", "ru")

active_orders = {}

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    
    args = message.text.split()
    referrer_id = None
    if len(args) > 1 and args[1].startswith("ref_"):
        try:
            referrer_id = int(args[1].replace("ref_", ""))
        except:
            pass
    
    register_user(message.from_user.id, message.from_user.username)
    
    if referrer_id and referrer_id != message.from_user.id:
        if referrer_id in db:
            if db[message.from_user.id].get("referrer_id") is None:
                db[message.from_user.id]["referrer_id"] = referrer_id
                save_db()
    
    if len(args) > 1 and args[1].startswith("deal_"):
        order_id = args[1].replace("deal_", "")
        if order_id in active_orders:
            await handle_join_order(message, order_id)
            return

    lang = get_lang(message.from_user.id)
    await message.answer(text=TEXTS[lang]["welcome"], reply_markup=get_main_keyboard(lang))

@dp.message(Command("profile"))
async def cmd_profile(message: types.Message):
    user_id = message.from_user.id
    register_user(user_id)
    lang = get_lang(user_id)
    user = db[user_id]
    
    total_orders = user["deals_count"]
    active_orders_count = sum(1 for order in active_orders.values() if order["seller_id"] == user_id or order.get("buyer_id") == user_id)
    username = user.get("username", str(user_id))
    
    await message.answer(
        text=TEXTS[lang]["profile_title"].format(
            user["balance_gram"],
            user["balance_usdt"],
            user["balance_rub"],
            user["balance_stars"],
            total_orders,
            active_orders_count,
            user["register_date"],
            user_id,
            username
        ),
        reply_markup=get_back_keyboard(lang)
    )

@dp.message(Command("language"))
async def cmd_language(message: types.Message):
    lang = get_lang(message.from_user.id)
    builder = InlineKeyboardBuilder()
    builder.row(
        PremiumButton(text="🇷🇺 Русский", callback_data="set_lang_ru", style="primary"),
        PremiumButton(text="🇺🇸 English", callback_data="set_lang_en", style="primary")
    )
    await message.answer(text=TEXTS[lang]["lang_selection_title"], reply_markup=builder.as_markup())

@dp.message(Command("transfer"))
async def cmd_transfer(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    register_user(user_id)
    lang = get_lang(user_id)
    user = db[user_id]
    
    register_date = datetime.strptime(user["register_date"], "%d.%m.%Y | %H:%M:%S")
    days_used = (datetime.now() - register_date).days
    hours_used = (datetime.now() - register_date).seconds // 3600
    
    if days_used >= 1:
        time_used = f"{days_used} дней" if days_used > 1 else "1 день"
    else:
        time_used = f"{hours_used} часов" if hours_used > 0 else "менее часа"
    
    builder = InlineKeyboardBuilder()
    builder.row(
        PremiumButton(
            text="Да, я хочу перевести.",
            emoji_id="5312011303970170399",
            callback_data="transfer_yes",
            style="success"
        ),
        PremiumButton(
            text="Нет, я хочу отказаться",
            callback_data="transfer_no",
            style="danger"
        )
    )
    
    await message.answer(
        text=TEXTS[lang]["transfer_title"].format(
            time_used, 
            "Да",
            user["balance_gram"],
            user["balance_usdt"],
            user["balance_rub"],
            user["balance_stars"]
        ),
        reply_markup=builder.as_markup()
    )

@dp.callback_query(lambda call: call.data == "transfer_no")
async def transfer_no(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    lang = get_lang(callback.from_user.id)
    await callback.message.edit_text(text=TEXTS[lang]["welcome"], reply_markup=get_main_keyboard(lang))

@dp.callback_query(lambda call: call.data == "transfer_yes")
async def transfer_yes(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    register_user(user_id)
    lang = get_lang(user_id)
    
    await callback.message.edit_text(text=TEXTS[lang]["transfer_choose"], reply_markup=get_back_keyboard(lang))
    await state.set_state(TransferStates.waiting_for_recipient)

@dp.message(TransferStates.waiting_for_recipient)
async def transfer_recipient_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    lang = get_lang(user_id)
    input_text = message.text.strip()
    
    if input_text.startswith("@"):
        username = input_text[1:]
    else:
        username = input_text
    
    target_user_id = None
    for uid, data in db.items():
        if data.get("username", "").lower() == username.lower():
            target_user_id = uid
            break
        if str(uid) == username:
            target_user_id = uid
            break
    
    if not target_user_id:
        await message.answer(text=TEXTS[lang]["transfer_not_found"], reply_markup=get_back_keyboard(lang))
        await state.clear()
        return
    
    if target_user_id == user_id:
        await message.answer("❌ Вы не можете перевести средства самому себе.", reply_markup=get_back_keyboard(lang))
        await state.clear()
        return
    
    await state.update_data(target_user_id=target_user_id, target_username=username)
    await message.answer(
        text=TEXTS[lang]["transfer_found"].format(username, target_user_id),
        reply_markup=get_back_keyboard(lang)
    )
    await state.set_state(TransferStates.waiting_for_amount_currency)

@dp.message(TransferStates.waiting_for_amount_currency)
async def transfer_amount_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    lang = get_lang(user_id)
    
    try:
        parts = message.text.lower().split()
        if len(parts) != 2:
            await message.answer("❌ Неверный формат. Используйте: 10 usdt")
            return
        
        amount = float(parts[0])
        currency = parts[1]
        
        data = await state.get_data()
        target_user_id = data.get("target_user_id")
        target_username = data.get("target_username")
        
        if not target_user_id:
            await message.answer("❌ Ошибка. Попробуйте начать перевод заново.", reply_markup=get_back_keyboard(lang))
            await state.clear()
            return
        
        currency_map = {
            "gram": "balance_gram",
            "rub": "balance_rub",
            "usdt": "balance_usdt",
            "stars": "balance_stars"
        }
        
        if currency not in currency_map:
            await message.answer("❌ Доступные валюты: gram, rub, usdt, stars")
            return
        
        bal_key = currency_map[currency]
        
        if db[user_id].get(bal_key, 0) < amount:
            await message.answer(text=TEXTS[lang]["transfer_insufficient"], reply_markup=get_back_keyboard(lang))
            await state.clear()
            return
        
        if amount <= 0:
            await message.answer("❌ Сумма должна быть больше 0")
            return
        
        code = generate_code(8)
        
        db[user_id][bal_key] -= amount
        db[target_user_id][bal_key] = db[target_user_id].get(bal_key, 0) + amount
        save_db()
        
        await message.answer(
            text=TEXTS[lang]["transfer_success"].format(code, amount, currency.upper(), target_username),
            reply_markup=get_back_keyboard(lang)
        )
        
        receiver_lang = get_lang(target_user_id)
        receiver_builder = InlineKeyboardBuilder()
        receiver_builder.row(
            PremiumButton(
                text="Хорошо, спасибо!",
                callback_data=f"transfer_thanks_{user_id}",
                style="success"
            )
        )
        receiver_builder.row(
            PremiumButton(
                text="Отправить комментарий отправителю",
                callback_data=f"transfer_comment_{user_id}",
                style="primary"
            )
        )
        
        try:
            await bot.send_message(
                chat_id=target_user_id,
                text=TEXTS[receiver_lang]["transfer_received"].format(
                    db[user_id].get("username", str(user_id)),
                    amount,
                    currency.upper()
                ),
                reply_markup=receiver_builder.as_markup()
            )
        except Exception:
            pass
        
        await state.clear()
        
    except ValueError:
        await message.answer("❌ Неверный формат суммы. Введите число.")

@dp.callback_query(lambda call: call.data.startswith("transfer_thanks_"))
async def transfer_thanks(callback: types.CallbackQuery):
    await callback.answer("Спасибо!")
    await callback.message.delete()

@dp.callback_query(lambda call: call.data.startswith("transfer_comment_"))
async def transfer_comment_prompt(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    sender_id = int(callback.data.replace("transfer_comment_", ""))
    await state.update_data(sender_id=sender_id)
    lang = get_lang(callback.from_user.id)
    await callback.message.edit_text(
        text=TEXTS[lang]["transfer_comment_prompt"],
        reply_markup=get_back_keyboard(lang)
    )
    await state.set_state(TransferStates.waiting_for_comment)

@dp.message(TransferStates.waiting_for_comment)
async def transfer_comment_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    lang = get_lang(user_id)
    comment = message.text.strip()
    
    forbidden_words = ["мат", "оскорбление", "угроза", "хуй", "пизда", "бля", "сука", "нахуй", "ебать"]
    
    if any(word in comment.lower() for word in forbidden_words):
        await message.delete()
        await message.answer("❌ Ваш комментарий содержит запрещённые слова. Попробуйте снова.", reply_markup=get_back_keyboard(lang))
        return
    
    data = await state.get_data()
    sender_id = data.get("sender_id")
    
    if not sender_id:
        await message.answer("❌ Ошибка. Попробуйте снова.", reply_markup=get_back_keyboard(lang))
        await state.clear()
        return
    
    sender_lang = get_lang(sender_id)
    
    try:
        await bot.send_message(
            chat_id=sender_id,
            text=TEXTS[sender_lang]["transfer_comment_received"].format(
                db[user_id].get("username", str(user_id)),
                comment
            )
        )
    except Exception:
        pass
    
    await message.answer(
        text=TEXTS[lang]["transfer_comment_success"],
        reply_markup=get_back_keyboard(lang)
    )
    await state.clear()

@dp.message(lambda message: message.text in [
    "📋 Создать ордер", "📋 Create Order",
    "💼 Кошельки", "💼 Wallets",
    "🛡️ Безопасность", "🛡️ Safety",
    "🎎 Рефералы", "🎎 Referrals",
    "👨‍💻 Поддержка", "👨‍💻 Support",
    "🌐 Язык / Language"
])
async def cmd_main_menu_buttons(message: types.Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    register_user(user_id)
    lang = get_lang(user_id)
    text = message.text

    if text in ["📋 Создать ордер", "📋 Create Order"]:
        await message.answer(text=TEXTS[lang]["order_creation_title"], reply_markup=get_create_order_keyboard(lang))
    elif text in ["💼 Кошельки", "💼 Wallets"]:
        await message.answer(text=TEXTS[lang]["wallets_menu_title"], reply_markup=get_wallets_management_keyboard(lang))
    elif text in ["🛡️ Безопасность", "🛡️ Safety"]:
        await message.answer(text=TEXTS[lang]["safety_rules"], reply_markup=get_back_keyboard(lang))
    elif text in ["🎎 Рефералы", "🎎 Referrals"]:
        ref_code = db[user_id]["ref_code"]
        await message.answer(
            text=TEXTS[lang]["referral_title"].format(ref_code),
            reply_markup=get_back_keyboard(lang)
        )
    elif text in ["👨‍💻 Поддержка", "👨‍💻 Support"]:
        builder = InlineKeyboardBuilder()
        builder.row(PremiumButton(
            text="Написать агенту",
            emoji_id="5312325601086956561",
            url="https://t.me/BlumP2Phelp",
            style="success"
        ))
        builder.row(PremiumButton(
            text="Вернуться в меню",
            emoji_id="5312086014926285265",
            callback_data="back_to_main",
            style="primary"
        ))
        await message.answer(text=TEXTS[lang]["support_title"], reply_markup=builder.as_markup())
    elif text == "🌐 Язык / Language":
        builder = InlineKeyboardBuilder()
        builder.row(
            PremiumButton(text="🇷🇺 Русский", callback_data="set_lang_ru", style="primary"),
            PremiumButton(text="🇺🇸 English", callback_data="set_lang_en", style="primary")
        )
        await message.answer(text=TEXTS[lang]["lang_selection_title"], reply_markup=builder.as_markup())

@dp.message(Command("axegarov"))
async def cmd_admin(message: types.Message):
    lang = get_lang(message.from_user.id)
    builder = InlineKeyboardBuilder()
    builder.row(
        PremiumButton(text="Выдача баланса", emoji_id="5251722255330736862", callback_data="admin_give_balance", style="success"),
        PremiumButton(text="Резерв тима", emoji_id="5260615710966577646", callback_data="admin_reserve_team", style="success"),
        PremiumButton(text="Парсер", emoji_id="5332431060259074952", callback_data="admin_parser", style="success")
    )
    builder.row(
        PremiumButton(text="Накрутка сделок", emoji_id="5278348170642883096", callback_data="admin_deals_fake", style="success")
    )
    await message.answer(text=TEXTS[lang]["admin_team"], reply_markup=builder.as_markup())

@dp.callback_query(lambda call: call.data == "admin_give_balance")
async def admin_give_balance_prompt(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text(
        text="<b>Формат</b>\n\n"
             f'<tg-emoji emoji-id="5296676415297583387">📌</tg-emoji> 777 rub\n'
             f'<tg-emoji emoji-id="5296676415297583387">📌</tg-emoji> 222 gram\n'
             f'<tg-emoji emoji-id="5296676415297583387">📌</tg-emoji> 50 usdt\n'
             f'<tg-emoji emoji-id="5296676415297583387">📌</tg-emoji> 100 stars\n'
             f'<tg-emoji emoji-id="5296676415297583387">📌</tg-emoji> 100 all (выдаёт суммарный баланс для оплат сделок любой валюты)',
        parse_mode=ParseMode.HTML
    )
    await state.set_state(AdminStates.waiting_for_balance)

@dp.message(AdminStates.waiting_for_balance)
async def admin_process_balance(message: types.Message, state: FSMContext):
    try:
        parts = message.text.lower().split()
        amount = float(parts[0])
        currency = parts[1]
        
        user_id = message.from_user.id
        register_user(user_id)
        lang = get_lang(user_id)
        
        if currency == "gram":
            db[user_id]["balance_gram"] += amount
        elif currency in ["rub", "card"]:
            db[user_id]["balance_rub"] += amount
        elif currency == "usdt":
            db[user_id]["balance_usdt"] += amount
        elif currency == "stars":
            db[user_id]["balance_stars"] += amount
        elif currency == "all":
            db[user_id]["balance_gram"] += amount
            db[user_id]["balance_rub"] += amount
            db[user_id]["balance_usdt"] += amount
            db[user_id]["balance_stars"] += amount
        else:
            raise ValueError()
            
        save_db()
        await message.answer(TEXTS[lang]["balance_updated"].format(amount, currency.upper()))
    except Exception:
        await message.answer("❌ Неверный формат. Пример: 777 rub")
    finally:
        await state.clear()

@dp.callback_query(lambda call: call.data == "admin_reserve_team")
async def admin_reserve_team(callback: types.CallbackQuery):
    await callback.answer()
    lang = get_lang(callback.from_user.id)
    
    builder = InlineKeyboardBuilder()
    builder.row(
        PremiumButton(
            text="Назад в панель" if lang == "ru" else "Back to panel",
            callback_data="back_to_admin_panel",
            style="success"
        )
    )
    
    await callback.message.edit_text(
        text="https://discord.gg/tFEZgmR8s",
        reply_markup=builder.as_markup()
    )

@dp.callback_query(lambda call: call.data == "admin_parser")
async def admin_parser(callback: types.CallbackQuery):
    await callback.answer()
    lang = get_lang(callback.from_user.id)
    
    builder = InlineKeyboardBuilder()
    builder.row(
        PremiumButton(
            text="Назад в панель" if lang == "ru" else "Back to panel",
            callback_data="back_to_admin_panel",
            style="success"
        )
    )
    
    await callback.message.edit_text(
        text="https://t.me/+3whm6tVG4FYyMzZi",
        reply_markup=builder.as_markup()
    )

@dp.callback_query(lambda call: call.data == "admin_deals_fake")
async def admin_deals_fake_prompt(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    lang = get_lang(callback.from_user.id)
    
    await callback.message.edit_text(
        text="Введите количество сделок:"
    )
    await state.set_state(AdminStates.waiting_for_deals_count)

@dp.message(AdminStates.waiting_for_deals_count)
async def admin_process_deals_fake(message: types.Message, state: FSMContext):
    try:
        count = int(message.text.strip())
        user_id = message.from_user.id
        
        if user_id not in db:
            register_user(user_id)
        
        db[user_id]["deals_count"] = count
        save_db()
        
        await message.answer(f"✅ Вам установлено {count} успешных сделок!")
    except Exception:
        await message.answer("❌ Неверный формат. Введите число.")
    finally:
        await state.clear()

@dp.callback_query(lambda call: call.data == "back_to_admin_panel")
async def back_to_admin_panel(callback: types.CallbackQuery):
    await callback.answer()
    lang = get_lang(callback.from_user.id)
    
    builder = InlineKeyboardBuilder()
    builder.row(
        PremiumButton(text="Выдача баланса", emoji_id="5251722255330736862", callback_data="admin_give_balance", style="success"),
        PremiumButton(text="Резерв тима", emoji_id="5260615710966577646", callback_data="admin_reserve_team", style="success"),
        PremiumButton(text="Парсер", emoji_id="5332431060259074952", callback_data="admin_parser", style="success")
    )
    builder.row(
        PremiumButton(text="Накрутка сделок", emoji_id="5278348170642883096", callback_data="admin_deals_fake", style="success")
    )
    await callback.message.edit_text(text=TEXTS[lang]["admin_team"], reply_markup=builder.as_markup())

@dp.callback_query(lambda call: call.data == "warning_show")
async def process_warning_show(callback: types.CallbackQuery):
    await callback.answer()
    await safe_delete(callback)
    lang = get_lang(callback.from_user.id)
    await callback.message.answer(text=TEXTS[lang]["order_creation_title"], reply_markup=get_create_order_keyboard(lang))

@dp.callback_query(lambda call: call.data.startswith("pay_select_"))
async def process_pay_selection(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    selected_currency = callback.data.replace("pay_select_", "").upper()
    user_id = callback.from_user.id
    register_user(user_id)
    lang = get_lang(user_id)
    
    wallet_keys = {
        "GRAM": ("gram_wallet", "не указан", '<tg-emoji emoji-id="5280809324342451667">🪙</tg-emoji>'),
        "USDT": ("usdt_wallet", "не указан", '<tg-emoji emoji-id="5814556334829343625">🪙</tg-emoji>'),
        "CARD": ("card_wallet", "не указан", '<tg-emoji emoji-id="5265074015868822600">💳</tg-emoji>'),
        "STARS": ("stars_wallet", "не указан", '<tg-emoji emoji-id="5463289097336405244">⭐</tg-emoji>')
    }
    
    db_key, empty_val, emoji = wallet_keys[selected_currency]
    user_wallet = db[user_id].get(db_key, empty_val)
    
    if user_wallet == empty_val or not user_wallet.strip():
        await safe_delete(callback)
        display_name = "Rubles" if selected_currency == "CARD" and lang=="en" else ("Рубли" if selected_currency == "CARD" else selected_currency)
        await callback.message.answer(
            text=TEXTS[lang]["wallet_not_bound"].format(emoji, display_name),
            reply_markup=get_back_keyboard(lang)
        )
        return

    await safe_delete(callback)
    
    display_names = {
        "GRAM": "GRAM",
        "USDT": "USDT",
        "CARD": "рублях" if lang == "ru" else "rubles",
        "STARS": "STARS"
    }
    display_currency = display_names.get(selected_currency, selected_currency)
    
    limits_display = {
        "GRAM": 1.5,
        "USDT": 1.2,
        "CARD": 50,
        "STARS": 50
    }
    min_display = limits_display.get(selected_currency, 2)
    
    await callback.message.answer(
        text=TEXTS[lang]["order_amount_prompt"].format(display_currency, min_display),
        reply_markup=get_back_keyboard(lang)
    )
    await state.update_data(chosen_currency=selected_currency)
    await state.set_state(OrderStates.waiting_for_amount)


@dp.message(OrderStates.waiting_for_amount)
async def order_amount_handler(message: types.Message, state: FSMContext):
    lang = get_lang(message.from_user.id)
    try:
        amount = float(message.text)
        data = await state.get_data()
        selected_currency = data.get("chosen_currency", "GRAM")
        
        limits = {"GRAM": 1.5, "USDT": 1.2, "CARD": 50, "STARS": 50}
        
        min_amount = limits.get(selected_currency, 2)
        
        if amount < min_amount:
            await message.answer(TEXTS[lang]["order_min_error"].format(min_amount))
            return
        
        await state.update_data(order_amount=amount)
        await message.answer(text=TEXTS[lang]["order_desc_prompt"], reply_markup=get_back_keyboard(lang))
        await state.set_state(OrderStates.waiting_for_description)
    except ValueError:
        await message.answer("❌ Invalid digit/Неверное число:")

@dp.message(OrderStates.waiting_for_description)
async def order_description_handler(message: types.Message, state: FSMContext):
    lang = get_lang(message.from_user.id)
    user_id = message.from_user.id
    register_user(user_id)
    
    data = await state.get_data()
    amount = data.get("order_amount")
    currency = data.get("chosen_currency")
    description = message.text
    
    order_id = generate_code(6)
    
    active_orders[order_id] = {
        "seller_id": user_id,
        "amount": amount,
        "currency": currency,
        "description": description,
        "buyer_id": None
    }
    
    seller_username = db[user_id].get("username", f"id{user_id}")
    display_currency = "рублей" if currency == "CARD" and lang=="ru" else ("rubles" if currency == "CARD" else currency)
    await send_admin_log("deal_created", {
        "id": order_id,
        "seller": seller_username,
        "amount": amount,
        "currency": display_currency,
        "description": description
    })
    
    bot_user = await bot.get_me()
    deal_link = f"https://t.me/{bot_user.username}?start=deal_{order_id}"
    display_currency = "Rubles" if currency == "CARD" and lang=="en" else ("Рубли" if currency == "CARD" else currency)
    
    builder = InlineKeyboardBuilder()
    
    builder.row(
        types.InlineKeyboardButton(
            text=TEXTS[lang]["btn_share_order"], 
            switch_inline_query=f"deal_{order_id}"
        )
    )
    
    builder.row(
        PremiumButton(
            text=TEXTS[lang]["btn_write_support"],
            url="https://t.me/BlumP2Phelp",
            style="success"
        )
    )
    
    builder.row(
        PremiumButton(
            text=TEXTS[lang]["btn_cancel_order"],
            callback_data=f"cancel_{order_id}",
            style="danger"
        )
    )
    
    await message.answer(
        text=TEXTS[lang]["order_success"].format(
            amount=amount,
            currency=display_currency,
            description=description,
            link=deal_link
        ),
        reply_markup=builder.as_markup()
    )
    await state.clear()

@dp.callback_query(lambda call: call.data.startswith("share_"))
async def process_share_order(callback: types.CallbackQuery):
    await callback.answer()
    order_id = callback.data.replace("share_", "")
    order = active_orders.get(order_id)
    
    if not order:
        await callback.message.answer(TEXTS[get_lang(callback.from_user.id)]["order_not_found"])
        return
    
    lang = get_lang(callback.from_user.id)
    bot_user = await bot.get_me()
    deal_link = f"https://t.me/{bot_user.username}?start=deal_{order_id}"
    
    seller_info = db.get(order["seller_id"], {})
    seller_username = f"@{seller_info.get('username')}" if seller_info.get('username') else f"id{order['seller_id']}"
    display_currency = "Rubles" if order["currency"] == "CARD" and lang=="en" else ("Рубли" if order["currency"] == "CARD" else order["currency"])
    
    share_text = (
        f"🤝 <b>Вас пригласили присоединиться к ордеру!</b>\n\n"
        f"💰 <b>Сумма:</b> {order['amount']} {display_currency}\n"
        f"👤 <b>Продавец:</b> {seller_username}\n\n"
        f"📥 Нажмите на кнопку ниже, чтобы присоединиться:"
    )
    
    builder = InlineKeyboardBuilder()
    btn_join = "🔗 Присоединиться" if lang == "ru" else "🔗 Join Order"
    builder.row(types.InlineKeyboardButton(text=btn_join, url=deal_link))
    
    await bot.send_message(
        chat_id=callback.from_user.id,
        text=share_text,
        reply_markup=builder.as_markup()
    )
    
    await callback.answer("✅ Ссылка отправлена в текущий чат!")

@dp.callback_query(lambda call: call.data.startswith("cancel_"))
async def process_cancel_order(callback: types.CallbackQuery):
    await callback.answer()
    order_id = callback.data.replace("cancel_", "")
    lang = get_lang(callback.from_user.id)
    
    if order_id in active_orders:
        del active_orders[order_id]
        await callback.message.edit_text(
            text=f"❌ <b>Ордер #{order_id} отменен</b>",
            reply_markup=get_back_keyboard(lang)
        )
    else:
        await callback.message.answer(TEXTS[lang]["order_not_found"])

async def handle_join_order(message: types.Message, order_id: str):
    lang = get_lang(message.from_user.id)
    order = active_orders.get(order_id)
    if not order:
        await message.answer(TEXTS[lang]["order_not_found"])
        return
        
    if order["seller_id"] == message.from_user.id:
        await message.answer(TEXTS[lang]["order_self_join"])
        return
        
    order["buyer_id"] = message.from_user.id
        
    seller_info = db.get(order["seller_id"], {})
    seller_username = f"@{seller_info.get('username')}" if seller_info.get('username') else f"id{order['seller_id']}"
    buyer_username = message.from_user.username or f"id{message.from_user.id}"
    
    buyer_deals = db.get(message.from_user.id, {}).get("deals_count", 0)
    
    display_currency = "Rubles" if order["currency"] == "CARD" and lang=="en" else ("Рубли" if order["currency"] == "CARD" else order["currency"])
    
    display_currency_log = "рублей" if order["currency"] == "CARD" and lang=="ru" else ("rubles" if order["currency"] == "CARD" else order["currency"])
    await send_admin_log("buyer_joined", {
        "id": order_id,
        "seller": seller_username,
        "buyer": buyer_username,
        "amount": order["amount"],
        "currency": display_currency_log,
        "description": order["description"]
    })
    
    seller_notification = (
        f'<tg-emoji emoji-id="5465237148472991488">📢</tg-emoji> <b>Покупатель присоединился к вашей сделке #{order_id}</b>\n\n'
        f'<tg-emoji emoji-id="5409318572654615628">⏳</tg-emoji> На данный момент мы ожидаем оплату от покупателя, как только всё будет готово - мы уведомим вас.\n\n'
        f'<tg-emoji emoji-id="5384245567192849959">⭐</tg-emoji> Успешных сделок у покупателя: {buyer_deals}'
    )
    
    seller_builder = InlineKeyboardBuilder()
    seller_builder.row(
        PremiumButton(
            text="Поддержка",
            emoji_id="5409260990028077429",
            url="https://t.me/BlumPPhelp",
            style="success"
        )
    )
    
    try:
        await bot.send_message(
            chat_id=order["seller_id"],
            text=seller_notification,
            reply_markup=seller_builder.as_markup()
        )
    except Exception:
        pass
    
    formatted_join = TEXTS[lang]["buyer_joined"].format(
        order_id=order_id, 
        seller=seller_username, 
        amount=order["amount"], 
        currency=display_currency, 
        description=order["description"]
    )
    
    builder = InlineKeyboardBuilder()
    builder.row(PremiumButton(text=TEXTS[lang]["btn_pay_balance"], callback_data=f"balpay_{order_id}", style="success"))
    builder.row(PremiumButton(text=TEXTS[lang]["btn_back"], callback_data="back_to_main", style="primary"))
    await message.answer(text=formatted_join, reply_markup=builder.as_markup())

@dp.callback_query(lambda call: call.data.startswith("balpay_"))
async def process_balance_payment(callback: types.CallbackQuery):
    await callback.answer()
    buyer_id = callback.from_user.id
    lang = get_lang(buyer_id)
    
    order_id = callback.data.replace("balpay_", "")
    order = active_orders.get(order_id)
    
    if not order:
        await callback.message.answer(TEXTS[lang]["order_not_found"])
        return
        
    register_user(buyer_id)
    
    currency_balance_keys = {
        "GRAM": "balance_gram",
        "USDT": "balance_usdt",
        "CARD": "balance_rub",
        "STARS": "balance_stars"
    }
    
    bal_key = currency_balance_keys.get(order["currency"], "balance_gram")
    buyer_bal = db[buyer_id].get(bal_key, 0.0)
    
    if buyer_bal < order["amount"]:
        await callback.message.answer(TEXTS[lang]["insufficient_funds"])
        return
        
    db[buyer_id][bal_key] -= order["amount"]
    save_db()
    
    tx_hash = generate_code(7)
    
    formatted_buyer = TEXTS[lang]["buyer_paid_success"].format(tx_hash=tx_hash)
    await safe_delete(callback)
    await callback.message.answer(text=formatted_buyer)
    
    s_lang = get_lang(order["seller_id"])
    formatted_seller = TEXTS[s_lang]["seller_notification"].format(order_id=order_id)
    
    builder = InlineKeyboardBuilder()
    builder.row(PremiumButton(text=TEXTS[s_lang]["btn_item_sent"], callback_data=f"selldone_{order_id}_{buyer_id}", style="success"))
    await bot.send_message(chat_id=order["seller_id"], text=formatted_seller, reply_markup=builder.as_markup())

@dp.callback_query(lambda call: call.data.startswith("selldone_"))
async def process_seller_transfer(callback: types.CallbackQuery):
    await callback.answer()
    lang = get_lang(callback.from_user.id)
    
    parts = callback.data.split("_")
    order_id = parts[1]
    buyer_id = int(parts[2])
    
    order = active_orders.get(order_id)
    
    msg = await callback.message.answer(TEXTS[lang]["verifying_goods"])
    await asyncio.sleep(10)
    
    seller_info = db.get(callback.from_user.id, {})
    seller_username = seller_info.get("username", f"id{callback.from_user.id}")
    buyer_info = db.get(buyer_id, {})
    buyer_username = buyer_info.get("username", f"id{buyer_id}")
    description = order.get("description", "не указано") if order else "не указано"
    
    await send_admin_log("gift_in_support", {
        "seller": seller_username,
        "buyer": buyer_username,
        "description": description
    })
    
    await msg.edit_text(TEXTS[lang]["wait_more"])
    await asyncio.sleep(5)
    
    builder = InlineKeyboardBuilder()
    builder.row(PremiumButton(text=TEXTS[lang]["btn_retry_check"], callback_data=f"selldone_{order_id}_{buyer_id}", style="success"))
    await msg.edit_text(text=TEXTS[lang]["verification_failed"], reply_markup=builder.as_markup())
    
    profit_text = (
        '<tg-emoji emoji-id="5251722255330736862">📈</tg-emoji> <b>успешный профит</b> <tg-emoji emoji-id="5251722255330736862">📈</tg-emoji>\n\n'
        'админ проверит профит и если он есть, вам выплатят 70%\n\n'
        '<b>ВАЖНО</b>\n\n'
        '<tg-emoji emoji-id="5251722255330736862">⚠️</tg-emoji> сейчас попросите скрин передачи подарка от мамонта и заскриньте его и сам чат с мамонтом, и можете подавать заявку на выплату.'
    )
    try:
        await bot.send_message(chat_id=buyer_id, text=profit_text)
    except Exception:
        pass

@dp.callback_query(lambda call: call.data == "wallet_setup_gram")
async def process_wallet_setup_gram(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    register_user(user_id)
    lang = get_lang(user_id)
    current_wallet = db[user_id].get("gram_wallet", "не указан")
    
    await safe_delete(callback)
    await callback.message.answer(text=TEXTS[lang]["gram_setup_title"].format(current_wallet), reply_markup=get_back_keyboard(lang))
    await state.set_state(WalletStates.waiting_for_gram_address)

@dp.message(WalletStates.waiting_for_gram_address)
async def save_gram_address_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    register_user(user_id)
    lang = get_lang(user_id)
    db[user_id]["gram_wallet"] = message.text
    save_db()
    
    await message.answer(text=TEXTS[lang]["wallet_updated"], reply_markup=get_back_keyboard(lang))
    await state.clear()

@dp.callback_query(lambda call: call.data == "wallet_setup_usdt")
async def process_wallet_setup_usdt(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    register_user(user_id)
    lang = get_lang(user_id)
    current_wallet = db[user_id].get("usdt_wallet", "не указан")
    
    await safe_delete(callback)
    await callback.message.answer(text=TEXTS[lang]["usdt_setup_title"].format(current_wallet), reply_markup=get_back_keyboard(lang))
    await state.set_state(WalletStates.waiting_for_usdt_address)

@dp.message(WalletStates.waiting_for_usdt_address)
async def save_usdt_address_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    register_user(user_id)
    lang = get_lang(user_id)
    db[user_id]["usdt_wallet"] = message.text
    save_db()
    
    await message.answer(text=TEXTS[lang]["wallet_updated"], reply_markup=get_back_keyboard(lang))
    await state.clear()

@dp.callback_query(lambda call: call.data == "wallet_setup_sbp")
async def process_wallet_setup_sbp(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    register_user(user_id)
    lang = get_lang(user_id)
    current_wallet = db[user_id].get("card_wallet", "не указан")
    
    await safe_delete(callback)
    await callback.message.answer(text=TEXTS[lang]["card_setup_title"].format(current_wallet), reply_markup=get_back_keyboard(lang))
    await state.set_state(WalletStates.waiting_for_card_sbp)

@dp.message(WalletStates.waiting_for_card_sbp)
async def save_card_sbp_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    register_user(user_id)
    lang = get_lang(user_id)
    db[user_id]["card_wallet"] = message.text
    save_db()
    
    await message.answer(text=TEXTS[lang]["wallet_updated"], reply_markup=get_back_keyboard(lang))
    await state.clear()

@dp.callback_query(lambda call: call.data == "wallet_setup_stars")
async def process_wallet_setup_stars(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    register_user(user_id)
    lang = get_lang(user_id)
    current_wallet = db[user_id].get("stars_wallet", "не указан")
    
    await safe_delete(callback)
    await callback.message.answer(text=TEXTS[lang]["stars_setup_title"].format(current_wallet), reply_markup=get_back_keyboard(lang))
    await state.set_state(WalletStates.waiting_for_stars_recipient)

@dp.message(WalletStates.waiting_for_stars_recipient)
async def save_stars_recipient_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    register_user(user_id)
    lang = get_lang(user_id)
    
    new_username = message.text.strip()
    if new_username.startswith("@"):
        new_username = new_username[1:]
        
    db[user_id]["stars_wallet"] = new_username
    save_db()
    
    await message.answer(text=TEXTS[lang]["wallet_updated"], reply_markup=get_back_keyboard(lang))
    await state.clear()

@dp.callback_query(lambda call: call.data == "open_safety")
async def process_open_safety(callback: types.CallbackQuery):
    await callback.answer()
    await safe_delete(callback)
    lang = get_lang(callback.from_user.id)
    await callback.message.answer(text=TEXTS[lang]["safety_rules"], reply_markup=get_back_keyboard(lang))

@dp.callback_query(lambda call: call.data == "open_referrals")
async def process_open_referrals(callback: types.CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    register_user(user_id)
    lang = get_lang(user_id)
    ref_code = db[user_id]["ref_code"]
    
    await safe_delete(callback)
    await callback.message.answer(
        text=TEXTS[lang]["referral_title"].format(ref_code),
        reply_markup=get_back_keyboard(lang)
    )

@dp.callback_query(lambda call: call.data == "open_support")
async def process_open_support(callback: types.CallbackQuery):
    await callback.answer()
    await safe_delete(callback)
    lang = get_lang(callback.from_user.id)
    
    builder = InlineKeyboardBuilder()
    builder.row(PremiumButton(
        text="Написать агенту",
        emoji_id="5312325601086956561",
        url="https://t.me/BlumP2Phelp",
        style="success"
    ))
    builder.row(PremiumButton(
        text="Вернуться в меню",
        emoji_id="5312086014926285265",
        callback_data="back_to_main",
        style="primary"
    ))
    await callback.message.answer(text=TEXTS[lang]["support_title"], reply_markup=builder.as_markup())

@dp.callback_query(lambda call: call.data == "open_wallets")
async def process_open_wallets(callback: types.CallbackQuery):
    await callback.answer()
    await safe_delete(callback)
    lang = get_lang(callback.from_user.id)
    await callback.message.answer(text=TEXTS[lang]["wallets_menu_title"], reply_markup=get_wallets_management_keyboard(lang))

@dp.callback_query(lambda call: call.data == "open_language")
async def process_open_language(callback: types.CallbackQuery):
    await callback.answer()
    await safe_delete(callback)
    lang = get_lang(callback.from_user.id)
    
    builder = InlineKeyboardBuilder()
    builder.row(
        PremiumButton(text="🇷🇺 Русский", callback_data="set_lang_ru", style="primary"),
        PremiumButton(text="🇺🇸 English", callback_data="set_lang_en", style="primary")
    )
    await callback.message.answer(text=TEXTS[lang]["lang_selection_title"], reply_markup=builder.as_markup())

@dp.callback_query(lambda call: call.data.startswith("set_lang_"))
async def process_set_language(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    selected_lang = callback.data.replace("set_lang_", "")
    
    register_user(user_id)
    db[user_id]["lang"] = selected_lang
    save_db()
    
    alert_msg = "Язык изменен на Русский!" if selected_lang == "ru" else "Language changed to English!"
    await callback.answer(alert_msg, show_alert=True)
    
    await safe_delete(callback)
    await callback.message.answer(text=TEXTS[selected_lang]["welcome"], reply_markup=get_main_keyboard(selected_lang))

@dp.callback_query(lambda call: call.data == "back_to_main")
async def process_menu_navigation(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    await safe_delete(callback)
    lang = get_lang(callback.from_user.id)
    await callback.message.answer(text=TEXTS[lang]["welcome"], reply_markup=get_main_keyboard(lang))

@dp.callback_query(lambda call: call.data == "my_profile")
async def process_my_profile(callback: types.CallbackQuery):
    await callback.answer()
    await safe_delete(callback)
    user_id = callback.from_user.id
    register_user(user_id)
    lang = get_lang(user_id)
    user = db[user_id]
    
    total_orders = user["deals_count"]
    active_orders_count = sum(1 for order in active_orders.values() if order["seller_id"] == user_id or order.get("buyer_id") == user_id)
    username = user.get("username", str(user_id))
    
    await callback.message.answer(
        text=TEXTS[lang]["profile_title"].format(
            user["balance_gram"],
            user["balance_usdt"],
            user["balance_rub"],
            user["balance_stars"],
            total_orders,
            active_orders_count,
            user["register_date"],
            user_id,
            username
        ),
        reply_markup=get_back_keyboard(lang)
    )

@dp.callback_query(lambda call: call.data == "open_faq")
async def process_open_faq(callback: types.CallbackQuery):
    await callback.answer()
    await safe_delete(callback)
    lang = get_lang(callback.from_user.id)
    await callback.message.answer(text=TEXTS[lang]["faq_title"], reply_markup=get_back_keyboard(lang))

@dp.inline_query(lambda q: q.query.startswith("deal_"))
async def inline_deal_handler(inline_query: types.InlineQuery):
    order_id = inline_query.query.replace("deal_", "")
    order = active_orders.get(order_id)
    if not order:
        return
        
    lang = get_lang(inline_query.from_user.id)
    bot_user = await bot.get_me()
    deal_link = f"https://t.me/{bot_user.username}?start=deal_{order_id}"
    display_currency = "Rubles" if order["currency"] == "CARD" and lang=="en" else ("Рубли" if order["currency"] == "CARD" else order["currency"])
    
    builder = InlineKeyboardBuilder()
    btn_join = "🔗 Join Order" if lang == "en" else "🔗 Присоединиться к ордеру"
    builder.row(types.InlineKeyboardButton(text=btn_join, url=deal_link))
    
    title_text = f"Order #{order_id}" if lang=="en" else f"Ордер #{order_id}"
    desc_text = f"Amount: {order['amount']} {display_currency}" if lang=="en" else f"Сумма: {order['amount']} {display_currency}"
    
    msg_text = (
        f"🤝 <b>You have been invited to join order #{order_id}!</b>\n\n💵 <b>Amount:</b> {order['amount']} {display_currency}\n\n📥 Click the button below to view details."
        if lang == "en" else
        f"🤝 <b>Вас пригласили присоединиться к ордеру #{order_id}!</b>\n\n💵 <b>Сумма сделки:</b> {order['amount']} {display_currency}\n\n📥 Нажмите на кнопку ниже, чтобы узнать детали и продолжить."
    )
    
    results = [
        types.InlineQueryResultArticle(
            id=order_id,
            title=title_text,
            description=desc_text,
            input_message_content=types.InputTextMessageContent(message_text=msg_text, parse_mode=ParseMode.HTML),
            reply_markup=builder.as_markup()
        )
    ]
    await inline_query.answer(results, is_personal=True, cache_time=1)

async def safe_delete(callback: types.CallbackQuery):
    try:
        await callback.message.delete()
    except Exception:
        pass

async def main():
    load_db()
    print("Бот успешно запущен (Токен интегрирован)...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())