from flask import Flask
from flask_restful import Resource, Api
from flask_cors import CORS
from blueprints.auth.blueprint_authentication import blueprint_authentication
from blueprints.scratch_off.blueprint_scratch_off import blueprint_scratch_off

app = Flask(__name__)
api = Api(app)
CORS(app)

app.register_blueprint(blueprint_authentication)
app.register_blueprint(blueprint_scratch_off)

if __name__ == "__main__":
    app.run(debug=True)
    print('name == __main__')


