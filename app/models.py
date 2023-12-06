# app/models.py
from app import db


book_authors = db.Table(
    'book_authors',
    db.Column('books_id', db.Integer, db.ForeignKey('book.id'), primary_key=True),
    db.Column('author_id', db.Integer, db.ForeignKey('author.id'), primary_key=True)
)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), index=True, unique=True)
    description = db.Column(db.Text)
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'))

    authors = db.relationship('Author', secondary=book_authors, backref=db.backref('books', lazy='dynamic'))

    # Define the relationship with Status
    status = db.relationship('Status', backref='book_status', lazy=True)

    def __str__(self):
        return f"<Book {self.title}>"


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    surname = db.Column(db.String(100))
    bio = db.Column(db.Text)

    def __str__(self):
        return f"<Author {self.name} {self.surname}>"


class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    available = db.Column(db.Boolean, default=True)
    borrower_name = db.Column(db.String(100))
    borrowed_date = db.Column(db.String(100))

    books = db.relationship('Book', backref='status_books', lazy=True)
    
    def __str__(self):
        if self.available:
            return "<Status: Available>"
        else:
            return f"<Status: Borrowed by {self.borrower_name} on {self.borrowed_date}>"

