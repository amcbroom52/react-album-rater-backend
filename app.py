import os

from flask import Flask, render_template, session, redirect, flash, g, url_for, request, jsonify
from models import connect_db, db,  User, Rating, Album, DEFAULT_USER_IMAGE
from sqlalchemy.exc import IntegrityError
from forms import LoginForm, SignupForm, CSRFProtectForm, EditRatingForm, AddRatingForm, EditUserForm
from spotify import get_access_token, get_album_info, album_search, artist_search, get_artist_info
from functools import wraps
from dotenv import load_dotenv
from datetime import datetime
from math import floor

app = Flask(__name__)

load_dotenv()

app.config['SECRET_KEY'] = os.environ['SECRET_KEY']

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL", 'postgresql:///album_rater')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True


connect_db(app)

CURR_USER_KEY = "active_user"

################################### Helpers ####################################

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

@app.before_request
def add_csrfform_to_g():
    """If we're logged in, add curr user to Flask global."""

    g.csrf_form = CSRFProtectForm()


def login_required(f):
    @wraps(f)
    def login_decorator(*args, **kwargs):
        if not g.user:
            flash("Access unauthorized.", "danger")
            return redirect(url_for("handle_login_page"))
        return f(*args, **kwargs)
    return login_decorator


def token_required(f):
    @wraps(f)
    def token_decorator(*args, **kwargs):
        if hasattr(g, 'spotify_token'):
            if g.spotify_token['exp_time'] > datetime.now():
                return f(*args, **kwargs)

        g.spotify_token = get_access_token()

        return f(*args, **kwargs)
    return token_decorator

@app.template_filter()
def format_runtime(milliseconds):
    total_sec = milliseconds / 1000
    min = floor(total_sec / 60)
    sec = floor(total_sec % 60)

    if sec < 10:
        sec_str = f'0{sec}'
    else:
        sec_str = f'{sec}'

    return f'{min}:{sec_str}'


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.username


def do_logout():
    """Log out user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

################################### Base Pages #################################

@app.get('/')
def homepage():
    """Show homepage"""

    if not g.user:
        return redirect(url_for("handle_login_page"))

    home_rating_usernames = [user.username for user in g.user.following] + [g.user.username]

    ratings = (Rating
                .query
                .filter(
                    Rating.author.in_(home_rating_usernames)
                ).order_by(Rating.timestamp.desc())
                .limit(100)
                .all())

    return render_template('homepage.html', ratings=ratings)



@app.route('/login', methods=["GET", "POST"])
def handle_login_page():
    """Login user"""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.login(
            username=form.username.data,
            password=form.password.data)

        if user:
            do_login(user)

            return redirect(url_for('homepage'))

        else:
            flash("Invalid Credentials", "danger")
            return redirect(url_for('handle_login_page'))

    return render_template('login.html', form=form)

@app.route('/signup', methods=["GET", "POST"])
def handle_signup_form():
    """Create new user and log them in"""

    form = SignupForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data or None,
                bio=form.bio.data or None,
                image_url=form.image_url.data or None,
                password=form.password.data
            )

            db.session.commit()
            do_login(user)

            flash("User created successfully", "success")
            return redirect(url_for('show_user_page', username=user.username))

        except IntegrityError:
            flash("Username Taken.", "danger")
            return redirect(url_for('handle_signup_form', form=form))

    return render_template('signup.html', form=form)



################################ Search Routes #################################


@app.get('/search')
@login_required
def search_items():
    """Search for albums or artists on spotify"""

    return render_template('search.html')


@app.get('/search/results')
@login_required
@token_required
def get_search_results():
    # """Takes a url in JSON and makes a returns a JSON object of the Spotify api
    # results of that json"""

    query = request.args.get("query", "a")
    search_type = request.args.get("type", "album")

    # results = []

    if search_type == "album":
        results = album_search(query=query, token=g.spotify_token['token'])

    elif search_type == "artist":
        results = artist_search(query=query, token=g.spotify_token['token'])

    elif search_type == "user":
        unserialized_results = User.search(search=query)
        results = [user.serialize() for user in unserialized_results]

    return jsonify(results)



################################# User Routes ##################################

@app.get('/users/<username>')
@login_required
def show_user_page(username):

    user = User.query.get_or_404(username)

    return render_template('userPage.html', user=user)

@app.route('/edit-user', methods=["GET", "POST"])
def handle_edit_user_form():
    """Edit user"""

    form = EditUserForm(obj=g.user)
    db.session.rollback()

    if form.validate_on_submit():
        try:
            g.user.first_name=form.first_name.data
            g.user.last_name=form.last_name.data or None
            g.user.bio=form.bio.data or None
            g.user.image_url=form.image_url.data or DEFAULT_USER_IMAGE

            db.session.commit()

            return redirect(url_for('show_user_page', username=g.user.username))

        except ValueError:
            flash("Username Taken.", "danger")
            return redirect(url_for('handle_edit_user_form', form=form))

    return render_template('editUserForm.html', form=form)


@app.post('/follow-user/<username>')
@login_required
def handle_user_follow(username):

    user = User.query.get_or_404(username)

    if g.user.is_following(user):
        g.user.following.remove(user)

    else:
        g.user.following.append(user)

    db.session.commit()

    return redirect(url_for('show_user_page', username=username))

@app.post('/logout')
@login_required
def logout_user():

    if not g.csrf_form.validate_on_submit():
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()
    return redirect(url_for('handle_login_page'))

@app.post('/delete-user')
@login_required
def delete_user():

    if not g.csrf_form.validate_on_submit():
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()
    g.user.delete_user()
    db.session.commit()
    return redirect(url_for('handle_signup_form'))



################################# Music Routes #################################


@app.get('/artists/<artist_id>')
@login_required
@token_required
def show_artist_page(artist_id):

    artist = get_artist_info(artist_id, token=g.spotify_token['token'])

    return render_template('artistPage.html', artist=artist)


@app.get('/albums/<album_id>')
@login_required
@token_required
def show_album(album_id):
    """Show individual album page"""

    album = get_album_info(album_id, g.spotify_token['token'])

    ratings = Rating.query.filter_by(album_id=album_id).all()

    return render_template("albumPage.html", album=album, ratings=ratings)



################################ Rating Routes #################################


@app.get('/ratings/<int:rating_id>')
@login_required
def show_rating(rating_id):
    """Show Rating"""

    rating = Rating.query.get_or_404(rating_id)

    return render_template('ratingPage.html', rating=rating)




@app.route('/rate-album/<album_id>', methods=["GET", "POST"])
@login_required
@token_required
def handle_rating_form(album_id):
    """Create new album rating"""

    form = AddRatingForm()

    album = get_album_info(album_id, g.spotify_token['token'])
    rating = Rating.query.filter_by(album_id=album_id, author=g.user.username).one_or_none()

    song_choices = [(song['name'], song['name']) for song in album['tracks']]
    song_choices.insert(0, ('',''))
    form.favorite_song.choices = song_choices

    if rating:
        flash("Redirected to edit previous rating", "alert-warning")
        return redirect(url_for('edit_rating', album_id=album_id))

    if form.validate_on_submit():
        rating = Rating(
            rating = form.rating.data,
            text = form.text.data,
            favorite_song = form.favorite_song.data,
            timestamp = datetime.now(),
            album_id = album_id,
            author = g.user.username
        )

        db_album = Album.query.get(album_id)

        if not db_album:
            db_album = Album(
                id=album['id'],
                name=album['name'],
                image_url=album['image_url'],
                artist_name=album['artist_name'],
                artist_id=album['artist_id']
            )

            db.session.add(db_album)

        db.session.add(rating)
        db.session.commit()

        return redirect(url_for('show_album', album_id=album_id))

    return render_template('addRatingForm.html', form=form, album=album)


@app.route('/edit-rating/<album_id>', methods=["GET", "POST"])
@login_required
@token_required
def edit_rating(album_id):
    """Edit a user's preexisting album rating"""

    album = get_album_info(album_id, g.spotify_token['token'])
    rating = Rating.query.filter_by(album_id=album_id, author=g.user.username).one_or_404()

    form = EditRatingForm(obj=rating)

    song_choices = [(song['name'], song['name']) for song in album['tracks']]
    song_choices.insert(0, ('',''))
    form.favorite_song.choices = song_choices

    if form.validate_on_submit():
        rating.rating = form.rating.data
        rating.text = form.text.data
        rating.favorite_song = form.favorite_song.data

        db.session.commit()

        return redirect(url_for('show_album', album_id=album_id))

    return render_template('editRatingForm.html', form=form, album=album)


@app.post('/delete-rating/<int:rating_id>')
@login_required
def delete_rating(rating_id):
    """Delete a rating"""

    rating = Rating.query.get_or_404(rating_id)

    if not g.csrf_form.validate_on_submit():
        flash("Access unauthorized.", "danger")
        return redirect("/")

    db.session.delete(rating)
    db.session.commit()

    return redirect(url_for('show_album', album_id=rating.album_id))


