import flask

mod = flask.Blueprint("index", __name__)


@mod.route("/", endpoint="index")
@mod.route("/index.html", endpoint="index")
def view():

    return flask.render_template("index.html")
