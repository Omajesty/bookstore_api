"""Bookstore API.

Run locally: uvicorn app.main:app --reload
Swagger UI:  http://localhost:8000/docs
"""

import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from app.auth import get_current_user, hash_password, verify_password
from app.database import get_db
from app.models import Author, Book, User
from app.schemas import (
    AuthorCreate,
    AuthorOut,
    AuthorUpdate,
    BookCreate,
    BookOut,
    BookUpdate,
    MessageOut,
    UserCreate,
    UserLogin,
    UserOut,
)

load_dotenv()

app = FastAPI(
    title="Bookstore API",
    version="1.0.0",
    description=(
        "Authors and books with PostgreSQL, Alembic, and cookie sessions.\n\n"
        "**How to test write endpoints in Swagger:**\n"
        "1. `POST /register` — create a user\n"
        "2. `POST /login` — this sets a session cookie\n"
        "3. Call `POST` / `PUT` / `DELETE` — Swagger sends the cookie automatically\n\n"
        "GET routes are public. Login is not required for reads."
    ),
)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "dev-secret-change-me"),
    session_cookie="bookstore_session",
    same_site="lax",
    https_only=os.getenv("RENDER") == "true",
    max_age=60 * 60 * 12,
)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}


@app.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED, tags=["auth"])
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == payload.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    user = User(username=payload.username, hashed_password=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/login", response_model=MessageOut, tags=["auth"])
def login(payload: UserLogin, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    request.session["user"] = user.username
    return {"message": f"Logged in as {user.username}"}


@app.post("/logout", response_model=MessageOut, tags=["auth"])
def logout(request: Request):
    request.session.clear()
    return {"message": "Logged out"}


@app.get("/me", response_model=UserOut, tags=["auth"])
def me(current_user: User = Depends(get_current_user)):
    return current_user



@app.get("/authors", response_model=list[AuthorOut], tags=["authors"])
def list_authors(db: Session = Depends(get_db)):
    return db.query(Author).order_by(Author.id).all()


@app.get("/authors/{author_id}", response_model=AuthorOut, tags=["authors"])
def get_author(author_id: int, db: Session = Depends(get_db)):
    author = db.query(Author).filter(Author.id == author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return author


@app.post(
    "/authors",
    response_model=AuthorOut,
    status_code=status.HTTP_201_CREATED,
    tags=["authors"],
)
def create_author(
    payload: AuthorCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    author = Author(name=payload.name, bio=payload.bio)
    db.add(author)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Author name already exists")
    db.refresh(author)
    return author


@app.put("/authors/{author_id}", response_model=AuthorOut, tags=["authors"])
def update_author(
    author_id: int,
    payload: AuthorUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    author = db.query(Author).filter(Author.id == author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    if payload.name is not None:
        author.name = payload.name
    if payload.bio is not None:
        author.bio = payload.bio
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Author name already exists")
    db.refresh(author)
    return author


@app.delete("/authors/{author_id}", response_model=MessageOut, tags=["authors"])
def delete_author(
    author_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    author = db.query(Author).filter(Author.id == author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    book_count = db.query(Book).filter(Book.author_id == author_id).count()
    if book_count:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot delete author with {book_count} book(s). Delete the books first.",
        )
    db.delete(author)
    db.commit()
    return {"message": "Author deleted"}



@app.get("/books", response_model=list[BookOut], tags=["books"])
def list_books(db: Session = Depends(get_db)):
    return db.query(Book).order_by(Book.id).all()


@app.get("/books/{book_id}", response_model=BookOut, tags=["books"])
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.post(
    "/books",
    response_model=BookOut,
    status_code=status.HTTP_201_CREATED,
    tags=["books"],
)
def create_book(
    payload: BookCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    author = db.query(Author).filter(Author.id == payload.author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    book = Book(
        title=payload.title,
        description=payload.description,
        author_id=payload.author_id,
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


@app.put("/books/{book_id}", response_model=BookOut, tags=["books"])
def update_book(
    book_id: int,
    payload: BookUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if payload.author_id is not None:
        author = db.query(Author).filter(Author.id == payload.author_id).first()
        if not author:
            raise HTTPException(status_code=404, detail="Author not found")
        book.author_id = payload.author_id
    if payload.title is not None:
        book.title = payload.title
    if payload.description is not None:
        book.description = payload.description
    db.commit()
    db.refresh(book)
    return book


@app.delete("/books/{book_id}", response_model=MessageOut, tags=["books"])
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()
    return {"message": "Book deleted"}
