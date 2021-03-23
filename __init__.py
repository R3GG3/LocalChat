from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify, session, flash
from datetime import timedelta, datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "Secret_key_Chat@413"
app.permanent_session_lifetime = timedelta(minutes=15)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///chat.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

old_amount = 0


class Users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(50))

    def __init__(self, name, password):
        self.name = name
        self.password = password

class Chat(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    author = db.Column(db.String(50))
    message = db.Column(db.String(128))
    date = db.Column(db.String(20))

    def __init__(self, author, message, date):
        self.author = author
        self.message = message
        self.date = date

@app.route("/")
def home():
    global old_amount
    
    if "name" not in session:
        return redirect(url_for("login"))
    
    data = Chat.query.all()
    old_amount = len(data)
    return render_template("chat.html", messages=data, user=session["name"])

@app.route("/login", methods=["POST", "GET"])
def login():
    if "name" in session:
        return redirect(url_for("home"))

    if request.method == "POST":
        #Login
        print(request.form.get("username"))

        #Register
        if request.form.get("username") == None:
            username = request.form["register-username"]
            password = request.form["register-password"]

            if len(username) < 3 and len(password) < 8:
                flash("Length of username or password is incorrect!")
                return redirect(url_for("login"))

            if Users.query.filter_by(name=username).count() == 0:
                push = Users(username, password)
                db.session.add(push)
                db.session.commit()
                session["name"] = username
                return redirect(url_for("home"))
            else:
                flash("Username already exists!")

        else:
            username = request.form["username"]
            password = request.form["password"]

            if len(username) < 3 and len(password) < 8:
                flash("Length of username or password is incorrect!")
                return redirect(url_for("login"))

            if Users.query.filter_by(name=username).count() > 0:
                if Users.query.filter_by(password=password).count() > 0:
                    found_user = Users.query.filter_by(name=username).first()
                    if found_user.password == password:
                        session["name"] = username
                        return redirect(url_for("home"))
                else:
                    flash("Incorrect username or password!")
            else:
                flash("Incorrect username or password!")
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("name")
    return redirect(url_for("login"))


###Test only###
@app.route("/list")
def list():
    listx = Users.query.all()
    for x in listx:
        print(x.name)
    return "OK"

@app.route("/reset_chat")
def reset_db():
    Chat.query.delete()
    db.session.commit()
    return "Done"

@app.route("/reset_users")
def reset_users():
    Users.query.delete()
    db.session.commit()
    session.pop("name")
    return "Done"

###################

@app.route("/json", methods=["POST"])
def json():
    req = request.get_json()

    author = session["name"]
    message = req["content"]
    date = str(datetime.now())
    date = date[:date.index(".")]
    date = date.replace(" ", " | ")
    push = Chat(author, message, date)

    db.session.add(push)
    db.session.commit()

    res = make_response(jsonify({"date": date}), 200)
    return res

@app.route("/check", methods=["POST"])
def check():
    global old_amount
    req = request.get_json()
    amount = len(Chat.query.all())

    if old_amount == amount:
        res = make_response(req, 200)
    else:
        res = make_response(jsonify({"status": 1}), 200)
    
    return res

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)