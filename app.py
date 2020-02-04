from flask import Flask, render_template
from external_apis import external_apis


app = Flask(__name__)
app.register_blueprint(external_apis)

@app.route('/')
def index():
	return render_template('index.html')