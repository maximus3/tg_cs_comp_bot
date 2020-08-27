from config import ADMIN_IDS, ADMIN_CODE
import views


class ResultsData:

    def getAll(self):
        return views.getData()

    def getByCompetition(self, competition):
        return views.getDataByCompetition(competition)

    def getByCommand(self, command):
        return views.getDataByCommand(command)

    def add(self, name, command, result):
        return views.addData(name, command, result)

class UserData:
    _defaultValues = {
        'admin': False,
        'step': 'main',
        'inline': None,
    }

    def __init__(self, chat_id):

        self.chat_id = chat_id
        self._admin = (chat_id in ADMIN_IDS)

        self._step = self._defaultValues['step']
        self._inline = self._defaultValues['inline']

    def prevStep(self):
        step = self._step.split('_')
        step.pop()
        self._step = '_'.join(step)
        if len(self._step) == 0:
            self._step = self._defaultValues['step']
        return self._step

    def getStep(self):
        return self._step

    def nextStep(self, step):
        if step not in self._step:
            self._step += '_' + step
        return self._step

    def setInline(self, inline):
        self._inline = inline

    def resetInline(self):
        message_id = self._inline
        self._inline = self._defaultValues['inline']
        return message_id

    def getInline(self):
        return self._inline

    def isAdmin(self):
        return self._admin

    def auth(self, code):
        if code == ADMIN_CODE:
            self._admin = True
        return self._admin
