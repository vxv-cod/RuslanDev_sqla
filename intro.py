# SqlAlchemy и базы данных

# Raw SQL

# sqlite3 db.sqlite

# CREATE TABLE books
# (id bigint, title varchar(50), author varchar(100), want_to_read bool);

# INSERT INTO books VALUES (1, 'The Hobbit', 'John R. R. Tolkien', false);

import sqlite3

conn = sqlite3.connect('db.sqlite')

cur = conn.cursor()

query_select = '''SELECT title, want_to_read
FROM books
WHERE author LIKE 'John R. R. Tolkien'
'''

cur.execute(query_select)
rows = cur.fetchall()
print('Raw SQL query:', rows)


query_update = '''UPDATE books
SET want_to_read=true
WHERE title='The Hobbit'
'''

cur.execute(query_update)

conn.commit()

cur.execute(query_select)
rows = cur.fetchall()
print('Updated:', rows)

conn.close()

# SqlAlchemy Core

import sqlalchemy as db
from sqlalchemy.sql import select
from sqlalchemy import create_engine, MetaData

conn = create_engine('sqlite:///db.sqlite', echo=True)
metadata = MetaData()

books = db.Table(
    'books', metadata,
    db.Column('id', db.Integer, primary_key=True),
    db.Column('title', db.String(50), nullable=False),
    db.Column('author', db.String(30), nullable=False),
    db.Column('want_to_read', db.Boolean, nullable=False)
)

metadata.create_all(bind=conn)

conn.execute(
    books.insert(),
    {
        'title': 'The Hobbit',
        'author': 'John R. R. Tolkien',
        'want_to_read': False
    }
)

rows = conn.execute(
    select([books.c.title]).where(books.c.author == 'John R. R. Tolkien')
)

print('Query by SqlAlchemy core methods:')
for row in rows:
    print(row)


# Sqlalchemy ORM

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Session = sessionmaker()
session = Session(bind=conn)

Base = declarative_base()


class Book(Base):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    author = db.Column(db.String(30), nullable=False)
    want_to_read = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f'{self.title}'


Base.metadata.create_all(bind=conn)

book = Book(title='The Hobbit',
            author='John R. R. Tolkien', want_to_read=False)
session.add(book)
session.commit()

rows = session.query(Book).filter(Book.author == 'John R. R. Tolkien').all()
print('Query by SqlAlchemy ORM:', rows)
