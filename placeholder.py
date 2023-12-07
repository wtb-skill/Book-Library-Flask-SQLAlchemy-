# Remove authors not associated with any book
authors_to_delete = (
    db.session.query(Author)
        .outerjoin(Author.books)
        .group_by(Author.id)
        .having(func.count(Book.id) == 0)
        .all()
)

for author in authors_to_delete:
    db.session.delete(author)