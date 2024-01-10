import random
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
    title = db.Column(db.String(50), nullable=False)
    author = db.Column(db.String(30), nullable=False)
    reviews = relationship('Review', backref='book', lazy=True)
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
        return f'By {self.text}'


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


Base.metadata.create_all(bind=conn)

# SqlAlchemy Query API
# sqlalchemy.orm.Query

books_data = [
    {'title': 'Властелин колец', 'author': 'Дж. Р. Р. Толкин'},
    {'title': 'Хроники Нарнии', 'author': 'К. С. Льюис'},
    {'title': 'Остров Сокровищ', 'author': 'Р. Стивенсон'},
    {'title': 'Грозовой перевал', 'author': 'Эмили Бронте'},
    {'title': 'Мартин Иден', 'author': 'Джек Лондон'}
]

# генерация записей для books
for data in books_data:
    book = Book(**data)
    session.add(book)
    session.commit()

all_books = session.query(Book).all()  # очень простой запрос

# генерация записей для users и reviews
for i in range(3):
    user = User(name=f'user{i+1}')
    random.shuffle(all_books)
    for j in range(5):
        book = all_books[j]
        review = Review(
            book_id=book.id,
            text=f'Ставлю {j+1} из 5'
        )
        user.reviews.append(review)
        if j % 2 == 0:
            user.books.append(book)
    session.add(user)
    session.commit()

# Запросы

books_by_title = session.query(Book).filter(
    Book.title == 'Властелин колец').all()
print('Запрос с фильтрацией:', books_by_title)

book_by_author = session.query(Book).filter_by(author='Р. Стивенсон').first()
print('Запрос с фильтрацией, способ 2:', book_by_author)

book_by_id = session.query(Book).get(3)
print('Запрос по id:', book_by_id)


books_5_score = session.query(Book).join(Review).filter(
    Review.text == 'Ставлю 5 из 5').all()

print('Запрос с JOIN:', books_5_score)

true_reviews = session.query(Review)\
    .join(User)\
    .filter(User.books.any(Book.id == Review.book_id)).all()

for review in true_reviews:
    print('Рецензированная книга:', review.book_id)
    print('Книги, прочитанные рецензентом:', [
          b.id for b in review.reviewer.books])
    print('-----------')


# Загрузка

# lazy loading

book = session.query(Book).first()
print('Теперь запрос будет выполнен:')
result = book.reviews  	# lazy
print(result)

from sqlalchemy.orm import lazyload

query = session.query(Book).options(lazyload(Book.reviews))
print('Теперь запрос будет выполнен:')
result = query.all()
print(result)

# eager loading, no loading
# ...
