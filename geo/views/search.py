import flask

mod = flask.Blueprint("search", __name__)


@mod.route("/search", endpoint="search")
def view():

    return flask.render_template("search.html")