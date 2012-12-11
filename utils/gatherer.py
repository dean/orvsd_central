from oursql import connect

# Deiails
user = "siteinfo"
pwrd = "cRzz942"
address = "applegate.orvsd.org"
DEBUG = True

# Connect to gather the db list
con = connect(host=address, user=user, passwd=pwrd)
curs = con.cursor()

# db with siteinfo
db_sites = []

find = "SELECT table_schema, table_name FROM information_schema.tables WHERE table_name = 'siteinfo' OR table_name = 'mdl_siteinfo';"
curs.execute(find)
check = curs.fetchall()

# Done getting stuff from applegate
con.close()

# store the db names and table name in an array to sift through
if len(check):
    for pair in check:
        db_sites.append(pair)

    # Setup a connection to the central db
    central = connect(user='root', host='localhost', db='central')
    c_curs = central.cursor()

    # Do all the works
    for db in db_sites:
        # Grab the site info data
        curs.execute("select * from `%s`;" % db[1])
        data = curs.fetchall()

        # For all the data, shove it into the central db
        for d in data:
           c_curs.execute("INSERT INTO siteinfo (baseurl, basepath, sitename, sitetype, siteversion, siterelease, adminemail, totalusers, adminusers, teachers, activeusers, totalcourses, courses, timemodified) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", d[1:])

    central.close()

