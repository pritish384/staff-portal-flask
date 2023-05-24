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

app.config["SECRET_KEY"] = config['SECRET_KEY']  # Set your secret key
app.config["DISCORD_CLIENT_ID"] = config["client_id"]  # Set your Discord Client ID
app.config["DISCORD_CLIENT_SECRET"] = config["client_secret"]  # Set your Discord Client Secret
app.config["DISCORD_REDIRECT_URI"] = config["callback_url"]  # Set your redirect URI


discord = DiscordOAuth2Session(app)


# Set the template folder
app.template_folder = 'pages'
app.static_folder = 'static'


@app.route('/staff/dashboard')
def staff_dashboard():
    if discord.authorized:
        user = discord.fetch_user()

        if db.members.find_one({"discord_id":user.id}) is None :
            session["error"] = "You are not a staff member"
            return redirect(url_for("error"))

        bot_access = db.members.find_one({"discord_id":user.id})["department"] in config['bots_staff_roles']

        return render_template('templates/staff.html', user=user , staff_info=db.members.find_one({"discord_id":user.id}) , bot_access=bot_access)
    return redirect(url_for("login"))


@app.route('/staff/manage-members' , methods=["GET" , "POST"])
def manage_members():
    if discord.authorized:
        user = discord.fetch_user()

        if db.members.find_one({"discord_id":user.id}) is None :
            session["error"] = "You are not a staff member"
            return redirect(url_for("error"))

        if db.members.find_one({"discord_id":user.id})["department"] in config['bots_staff_roles'] :
            bot_access = True
        else:
            bot_access = False
            session["error"] = "You do not have access to this page"
            return redirect(url_for("/error"))

        staff_members = db.members.find()

        # if there is post['modify']
        if request.method == "POST":

            # if request.form['modify']:
            #     document={
            #         "staff_code":request.form['staff_code'],
            #         "discord_id":request.form['discord_id'],
            #         "department":request.form['member_department'],
            #         "salary":request.form['member_salary']
            #     }
            #     db.members.update_one({"staff_code":request.form['staff_code']} , {"$set":document})

            # elif request.form['remove']:
            #     db.members.delete_one({"staff_code":request.form['staff_code']})
            print(request.form)
            return redirect(url_for("staff_dashboard"))

        return render_template('templates/manage_members.html', user=user , staff_info=db.members.find_one({"discord_id":user.id}) , bot_access=bot_access , staff_members=staff_members)
    return redirect(url_for("login"))


@app.route("/login")
def login():
    return discord.create_session(scope=["identify" , "guilds" , "guilds.members.read"])  # Add additional scopes as needed


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
