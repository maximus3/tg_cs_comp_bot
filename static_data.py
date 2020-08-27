
class StaticMessage:
    def __init__(self, forUser=None, forLog=None):
        self.forUser = forUser
        self.forLog = forLog

    def __str__(self):
        return self.forUser


RULES_MESSAGE = { # Format: 'Short_name': ('Name', 'Rules')
    'toxic': ('Сбор токсичных осколков', '''
Правил нет!
'''),
    'demining': ('Разминирование', '''
Правил нет!
'''),
    'shrek': ('Переправа через болото', '''
Правил нет!
'''),
    'search': ('Поиск артефактов', '''
Правил нет!
'''),
    'readiness': ('Полная готовность', '''
Правил нет!
'''),
    'grenade': ('Метание гранат', '''
Правил нет!
'''),
    'field': ('Минное поле', '''
Правил нет!
'''),
}


MESSAGES = {
    'any': {
        'old_message': StaticMessage('_Данное сообщение уже устарело_'),
        'loading': StaticMessage('Загрузка...'),
    },
    'main': {
        'start': StaticMessage('Добро пожаловать!'),
    },
    'main_rules': {
        'start': StaticMessage('Выберите конкурс'),
    },
    'main_adminPanel': {
        'start': StaticMessage('Выберите соревнование для внесения результатов'),
        'done': StaticMessage('Результат успешно записан')
    },
    'main_adminPanel_group': {
        'start': StaticMessage('Введите номер команды'),
        'not_digit': StaticMessage('Номер группы должен быть числом')
    },
    'main_adminPanel_result': {
        'start': StaticMessage('Введите результат'),  # TODO: Description
        'not_digit': StaticMessage('Результат должен быть числом')
    },
    'main_showByCompetition': {
        'start': StaticMessage('Выберите конкурс'),
    },
    'main_showByCommands': {
        'start': StaticMessage('Введите номер команды'),
        'not_digit': StaticMessage('Номер группы должен быть числом')
    },
    'main_adminAuth': {
        'start': StaticMessage('Введите код авторизации'),
        'not_valid': StaticMessage('Вы ввели неправильный код')
    }
}