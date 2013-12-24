import flask

mod = flask.Blueprint("form", __name__)

@mod.route("/form.php", defaults={'pid': 0})
@mod.route("/geoid/<int:pid>")
def view(pid):
    #mod = Moderation(db)

    #keys, values = mod.get_all_resources(225, 1)
    #s.extend(sel.read("Type", ["Type", "Type_ID"], [["Type_ID", "=", "1"]], ("Type_ID", "desc"), ("0","1")))

    #types = db.Type.all()
    return flask.jsonify(keys=[], values=[])

#if __name__ == "__main__":
#    app.run(debug=True)

