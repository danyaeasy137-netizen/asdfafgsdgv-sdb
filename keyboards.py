from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class PremiumButton(InlineKeyboardButton):
    """
    Кастомный класс кнопки, поддерживающий icon_custom_emoji_id и кастомный style.
    Для обычных кнопок без премиум-эмодзи параметр emoji_id передаем как None.
    """
    def __init__(self, text: str, emoji_id: str = None, callback_data: str = None, url: str = None, style: str = "default"):
        super().__init__(
            text=text,
            callback_data=callback_data,
            url=url,
            icon_custom_emoji_id=emoji_id
        )
        self.style = style

def get_main_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """
    Генерирует главное инлайн-меню бота (EN по умолчанию / RU).
    """
    builder = InlineKeyboardBuilder()
    
    # Кнопка 1: Создать ордер
    btn_order_text = "Создать ордер" if lang == "ru" else "Create order"
    builder.row(
        PremiumButton(
            text=btn_order_text, 
            emoji_id="5845872131090422743", 
            callback_data="warning_show",
            style="success"
        )
    )
    
    # Кнопки 2: Кошельки и Безопасность
    btn_wallets_text = "Кошельки" if lang == "ru" else "Wallets"
    btn_safety_text = "Безопасность" if lang == "ru" else "Safety"
    builder.row(
        PremiumButton(text=btn_wallets_text, emoji_id="5818824140752163681", callback_data="open_wallets", style="primary"),
        PremiumButton(text=btn_safety_text, emoji_id="5409260990028077429", callback_data="open_safety", style="primary")
    )
    
    # Кнопки 3: Рефералы и Канал
    btn_ref_text = "Рефералы" if lang == "ru" else "Referrals"
    btn_channel_text = "Канал" if lang == "ru" else "Channel"
    builder.row(
        PremiumButton(text=btn_ref_text, emoji_id="5384245567192849959", callback_data="open_referrals", style="primary"),
        PremiumButton(text=btn_channel_text, emoji_id="5465237148472991488", url="https://t.me/BlumCrypto", style="primary")
    )
    
    # Кнопки 4: Поддержка и Язык
    btn_support_text = "Поддержка" if lang == "ru" else "Support"
    builder.row(
        PremiumButton(text=btn_support_text, emoji_id="5408848183541390145", callback_data="open_support", style="primary"),
        PremiumButton(text="Язык / Language", emoji_id="6001402990051725225", callback_data="open_language", style="primary")
    )
    
    return builder.as_markup()

def get_back_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """
    Универсальная клавиатура с кнопкой возврата в меню.
    """
    builder = InlineKeyboardBuilder()
    btn_back_text = "Вернуться в меню" if lang == "ru" else "Back to menu"
    builder.row(
        PremiumButton(
            text=btn_back_text,
            emoji_id="5330131801056768633",
            callback_data="back_to_main",
            style="primary"
        )
    )
    return builder.as_markup()

def get_create_order_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """
    Генерирует меню выбора оплаты для Создания ордера.
    """
    builder = InlineKeyboardBuilder()
    btn_card_text = "Рубли" if lang == "ru" else "Rubles"
    btn_back_text = "Вернуться в меню" if lang == "ru" else "Back to menu"
    
    builder.row(
        PremiumButton(text="GRAM", emoji_id="5834698898223933128", callback_data="pay_select_gram", style="primary"),
        PremiumButton(text="USDT", emoji_id="5814556334829343625", callback_data="pay_select_usdt", style="primary")
    )
    builder.row(
        PremiumButton(text=btn_card_text, emoji_id="5265074015868822600", callback_data="pay_select_card", style="primary"),
        PremiumButton(text="STARS", emoji_id="5463289097336405244", callback_data="pay_select_stars", style="primary")
    )
    builder.row(
        PremiumButton(text=btn_back_text, emoji_id="5330131801056768633", callback_data="back_to_main", style="primary")
    )
    
    return builder.as_markup()

def get_wallets_management_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """
    Генерирует клавиатуру управления кошельками.
    """
    builder = InlineKeyboardBuilder()
    
    btn_gram = "GRAM кошелек" if lang == "ru" else "GRAM wallet"
    btn_card = "Рубли/СБП" if lang == "ru" else "Rubles/P2P"
    btn_usdt = "USDT кошелек" if lang == "ru" else "USDT wallet"
    btn_stars = "STARS кошелек" if lang == "ru" else "STARS wallet"
    btn_back = "Вернуться в меню" if lang == "ru" else "Back to menu"
    
    builder.row(
        PremiumButton(text=btn_gram, emoji_id="5280809324342451667", callback_data="wallet_setup_gram", style="primary"),
        PremiumButton(text=btn_card, emoji_id="5265074015868822600", callback_data="wallet_setup_sbp", style="primary")
    )
    builder.row(
        PremiumButton(text=btn_usdt, emoji_id="5814556334829343625", callback_data="wallet_setup_usdt", style="primary"),
        PremiumButton(text=btn_stars, emoji_id="5463289097336405244", callback_data="wallet_setup_stars", style="primary")
    )
    builder.row(
        PremiumButton(text=btn_back, emoji_id="5330131801056768633", callback_data="back_to_main", style="primary")
    )
    return builder.as_markup()