from flask import Flask, render_template , redirect , url_for , session , request
from flask_discord import DiscordOAuth2Session
import json
import os
from db import db

# Set environment variables
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # !! Only in development environment.


with open('oauth/config.json') as f:
    config = json.load(f)


app = Flask(__name__)

app.config["SECRET_KEY"] = config['SECRET_KEY']
app.config["DISCORD_CLIENT_ID"] = config["client_id"]
app.config["DISCORD_CLIENT_SECRET"] = config["client_secret"]
app.config["DISCORD_REDIRECT_URI"] = config["callback_url"]


discord = DiscordOAuth2Session(app)


# Set the template folder
app.template_folder = 'pages'
app.static_folder = 'static'


@app.route('/staff/dashboard')
def staff_dashboard():
    if discord.authorized:
        user = discord.fetch_user()

        if db.members.find_one({"discord_id":user.id}) is None:
            session["error"] = "You are not a staff member"
            return redirect(url_for("error"))

        bot_access = db.members.find_one({"discord_id":user.id})["department"] in config['bots_staff_roles']

        return render_template('templates/staff.html', user=user,staff_info=db.members.find_one({"discord_id":user.id}),bot_access=bot_access)

    return redirect(url_for("login"))


@app.route('/staff/manage-members' , methods=["GET"])
def manage_members():
    if discord.authorized:
        user = discord.fetch_user()

        if db.members.find_one({"discord_id":user.id}) is None:
            session["error"] = "You are not a staff member"
            return redirect(url_for("error"))

        if db.members.find_one({"discord_id":user.id})["department"] in config['bots_staff_roles']:
            bot_access = True
        else:
            bot_access = False
            session["error"] = "You do not have access to this page"
            return redirect(url_for("/error"))

        staff_members = db.members.find()
        return render_template('templates/manage_members.html', user=user, staff_info=db.members.find_one({"discord_id":user.id}),bot_access=bot_access, staff_members=staff_members)

    return redirect(url_for("login"))


@app.route('/staff/manage-members' , methods=["POST"])
def manage_members_post():
    if discord.authorized:
        user = discord.fetch_user()

        if db.members.find_one({"discord_id":user.id}) is None:
            session["error"] = "You are not a staff member"
            return redirect(url_for("error"))
        
        if db.members.find_one({"discord_id":user.id})["department"] in config['bots_staff_roles']:
            bot_access = True
        else:
            bot_access = False
            session["error"] = "You do not have access to this page"
            return redirect(url_for("/error"))
        
        staff_members = db.members.find()
        print(request.form)
        return render_template('templates/manage_members.html', user=user, staff_info=db.members.find_one({"discord_id":user.id}),bot_access=bot_access, staff_members=staff_members)
    
    return redirect(url_for("login"))



@app.route("/login")
def login():
    return discord.create_session(scope=["identify", "guilds", "guilds.members.read"])


@app.route("/callback")
def callback():
    discord.callback()
    return redirect(url_for("staff_dashboard"))


@app.route("/error")
def error():
    ERROR = session.get("error", None)
    if not ERROR:
        ERROR = "An error occured"

    return render_template('templates/error.html' , error=error)


@app.route("/logout")
def logout():
    discord.revoke()
    ERROR = "You have been logged out"
    session["error"] = ERROR
    return redirect(url_for("error"))


@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')


if __name__ == '__main__':
    app.run(debug=True)
