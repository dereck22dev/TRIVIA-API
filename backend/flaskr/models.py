# ----------------------------------------------------------------------------#
# Imports.
# ----------------------------------------------------------------------------#
from sqlalchemy import Column, String, Integer
from flask_sqlalchemy import SQLAlchemy
from settings import DB_HOST,DB_NAME,DB_USER,DB_PASSWORD,DB_TEST

# ----------------------------------------------------------------------------#
# Database set..
# ----------------------------------------------------------------------------#

#FOR TEST use DB_TEST instead  DB_NAME
database_dir = 'postgresql://{}:{}@{}/{}'.format(DB_USER,DB_PASSWORD,DB_HOST,DB_NAME)

db = SQLAlchemy()

#config
def setup_db(app, database_dir=database_dir):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_dir
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#
class Question(db.Model):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    question = Column(String)
    answer = Column(String)
    category = Column(String)
    difficulty = Column(Integer)

    def __init__(self, question, answer, category, difficulty):
        self.question = question
        self.answer = answer
        self.category = category
        self.difficulty = difficulty

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'category': self.category,
            'difficulty': self.difficulty
            }

class Category(db.Model):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    type = Column(String)

    def __init__(self, type):
        self.type = type

    def format(self):
        return {
            'id': self.id,
            'type': self.type
            }
