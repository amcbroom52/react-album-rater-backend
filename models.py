from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from flask_bcrypt import Bcrypt
from datetime import datetime

db = SQLAlchemy()
bcrypt = Bcrypt()

DEFAULT_USER_IMAGE = (
    "https://braverplayers.org/wp-content/uploads/2022/09/blank-pfp.png")


def connect_db(app):
    """Connect this database to provided Flask app. Called in app.py"""

    app.app_context().push()
    db.app = app
    db.init_app(app)


class Follow(db.Model):
    """Follower/following table"""

    __tablename__ = "follows"

    user_being_followed = db.Column(
        db.String(20),
        db.ForeignKey('users.username', ondelete='cascade'),
        primary_key=True,
        nullable=False
    )

    user_following = db.Column(
        db.String(20),
        db.ForeignKey('users.username', ondelete='cascade'),
        primary_key=True,
        nullable=False
    )


class User(db.Model):
    """Users of the app"""

    __tablename__ = "users"

    username = db.Column(
        db.String(20),
        primary_key=True,
        nullable=False
    )

    first_name = db.Column(
        db.String(25),
        nullable=False
    )

    last_name = db.Column(
        db.String(25),
    )

    image_url = db.Column(
        db.String(255),
        nullable=False,
        default=DEFAULT_USER_IMAGE
    )

    bio = db.Column(
        db.Text
    )

    password = db.Column(
        db.String(100),
        nullable=False,
    )

    followers = db.relationship(
        "User",
        secondary="follows",
        primaryjoin=(Follow.user_being_followed == username),
        secondaryjoin=(Follow.user_following == username),
        backref="following"
    )

    ratings = db.relationship('Rating', backref='user')

    def serialize(self):
        """Returns a dictionary of the information about the user"""

        return {
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'image_url': self.image_url,
            'bio': self.bio
        }

    def is_following(self, user):
        """Checks if current user is following given user"""

        found_user_list = [
            following for following in self.following if following == user]
        return len(found_user_list) == 1

    def is_followed_by(self, user):
        """Checks if given user is following current user"""

        found_user_list = [
            follower for follower in self.followers if follower == user]
        return len(found_user_list) == 1

    def delete_user(self):
        """Deletes current user and all their ratings and followings"""

        Rating.query.filter_by(author=self.username).delete()
        Follow.query.filter(
            or_(
                Follow.user_following == self.username,
                Follow.user_being_followed == self.username)).delete()

        db.session.delete(self)

    def __repr__(self):
        return f"<User {self.username}: {self.first_name} {self.last_name}>"

    @classmethod
    def signup(cls, username, first_name, last_name, password):
        """Sign up user.

        Hashes password and adds user to session.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=hashed_pwd,
        )

        db.session.add(user)
        return user

    @classmethod
    def login(cls, username, password):
        """Searches for the given username in the table and checks to see if the
        hashed passwords matches. If username and password match returns the user,
        otherwise returns false.
        """

        user = cls.query.filter_by(username=username).one_or_none()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

    @classmethod
    def search(cls, search, offset):
        """Searches for users in the database that match the search string"""

        users = (cls
                 .query
                 .filter(or_(
                     cls.username.ilike(f'%{search}%'),
                     cls.first_name.ilike(f"%{search}%"),
                     cls.last_name.ilike(f'%{search}%')
                 )).limit(20)
                 .offset(offset))

        return users


class Rating(db.Model):
    """User's ratings of albums"""

    __tablename__ = "ratings"

    __table_args__ = (db.UniqueConstraint('album_id', 'author'),)

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    rating = db.Column(
        db.Float,
        nullable=False
    )

    favorite_song = db.Column(
        db.Text,
    )

    text = db.Column(
        db.Text,
        nullable=False,
        default=""
    )

    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now(),
    )

    album_id = db.Column(
        db.String(30),
        db.ForeignKey("albums.id", ondelete="cascade"),
        nullable=False
    )

    author = db.Column(
        db.String(20),
        db.ForeignKey('users.username', ondelete="cascade"),
        nullable=False
    )

    def serialize(self):
        """Returns a dictionary of the information about the rating"""
        return {
            'id': self.id,
            'rating': self.rating,
            'favorite_song': self.favorite_song,
            'text': self.text,
            'timestamp': self.timestamp,
            'album_id': self.album_id,
            'author': self.author
        }


class Album(db.Model):
    """Albums that have been reviewed on the app"""

    __tablename__ = "albums"

    id = db.Column(
        db.String(30),
        primary_key=True,
        nullable=False,
    )

    name = db.Column(
        db.Text,
        nullable=False
    )

    image_url = db.Column(
        db.String(100),
        nullable=False
    )

    artist_name = db.Column(
        db.Text,
        nullable=False
    )

    artist_id = db.Column(
        db.String(30),
        nullable=False
    )

    ratings = db.relationship("Rating", backref="album")
