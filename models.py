import peewee

from config import DATA_BACKUP_FILE

database = peewee.SqliteDatabase(DATA_BACKUP_FILE)


class BaseModel(peewee.Model):
    name = peewee.CharField(max_length=16, verbose_name='Competition name')
    command = peewee.IntegerField(verbose_name='Command name')
    result = peewee.IntegerField(verbose_name='Result')

    class Meta:
        database = database


class Competition(BaseModel):
    pass
