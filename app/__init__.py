from flask import Flask
from flask.ext.mongoengine import MongoEngine
from flask.ext.assets import Environment, Bundle
from werkzeug.contrib.cache import SimpleCache
import json

db = MongoEngine()
app = None
assets = None
cache = SimpleCache()

def create_app(**config_overrides):
    """This is normal setup code for a Flask app, but we give the option
    to provide override configurations so that in testing, a different
    database can be used.
    """
    # we want to modify the global app, not a local copy
    global app
    global assets
    app = Flask(__name__)

    # Load config then apply overrides
    app.config.from_object('config.flask_config')
    app.config.update(config_overrides)

    # Initialize assets
    assets = Environment(app)
    register_scss()

    # Setup the database.
    db.init_app(app)

    register_blueprints()


def register_blueprints():
    """Registers all the Blueprints (modules) in a function, to avoid
    circular dependancies.

    Be careful rearranging the order of the app.register_blueprint()
    calls, as it can also result in circular dependancies.
    """
    from app.base.routes import base
    from app.user.routes import user
    from app.diff.routes import diff
    from app.repo.routes import repo
    from app.active_window.routes import active_window

    blueprints = [base, user, diff, repo, active_window]
    for blueprint in blueprints:
        app.register_blueprint(blueprint)


def register_scss():
    """"""
    assets.url = app.static_url_path
    defaults = {
        'filters':'scss',
        'depends':['scss/_colors.scss', 'scss/_media_queries.scss', 'scss/app.scss']
    }

    with open('config/scss.json') as f:
        bundle_instructions = json.loads(f.read())
        for bundle_name, instructions in bundle_instructions.iteritems():
            bundle = Bundle(*instructions["inputs"],
                            output=instructions["output"],
                            **defaults)
            assets.register(bundle_name, bundle)


def run():
	app.run(host='0.0.0.0', port=5000)
