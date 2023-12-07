# app/routes.py

from flask import render_template, request, redirect, url_for, flash
from app import app, db
from app.models import Book, Status, Author
from datetime import datetime


@app.route('/books/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']

        # Create the book and status
        new_book = Book(title=title, description=description)
        new_status = Status(available=True, borrower_name=None, borrowed_date=None)

        try:
            # Add the new_book and new_status to the session
            db.session.add(new_book)
            db.session.add(new_status)

            # Loop through form data to get author information
            authors = []
            for key in request.form.keys():
                if key.startswith('name'):
                    author_num = key.replace('name', '')
                    name = request.form[f'name{author_num}']
                    surname = request.form[f'surname{author_num}']
                    bio = request.form[f'bio{author_num}']

                    # Create author objects
                    author = Author(name=name, surname=surname, bio=bio)
                    authors.append(author)
                    db.session.add(author)

                    # Associate the author with the new_book
                    new_book.authors.extend(authors)

            # Set the status of the new_book
            new_book.status = new_status

            # Commit changes to the database
            db.session.commit()

            flash('Book added successfully!')
            return redirect(url_for('add_book'))

        except Exception as e:
            flash(f'Error adding book: {str(e)}')
            return redirect(url_for('add_book'))

    return render_template("add_book.html")


# OLD
# @app.route('/books/add', methods=['GET', 'POST'])
# def add_book():
#     if request.method == 'POST':
#         title = request.form['title']
#         description = request.form['description']
#
#         # Create the book and status
#         new_book = Book(title=title, description=description)
#         new_status = Status(available=True, borrower_name=None, borrowed_date=None)
#
#         try:
#             db.session.add(new_book)
#             db.session.add(new_status)
#
#             new_book.status = new_status
#             db.session.commit()
#
#             flash('Book added successfully!')
#             return redirect(url_for('add_book'))
#
#         except Exception as e:
#             flash(f'Error adding book: {str(e)}')
#             return redirect(url_for('add_book'))
#
#     all_books = Book.query.all()
#     return render_template("add_book.html", books=all_books)


@app.route('/books')
def books():
    # Fetch all books from the database
    all_books = Book.query.all()

    return render_template("books.html", books=all_books)


@app.route('/authors')
def authors():
    # Fetch all authors from the database
    all_authors = Author.query.all()
    return render_template("authors.html", authors=all_authors)


@app.route('/authors/add', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        bio = request.form['bio']

        # Create the author
        new_author = Author(name=name, surname=surname, bio=bio)

        try:
            db.session.add(new_author)
            db.session.commit()

            flash('Author added successfully!')
            return redirect(url_for('add_author'))

        except Exception as e:
            flash(f'Error adding author: {str(e)}')
            return redirect(url_for('add_author'))

    all_books = Book.query.all()
    return render_template("add_author.html")


@app.route('/')
def homepage():
    return render_template("index.html")


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

