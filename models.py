from app import db
from werkzeug.security import check_password_hash, generate_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(28), nullable=False, unique=True)
    public_id = db.Column(db.String, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    todos=db.relationship('Todo', backref='owner', lazy='dynamic')
    password= db.Column(db.String(120), nullable=False)

    def set_password(self, password):
      self.password = generate_password_hash(password)

    def check_password(self, password):
      return check_password_hash(self.password, password)

    @staticmethod
    def get_user(id):
      return User.query.get(int(id))
    
    def get_json(self):
      return{
        'id': self.public_id, 'name': self.name, 
        'email': self.email, 'is admin': self.is_admin,
        'todos': self.todos.all()
      }

    def __repr__(self):
      return f'User <{self.email}>'

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(20), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    public_id = db.Column(db.String, nullable=False)
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def get_json(self):
      return { 
        'id': self.public_id, 'name': self.name,
        'completed': self.is_completed,
        'owner': {
          'name': self.owner.name,
          'email': self.owner.email,
          'public_id': self.owner.public_id
        }
      }
    
    def __repr__(self):
      return f'Todo: <{self.name}>'