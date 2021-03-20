from flask import jsonify, request, redirect
import uuid, jwt
from  app import app, db, token_required, admin_required
from models import User, Todo

DOC_URI='https://documenter.getpostman.com/view/11853513/Tz5wVDgr'

@app.route('/')
def home():
	return {
		'message': 'Welcome to building RESTful APIs with Flask and SQLAlchemy, you an click on this link to check the docs at '+DOC_URI
	}

@app.route('/docs/')
def docs():
	return redirect('https://documenter.getpostman.com/view/11853513/Tz5wVDgr')

@app.route('/users/')
@token_required
@admin_required
def get_users(current_user):
	return jsonify([
		user.get_json() for user in User.query.all()
	])
		
@app.route('/users/me/')
@token_required
def get_user(current_user: User):
	return current_user.get_json()

@app.route('/users/', methods=['POST'])
def create_user():
	data = request.get_json()
	if not 'name' in data or not 'email' in data or 'password' not in data:
		return jsonify({
			'error': 'Bad Request',
			'message': 'Name, email or password not given'
		}), 400
	if len(data['name']) < 4 or len(data['email']) < 6:
		return jsonify({
			'error': 'Bad Request',
			'message': 'Name and email must be contain minimum of 4 letters'
		}), 400
	u = User(
			name=data['name'], 
			email=data['email'],
			is_admin=data.get('is admin', False),
			public_id=str(uuid.uuid4())
		)
	u.set_password(data['password'])
	db.session.add(u)
	db.session.commit()
	return u.get_json(), 201

@app.route('/users/token/', methods=['POST'])
def get_token():
	try:
		data = request.get_json()
		if 'email' not in data or 'password' not in data:
				return {
						'error': 'Invalid data',
						'message': 'email and password must be present.'
				}, 400
		u = User.query.filter_by(email=data['email']).first()
		if not u or not u.check_password(data['password']):
				return {
						'error': 'Invalid Data',
						'message': 'invalid email or password'
				}, 401
		try:
			token = jwt.encode(
				{'user_id': str(u.id)},
				app.config['SECRET_KEY']
			)
			return {
					'token': token
			}, 200
		except Exception as e:
			return {
				'error': 'Sonething went wrong',
				'message': str(e)
			}, 500
	except Exception as e:
		return {
			'error': 'Bad data',
			'message': str(e)
		}, 400 

@app.route('/users/', methods=['PUT'])
@token_required
def update_user(current_user):
	data = request.get_json()
	current_user.name=data.get('name', current_user.name)
	if 'admin' in data:
		current_user.is_admin=data['admin']
	db.session.commit()
	return jsonify(current_user.get_json())

@app.route('/users/', methods=['DELETE'] )
@token_required
def delete_user(current_user):
	db.session.delete(current_user)
	db.session.commit()
	return {
		'success': 'User deleted successfully'
	}

@app.route('/users/todos/')
@token_required
@admin_required
def get_todos(current_user):
	return jsonify([
		todo.get_json() for todo in Todo.query.all()
	])

@app.route('/users/todos/<id>/')
@token_required
def get_todo(current_user, id):
	todo: Todo = Todo.query.filter_by(public_id=id).first_or_404()
	if current_user != todo.owner or not todo.owner.is_admin:
		return {
			'error': 'Forbidden',
			'message': 'You don\'t have access to that todo and you are not an admin'
		}, 403
	return jsonify(todo.get_json())

@app.route('/users/todos/', methods=['POST'])
@token_required
def create_todo(current_user: User):
	data = request.get_json()
	if not 'name' in data:
		return jsonify({
			'error': 'Bad Request',
			'message': 'Name of todo not given'
		}), 400
	if len(data['name']) < 4:
		return jsonify({
			'error': 'Bad Request',
			'message': 'Name of todo contain minimum of 4 letters'
		}), 400

	is_completed = data.get('is completed', False)
	todo = Todo(
		name=data['name'], user_id=current_user.id,
		is_completed=is_completed, public_id=str(uuid.uuid4())
	)
	db.session.add(todo)
	db.session.commit()
	return todo.get_json(), 201

@app.route('/users/todos/<id>/', methods=['PUT'])
@token_required
def update_todo(current_user, id):
	data = request.get_json()
	if not data.get('name') and not  data.get('completed'):
		return {
			'error': 'Bad Request',
			'message': 'Name or completed fields need to be present'
		}, 400
	todo = Todo.query.filter_by(public_id=id).first_or_404()
	if current_user != todo.owner:
		return {
			'error': 'Forbidden',
			'message': 'You don\'t have access to that todo'
		}, 403
	todo.name=data.get('name', todo.name)
	todo.is_completed=data.get('completed', False)
	db.session.commit()
	return todo.get_json(), 201

@app.route('/users/todos/<id>/', methods=['DELETE'] )
@token_required
def delete_todo(current_user, id):
	todo = Todo.query.filter_by(public_id=id).first_or_404()
	if current_user != todo.owner:
		return {
			'error': 'Forbidden',
			'message': 'You don\'t have access to that todo'
		}, 403
	db.session.delete(todo)
	db.session.commit()
	return {
		'success': 'Data deleted successfully'
	}