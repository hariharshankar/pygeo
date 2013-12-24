import flask
from db import connection
import views.form as form
import views.resources as resources
import views.search as search
import views.menu as menu
import views.map
import views.location as location


app = flask.Flask(__name__)

conn = connection.Db()

form.db = conn
resources.db = conn
menu.db = conn
views.map.db = conn
location.db = conn

app.register_blueprint(form.mod)
app.register_blueprint(resources.mod)
app.register_blueprint(search.mod)
app.register_blueprint(menu.mod)
app.register_blueprint(views.map.mod)
app.register_blueprint(location.mod)
