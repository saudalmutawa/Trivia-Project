import os
from flask import Flask, json, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page',1,type=int)

  start =  (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  question = [question.format() for question in selection]
  current_question = question[start:end]

  return current_question

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app,  resources={"/": {"origins": "*"}})



  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
    return response
  
  @app.route('/categories')
  def retrive_categories():
    categories = Category.query.order_by(Category.id).all()
   
      
    if len(categories) ==0:
      abort(404)
    
    return jsonify ({
      'success':True,
      'categories':{category.id: category.type for category in categories}

    })



  @app.route('/questions')
  def retrive_questions():
    selection = Question.query.order_by(Question.id).all()
    questions = paginate_questions(request,selection)
    categories=Category.query.order_by(Category.id).all()
    
    if len(questions) == 0:
      abort(404)
    return jsonify({
      'success':True,
      'questions':questions,
      'total_questions':len(Question.query.all()),
      'categories': {category.id: category.type for category in categories},              #There is another way to json serialize object USING "JSONENCODER"
      'current_category': None
      
    })
    
  

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id==question_id).one_or_none()
      if question is None:
        abort(404)
      question.delete()

      selection = Question.query.order_by(Question.id).all()
      questions = paginate_questions(request,selection)

      return jsonify({
        'success':True,
        'deleted':question_id,
        'questions':questions,
        'total_questions':len(selection),
        'current_category':None
      })
    except():
      abort(422)


  @app.route('/questions',methods=['POST','GET'])
  def post_question():
    form = request.get_json()
    new_question = form.get('question',None)
    new_answer = form.get('answer',None)
    new_difficulty=form.get('difficulty')
    new_category=form.get('category')
    if new_question=="" or new_answer=="":
      abort(422)
    else:
      try:
        question = Question(question=new_question,answer=new_answer,difficulty=new_difficulty,category=new_category)
        question.insert()
        selection = Question.query.order_by(Question.id).all()
        questions = paginate_questions(request,selection)
        
        return jsonify({  #Useles return (:
        'success':True,
        'questions':questions,
        'total_questions':len(selection),
        'current_category':None 
      })
      except():
        abort(422)
        
  
  
  @app.route('/questions-search',methods=['POST','GET'])
  def search_question():
    form = request.get_json()

    search = form.get('searchTerm')

    selection = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search))).all()
    questions= paginate_questions(request,selection)
    

    return jsonify({
        'success':True,
        'questions':questions,
        'total_questions':len(selection),
        'current_category':None
      })

    
 
  @app.route('/categories/<int:cat_id>/questions')
  def get_category_questions(cat_id):
    
    selection = Question.query.filter(Question.category==cat_id).order_by(Question.id).all()
    questions = paginate_questions(request,selection)

    return jsonify({
        'success':True,
        'questions':questions,
        'total_questions':len(selection),
        'current_category':None})

  
  @app.route('/quizzes',methods=['POST'])
  def quiz():
    form = request.get_json()
    quiz_category=form.get('quiz_category',None)
    previous_question=form.get('previous_questions',None)

    if quiz_category['id'] == 0:
      questions = Question.query.order_by(Question.id).all()
    else:
      questions = Question.query.filter(Question.category == quiz_category['id']).order_by(Question.id).all()
    
    question=random.choice(questions).format()
 
    existed=False
    if question['id'] in previous_question:
      existed = True
    #if the question exists in the prev questions take another one and stop if the user played all questions
    while existed :
      if (len(questions)==len(previous_question)):
        return jsonify({
          'success':True,
          
        })

      question=random.choice(questions).format

      if question['id'] in previous_question:
        flag = True
      else:
        flag=False
      
        
      
    return jsonify({
      'success':True,
      'question':question
    })

 
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "resource not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "unprocessable"
      }), 422

  
  
  return app
  


    