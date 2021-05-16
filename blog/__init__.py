from flask import Flask


app = Flask(__name__)
app.config['SECRET_KEY'] = '41c308f9f8d93d135dc81006f0e4363f'

from blog import routes