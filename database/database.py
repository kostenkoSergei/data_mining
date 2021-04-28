import sqlalchemy.exc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import models


class Database:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        models.Base.metadata.create_all(bind=self.engine)
        self.maker = sessionmaker(bind=self.engine)

    def add_post(self, data):
        session = self.maker()
        post = models.Post(**data["post_data"], author=models.Author(**data["author_data"]))
        for tag_el in data["tags_data"]:
            tag = models.Tag(**tag_el)
            post.tags.append(tag)

        try:
            session.add(post)
            session.commit()
        except sqlalchemy.exc.IntegrityError:
            session.rollback()
        finally:
            session.close()
