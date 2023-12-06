# app/routes.py

from flask import render_template, request, redirect, url_for, flash
from app import app, db
from app.models import Book, Status, Author
from datetime import datetime


@app.route('/', methods=['GET', 'POST'])
def homepage():
    if request.method == 'POST':
        # Fetch data from the form
        title = request.form['title']
        description = request.form['description']

        # Create a new Book object
        new_book = Book(title=title, description=description)

        # Create a new Status object for the new book
        new_status = Status(available=True, borrower_name=None, borrowed_date=None)

        try:
            # Add the book and status to the database session
            db.session.add(new_book)
            db.session.add(new_status)

            # Establish the relationship between book and status
            new_book.status = new_status

            # Commit changes to the database
            db.session.commit()

            flash('Book added successfully!')
            return redirect(url_for('homepage'))

        except Exception as e:
            flash(f'Error adding book: {str(e)}')
            return redirect(url_for('homepage'))

    # Fetch all books from the database
    all_books = Book.query.all()
    return render_template("home.html", books=all_books)


@app.route('/books')
def books():
    # Fetch all books from the database
    all_books = Book.query.all()

    return render_template("books.html", books=all_books)


@app.route('/authors')
def authors():
    return render_template("authors.html")


@app.route('/books/<int:book_id>', methods=['GET', 'POST'])
def books_details(book_id):
    book = Book.query.get(book_id)
    previous_status = book.status

    if request.method == 'POST':
        book.title = request.form['title']
        book.description = request.form['description']

        status = request.form.get('status')

        if status == 'available':
            book.status.borrower_name = None
            book.status.borrowed_date = None
            book.status.available = True
        elif status == 'borrowed':
            borrower_name = request.form['borrower_name']
            if not previous_status.available:
                # Retain the existing borrowed_date if status remains borrowed
                book.status.borrowed_date = previous_status.borrowed_date
            else:
                # Store the current date in the specified format
                book.status.borrowed_date = datetime.now().strftime('%Y-%m-%d')
                # book.status.borrowed_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # for tests
            book.status.borrower_name = borrower_name
            book.status.available = False

        db.session.commit()
        flash('Book details updated successfully!')
        return redirect(url_for('books_details', book_id=book_id))

    return render_template('book_details.html', book=book)

