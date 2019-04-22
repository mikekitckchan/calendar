from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


event_index = 0

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calendar')
def calendar():
    return render_template('calendar.html')

@app.route('/create', methods = ['GET', 'POST'])
def create():
    global event_index
    if request.method == 'POST':
        result = request.form.to_dict(flat=False)
        for items in result:
            print(items)
        return redirect(url_for('calendar'))

    else:
        return render_template('create.html')