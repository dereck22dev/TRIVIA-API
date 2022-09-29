# ----------------------------------------------------------------------------#
# Imports.
# ----------------------------------------------------------------------------#

from http.client import FOUND
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from models import setup_db, Question, Category


# ----------------------------------------------------------------------------#
# Pagination.
# ----------------------------------------------------------------------------#

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions

# ----------------------------------------------------------------------------#
# App.
# ----------------------------------------------------------------------------#

def create_app(test_config=None):

    #config.
    app = Flask(__name__)
    setup_db(app)

    #allow request origin
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    #CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    #get categories.
    @app.route("/categories")
    def get_all_categories():
        #get all valid categories
        all_categories = Category.query.all()
        #create categories list for categories were are founds
        new_categories_list= {}

        #adding all categories in new_categories_list
        for category in all_categories:
            new_categories_list[category.id] = category.type

        return jsonify({
            'success': True,
            'categories': new_categories_list
        })

    #GET endpoint to get paginated questions.
    @app.route("/questions")
    def get_questions():
        try:
            #get all questions
            questions = Question.query.order_by(Question.id).all()
            #get all questions lenght
            questionsLenght = len(questions)
            #get current questions
            currentQuestions = paginate_questions(request, questions)

            #if question number not exist abort
            if (len(currentQuestions) == 0):
                abort(404)

            #let's get all categories
            all_categories = Category.query.all()
            new_categories_list = {}

            for category in all_categories:
                new_categories_list[category.id] = category.type

            return jsonify({
                'success': True,
                'questions': currentQuestions,
                'total_questions': questionsLenght,
                'categories': new_categories_list
            })
        except Exception as e:
            print(e)
            abort(400)

    #DELETE question with  question ID.
    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):
        try:
            question = Question.query.filter_by(id=id).one_or_none()
            #if the question not exist abort
            if question is None:
                abort(404)

            question.delete()

            #let's update front end
            questions = Question.query.order_by(Question.id).all()
            currentQuestions = paginate_questions(request, questions)

            return jsonify({
                'success': True,
                'questions': currentQuestions,
                'total_questions': len(questions)
            })

        except Exception as e:
            print(e)
            abort(404)
    
    #POST a new question
    @app.route("/questions/add", methods=['POST'])
    def add_question():
        
        #let's fetch body
        body = request.get_json()

        #get updated data from body
        newQuestion = body.get('question', None)
        newAnswer = body.get('answer', None)
        newCategory = body.get('category', None)
        newDifficulty = body.get('difficulty', None)

        try:
            #try new question adding
            question = Question(question=newQuestion, answer=newAnswer,
                                category=newCategory, difficulty=newDifficulty)
            question.insert()

            #then try updating
            questions = Question.query.order_by(Question.id).all()
            currentQuestions = paginate_questions(request, questions)

            return jsonify({
                'success': True,
                'created': question.id,
                'questions': currentQuestions,
                'total_questions': len(questions)
            })

        except Exception as e:
            print(e)
            abort(422)


    #POST endpoint to get questions based on a search term.
    @app.route("/questions/search", methods=['POST'])
    def search():
        body = request.get_json()
        search = body.get('searchTerm')
        print(search)
        questions_founds = Question.query.filter(Question.question.ilike(f"%{search}%")).all()

        if questions_founds:
            currentQuestions = paginate_questions(request, questions_founds)
            return jsonify({
                'success': True,
                'questions': currentQuestions,
                'total_questions': len(questions_founds)
            })
        else:
            print('not FOUND hahahahaa')
            abort(404)

    #GET questions based on category.
    @app.route("/categories/<int:id>/questions")
    def questions_in_category(id):
        #get category 
        category = Category.query.filter_by(id=id).one_or_none()
        if category:
            #get all questions in a category
            questions = Question.query.filter_by(category=str(id)).all()
            currentQuestions = paginate_questions(request, questions)

            return jsonify({
                'success': True,
                'questions': currentQuestions,
                'total_questions': len(questions),
                'current_category': category.type
            })
        #if category not founds abort
        else:
            abort(404)

    #GET questions to play the quiz
    @app.route('/quizzes/play', methods=['POST'])
    def quiz():

        body = request.get_json()
        quizCategory = body.get('quiz_category')
        last_question = body.get('previous_questions')

        try:
            if (quizCategory['id'] == 0):
                get_questions = Question.query.all()
                #print(len(get_questions))
            else:
                get_questions = Question.query.filter_by(
                category=quizCategory['id']).all()

            random_Number = random.randint(0, len(get_questions)-1)
            next_question = get_questions[random_Number]

            while next_question not in last_question:
                next_question = get_questions[random_Number]
                return jsonify({
                    'success': True,
                    'question': {
                        "answer": next_question.answer,
                        "category": next_question.category,
                        "difficulty": next_question.difficulty,
                        "id": next_question.id,
                        "question": next_question.question
                    },
                    'last_question': last_question
                })

        except Exception as e:
            print(e)
            abort(404)


    # ----------------------------------------------------------------------------#
    # Errors Handler.
    # ----------------------------------------------------------------------------#

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            'error': 400,
            "message": "Bad request"
        }), 400

    @app.errorhandler(404)
    def page_not_found(error):
        return jsonify({
            "success": False,
            'error': 404,
            "message": "Page not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable_recource(error):
        return jsonify({
            "success": False,
            'error': 422,
            "message": "Unprocessable recource"
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            'error': 500,
            "message": "Internal server error"
        }), 500

    @app.errorhandler(405)
    def invalid_method(error):
        return jsonify({
            "success": False,
            'error': 405,
            "message": "Invalid method!"
        }), 405
    
    return app

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == "__main__":
    create_app()