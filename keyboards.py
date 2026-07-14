from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class PremiumButton(InlineKeyboardButton):
    def __init__(self, text: str, emoji_id: str = None, callback_data: str = None, url: str = None, style: str = "default"):
        super().__init__(
            text=text,
            callback_data=callback_data,
            url=url,
            icon_custom_emoji_id=emoji_id
        )
        self.style = style

def get_main_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    builder.row(
        PremiumButton(
            text="Мой профиль" if lang == "ru" else "My Profile",
            emoji_id="5409260990028077429",
            callback_data="my_profile",
            style="success"
        ),
        PremiumButton(
            text="Создать ордер" if lang == "ru" else "Create order",
            emoji_id="5312517474455938468",
            callback_data="warning_show",
            style="success"
        )
    )
    
    builder.row(
        PremiumButton(
            text="Кошельки" if lang == "ru" else "Wallets",
            emoji_id="5312449897440506395",
            callback_data="open_wallets",
            style="success"
        ),
        PremiumButton(
            text="Безопасность" if lang == "ru" else "Safety",
            emoji_id="5312401587648359164",
            callback_data="open_safety",
            style="success"
        )
    )
    
    builder.row(
        PremiumButton(
            text="Рефералы" if lang == "ru" else "Referrals",
            emoji_id="5314339811899762638",
            callback_data="open_referrals",
            style="primary"
        ),
        PremiumButton(
            text="Канал" if lang == "ru" else "Channel",
            emoji_id="5312083382111331507",
            url="https://t.me/BlumCrypto",
            style="primary"
        )
    )
    
    builder.row(
        PremiumButton(
            text="Агент поддержки" if lang == "ru" else "Support Agent",
            emoji_id="5312325601086956561",
            callback_data="open_support",
            style="primary"
        ),
        PremiumButton(
            text="Язык / Language",
            emoji_id="5312048743200089463",
            callback_data="open_language",
            style="primary"
        )
    )
    
    builder.row(
        PremiumButton(
            text="FAQ",
            emoji_id="5312146307677186233",
            callback_data="open_faq",
            style="success"
        )
    )
    
    return builder.as_markup()

def get_back_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    btn_back_text = "Вернуться в меню" if lang == "ru" else "Back to menu"
    builder.row(
        PremiumButton(
            text=btn_back_text,
            emoji_id="5312086014926285265",
            callback_data="back_to_main",
            style="primary"
        )
    )
    return builder.as_markup()

def get_create_order_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    btn_card_text = "Рубли" if lang == "ru" else "Rubles"
    btn_back_text = "Вернуться в меню" if lang == "ru" else "Back to menu"
    
    builder.row(
        PremiumButton(text="GRAM", emoji_id="5280809324342451667", callback_data="pay_select_gram", style="primary"),
        PremiumButton(text="USDT", emoji_id="5814556334829343625", callback_data="pay_select_usdt", style="primary")
    )
    builder.row(
        PremiumButton(text=btn_card_text, emoji_id="5265074015868822600", callback_data="pay_select_card", style="primary"),
        PremiumButton(text="STARS", emoji_id="5463289097336405244", callback_data="pay_select_stars", style="primary")
    )
    builder.row(
        PremiumButton(text=btn_back_text, emoji_id="5312086014926285265", callback_data="back_to_main", style="primary")
    )
    
    return builder.as_markup()

def get_wallets_management_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
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
        PremiumButton(text=btn_back, emoji_id="5312086014926285265", callback_data="back_to_main", style="primary")
    )
    return builder.as_markup()