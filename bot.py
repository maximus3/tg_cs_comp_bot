# -*- coding: utf-8 -*-
import telebot
from functools import wraps

import config
import utils
import markups
import static_data
import views

# For logs
import logging

logging.basicConfig(format=u'%(filename)s %(funcName)s [LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s] %(name)s: %('
                           u'message)s',
                    level=logging.INFO, filename=config.DIRECTORY + 'cs_comp.log')

# Data
sessionStorage = {}
results = utils.ResultsData()

# Launch
views.create_tables()
bot = telebot.TeleBot(config.TOKEN)
logging.info('Server started')
print('Server started')


# sessionStorage decorator
def ss_dec(function_to_decorate):
    @wraps(function_to_decorate)
    def wrapped(message, *args, **kwargs):
        chat_id = message.chat.id
        if chat_id not in sessionStorage:
            sessionStorage[chat_id] = utils.UserData(chat_id)
        return function_to_decorate(message, *args, **kwargs)

    return wrapped


# sessionStorage callback decorator
def ss_call_dec(function_to_decorate):
    @wraps(function_to_decorate)
    def wrapped(call, *args, **kwargs):
        chat_id = call.message.chat.id
        if chat_id not in sessionStorage:
            sessionStorage[chat_id] = utils.UserData(chat_id)
        return function_to_decorate(call, *args, **kwargs)

    return wrapped


def noInline_dec(function_to_decorate):
    @wraps(function_to_decorate)
    def wrapped(message):
        chat_id = message.chat.id
        inline_message_id = sessionStorage[chat_id].resetInline()
        if inline_message_id:
            bot.edit_message_text(chat_id=chat_id,
                                  message_id=inline_message_id,
                                  text=static_data.MESSAGES['any']['old_message'],
                                  parse_mode='Markdown')
        return function_to_decorate(message)

    return wrapped


def checkInline_dec(function_to_decorate):
    @wraps(function_to_decorate)
    def wrapped(call):
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        user = sessionStorage[chat_id]
        bot.edit_message_text(chat_id=chat_id,
                              message_id=message_id,
                              text=static_data.MESSAGES['any']['loading'].forUser + '\n' + call.message.text,
                              parse_mode='Markdown')
        inline_message_id = sessionStorage[chat_id].resetInline()
        if inline_message_id is None or inline_message_id != message_id:
            bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                  text=static_data.MESSAGES['any']['old_message'],
                                  parse_mode='Markdown')
            if inline_message_id:
                bot.edit_message_text(chat_id=chat_id,
                                      message_id=inline_message_id,
                                      text=static_data.MESSAGES['any'][
                                               'old_message'].forUser + '\n' + call.message.text,
                                      parse_mode='Markdown')
            return
        return function_to_decorate(call)

    return wrapped


@ss_call_dec
def check_call_step(call, data, step=None):
    if not call.message:
        return False
    chat_id = call.message.chat.id
    cur_step = sessionStorage[chat_id].getStep()
    cur_data = call.data

    condition1 = True
    condition2 = cur_data.startswith(data)

    if step is not None:
        condition1 = cur_step == step if step[-1] != '_' else cur_step.startswith(step)

    return condition1 and condition2


@ss_dec
def check_step(message, step, text=None):
    chat_id = message.chat.id
    cur_step = sessionStorage[chat_id].getStep()

    condition1 = cur_step == step if step[-1] != '_' else cur_step.startswith(step)
    condition2 = message.text.lower() == text.lower() if (text and message.text) else True

    return condition1 and condition2


@bot.message_handler(commands=['start'])
@ss_dec
@noInline_dec
def handle_start(message):
    chat_id = message.chat.id
    user = sessionStorage[chat_id]
    step = user.getStep()

    sent = bot.send_message(chat_id, static_data.MESSAGES[step]['start'], reply_markup=markups.MUP.setdefault(step, markups.back_pad))

    user.setInline(sent.message_id)


@bot.callback_query_handler(func=lambda call: check_call_step(call, 'back'))
@checkInline_dec
def handler_inline_back(call):
    chat_id = call.message.chat.id
    user = sessionStorage[chat_id]

    step = user.prevStep()

    bot.edit_message_text(chat_id=chat_id,
                          message_id=call.message.message_id,
                          text=static_data.MESSAGES[step]['start'],
                          reply_markup=markups.MUP.setdefault(step, markups.back_pad),
                          parse_mode='Markdown')

    user.setInline(call.message.message_id)


@bot.callback_query_handler(func=lambda call: check_call_step(call, 'result', 'main'))
@checkInline_dec
def handler_inline_result(call):
    chat_id = call.message.chat.id
    user = sessionStorage[chat_id]
    step = user.getStep()

    text = results.getAll()

    bot.edit_message_text(chat_id=chat_id,
                          message_id=call.message.message_id,
                          text=text,
                          reply_markup=markups.MUP.setdefault(step, markups.back_pad),
                          parse_mode='Markdown')

    user.setInline(call.message.message_id)


@bot.callback_query_handler(func=lambda call: check_call_step(call, 'by_commands', 'main'))
@checkInline_dec
def handler_inline_by_commands(call):
    chat_id = call.message.chat.id
    user = sessionStorage[chat_id]
    step = user.nextStep('showByCommands')

    bot.edit_message_text(chat_id=chat_id,
                          message_id=call.message.message_id,
                          text=static_data.MESSAGES[step]['start'],
                          reply_markup=markups.MUP.setdefault(step, markups.back_pad),
                          parse_mode='Markdown')

    user.setInline(call.message.message_id)


@bot.message_handler(func=lambda message: check_step(message, 'main_showByCommands'), content_types=['text'])
@noInline_dec
def handler_main_showByCommands(message):
    chat_id = message.chat.id
    user = sessionStorage[chat_id]

    if not message.text.isdigit():
        sent = bot.send_message(chat_id, static_data.MESSAGES[user.getStep()]['not_digit'],
                                reply_markup=markups.MUP.setdefault(user.prevStep(), markups.back_pad))
    else:
        command = int(message.text)
        text = results.getByCommand(command)
        sent = bot.send_message(chat_id, text, reply_markup=markups.MUP.setdefault(user.prevStep(), markups.back_pad),
                                parse_mode='Markdown')

    user.setInline(sent.message_id)


@bot.callback_query_handler(func=lambda call: check_call_step(call, 'by_competitions', 'main'))
@checkInline_dec
def handler_inline_by_competitions(call):
    chat_id = call.message.chat.id
    user = sessionStorage[chat_id]
    step = user.nextStep('showByCompetition')

    bot.edit_message_text(chat_id=chat_id,
                          message_id=call.message.message_id,
                          text=static_data.MESSAGES[step]['start'],
                          reply_markup=markups.MUP.setdefault(step, markups.back_pad),
                          parse_mode='Markdown')

    user.setInline(call.message.message_id)


@bot.callback_query_handler(func=lambda call: check_call_step(call, 'showByCompetition_'))
@checkInline_dec
def handler_inline_showByCompetition(call):
    chat_id = call.message.chat.id
    user = sessionStorage[chat_id]
    step = user.prevStep()

    competition = call.data.split('_')[-1]
    text = results.getByCompetition(competition)

    bot.edit_message_text(chat_id=chat_id,
                          message_id=call.message.message_id,
                          text=text,
                          reply_markup=markups.MUP.setdefault(step, markups.back_pad),
                          parse_mode='Markdown')

    user.setInline(call.message.message_id)


@bot.callback_query_handler(func=lambda call: check_call_step(call, 'rules', 'main'))
@checkInline_dec
def handler_inline_rules(call):
    chat_id = call.message.chat.id
    user = sessionStorage[chat_id]
    step = user.nextStep('rules')

    bot.edit_message_text(chat_id=chat_id,
                          message_id=call.message.message_id,
                          text=static_data.MESSAGES[step]['start'],
                          reply_markup=markups.MUP.setdefault(step, markups.back_pad),
                          parse_mode='Markdown')

    user.setInline(call.message.message_id)


@bot.callback_query_handler(func=lambda call: check_call_step(call, 'rules_', 'main_rules'))
@checkInline_dec
def handler_inline_showRules(call):
    chat_id = call.message.chat.id
    user = sessionStorage[chat_id]
    step = user.prevStep()

    competition = call.data.split('_')[-1]
    rule = static_data.RULES_MESSAGE[competition][1]

    bot.edit_message_text(chat_id=chat_id,
                          message_id=call.message.message_id,
                          text=rule,
                          reply_markup=markups.MUP.setdefault(step, markups.back_pad),
                          parse_mode='Markdown')

    user.setInline(call.message.message_id)


@bot.callback_query_handler(func=lambda call: check_call_step(call, 'admin_auth', 'main'))
@checkInline_dec
def handler_inline_admin_auth(call):
    chat_id = call.message.chat.id
    user = sessionStorage[chat_id]
    step = user.nextStep('adminAuth')

    if user.isAdmin():
        user.prevStep()
        step = user.nextStep('adminPanel')

    bot.edit_message_text(chat_id=chat_id,
                          message_id=call.message.message_id,
                          text=static_data.MESSAGES[step]['start'],
                          reply_markup=markups.MUP.setdefault(step, markups.back_pad),
                          parse_mode='Markdown')

    user.setInline(call.message.message_id)


@bot.message_handler(func=lambda message: check_step(message, 'main_adminAuth'), content_types=['text'])
@noInline_dec
def handler_main_adminAuth(message):
    chat_id = message.chat.id
    user = sessionStorage[chat_id]

    if user.auth(message.text):
        user.prevStep()
        step = user.nextStep('adminPanel')
        sent = bot.send_message(chat_id, static_data.MESSAGES[step]['start'],
                                reply_markup=markups.MUP.setdefault(step, markups.back_pad))
    else:
        sent = bot.send_message(chat_id, static_data.MESSAGES[user.getStep()]['not_valid'],
                                reply_markup=markups.MUP.setdefault(user.prevStep(), markups.back_pad))

    user.setInline(sent.message_id)


@bot.callback_query_handler(func=lambda call: check_call_step(call, 'admin_', 'main_adminPanel'))
@checkInline_dec
def handler_inline_adminPanel(call):
    chat_id = call.message.chat.id
    user = sessionStorage[chat_id]
    step = user.nextStep('group')

    user.competition_to_add = call.data.split('_')[-1]

    bot.edit_message_text(chat_id=chat_id,
                          message_id=call.message.message_id,
                          text=static_data.MESSAGES[user.getStep()]['start'],
                          reply_markup=markups.MUP.setdefault(step, markups.back_pad),
                          parse_mode='Markdown')

    user.setInline(call.message.message_id)


@bot.message_handler(func=lambda message: check_step(message, 'main_adminPanel_group'), content_types=['text'])
@noInline_dec
def handler_main_adminPanel_group(message):
    chat_id = message.chat.id
    user = sessionStorage[chat_id]
    step = user.getStep()

    if not message.text.isdigit():
        sent = bot.send_message(chat_id, static_data.MESSAGES[step]['not_digit'],
                                reply_markup=markups.MUP.setdefault(step, markups.back_pad))
    else:
        user.command_to_add = int(message.text)
        user.prevStep()
        step = user.nextStep('result')
        sent = bot.send_message(chat_id, static_data.MESSAGES[step]['start'],
                         reply_markup=markups.MUP.setdefault(step, markups.back_pad))

    user.setInline(sent.message_id)


@bot.message_handler(func=lambda message: check_step(message, 'main_adminPanel_result'), content_types=['text'])
@noInline_dec
def handler_main_adminPanel_result(message):
    chat_id = message.chat.id
    user = sessionStorage[chat_id]
    step = user.getStep()

    if not message.text.isdigit():
        sent = bot.send_message(chat_id, static_data.MESSAGES[step]['not_digit'],
                                reply_markup=markups.MUP.setdefault(step, markups.back_pad))
    else:
        user.result_to_add = int(message.text)
        results.add(user.competition_to_add, user.command_to_add, user.result_to_add)
        step = user.prevStep()
        sent = bot.send_message(chat_id, static_data.MESSAGES[step]['done'],
                         reply_markup=markups.MUP.setdefault(step, markups.back_pad))

    user.setInline(sent.message_id)


if __name__ == '__main__':
    bot.infinity_polling()
