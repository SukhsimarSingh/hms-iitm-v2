from flask import Flask, render_template
from app.db.db import db

template_folder = 'app/templates'

app = Flask(__name__, template_folder=template_folder)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hmsdb.db'
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('/index.html')

if __name__ == '__main__':
    app.run(debug=True)