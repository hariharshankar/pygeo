import flask

mod = flask.Blueprint("index", __name__)


@mod.route("/", endpoint="home")
@mod.route("/index.html")
def view():

    return flask.render_template("index.html")
