import uuid
from flask import session
from src.common.database import Database
from src.models.blog import Blog


class User(object):

    def __init__(self,email,password,_id,id=None):
        self.email = email
        self.password = password
        self.id = id if id else uuid.uuid4().hex

    @classmethod
    def getByEmail(cls,email):
        user = Database.find_one('users',{'email':email})
        if user is not None:
            return cls(**user)

    @classmethod
    def getById(cls,id):
        user = Database.find_one('users', {'id': id})
        if user is not None:
            return cls(**user)

    @staticmethod
    def valid_login(email,password):
        #check whether a user's email matches the password that they sent us
        user = User.getByEmail(email)
        if user is not None:
            return user.password == password
        return False

    @staticmethod
    def login(user_email):
        #valid_login() has already been called
        session['email'] = user_email


    @staticmethod
    def logout(user_email):
        session['email'] = None

    @classmethod
    def register(cls,email,password):
        user  = cls.getByEmail(email)
        if user is None:
            new_user = cls(email,password)
            new_user.save_database()
            session['email'] = email
            return True
        else:
            return False


    def getBlogs(self):
        return Blog.getBlogsByAuthorId(self.id)

    def new_blog(self,title,description):
        blog = Blog(author=self.email,title=title,description=description,author_id=self.id)
        blog.save_database()

    @staticmethod
    def new_post(blog_id,title,content):
        blog = Blog.getOneBlog(blog_id)
        blog.new_post(title,content)


    def save_database(self):
        Database.insert('users', self.json())

    def json(self):
        return {
            "email": self.email,
            "password": self.password,
            "id": self.id
        }
