from __init__ import db

class Blog(db.Model):
    __tablename__ = 'blog_posts'

    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    date = db.Column(db.String(255), nullable=False)
    content = db.Column(db.String(4000), nullable=False)


    def __init__(self, name, school_name, owner_teacher_id, status='active'):
        self._name = name
        self._school_name = school_name
        self._owner_teacher_id = owner_teacher_id
        self._status = status
