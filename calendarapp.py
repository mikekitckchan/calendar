from flask import Flask, render_template, request, redirect, url_for, Response
import json

app = Flask(__name__)


events =[
{
    "title": "Happy Hour",
    "start": "2019-04-30T17:30:00-05:00"
  }]

@app.route('/')
def index():
    return redirect(url_for('calendar'))

@app.route('/data')
def data():
    return Response(json.dumps(events),  mimetype='application/json')


@app.route('/calendar')
def calendar():

    return render_template('calendar.html')

@app.route('/create', methods = ['GET', 'POST'])
def create():
    global event_index
    if request.method == 'POST':
        calendar_data = {}
        calendar_data['title']=request.form['title']
        calendar_data['start']=request.form['startdate']+"T"+request.form['starttime']
        calendar_data['end']=request.form['enddate']+"T"+request.form['endtime']
        events.append(calendar_data)
        return redirect(url_for('calendar'))

    else:
        return render_template('create.html')

