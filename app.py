from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required, LoginManager, UserMixin, login_user,current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import urlparse, urljoin

app = Flask(__name__)

'''Set up secret key config'''
app.config['SECRET_KEY'] = 'Your Key'

'''instantiate LoginManager object'''
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
login_manager.init_app(app)


'''Adding configuration for database'''
SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="mikekitckchan",
    password="Fong1029$",
    hostname="mikekitckchan.mysql.pythonanywhere-services.com",
    databasename="mikekitckchan$calendar",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

'''Definning is_safe_url function for user_login'''
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

'''Create a table for events'''
class Event(db.Model):
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user = db.Column(db.String(80), default="mikekitckchan")
    title = db.Column(db.String(80))
    start_date = db.Column(db.Date)
    start_time = db.Column(db.Time)
    end_date = db.Column(db.Date)
    end_time = db.Column(db.Time)

    def __init__(self, user, title, start_date, start_time, end_date, end_time):
        self.user = user
        self.title = title
        self.start_date = start_date
        self.start_time = start_time
        self.end_date = end_date
        self.end_time = end_time

    @property
    def serialize(self):
       """Return object data in easily serializable format"""
       return {
           'id': self.id,
           'title': self.title,
           'start': str(self.start_date)+"T"+str(self.start_time),
           'end': str(self.end_date)+"T"+str(self.end_date)
       }

'''Create a table for users'''
class User(UserMixin,db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password = db.Column(db.String(100))
    authenticated = db.Column(db.Boolean, default=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def is_active(self):
        """True, as all users are active."""
        return True

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

    def get_id(self):
        return self.id



'''main routing logic'''
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        # check if user actually exists
        # take the user supplied password, hash it, and compare it to the hashed password in database
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            return "<p>What are you doing</p>" # if user doesn't exist or password is wrong, reload the page
        login_user(user)
        user.authenticated = True
        db.session.add(user)
        db.session.commit()
        next_page = request.args.get('next')
        if not is_safe_url(next_page):
            return abort(400)

        return redirect(next_page or url_for('calendar'))
    else:
        if current_user.is_authenticated:
            return redirect(url_for('calendar'))
        else:
            return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('login')

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first() # return a user by username

        if user: # if a user is found, we want to redirect back to signup page so user can try again
            flash('username already exists')
            return redirect(url_for('register'))

        # create new user with the form data. Hash the password so plaintext version isn't saved.
        new_user = User(username=username, password=generate_password_hash(password))

        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    else:
        return render_template('register.html')

@app.route ('/event/<int:event_id>')
@login_required
def event(event_id):
    event_query = Event.query.filter_by(id = event_id)
    return render_template('event.html', event = event_query)

@app.route ('/delete', methods = ['POST'])
@login_required
def delete_event():
    Event.query.filter_by(id = int(request.form["event_id"])).delete()
    db.session.commit()
    return redirect(url_for('calendar'))

@app.route('/data')
@login_required
def data():
    qryresult = Event.query.filter_by(user = current_user.id)
    return jsonify([i.serialize for i in qryresult])

@app.route('/calendar')
@login_required
def calendar():
    return render_template('calendar.html')

@app.route('/create', methods = ['GET', 'POST'])
@login_required
def create():
    global event_index
    if request.method == 'POST':
        event = Event(title=request.form["title"], user=current_user.id, start_date = request.form["startdate"], start_time = request.form["starttime"], end_date = request.form["enddate"], end_time = request.form["endtime"])
        db.session.add(event)
        db.session.commit()
        return redirect(url_for('calendar'))

    else:
        return render_template('create.html')

@login_manager.user_loader
def user_loader(user_id):
    """Given *user_id*, return the associated User object.

    :param unicode user_id: user_id (email) user to retrieve

    """
    return User.query.filter_by(id=user_id).first()

@login_manager.unauthorized_handler
def unauthorized():
    # do stuff
    return "<p> You are not unauthorized to visit the page </p>"
