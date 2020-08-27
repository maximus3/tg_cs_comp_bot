from telebot import types
from static_data import RULES_MESSAGE

back_btn = types.InlineKeyboardButton(text='Назад', callback_data='back')
back_pad = types.InlineKeyboardMarkup()
back_pad.add(back_btn)

main_pad = types.InlineKeyboardMarkup()
main_pad.add(types.InlineKeyboardButton(text='Результаты', callback_data='result'))
main_pad.add(types.InlineKeyboardButton(text='Результаты по командам', callback_data='by_commands'))
main_pad.add(types.InlineKeyboardButton(text='Результаты по конкурсам', callback_data='by_competitions'))
main_pad.add(types.InlineKeyboardButton(text='Правила', callback_data='rules'))
main_pad.add(types.InlineKeyboardButton(text='Вход для админов', callback_data='admin_auth'))


def make_pad_with_names(callback_data):
    pad = types.InlineKeyboardMarkup()
    for competition in RULES_MESSAGE:
        name = RULES_MESSAGE[competition][0]
        pad.add(types.InlineKeyboardButton(text=name, callback_data=callback_data + '_' + competition))
    pad.add(back_btn)
    return pad


MUP = {
    'main': main_pad,
    'main_adminPanel': make_pad_with_names('admin'),
    'main_rules': make_pad_with_names('rules'),
    'main_showByCompetition': make_pad_with_names('showByCompetition'),
}
