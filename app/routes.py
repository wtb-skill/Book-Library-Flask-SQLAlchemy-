# app/routes.py

from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import and_, or_, func
from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import null
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
            for key in request.form.keys():
                if key.startswith('name'):
                    author_num = key.replace('name', '')
                    name = request.form[f'name{author_num}']
                    surname = request.form[f'surname{author_num}']
                    bio = request.form[f'bio{author_num}']

                    # Check if the author already exists
                    existing_author = Author.query.filter(and_(Author.name == name, Author.surname == surname)).first()

                    if existing_author:
                        # Use the existing author
                        new_book.authors.append(existing_author)
                    else:
                        # Create a new author
                        new_author = Author(name=name, surname=surname, bio=bio)
                        db.session.add(new_author)
                        new_book.authors.append(new_author)

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
                book.status.borrowed_date = previous_status.borrowed_date
            else:
                book.status.borrowed_date = datetime.now().strftime('%Y-%m-%d')
            book.status.borrower_name = borrower_name
            book.status.available = False

        # Collecting the author IDs from the form data
        updated_author_ids = set()
        # Loop through form data to edit author names
        for key in request.form.keys():
            if key.startswith('author_name'):
                author_num = key.replace('author_name', '')
                new_name = request.form[f'author_name{author_num}']
                new_surname = request.form[f'author_surname{author_num}']

                # Find the corresponding author for the book
                existing_author = Author.query.filter(
                    and_(Author.name == new_name, Author.surname == new_surname)).first()

                if existing_author:
                    updated_author_ids.add(existing_author.id)
                    # Use the existing author for this book
                    if existing_author not in book.authors:
                        book.authors.append(existing_author)
                else:
                    # Create a new author and associate with the book
                    new_author = Author(name=new_name, surname=new_surname, bio="")
                    db.session.add(new_author)
                    book.authors.append(new_author)
                    updated_author_ids.add(new_author.id)

        # Remove authors that were associated previously but not present now
        authors_to_remove = [author for author in book.authors if author.id not in updated_author_ids]
        for author in authors_to_remove:
            book.authors.remove(author)

        # Remove authors not associated with any book
        authors_to_delete = (
            db.session.query(Author)
                .filter(~Author.books.any())
                .all()
        )

        for author in authors_to_delete:
            db.session.delete(author)

        db.session.commit()
        flash('Book details updated successfully!')
        return redirect(url_for('books_details', book_id=book_id))

    return render_template('book_details.html', book=book)


@app.route('/authors/<int:author_id>', methods=['GET', 'POST'])
def authors_details(author_id):
    author = Author.query.get(author_id)

    if request.method == 'POST':
        author.name = request.form['name']
        author.surname = request.form['surname']
        author.bio = request.form['bio']

        # Collecting the book IDs from the form data
        updated_book_ids = set()
        # Loop through form data to edit book titles
        for key in request.form.keys():
            if key.startswith('book_title'):
                book_num = key.replace('book_title', '')
                new_title = request.form[f'book_title{book_num}']

                # Find the corresponding book for the author
                existing_book = Book.query.filter_by(title=new_title).first()

                if existing_book:
                    print("EXISTING BOOK")
                    updated_book_ids.add(existing_book.id)
                    # Use the existing book for this author
                    if existing_book not in author.books:
                        author.books.append(existing_book)
                else:
                    print("ELSE BOOK")

                    # Create a new book and associate with the author
                    new_book = Book(title=new_title, description="")
                    print(new_book)
                    new_status = Status(available=True, borrower_name=None, borrowed_date=None)
                    db.session.add(new_book)
                    db.session.add(new_status)
                    author.books.append(new_book)
                    # new_book.authors.append(author)
                    new_book.status = new_status
                    db.session.commit()
                    updated_book_ids.add(new_book.id)

                    print(updated_book_ids)

        # Remove books that were associated previously but not present now
        books_to_remove = [book for book in author.books if book.id not in updated_book_ids]
        for book in books_to_remove:
            author.books.remove(book)

        # Remove books not associated with any author
        books_to_delete = (
            db.session.query(Book)
                .filter(~Book.authors.any())
                .all()
        )

        for book in books_to_delete:
            db.session.delete(book)

        db.session.commit()
        flash('Author details updated successfully!')
        return redirect(url_for('authors_details', author_id=author_id))

    return render_template('author_details.html', author=author)
