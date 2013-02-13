from flask import request, render_template, flash, g, session, redirect, url_for
from flask.ext.login import login_required, login_user, logout_user, current_user
from werkzeug import check_password_hash, generate_password_hash
from orvsd_central import db, app, login_manager
from forms import LoginForm, AddDistrict, AddSchool, AddUser, InstallCourse
from models import District, School, Site, SiteDetail, Course, CourseDetail, User

import re
import subprocess
import StringIO
import urllib

def no_perms():
    return "You do not have permission to be here!"

@login_manager.unauthorized_handler
def unauthorized():
    flash('You are not authorized to view this page, please login.')
    return redirect('/login')

@app.route("/")
@login_required
def main_page():
    return redirect('/report')

@login_manager.user_loader
def load_user(userid):
    return User.query.filter_by(id=userid).first()

@app.route("/login", methods=['GET', 'POST'])
def login():
    form=LoginForm(csrf_enabled=False)
    if form.validate_on_submit():
        # login and validate the user...
        user = User.query.filter_by(name=form.name.data).first()
        print check_password_hash
        if user and user.password == form.password.data:
            login_user(user)
            flash("Logged in successfully.")
            return redirect("/add_school")

    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")

@app.route("/add_district", methods=['GET', 'POST'])
def add_district():
    form = AddDistrict()
    user = current_user
    if request.method == "POST":
        #Add district to db.
        db.session.add(District(form.name.data, form.shortname.data,
                        form.base_path.data))
        db.session.commit()

    return render_template('add_district.html', form=form, user=user)

@login_required
@app.route("/add_school", methods=['GET', 'POST'])
def add_school():
    form = AddSchool()
    user = current_user
    msg = ""

    if request.method == "POST":
        #The district_id is supposed to be an integer
        #try:
            #district = District.query.filter_by(id=int(form.district_id)).all()
            #if len(district) == 1:
                #Add School to db
        db.session.add(School(int(form.district_id.data),
                        form.name.data, form.shortname.data,
                        form.domain.data. form.license.data))
        db.session.commit()
            #else:
            #    error_msg= "A district with that id doesn't exist!"
        #except:
        #    error_msg= "The entered district_id was not an integer!"
    return render_template('add_school.html', form=form,
                        msg=msg, user=user)

@app.route("/add_course", methods=['GET', 'POST'])
def add_course():
    form = AddCourse()
    user = current_user
    msg = ""
    if request.method == "POST":
        db.session.add(Course(int(form.serial.data), form.name.data,
                            form.shortname.data, form.license.data,
                            form.category.data))
        db.session.commit()
        msg = "Course: "+form.name.data+"added successfully!"

    return render_template('add_course.html', form=form, msg=msg, user=user)

@app.route('/me')
@login_required
def home():
    """
    Loads a users home information page
    """
    return render_template('users/templates/profile.html', user=current_user) #not sure current_user works this way, write test

"""
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm(csrf_enabled=False)

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Successful Login!")
            return redirect("/users/me/")
    return render_template("login.html", form=form)
"""
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/login')

@app.route("/report", methods=['GET', 'POST'])
@login_required
def report():
    user = current_user

    all_districts = District.query.order_by("name").all()
    all_schools = School.query.order_by("name").all()
    all_courses = Course.query.order_by("name").all()
    all_sites = Site.query.order_by("sitename").all()

    districts = all_districts
    schools = all_schools
    courses = all_courses

    # Once filters have been applied
    if request.method== "POST":
        form = request.form
        # Check to see if the user wants to see district info
        if request.form['all_districts'] != "None":
        # Getting district related information
            if request.form['all_districts'] != "All":
                districts = District.query.filter_by(name=request.form['filter_districts'])
            for district in districts:
                district.schools = School.query.filter_by(disctrict_id=district.id).order_by("name").all()
                for school in district.schools:
                    school.sites = Site.query.filter_by(school_id=school.id).order_by("name").all()
                    for site in sites:
                        related_courses = session.execute("select course_id where site_id="+site.id+" from sites_courses")
                        site.courses = []
                        site.courses.append(Course.query.get(course))

            districts = None
            # Check to see if the user wanted school information
            if request.form['all_schools'] != "None":
                if request.form['all_schools'] != "All":
                    schools = School.query.filter_by(name=request.form['filter_schools']).order_by("name").all()
                for school in schools:
                    school.sites = Site.query.filter_by(school_id=school.id).order_by("name").all()
                    for site in sites:
                        related_courses = session.execute("select course_id where site_id="+site.id+" from sites_courses")
                        for course in related_courses:
                            # course is the primary key which is used to relate a site's course to a specific course.
                            site.courses.append(Course.query.get(course))
                        for course in site.courses:
                            # Parse information from SiteDetails
                            continue

            else:
                schools = None
                # Check to see if the user wanted course information
                if request.form['all_courses'] != "None":
                    if request.form['all_courses'] != "All":
                        courses = Course.query.filter_by(name=request.form['filter_courses']).order_by("name").all()
                    for course in courses:
                        #Calculate num of users in total
                        continue
                else:
                    return "Error: No filter provided!!"
    else:
        districts = all_districts
        schools = all_schools
        courses = all_courses

    if request.method == "GET":
        dist_count = District.query.count()
        school_count = School.query.count()
        course_count = Course.query.count()
        site_count = SiteDetail.query.count()

    return render_template("report.html", all_districts=all_districts,
                                          all_schools=all_schools,
                                          all_courses=all_courses,
                                          all_sites=all_sites, user=user)


@app.route("/add_user", methods=['GET', 'POST'])
@login_required
def register():
    user = current_user
    form = AddUser()
    message = ""

    if request.method == "POST":
        if form.password.data != form.confirm_pass.data:
            message="The passwords provided did not match!\n"
        elif not re.match('^[a-zA-Z0-9._%-]+@[a-zA-Z0-9._%-]+.[a-zA-Z]{2,6}$', form.email.data):
            message="Invalid email address!\n"
        else:
            #Add user to db
            db.session.add(User(name=form.user.data,
                email = form.email.data, password=form.password.data))

            message = form.user.data+" has been added successfully!\n"

    return render_template('add_user.html', form=form, message=message, user=user)

@app.route("/display/<category>")
def remove(category):
    user = get_user()
    obj = get_obj_by_category(category)
    objects = obj.query.all()
    if objects:
        # fancy way to get the properties of an object
        properties = objects[0].get_properties()
        return render_template('removal.html', category=category, objects=objects, properties=properties, user=user)


@app.route("/remove/<category>", methods=['POST'])
def remove_objects(category):
    obj = get_obj_by_category(category)
    remove_ids = request.form.getlist('remove')
    for remove_id in remove_ids:
        # obj.query returns a list, but should only have one element because
        # ids are unique.
        remove = obj.query.filter_by(id=remove_id)[0]
        db.session.delete(remove)

    db.session.commit()

    return redirect('display/'+category)

@app.route('/install/course', methods=['GET'])
def install_course():

    form = InstallCourse()

    # Get all the available course modules
    all_courses = CourseDetail.query.all()

    # Generate the list of choices for the template
    choices = []

    for course in all_courses:
        choices.append((course.course_id,
                   "%s - Version: %s - Moodle Version: %s" %
                   (course.course.name, course.version, course.moodle_version)))

    form.course.choices = choices

    return render_template('install_course.html', form=form)

@app.route('/install/course/output', methods=['POST'])
def install_course_output():
    """
    Displays the output for any course installs
    """

    # Some needed vars
    wstoken = '13f6df8a8b66742e02f7b3791710cf84'
    wsfunction = 'local_orvsd_create_course'

    # An array of unicode strings will be passed, they need to be integers for the query
    selected_courses = [int(cid) for cid in request.form.getlist('course')]

    # The site to install the courses
    site = "%s/webservice/rest/server.php?wstoken=%s&wsfunction=%s" % (
                request.form.get('site'),
                wstoken,
                wsfunction
            )
    site=str(site.encode('utf-8'))

    # The CourseDetail objects of info needed to generate the url
    courses = CourseDetail.query.filter(CourseDetail.course_id.in_(selected_courses)).all()

    # Appended to buy all the courses being installed
    output = ''

    # Loop through the courses, generate the command to be run, run it, and
    # append the ouput to output
    #
    # Currently this will break ao our db is not setup correctly yet
    for course in courses:
        # To get the file path we need the text input, the lowercase of source, and
        # the filename
        fp = request.form.get('filepath')
        fp = fp if fp.endswith('/') else fp + '/'
        fp += course.source.lower() + '/'

        data = {'filepath': fp,
                'file': course.filename,
                'courseid': course.course_id,
                'coursename': course.course.name,
                'shortname': course.course.shortname,
                'category': '1',
                'firstname': 'orvsd',
                'lastname': 'central',
                'city': 'none',
                'username': 'admin',
                'email': 'a@a.aa',
                'pass': 'testo123'}

        postdata = urllib.urlencode(data)

        resp = urllib.urlopen(site, data=postdata)

        output += "%s\n\n%s\n\n\n" % (course.course.shortname, resp.read())

    return render_template('install_course_output.html', output=output)


def get_obj_by_category(category):
    if category == "District":
        return District
    elif category == "School":
        return School
    elif category == "Site":
        return Site
    elif category == "Course":
        return Course
    else:
        raise Exception('Invalid category: '+category)



