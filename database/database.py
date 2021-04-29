import sqlalchemy.exc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import models


class Database:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        models.Base.metadata.create_all(bind=self.engine)
        self.maker = sessionmaker(bind=self.engine)

    def get_comments(self, data, post):
        for parent_el in data:
            comment = models.Comment(parent_id=parent_el["comment"]["parent_id"], body=parent_el["comment"]["body"],
                                     comment_id=parent_el["comment"]["id"])
            if parent_el["comment"]["children"]:
                self.get_comments(parent_el["comment"]["children"], post)
            post.comments.append(comment)

    def add_post(self, data):
        session = self.maker()
        post = models.Post(**data["post_data"], author=models.Author(**data["author_data"]))
        for tag_el in data["tags_data"]:
            tag = models.Tag(**tag_el)
            post.tags.append(tag)

        self.get_comments(data["comments_data"], post)
        try:
            session.add(post)
            session.commit()
        except sqlalchemy.exc.IntegrityError:
            session.rollback()
        finally:
            session.close()
