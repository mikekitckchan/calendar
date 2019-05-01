from flask import Flask, render_template, request, redirect, url_for, Response, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

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


'''main routing logic'''
@app.route('/')
def index():
    return redirect(url_for('calendar'))

@app.route ('/event/<int:event_id>')
def event(event_id):
    event_query = Event.query.filter_by(id = event_id)
    return render_template('event.html', event = event_query)

@app.route ('/delete', methods = ['POST'])
def delete_event():
    Event.query.filter_by(id = int(request.form["event_id"])).delete()
    db.session.commit()
    return redirect(url_for('calendar'))

@app.route('/data')
def data():
    qryresult = Event.query.all()
    return jsonify([i.serialize for i in qryresult])

@app.route('/calendar')
def calendar():
    return render_template('calendar.html')

@app.route('/create', methods = ['GET', 'POST'])
def create():
    global event_index
    if request.method == 'POST':
        event = Event(title=request.form["title"], user="mikekitckchan", start_date = request.form["startdate"], start_time = request.form["starttime"], end_date = request.form["enddate"], end_time = request.form["endtime"])
        db.session.add(event)
        db.session.commit()
        return redirect(url_for('calendar'))

    else:
        return render_template('create.html')

