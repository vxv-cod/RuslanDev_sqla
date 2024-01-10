import sqlalchemy as db
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///db.sqlite', echo=False)

Base = declarative_base()

association = db.Table(
    'association', Base.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('book_id', db.Integer, db.ForeignKey('books.id')),
)


class Book(Base):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    author = db.Column(db.String(30), nullable=False)
    reviews = relationship('Review', backref='book', lazy='joined')
    readers = relationship(
        'User', secondary=association,
        back_populates='books', lazy=True
    )

    def __repr__(self):
        return f'{self.title}'


class Review(Base):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    text = db.Column(db.String(3000), nullable=False)

    def __repr__(self):
        return f'{self.text}'


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


Base.metadata.create_all(bind=engine)
