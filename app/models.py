from . import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(28), nullable=False, unique=True)
    public_id = db.Column(db.String, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    todos=db.relationship('Todo', backref='owner', lazy='dynamic')

    def get_user(self, id):
      return User.query.get(id).first()

    def __repr__(self):
      return f'User <{self.email}>'

class Todo(db.Model):
	id = db.Column(db.Integer, primary_key=True, index=True)
	name = db.Column(db.String(20), nullable=False)
	is_completed = db.Column(db.Boolean, default=False)
	public_id = db.Column(db.String, nullable=False)
	user_id=db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	
	def __repr__(self):
		return f'Todo: <{self.name}>'