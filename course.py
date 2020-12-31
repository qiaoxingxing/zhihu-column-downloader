from peewee import *

db = SqliteDatabase('course.db')

class Course(Model):
    id = CharField()
    title = CharField()
    author = CharField()
    url = CharField()
    price = FloatField()
    is_done = BooleanField() #是否完成
    log = CharField() #错误日志
    priority = FloatField() #下载优先级


    class Meta:
        database = db # This model uses the "people.db" database.


if __name__ == "__main__":
    # db.connect()
    # db.create_tables([Course])
    courses = [x for x in Course.select() if not x.is_done]
    courses.sort(key=lambda a: a.price,reverse=True)

    a = ""
