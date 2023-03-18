# from msilib.schema import Environment
# import jinja2.ext.loopcontrols
import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import func
from flask_login import UserMixin, login_user, logout_user, login_required, current_user, LoginManager

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField, IntegerField
from wtforms.validators import DataRequired, EqualTo, Length, Optional
from wtforms.widgets import TextArea
# from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField

from PIL import Image


app = Flask(__name__)

# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#secret key
app.secret_key = 'your secret key'
#add database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:cherry18@localhost/ty606'

#initialize the database
db = SQLAlchemy(app)
app.app_context().push()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'landingPage'

# jinja_env = Environment(extensions=['jinja2.ext.loopcontrols'])

@login_manager.user_loader
def load_user(user_id):
	return Users.query.get(int(user_id))

# # Pass Stuff To Navbar
# @app.context_processor
# def base_user():
# 	current_u = current_user.id
# 	return dict(form=form)

@app.route('/user_logout', methods=['GET', 'POST'])
@login_required
def user_logout():
	logout_user()
	flash("You Have Been Logged Out!  Thanks For Stopping By...")
	return redirect(url_for('login'))

@app.route("/", methods=['GET', 'POST'])
def landingPage():
    username = None
    if request.method == 'POST':
        username = request.form.get("username")
        pwd1 = request.form.get("pwd1")
        pwd2 = request.form.get("pwd2")
        utype = request.form.get("utype")

        username_exists = Users.query.filter_by(username=username).first()

        if username_exists:
            flash('Username is already in use.', category='error')
            print('Username is already in use.')
            # return render_template('landingPage.html')
        elif pwd1 != pwd2:
            flash('Password not matching.', category='error')
            print('Password not matching.')
        else:
            # if request.form.validate_on_submit():
            new_user = Users(username=username, password=generate_password_hash(pwd1, method='sha256'), utype=utype)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('User created!')
            print('user created')
            our_users = Users.query.order_by(Users.date_created)
            if current_user.utype == 'User':
                return redirect(url_for('user_details'))
            elif current_user.utype == 'Org':
                return redirect(url_for('org_details'))
            else:
                return render_template("landingPage.html", our_users=our_users, name=username)
    return render_template('landingPage.html', name=username)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("pwd1")

        user = Users.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                # flash("Logged in!", category='success')
                print("logged in")
                login_user(user, remember=True)
                if current_user.utype == 'User':
                    flash("Logged in!", category='success')
                    return redirect(url_for('user_dashboard'))
                elif current_user.utype == 'Org':
                    flash("Logged in!", category='success')
                    return redirect(url_for('org_dashboard'))
                else:
                    flash('Something went wrong! Could not login!')
                    return redirect(url_for('login'))
            else:
                flash('Password is incorrect.', category='error')
                print('password incorrect')
        else:
            flash('Email does not exist.', category='error')
            print("email does not exist")

    return render_template("login.html")


@app.route('/user_details', methods=['GET', 'POST'])
@login_required
def user_details():
    if current_user.utype == 'User':
        name = None
        if request.method == 'POST':
            uid = current_user.id
            username = current_user.username
            password = current_user.password
            name = request.form.get("name")
            email = request.form.get("email")
            contact = request.form.get("contact")
            address = request.form.get("address")

            email_exists = user_table.query.filter_by(email=email).first()
            # username_exists = User.query.filter_by(username=username).first()

            if email_exists:
                flash('Email is already in use.', category='error')
                print('Email is already in use.')
                return redirect(url_for('user_details'))
            else:
                # if request.form.validate_on_submit():
                new_user = user_table(uid=uid, username=username, password=password, name=name, email=email, contact=contact, address=address)
                db.session.add(new_user)
                db.session.commit()

                # login_user(new_user, remember=True)
                flash('User Signed up')
                print('user created added to user table')
                our_users = user_table.query.order_by(user_table.date_created)
                return render_template('user_dashboard.html', our_users=our_users, name=name)
        return render_template('user_details.html', name=name)
    else:
        return render_template('error.html')

# Create a user update Form
class update_user_form(FlaskForm):
    username = StringField("Username", validators=[Optional()])
    # password = PasswordField("password")
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    contact = StringField("Contact", validators=[DataRequired(), Length(min=10, max=10)])
    address = StringField("Address",  widget=TextArea())
    submit = SubmitField("Submit")

@app.route('/user_details_update/<int:id>', methods=['GET', 'POST'])
@login_required
def user_details_update(id):
    if current_user.utype == 'User':
        form = update_user_form()
        our_current_user = current_user.id
        our_users = user_table.query.order_by(user_table.date_created)
        for user in our_users:
            # print(our_current_user.username)
            # print(user.uid)
            if user.uid == our_current_user:
                print(our_current_user, ' and ', user.uid)
                our_user = user
                break
        print(our_user.name, " and ", our_user)
        # name = None
        user_to_update = user_table.query.get_or_404(our_user.id)
        print(user_to_update.name)
        form.username.data = user_to_update.username
        # form.password.data = user_to_update.password
        form.name.data = user_to_update.name
        form.email.data = user_to_update.email
        form.contact.data = user_to_update.contact
        form.address.data = user_to_update.address
        if request.method == "POST":
            user_to_update.name = request.form.get("name")
            user_to_update.email = request.form.get("email")
            user_to_update.contact = request.form.get("contact")
            user_to_update.address = request.form.get("address")
            try:
                db.session.commit()
                flash("User Updated Successfully!")
                form.username.data = user_to_update.username
                # form.password.data = user_to_update.password
                form.name.data = user_to_update.name
                form.email.data = user_to_update.email
                form.contact.data = user_to_update.contact
                form.address.data = user_to_update.address
                return render_template("user_details_update.html", form=form, user_to_update = user_to_update, id=our_user.id)
            except:
                flash("Error!  Looks like there was a problem...try again!")
                return render_template("user_details_update.html", form=form, user_to_update = user_to_update, id=our_user.id)
        else:
            return render_template("user_details_update.html", form=form, user_to_update = user_to_update, id=our_user.id)
    else:
        return render_template('error.html')

@app.route("/user_delete/<int:id>", methods=['GET', 'POST'])
@login_required
def user_delete(id):
    if current_user.utype == 'User':
        # req_to_delete = pickup_request.query.get_or_404(id)

        current_u = current_user.id
        user_to_delete = Users.query.get_or_404(id)
        
        our_users = user_table.query.order_by(user_table.date_created)
        for users in our_users:
            if users.uid == current_u:
                user = users
        print(user)
        user_to_delete_usertable = user_table.query.get_or_404(user.id)

        reqs = pickup_request.query.order_by(pickup_request.request_created)
        for req in reqs:
            if req.user_id == user.id:
                req_to_delete = pickup_request.query.get_or_404(req.id)
                db.session.delete(req_to_delete)
                db.session.commit()

        if user.uid == user_to_delete.id:
            try:
                logout_user()
                db.session.delete(user_to_delete)
                db.session.delete(user_to_delete_usertable)
                db.session.commit()

                # Return a message
                flash("User Was Deleted!")

                # Grab all the posts from the database
                # reqs = pickup_request.query.order_by(pickup_request.request_created)
                return redirect("/")

            except:
                # Return an error message
                flash("Whoops! There was a problem deleting user, try again...")

                # Grab all the posts from the database
                # reqs = pickup_request.query.order_by(pickup_request.request_created)
                return redirect("user_details_update.html")
        else:
            # Return a message
            flash("You Aren't Authorized To Delete That User!")
            # Grab all the posts from the database
            # reqs = pickup_request.query.order_by(pickup_request.request_created)
            return redirect("user_details_update.html")
        # return render_template("user_my_requests.html", reqs=reqs, user=user)
    else:
        return render_template('error.html')

@app.route("/org_delete/<int:id>", methods=['GET', 'POST'])
@login_required
def org_delete(id):
    if current_user.utype == 'Org':
        current_org = current_user.id
        org_to_delete = Users.query.get_or_404(id)
        
        our_orgs = org_table.query.order_by(org_table.date_created)
        for orgs in our_orgs:
            if orgs.cid == current_org:
                org = orgs
        # print(user)
        org_to_delete_orgtable = org_table.query.get_or_404(org.id)

        our_orgs_posts = org_posts.query.order_by(org_posts.date_posted)
        for org_postss in our_orgs_posts:
            if org_postss.org_id == org.id:
                org_post = org_postss
        # print(user)
        org_post_to_delete_orgpost = org_posts.query.get_or_404(org_post.id)

        # reqs = pickup_request.query.order_by(pickup_request.request_created)
        # for req in reqs:
        #     if req.user_id == user.id:
        #         req_to_delete = pickup_request.query.get_or_404(req.id)
        #         db.session.delete(req_to_delete)
        #         db.session.commit()

        if org.cid == org_to_delete.id:
            try:
                logout_user()
                db.session.delete(org_to_delete)
                db.session.delete(org_to_delete_orgtable)
                db.session.delete(org_post_to_delete_orgpost)
                db.session.commit()

                # Return a message
                flash("Organization Was Deleted!")

                # Grab all the posts from the database
                # reqs = pickup_request.query.order_by(pickup_request.request_created)
                return redirect("/")

            except:
                # Return an error message
                flash("Whoops! There was a problem deleting organization, try again...")

                # Grab all the posts from the database
                # reqs = pickup_request.query.order_by(pickup_request.request_created)
                return redirect("org_details_update.html")
        else:
            # Return a message
            flash("You Aren't Authorized To Delete That Organization!")
            # Grab all the posts from the database
            # reqs = pickup_request.query.order_by(pickup_request.request_created)
            return redirect("org_details_update.html")
        # return render_template("user_my_requests.html", reqs=reqs, user=user)
    else:
        return render_template('error.html')



@app.route('/org_details', methods=['GET', 'POST'])
@login_required
def org_details():
    if current_user.utype == 'Org':
        name = None
        msg = 'Details filled already!'
        current_org_id =current_user.id
        org_exists_in_org_table = org_table.query.filter_by(cid=current_org_id).first()
        if org_exists_in_org_table:
            return render_template('org_details.html', name=name, msg=msg)
        else:
            msg = 'details need to be filled!'
            if request.method == 'POST':
                cid = current_user.id
                username = current_user.username
                password = current_user.password
                name = request.form.get("name")
                email = request.form.get("email")
                contact = request.form.get("contact")
                alt_contact = request.form.get("alt_contact")
                address = request.form.get("address")
                city = request.form.get("city")
                state = request.form.get("state")
                types = request.form.get("types")
                description = request.form.get("description")
                photo = request.form.get("photo")
                print(photo)
                website = request.form.get("website")
                maps = request.form.get("maps")

                email_exists = org_table.query.filter_by(email=email).first()

                if email_exists:
                    flash('Email is already in use.', category='error')
                    print('Email is already in use.')
                    return redirect(url_for('org_details'))
                else:
                    new_user = org_table(cid=cid, username=username, password=password, name=name, email=email, contact=contact, alt_contact=alt_contact, address=address, city=city, state=state, types=types, description=description, photo=photo, website=website, maps=maps)
                    db.session.add(new_user)
                    db.session.commit()
                    # login_user(new_user, remember=True)
                    flash('Org Signed up')
                    print('org created')
                    our_orgs = org_table.query.order_by(org_table.date_created)
                    for orgs in our_orgs:
                        if orgs.cid == current_org_id:
                            org = orgs
                            # return render_template('org_dashboard.html', org=orgs)
                    return render_template('org_dashboard.html', our_orgs=our_orgs, name=name, org=org)
            return render_template('org_details.html', name=name, msg=msg)
    else:
        return render_template('error.html')

# Create a Posts Form
class update_org_form(FlaskForm):
    username = StringField("username", validators=[Optional()])
    # password = PasswordField("password")
    name = StringField("name", validators=[DataRequired()])
    email = StringField("email", validators=[DataRequired()])
    contact = StringField("contact", validators=[DataRequired()])
    alt_contact = StringField("alternate contact")
    address = StringField("address", validators=[DataRequired()], widget=TextArea())
    city = StringField("city", validators=[DataRequired()])
    state = StringField("state", validators=[DataRequired()])
    types = StringField("Type of organization", validators=[DataRequired()])
    description = TextAreaField('description', validators=[DataRequired()])
    photo = FileField('Photo')
    website  = StringField("website")
    maps = StringField("Location link")
    submit = SubmitField("Submit")


@app.route('/org_details_update/<int:id>', methods=['GET', 'POST'])
@login_required
def org_details_update(id):
    if current_user.utype == 'Org':
        form = update_org_form()
        our_current_org = current_user.id
        our_orgs = org_table.query.order_by(org_table.date_created)
        for org in our_orgs:
            # print(our_current_user.username)
            # print(user.uid)
            if org.cid == our_current_org:
                # print(our_current_user, ' and ', user.uid)
                our_org = org
                break
        print(our_org.name, " and ", our_org)
        # name = None
        org_to_update = org_table.query.get_or_404(our_org.id)
        print(org_to_update.name)
        form.username.data = org_to_update.username
        # form.password.data = user_to_update.password
        form.name.data = org_to_update.name
        form.email.data = org_to_update.email
        form.contact.data = org_to_update.contact
        form.alt_contact.data = org_to_update.alt_contact
        form.address.data = org_to_update.address
        form.city.data = org_to_update.city
        form.state.data = org_to_update.state
        form.types.data = org_to_update.types
        form.description.data = org_to_update.description
        form.photo.data = org_to_update.photo
        print("photo:  ", org_to_update.photo)
        # form.photo.data = Image.open(org_to_update.photo)
        form.website.data = org_to_update.website
        form.maps.data = org_to_update.maps
        print("maps: ", org_to_update.maps)
        if request.method == "POST":
            org_to_update.name = request.form.get("name")
            org_to_update.email = request.form.get("email")
            org_to_update.contact = request.form.get("contact")
            org_to_update.alt_contact = request.form.get("alt_contact")
            org_to_update.address = request.form.get("address")
            org_to_update.city = request.form.get("city")
            org_to_update.state = request.form.get("state")
            org_to_update.types = request.form.get("types")
            org_to_update.description = request.form.get("description")
            org_to_update.photo = request.form.get("photo")
            org_to_update.website = request.form.get("website")
            org_to_update.maps = request.form.get("maps")
            try:
                db.session.commit()
                flash("User Updated Successfully!")
                form.username.data = org_to_update.username
                # form.password.data = user_to_update.password
                form.name.data = org_to_update.name
                form.email.data = org_to_update.email
                form.contact.data = org_to_update.contact
                form.alt_contact.data = org_to_update.alt_contact
                form.address.data = org_to_update.address
                form.city.data = org_to_update.city
                form.state.data = org_to_update.state
                form.types.data = org_to_update.types
                form.description.data = org_to_update.description
                form.photo.data = org_to_update.photo
                # form.photo.data = Image.open(org_to_update.photo)
                form.website.data = org_to_update.website
                form.maps.data = org_to_update.maps
                return render_template("org_details_update.html", form=form, org_to_update = org_to_update, id=our_org.id)
            except:
                flash("Error!  Looks like there was a problem...try again!")
                return render_template("org_details_update.html", form=form, org_to_update = org_to_update, id=our_org.id)
        else:
            return render_template("org_details_update.html", form=form, org_to_update = org_to_update, id=our_org.id)
        # return render_template("org_details_update.html", form=form)
    else:
        return render_template('error.html')


@app.route('/user_dashboard', methods=['GET', 'POST'])
@login_required
def user_dashboard():
    if current_user.utype == 'User':
        current_u = current_user.id
        our_users = user_table.query.order_by(user_table.date_created)
        for users in our_users:
            print(current_u)
            print(users.uid)
            if current_u == users.uid:
                print(current_u, ' and ', users.uid)
                return render_template('user_dashboard.html', user=users.name)
            # else:
        flash('details are pending!', category='error')
        return redirect(url_for('user_details'))
        # return render_template('user_dashboard.html')
    else:
        return render_template('error.html')

@app.route('/org_dashboard', methods=['GET', 'POST'])
@login_required
def org_dashboard():
    if current_user.utype == 'Org':
        current_org = current_user.id
        our_orgs = org_table.query.order_by(org_table.date_created)
        for orgs in our_orgs:
            if orgs.cid == current_org:
                return render_template('org_dashboard.html', org=orgs)
            # else:
        flash('Another step to go! Looks like you havent filled the details yet! Please do so to move forward!', category='error')
        return redirect(url_for('org_details'))
    else:
        return render_template('error.html')

@app.route('/search', methods=['GET','POST'])
@login_required
def search():
    if current_user.utype == 'User':
        location = request.form.get("search")
        orgs = org_table.query
        if request.method == "POST":
            # Query the Database
            orgs = orgs.filter(org_table.city.like('%' + location + '%'))
            orgs = orgs.order_by(org_table.name).all()
        print(orgs)
        org_count = len(orgs)
        return render_template("search.html",locationSearched = location, orgs = orgs, org_count=org_count)
    else:
        return render_template('error.html')

@app.route("/search_details/<int:id>", methods=['GET', 'POST'])
@login_required
def search_details(id):
    if current_user.utype == 'User':
        org = org_table.query.get_or_404(id)
        print("reach1")
        current_u = current_user.id
        our_users = user_table.query.order_by(user_table.date_created)
        
        for users in our_users:
            if users.uid == current_u:
                user = users
        print(user)
        user_to_update = user_table.query.get_or_404(user.id)
        if request.method == 'POST':
            print("reach inside")
            pickup_date = request.form["pickup_date"]
            pickup_time_form = request.form["pickup_time"]
            pickup_item = request.form["pickup_item"]
            user_address = request.form["pickup_address"]
            # pickup_date = request.form.get("pickup_date")
            # pickup_time_form = request.form.get("pickup_time")
            print("pickup_date ", pickup_date," pickup_time_form ",pickup_time_form)
            d = datetime.strptime(pickup_time_form, "%H:%M")
            pickup_time = d.strftime("%I:%M %p")
            
            print(pickup_date," and ",pickup_time)

            new_request = pickup_request(user_id=user.id, org_id=org.id, user_name=user.name, user_email=user.email, user_contact=user.contact, user_address=user_address, org_name=org.name, org_address=org.address, pickup_date=pickup_date, pickup_time=pickup_time, pickup_item=pickup_item)
            user_to_update.address = request.form.get("pickup_address")
            db.session.add(new_request)
            db.session.commit()
            msg = 'reached inside'
            return render_template('request_success.html', msg=msg, org=org.id, pickup_date=pickup_date, pickup_time=pickup_time, pickup_item=pickup_item)
        return render_template('search_details.html', org=org, user=user)
    else:
        return render_template('error.html')

@app.route("/request_success", methods=['GET', 'POST'])
@login_required
def request_success():
    if current_user.utype == 'User':
        return render_template('request_success.html')
    else:
        return render_template('error.html')

@app.route("/user_request_delete/<int:id>", methods=['GET', 'POST'])
@login_required
def user_request_delete(id):
    if current_user.utype == 'User':
        req_to_delete = pickup_request.query.get_or_404(id)

        current_u = current_user.id
        our_users = user_table.query.order_by(user_table.date_created)
        
        for users in our_users:
            if users.uid == current_u:
                user = users
        print(user)
        if user.id == req_to_delete.user_id:
            try:
                db.session.delete(req_to_delete)
                db.session.commit()

                # Return a message
                flash("Request Was Deleted!")
                req_created = pickup_request.query
                pts = req_created.filter(pickup_request.user_id.like(current_u))
                pts = req_created.order_by(desc(pickup_request.request_created)).all()
                check = False
                req_count = 0
                for req in pts:
                    print("req there")
                    if req.user_id == user.id:
                        print("req.user_id = ", req.user_id, "  user.id = ", user.id)
                        req_count = req_count + 1
                        print("req_count = ", req_count)
                        check = True
                        reqs = pickup_request.query.order_by(desc(pickup_request.request_created))
                        return render_template('user_my_requests.html', reqs=reqs, user=user,  check=check)        

                return render_template("user_my_requests.html", reqs=reqs, user=user)

            except:
                # Return an error message
                flash("Whoops! There was a problem deleting request, try again...")
                req_created = pickup_request.query
                pts = req_created.filter(pickup_request.user_id.like(current_u))
                pts = req_created.order_by(desc(pickup_request.request_created)).all()
                check = False
                req_count = 0
                for req in pts:
                    print("req there")
                    if req.user_id == user.id:
                        print("req.user_id = ", req.user_id, "  user.id = ", user.id)
                        req_count = req_count + 1
                        print("req_count = ", req_count)
                        check = True
                        reqs = pickup_request.query.order_by(desc(pickup_request.request_created))
                        return render_template('user_my_requests.html', reqs=reqs, user=user,  check=check)        

                return render_template("user_my_requests.html", reqs=reqs, user=user)
        else:
            # Return a message
            flash("You Aren't Authorized To Delete That Request!")
            # Grab all the posts from the database
            reqs = pickup_request.query.order_by(pickup_request.request_created)
            return render_template("user_my_requests.html", reqs=reqs, user=user)
        # return render_template("user_my_requests.html", reqs=reqs, user=user)

    elif current_user.utype == 'Org':
        req_to_delete = pickup_request.query.get_or_404(id)
        current_org = current_user.id
        our_orgs = org_table.query.order_by(org_table.date_created)
        
        for orgs in our_orgs:
            if orgs.cid == current_org:
                org = orgs
        # print(user)
        if org.id == req_to_delete.org_id:
            try:
                db.session.delete(req_to_delete)
                db.session.commit()

                # Return a message
                flash("Request Was Deleted!")
                req_created = pickup_request.query
                pts = req_created.filter(pickup_request.user_id.like(current_org))
                pts = req_created.order_by(desc(pickup_request.request_created)).all()
                check = False
                req_count = 0
                for req in pts:
                    print("req there")
                    if req.org_id == org.id:
                        print("req.org_id = ", req.org_id, "  org.id = ", org.id)
                        req_count = req_count + 1
                        print("req_count = ", req_count)
                        check = True
                        reqs = pickup_request.query.order_by(pickup_request.request_created)
                        return render_template('requests_received.html', reqs=reqs, org=org,  check=check)        


                # Grab all the posts from the database
                # reqs = pickup_request.query.order_by(pickup_request.request_created)
                return render_template("requests_received.html", reqs=reqs, org=org)

            except:
                # Return an error message
                flash("Whoops! There was a problem deleting request, try again...")
                req_created = pickup_request.query
                pts = req_created.filter(pickup_request.user_id.like(current_org))
                pts = req_created.order_by(desc(pickup_request.request_created)).all()
                check = False
                req_count = 0
                for req in pts:
                    print("req there")
                    if req.org_id == org.id:
                        print("req.org_id = ", req.org_id, "  org.id = ", org.id)
                        req_count = req_count + 1
                        print("req_count = ", req_count)
                        check = True
                        reqs = pickup_request.query.order_by(pickup_request.request_created)
                        return render_template('requests_received.html', reqs=reqs, org=org,  check=check)        

                return render_template("requests_received.html", reqs=reqs, org=org)
        else:
            # Return a message
            flash("You Aren't Authorized To Delete That Request!")
            # Grab all the posts from the database
            reqs = pickup_request.query.order_by(pickup_request.request_created)
            return render_template("user_my_requests.html", reqs=reqs, user=user)
        # return render_template("user_my_requests.html", reqs=reqs, user=user)
    else:
        return render_template('error.html')

@app.route("/requests_received", methods=['GET', 'POST'])
@login_required
def requests_received():
    if current_user.utype == 'Org':
        current_org = current_user.id
        our_pickup_requests = pickup_request.query.order_by(desc(pickup_request.request_created))
        our_orgs = org_table.query.order_by(org_table.date_created)
        our_users = user_table.query.order_by(user_table.date_created)
        print("outside")
        for our_org in our_orgs:
            if our_org.cid == current_org:
                org = our_org
                print("got org")
        user_ids = []
        for requests in our_pickup_requests:
            print("inside requests")
            print(requests.id)
            if requests.org_id == org.id:
                print("got org id in pickup")
                uids = requests.user_id
                user_ids.append(uids)
                print("got user id in pickup")
        print(user_ids)
        users = []
        for our_user in our_users:
            print("got user in user table: user id = ", our_user.id)
            for i in user_ids:
                if our_user.id == i:
                    u = our_user
                    users.append(u)
                    print("got user")
        print(users)

        req_created = pickup_request.query
        pts = req_created.filter(pickup_request.user_id.like(current_org))
        pts = req_created.order_by(desc(pickup_request.request_created)).all()
        check = False
        req_count = 0
        for req in pts:
            print("req there")
            if req.org_id == org.id:
                print("req.org_id = ", req.org_id, "  org.id = ", org.id)
                req_count = req_count + 1
                print("req_count = ", req_count)
                check = True
                reqs = pickup_request.query.order_by(desc(pickup_request.request_created))
                return render_template('requests_received.html', reqs=reqs, org=org, users=users, check=check)        
        return render_template('requests_received.html', reqs=our_pickup_requests, org=org, users=users)
    else:
        return render_template('error.html')

@app.route("/request_status/<int:id>", methods=['GET', 'POST'])
@login_required
def change_request_status(id):
    if current_user.utype == 'Org':
        current_org = current_user.id
        our_pickup_requests = pickup_request.query.order_by(pickup_request.request_created)
        our_orgs = org_table.query.order_by(org_table.date_created)
        our_users = user_table.query.order_by(user_table.date_created)
        for our_org in our_orgs:
            if our_org.cid == current_org:
                org = our_org
        user_ids = []
        for requests in our_pickup_requests:
            if requests.org_id == org.id:
                print("got org id in pickup")
                uids = requests.user_id
                user_ids.append(uids)
        users = []
        for our_user in our_users:
            print("got user in user table: user id = ", our_user.id)
            for i in user_ids:
                if our_user.id == i:
                    u = our_user
                    users.append(u)
        
        req_status_update = pickup_request.query.get_or_404(id)

        if request.method == "POST":
            status = request.form.get('status')
            req_status_update.request_status = request.form.get('status')
            print("g status:    ", status," status:   ", req_status_update.request_status)
            try:
                db.session.commit()
                flash("Request status updated!")

                req_created = pickup_request.query
                pts = req_created.filter(pickup_request.user_id.like(current_org))
                pts = req_created.order_by(desc(pickup_request.request_created)).all()
                check = False
                req_count = 0
                for req in pts:
                    print("req there")
                    if req.org_id == org.id:
                        print("req.org_id = ", req.org_id, "  org.id = ", org.id)
                        req_count = req_count + 1
                        print("req_count = ", req_count)
                        check = True
                        return render_template('requests_received.html', reqs=our_pickup_requests, org=org, users=users, check=check)        
                return render_template('requests_received.html', reqs=our_pickup_requests, org=org, users=users)
            except:
                flash("Request status not updated!")
                req_created = pickup_request.query
                pts = req_created.filter(pickup_request.user_id.like(current_org))
                pts = req_created.order_by(desc(pickup_request.request_created)).all()
                check = False
                req_count = 0
                for req in pts:
                    print("req there")
                    if req.org_id == org.id:
                        print("req.org_id = ", req.org_id, "  org.id = ", org.id)
                        req_count = req_count + 1
                        print("req_count = ", req_count)
                        check = True
                        return render_template('requests_received.html', reqs=our_pickup_requests, org=org, users=users, check=check)        
                return render_template('requests_received.html', reqs=our_pickup_requests, org=org, users=users)
        else:
            return render_template('requests_received.html', reqs=our_pickup_requests, org=org, users=users)
    else:
        return render_template('error.html')


@app.route("/user_my_requests", methods=['GET', 'POST'])
@login_required
def user_my_requests():
    if current_user.utype == 'User':
        current_u = current_user.id
        our_pickup_requests = pickup_request.query.order_by(pickup_request.request_created)
        our_orgs = org_table.query.order_by(org_table.date_created)
        our_users = user_table.query.order_by(user_table.date_created)
        print("outside")
        for our_user in our_users:
            if our_user.uid == current_u:
                user = our_user
                print("got current user")
        org_ids = []
        for requests in our_pickup_requests:
            print("inside requests")
            print(requests.id)
            if requests.user_id == user.id:
                print("got org id in pickup")
                oids = requests.org_id
                org_ids.append(oids)
                print("got user id in pickup")
        print(org_ids)
        orgs= []
        for our_org in our_orgs:
            print("got org in org table: org id = ", our_org.id)
            for i in org_ids:
                if our_org.id == i:
                    o = our_org
                    orgs.append(o)
                    print("got org")
        print(orgs)
        req_created = pickup_request.query
        pts = req_created.filter(pickup_request.user_id.like(current_u))
        pts = req_created.order_by(desc(pickup_request.request_created)).all()
        check = False
        req_count = 0
        for req in pts:
            print("req there")
            if req.user_id == user.id:
                print("req.user_id = ", req.org_id, "  user.id = ", user.id)
                req_count = req_count + 1
                print("req_count = ", req_count)
                check = True
                reqs = pickup_request.query.order_by(desc(pickup_request.request_created))
                return render_template('user_my_requests.html', reqs=reqs, user=user, orgs=orgs, check=check)
        return render_template('user_my_requests.html', reqs=our_pickup_requests, user=user, orgs=orgs)
    else:
        return render_template('error.html')


@app.route('/error')
def error():
    return render_template('error.html')

####posts feature
@app.route("/new_post", methods=['GET', 'POST'])
@login_required
def new_post():
    if current_user.utype == 'Org':
        if request.method == 'POST':
            cid = current_user.id
            title = request.form.get("title")
            content = request.form.get("content")
            picture = request.form.get("picture")

            our_orgs = org_table.query.order_by(org_table.date_created)
            for our_org in our_orgs:
                if our_org.cid == cid:
                    org = our_org

            new_post = org_posts(org_id=org.id, org_name=org.name , title=title, content=content, picture=picture)
            db.session.add(new_post)
            db.session.commit()
            
            flash('Post created!')
            print('Post created')
            our_posts = org_posts.query.order_by(org_posts.date_posted)
            return render_template('new_post.html', our_posts=our_posts)
        return render_template('new_post.html')
    else:
        return render_template('error.html')

@app.route("/view_post", methods=['GET', 'POST'])
@login_required
def view_post():
    if current_user.utype == 'Org':
        current_org = current_user.id
        our_orgs = org_table.query.order_by(org_table.date_created)
        for our_org in our_orgs:
            if our_org.cid == current_org:
                org = our_org
        print("current org id from org table = ", org.id)
        posts_created = org_posts.query
        pts = posts_created.filter(org_posts.org_id.like(current_org))
        pts = posts_created.order_by(desc(org_posts.date_posted)).all()

        check = False
        post_count = 0
        for post in pts:
            print("post there")
            if post.org_id == org.id:
                print("post.org_id = ", post.org_id, "  org.id = ", org.id)
                post_count = post_count + 1
                print("post_count = ", post_count)
                check = True
                return render_template('view_post.html', org=org, posts=pts, check=check)
        return render_template('view_post.html', org=org)
    else:
        return render_template('error.html')


@app.route("/post_delete/<int:id>", methods=['GET','POST'])
@login_required
def post_delete(id):
    if current_user.utype == 'Org':
        post_to_delete = org_posts.query.get_or_404(id)
        # post_to_delete = posts.query.get_or_404(id)

        current_org = current_user.id
        our_orgs = org_table.query.order_by(org_table.date_created)
        
        for orgs in our_orgs:
            if orgs.cid == current_org:
                org = orgs
        # print(user)
        if org.id == post_to_delete.org_id:
            try:
                db.session.delete(post_to_delete)
                db.session.commit()

                # Return a message
                flash("Post Was Deleted!")

                # Grab all the posts from the database
                posts = org_posts.query.order_by(org_posts.date_posted)
                check = False
                post_count = 0
                for post in posts:
                    print("post there")
                    if post.org_id == org.id:
                        print("post.org_id = ", post.org_id, "  org.id = ", org.id)
                        post_count = post_count + 1
                        print("post_count = ", post_count)
                        check = True
                        return render_template('view_post.html', org=org, posts=posts, check=check)
                return render_template('view_post.html', org=org)
                # return render_template("view_post.html", posts=posts, org=org, check=True)
            except:
                # Return an error message
                flash("Whoops! There was a problem deleting post, try again...")

                # Grab all the posts from the database
                posts = posts.query.order_by(posts.date_posted)
                check = False
                post_count = 0
                for post in posts:
                    print("post there")
                    if post.org_id == org.id:
                        print("post.org_id = ", post.org_id, "  org.id = ", org.id)
                        post_count = post_count + 1
                        print("post_count = ", post_count)
                        check = True
                        return render_template('view_post.html', org=org, posts=posts, check=check)
                return render_template('view_post.html', org=org)
                # return render_template("user_my_requests.html", reqs=reqs, user=user)
        else:
            # Return a message
            flash("You Aren't Authorized To Delete That Post!")
            # Grab all the posts from the database
            posts = posts.query.order_by(posts.date_posted)
            check = False
            post_count = 0
            for post in posts:
                print("post there")
                if post.org_id == org.id:
                    print("post.org_id = ", post.org_id, "  org.id = ", org.id)
                    post_count = post_count + 1
                    print("post_count = ", post_count)
                    check = True
                    return render_template('view_post.html', org=org, posts=posts, check=check)
            return render_template('view_post.html', org=org)
    else:
        return render_template('error.html')


@app.route("/user_view_posts/<int:id>", methods=['GET', 'POST'])
@login_required
def user_view_posts(id):
    if current_user.utype == 'User':
        org = org_table.query.get_or_404(id)
        our_orgs = org_table.query.order_by(org_table.date_created)
        print(org.id)
        
        posts_created = org_posts.query
        pts = posts_created.filter(org_posts.org_id.like(org.id))
        pts = posts_created.order_by(desc(org_posts.date_posted)).all()

        check = False
        post_count = 0
        for post in pts:
            if post.org_id == org.id:
                post_count = post_count + 1
                # print(post_count)
                check = True
                return render_template('user_view_posts.html', org=org, posts=pts, check=check)
        return render_template('user_view_posts.html', org=org)
        # return render_template('user_view_posts.html')
    else:
        return render_template('error.html')



########### contact us ###########
@app.route("/contact_us", methods=['GET', 'POST'])
def contact_us():
    try:
        if request.method == 'POST':
            name = request.form.get("person_name")
            email = request.form.get("person_email")
            message = request.form.get("person_message")

            feedback = contact_us(name=name , email=email, message=message)
            db.session.add(feedback)
            db.session.commit()
            
            flash('Message sent successfully!')
            print('Message sent successfully!')
            return redirect('/')
        return redirect('/')
    except:
        flash('Message error!', category='error')
        print('Message error!')
        return render_template('landingPage.html')


############## creating new models#####
class Users(db.Model, UserMixin):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable = False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    utype = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())

class user_table(db.Model):
    __tablename__ = 'user_table'
    id = db.Column(db.Integer, primary_key=True)

    # uid = db.Column(db.Integer, db.ForeignKey('Users.uid'))
    # user_id = db.relationship('Users', backref='Users')

    uid = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    # password = db.Column(db.String(150), nullable=False)
    contact = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(500))
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())

class org_table(db.Model):
    __tablename__ = 'org_table'
    id = db.Column(db.Integer, primary_key=True)

    # cid = db.Column(db.Integer, db.ForeignKey('Cust.uid'))
    # org_id = db.relationship('Users', backref='Users')

    cid = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(200), nullable=False) 
    # username = db.Column(db.String(200), nullable=False, unique=True) 
    email = db.Column(db.String(150), nullable=False, unique=True) 
    # password = db.Column(db.String(150), nullable=False) 
    contact = db.Column(db.String(100), nullable=False) 
    alt_contact = db.Column(db.String(100), nullable=True) 
    address = db.Column(db.String(500), nullable=False) 
    city = db.Column(db.String(200), nullable=False) 
    state = db.Column(db.String(200), nullable=False) 
    types = db.Column(db.String(200), nullable=False) 
    description = db.Column(db.Text, nullable=False) 
    photo = db.Column(db.String(200))
    website = db.Column(db.String(200))
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())

    maps = db.Column(db.String(500))

class pickup_request(db.Model):
    id = db.Column(db.Integer, primary_key=True) #0
    #foreign key to link to user id
    user_id = db.Column(db.Integer, db.ForeignKey('user_table.id')) #1
    user_pickup = db.relationship('user_table', backref='user_table')
    #foreign key to link to customer_org is
    org_id = db.Column(db.Integer, db.ForeignKey('org_table.id')) #2
    org_pickup = db.relationship('org_table', backref='org_table')

    user_name = db.Column(db.String(200), nullable=False) 
    user_email = db.Column(db.String(150), nullable=False)
    user_contact = db.Column(db.String(100), nullable=False)
    user_address = db.Column(db.String(500), nullable=False)

    org_name = db.Column(db.String(200), nullable=False)
    org_address = db.Column(db.String(500), nullable=False)

    #foreign keys from user table
    # user_name = db.Column(db.String(200), db.ForeignKey('user.name')) #3
    # user_email = db.Column(db.String(150), db.ForeignKey('user.email')) #4
    # user_contact = db.Column(db.String(100), db.ForeignKey('user.contact')) #5
    # user_address = db.Column(db.String(500), db.ForeignKey('user.address')) #6

    pickup_date = db.Column(db.String(200), nullable=False)
    pickup_time = db.Column(db.String(200), nullable=False)

    pickup_item = db.Column(db.String(200), nullable=False)

    request_status = db.Column(db.String(100))

    request_created = db.Column(db.DateTime(timezone=True), default=func.now())

class org_posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    org_id = db.Column(db.Integer, nullable=False)
    # org_post = db.relationship('org_table', backref='org_table')
    org_name = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    picture = db.Column(db.String(255), nullable=False)
    date_posted = db.Column(db.DateTime(timezone=True), default=func.now())
    # slug = db.Column(db.String(255))


class contact_us(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())

if __name__ == "__main__":
    app.run(debug=True)