from models import database, Competition
import os
from config import DIRECTORY, DATA_BACKUP_FILE
from static_data import RULES_MESSAGE
import logging

competition_data = {}
competition_table_data = {}

BASE_SCORE = 7

PLACES_TO_SCORE = {
    1: 7,
    2: 6,
    3: 5,
    4: 4,
    7: 3,
    11: 2,
    15: 1,
}


def get_places_and_results(data, reverse=True):
    results = []
    for command in data:
        results.append((data[command], command))
    results.sort(reverse=reverse)

    places = {}
    for i, res in enumerate(results):
        places[res[1]] = i + 1
    return places, results


def score_koef(data):
    places, results = get_places_and_results(data)
    all_data = {}
    max_res = max(results)[0]
    for command in data:
        all_data[command] = (places[command], round(BASE_SCORE * data[command] / max_res), data[command])
    return all_data


def score_demining(data):
    places, results = get_places_and_results(data)
    all_data = {}
    for command in data:
        all_data[command] = (places[command], data[command] // 2 + data[command] % 2, data[command])
    return all_data


def score_time(data):
    places, results = get_places_and_results(data, False)
    all_data = {}
    for command in data:
        place = places[command]
        while PLACES_TO_SCORE.get(place) is None:
            place -= 1
        all_data[command] = (places[command], PLACES_TO_SCORE.get(place), data[command])
    return all_data



types_of_score = { # Format: 'Short_name': function to get scores
    # Function return format: Dict(Command: (Place, Score, Result))
    'toxic': score_koef,
    'demining': score_demining,
    'shrek': score_time,
    'search': score_time,
    'readiness': score_time,
    'grenade': score_koef,
    'field': score_time,
}


def create_tables():
    logger = logging.getLogger('FUNC')
    if os.path.exists(DIRECTORY + DATA_BACKUP_FILE):
        logger.info('DB file already exists, updating data')
        updateData()
        return False
    with database:
        database.create_tables([Competition])
    logger.info('DB file created')
    return True


def updateData():
    logger = logging.getLogger('FUNC')
    global competition_data, competition_table_data

    data_db = Competition.select()

    for comp in data_db:
        if competition_data.get(comp.name) is None:
            competition_data[comp.name] = {}
            competition_table_data[comp.name] = {}
        competition_data[comp.name][comp.command] = comp.result

    for competition in competition_data:
        competition_table_data[competition] = types_of_score[competition](competition_data[competition])

    logger.info(f'Data updated')


def addData(competition, command, result):
    logger = logging.getLogger('FUNC')

    comp = Competition.select().where(Competition.name == competition, Competition.command == command)
    if len(comp):
        Competition.update({Competition.result: result}).where(Competition.name == competition,
                                                               Competition.command == command).execute()
    else:
        Competition.create(name=competition, command=command, result=result)
    if competition_data.get(competition) is None:
        competition_data[competition] = {}
    competition_data[competition][command] = result
    competition_table_data[competition] = types_of_score[competition](competition_data[competition])

    logger.info(f'Data saved')
    return True


def getDataByCompetition(competition):
    data = []
    if competition_table_data.get(competition) is not None:
        for command in competition_table_data[competition]:
            place, score, result = competition_table_data[competition][command]
            data.append(f'{place} место: Комманда *{command}* - {score}б ({result})')

    data.sort()
    ans = '\n'.join(data) if len(data) else 'Результатов пока нет'
    ans = f'Результаты по соревнованию *{RULES_MESSAGE[competition][0]}*:\n' + ans
    return ans


def getDataByCommand(command):
    data = []
    for competition in competition_table_data:
        place, score, result = competition_table_data[competition].get(command)
        if result:
            data.append(f'*{RULES_MESSAGE[competition][0]}*: {place} место - {score}б ({result})')
    ans = '\n'.join(data) if len(data) else 'Результатов пока нет'
    ans = f'Результаты по комманде *{command}*:\n' + ans
    return ans


def getData():
    data = []
    for competition in competition_data:
        data.append(getDataByCompetition(competition))

    ans = '\n\n'.join(data) if len(data) else 'Результатов пока нет'
    ans = f'Текущие результаты:\n\n' + ans
    return ans