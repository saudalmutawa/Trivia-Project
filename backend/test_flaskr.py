import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format('postgres','9048','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)
        self.new_question={
            
            "question":"Testing",
            "answer":"yes",
            "difficulty":3,
            "category":3
        }
    
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass
   
    def test_get_pagination(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        self.assertEqual(data['current_category'],None)

    def test_404error_get_pagination(self):
        res = self.client().get('/questions?page=100')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'resource not found')

    #There is no error or abort in this method
    def test_get_category(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True) 
        self.assertTrue(data['categories'])


       #run different question id each test
    def test_delete_question_by_id(self):
        res = self.client().delete('/questions/15')
        data = json.loads(res.data)
    
        question = Question.query.filter(Question.id==15).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 15)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'], None)
        self.assertEqual(question, None)
        
    def test_404error_delete_question_by_id(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)
    
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
        

    def test_add_question(self):
        res = self.client().post('/questions',json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'],None)
    
    def test_422error_add_question(self):
        res = self.client().post('/questions', json={'question':'','answer':'','difficulty':2,'category':2})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

     #There is no error or abort in this method
    def test_search_question(self):
        res = self.client().post('/questions-search',json={'searchTerm':"who"})
        data = json.loads(res.data)

        questions=Question.query.order_by(Question.id).filter(Question.question.ilike('%who%')).all()
        count = len(questions)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['questions'])
        self.assertEqual(data['total_questions'],count) #compare between number of questions in result and in the query
        self.assertEqual(data['current_category'],None)

    #There is no error or abort in this method
    def test_get_question_by_category(self):
        res = self.client().get('/categories/3/questions')
        data = json.loads(res.data)

        questions = Question.query.filter(Question.category==3).all()
        count=len(questions)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['questions'])
        self.assertEqual(data['total_questions'], count) #compare between number of questions in result and in the query
        self.assertEqual(data['current_category'],None)

    #Testing if the previous questions list are empty
    def test_question_quiz_empty(self):
        res = self.client().post('/quizzes',json={
            'quiz_category':{
                "id":2,
                "type":"Art"
            },
            'previous_questions':[]
        })
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['question'])

    #Testing if the previous questions list is full
    def test_question_quiz_full(self):
        res = self.client().post('/quizzes',json={
            'quiz_category':{
                "id":5,
                 },
            'previous_questions':[6]
        })
        data = json.loads(res.data)
        

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()