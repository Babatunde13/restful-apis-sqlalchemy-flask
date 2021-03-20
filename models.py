from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(28), nullable=False, unique=True)
    public_id = db.Column(db.String, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    todos=db.relationship('Todo', backref='owner', lazy='dynamic')

    def get_user(self, id):
      return User.query.get(id).first()
    
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
        'owner': {
          'name': self.owner.name,
          'email': self.owner.email,
          'public_id': self.owner.public_id
        }
      }
    
    def __repr__(self):
      return f'Todo: <{self.name}>'