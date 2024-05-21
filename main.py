from flask import Flask
from blueprints.movies import movies_bp

app = Flask(__name__)
app.register_blueprint(movies_bp)


if __name__=='__main__':
    app.run(debug=True)