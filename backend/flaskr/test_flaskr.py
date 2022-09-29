# ----------------------------------------------------------------------------#
# Imports.
# ----------------------------------------------------------------------------#
import os
from random import random
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from app import create_app
from models import setup_db, Question, Category
from settings import DB_HOST,DB_TEST,DB_USER,DB_PASSWORD


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_dir = 'postgresql://{}:{}@{}/{}'.format(DB_USER,DB_PASSWORD,DB_HOST,DB_TEST)
        setup_db(self.app, self.database_dir)

        # binds the app 
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            #create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_valid_page_questions(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["categories"]))
        self.assertTrue(len(data["questions"]))

    def test_get_page_bad_request(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Bad request')

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])

    def test_get_categories_not_allowed_method(self):
        res = self.client().delete('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)

    def test_delete_question(self):

        #let's fetch  all question and assure us to use a valid id
        list_of_questions=Question.query.order_by(Question.id).all()
        
        #w'ill use a first ID only
        firstId=list_of_questions[0].id
        #print(firstId)

        res = self.client().delete('/questions/'+ str(firstId))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_delete_question_not_found(self):
        res = self.client().delete('/questions/2000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Page not found")

    def test_add_question(self):
        newQuestion = {
            'question': 'Are you Happy?',
            'answer': 'Yes',
            'difficulty': 2,
            'category': 3
        }
        res = self.client().post("/questions/add", json=newQuestion)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_search(self):
        search = {'searchTerm': 'What'}
        res = self.client().post('/questions/search', json=search)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions'])> 0)

    def test_search_not_found(self):
        search = {
            'searchTerm': 'blabla bla bla',
        }
        res = self.client().post('/questions/search', json=search)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Page not found')

    def test_questions_in_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertNotEqual(len(data['questions']), 0)
        self.assertEqual(data['current_category'], 'Science')

    def test_questions_in_category_not_found(self):
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_quiz(self):
        quizz = {
            'previous_questions': [13],
            'quiz_category': {
                'type': 'Entertainment',
                'id': 3
            }
        }
        res = self.client().post('/quizzes/play', json=quizz)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['question']['category'], 3)

    def test_quiz_not_found_category(self):
        quizz = {
            'previous_questions': [2],
            'quiz_category': {
                'type': 'blabla',
                'id': 'blabla'
            }
        }
        res = self.client().post('/quizzes', json=quizz)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

# test launcher
if __name__ == "__main__":
    unittest.main()