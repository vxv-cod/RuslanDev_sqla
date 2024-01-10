# Для чего нужна сессия?
# 1. Производит все требуемые обращения к БД
# 2. Содержит ссылки на все загруженные во время запросов объекты
#    (если эти запросы и объекты были ассоциированы с текущей сессией)
# 3. Предоставляет доступ к Query object
# 4. Обеспечивает уникальность каждого объекта, созданного при маппинге,
#    если этот объект имеет уникальный первичный ключ (primary key)

from sqlalchemy.orm import sessionmaker

Session = sessionmaker()

from models import *

# Жизненный цикл сессии

# простой пример (https://docs.sqlalchemy.org/en/13/orm/session_basics.html#what-does-the-session-do)
def create_book(title, author):
    session = Session(bind=engine)
    try:
        # бизнес-логика
        book = Book(title=title, author=author)
        session.add(book)
        #

        session.commit()
        print(f'В базу записана строка {book.id}')
    except:
        session.rollback()
        print('rolled back')
        raise
    finally:
        session.close()


create_book('Война и мир', 'Л. Н. Толстой')

# пример с контекстным менеджером
from contextlib import contextmanager


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session(bind=engine)
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def create_many_books(data):
    with session_scope() as session:
        books = [Book(**item) for item in data]
        session.add_all(books)
        print(f'Записано в базу {session.query(Book).count()} строк')

books_data = [
    {'title': 'Властелин колец', 'author': 'Дж. Р. Р. Толкин'},
    {'title': 'Хроники Нарнии', 'author': 'К. С. Льюис'},
    {'title': 'Остров Сокровищ', 'author': 'Р. Стивенсон'},
    {'title': 'Грозовой перевал', 'author': 'Эмили Бронте'},
    {'title': 'Мартин Иден', 'author': 'Джек Лондон'}
]
create_many_books(books_data)


# практические примеры операций с сессией
def create_reviews(user):
    session = Session(bind=engine)
    try:
        user.reviews = [Review(book_id=i, text=f'{i} из 5') for i in range(1, 6)]
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def insert_many2many(user, data):
    session = Session(bind=engine)
    try:
        user.books = [Book(**item) for item in data]
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


session = Session(bind=engine)


user = User(name='Руслан')
session.add(user)
session.commit()

create_reviews(user)
print('Reviews:', user.reviews)

insert_many2many(user, books_data)
print('Книги пользователя:', user.books)


expire(), refresh(), flush()

import sqlite3
conn = sqlite3.connect('db.sqlite')
cur = conn.cursor()

query_update = f'''UPDATE users
SET name='Владимир'
WHERE id={user.id}
'''
print('База изменяется вне сессии')
cur.execute(query_update)
conn.commit()

print('До expire/refresh:', user.name)    # атрибут name был изменен за пределами сессии

session.expire(user)
print('expired')

print('После expire:', user.name)

session.refresh(user)
print('refreshed')

print('После refresh:', user.name)


def get_pk_before_commit(obj):
    session.add(obj)
    session.flush()
    session.refresh(obj)
    return obj.id


user = User(name='Александр')
print('Первичный ключ после flush():', get_pk_before_commit(user))

session.rollback()
print('Примечание: данные не записаны в базу', session.query(User).all())
