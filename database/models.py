from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, BigInteger, Text, Table

from .mixins import IdMixin, UrlMixin

Base = declarative_base()

tag_post = Table(
    "tag_post",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("post.id")),
    Column("tag_id", Integer, ForeignKey("tag.id")),
)

comment_post = Table(
    "comment_post",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("post.id")),
    Column("comment_id", Integer, ForeignKey("comment.id")),
)


class Post(Base, UrlMixin):
    __tablename__ = "post"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(250), nullable=False, unique=False)
    author_id = Column(Integer, ForeignKey("author.id"), nullable=True)
    author = relationship("Author", backref="posts")
    tags = relationship("Tag", secondary=tag_post)
    comments = relationship("Comment", secondary=comment_post)


class Author(Base, UrlMixin):
    __tablename__ = "author"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)


class Tag(Base, UrlMixin):
    __tablename__ = "tag"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    # posts = relationship(Post, secondary=tag_post, back_populates="tags")


class Comment(Base):
    __tablename__ = "comment"
    id = Column(Integer, primary_key=True, autoincrement=True)
    comment_id = Column(String(100), nullable=False, unique=False)
    parent_id = Column(Integer, nullable=True)
    body = Column(String(250), nullable=False, unique=False)
    post_id = Column(Integer, ForeignKey("post.id"), nullable=True)
