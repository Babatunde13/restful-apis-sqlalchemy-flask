import os, jwt
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from functools import wraps

load_dotenv()

app = Flask(__name__)
db = SQLAlchemy(app)

from models import User

app.config['SECRET_KEY']='secret'
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[1]
        if not token: 
            return jsonify({
                'error': 'Unauthorized',
                'message': 'You are not signed in'
                }), 403
        try:
            data=jwt.decode(token, app.config['SECRET_KEY'])
            current_user=User().get_user(data['user']['_id'])
        except Exception as e:
            return jsonify({
                'error': 'Something went wrong',
                'message': str(e)
                }), 500

        return f(current_user, *args, **kwargs)

    return decorated

def admin_required(f):
	@wraps(f)
	def decorated(current_user: User, *args, **kwargs):
		if not current_user.is_admin:
			return jsonify({
				'error': 'Forbidden',
				'message': 'You need to be an admin to make this request!'
			}), 403
		return f(current_user, *args, **kwargs)
	
	return decorated

import views

if __name__ == '__main__':
	app.run()