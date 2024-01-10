# Primary key and foreign key
# Basic Relationship Patterns: One To Many, Many To Many, One To One


import sqlalchemy as db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship, backref

conn = create_engine('sqlite:///db.sqlite', echo=True)

Session = sessionmaker()
session = Session(bind=conn)

Base = declarative_base()


association = db.Table(
    'association', Base.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('book_id', db.Integer, db.ForeignKey('books.id')),
)


class Book(Base):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    cover_id = db.Column(db.Integer, db.ForeignKey('covers.id'))
    title = db.Column(db.String(50), nullable=False)
    author = db.Column(db.String(30), nullable=False)
    want_to_read = db.Column(db.Boolean, nullable=False, default=False)
    reviews = relationship('Review', backref='book', lazy=True)				# books to reviews as one to many
    readers = relationship(													# users to books as many to many
        'User', secondary=association,
        back_populates='books', lazy=True
    )
    cover = relationship('Cover', backref=backref('book', uselist=False))	# book to cover as one to one

    def __repr__(self):
        return f'{self.title}'


class Review(Base):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    text = db.Column(db.String(3000), nullable=False)

    def __repr__(self):
        return f'By {self.reviewer}'


class User(Base):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    reviews = relationship('Review', backref='reviewer', lazy=True)
    books = relationship(
        'Book', secondary=association,
        back_populates='readers', lazy=True
    )

    def __repr__(self):
        return f'{self.name}'


class Cover(Base):
    __tablename__ = 'covers'
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String, nullable=False)
    artist = db.Column(db.String)


Base.metadata.create_all(bind=conn)
