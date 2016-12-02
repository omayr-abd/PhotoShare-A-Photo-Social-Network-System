######################################
# author: Omayr Abdelgany
#		  omaaa@bu.edu
#		  U54298732
######################################
# Some code adapted from 
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask.ext.login as flask_login
import datetime

#for image uploading
from werkzeug import secure_filename
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'wtfidget7120'
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users") 
users = cursor.fetchall()

def getUserList():
	cursor = conn.cursor()
	cursor.execute("SELECT email from Users") 
	return cursor.fetchall()

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	users = getUserList()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0] )
	user.is_authenticated = request.form['password'] == pwd 
	return user

'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
	#The request method is POST (page is recieving data)
	email = flask.request.form['email']
	cursor = conn.cursor()
	#check if email is registered
	if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		pwd = str(data[0][0] )
		if flask.request.form['password'] == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) #okay login in user
			return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file

	#information did not match
	return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"

@app.route('/logout')
def logout():
	flask_login.logout_user()
	return render_template('hello.html', message='Logged out') 

@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html') 

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
	return render_template('register.html', supress='True')  

@app.route("/register", methods=['POST'])
def register_user():
	email=request.form.get('email')
	password=request.form.get('password')
	firstname=request.form.get('firstname')
	lastname=request.form.get('lastname')
	DOB=request.form.get('DOB')
	hometown=request.form.get('hometown')
	gender=request.form.get('gender')

	if not email:
		print "couldn't find all tokens"
		return flask.redirect(flask.url_for('register'))
	if not password:
		print "couldn't find all tokens"
		return flask.redirect(flask.url_for('register'))
	if not firstname:
		print "couldn't find all tokens"
		return flask.redirect(flask.url_for('register'))
	if not lastname:
		print "couldn't find all tokens"
		return flask.redirect(flask.url_for('register'))
	if not DOB:
		print "couldn't find all tokens"
		return flask.redirect(flask.url_for('register'))

#	if not validate(DOB):
#		print "date format incorrect"
#		return flask.redirect(flask.url_for('register'))
	
	if email:
		cursor = conn.cursor()
		test =  isEmailUnique(email)
		if test:
			print cursor.execute("INSERT INTO Users (email, password, firstname, lastname, DOB, hometown, gender) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}')".format(email, password, firstname, lastname, DOB, hometown, gender))
			conn.commit()
			#log user in
			user = User()
			user.id = email
			flask_login.login_user(user)
			return render_template('hello.html', name=email, message='Account Created!')
	
		else:
			print "email already taken"
			return flask.redirect(flask.url_for('register'))
	

def getUsersPhotos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]

def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]
 
def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)): 
		#this means there are greater than zero entries with that email
		return False
	else:
		return True
	#end login code
	
def validate(date_text):
	if datetime.datetime.strptime(date_text, '%Y-%m-%d'):
		return True
	else:
		return False


def getUserbaseEmail():
	cursor=conn.cursor()
	cursor.execute("SELECT email FROM USERS")
	return cursor.fetchall()
	
def getUserbaseId():
	cursor=conn.cursor()
	cursor.execute("SELECT user_id FROM USERS")
	return cursor.fetchall()
	
def getUserEmailFromId(id):
	cursor = conn.cursor()
	cursor.execute("SELECT email FROM Users WHERE user_id ="+str(id))
	return cursor.fetchone()[0]
	
def getUserFriendsList(id):
	cursor = conn.cursor()
	cursor.execute("SELECT user2 FROM Friends where user1= '{0}'".format(id))
	return cursor.fetchall()
	
def getUserFriendsListEmail(id):
	cursor = conn.cursor()
	cursor.execute("SELECT email FROM (Users, Friends) WHERE user_id = user2 AND user1= '{0}'".format(id))
	return cursor.fetchall()
	
def getUserAlbums(id):
	cursor = conn.cursor()
	cursor.execute("SELECT album_id FROM Albums where owner_id= '{0}'".format(id))
	return cursor.fetchall()

def getUserAlbumNames(id):
	cursor = conn.cursor()
	cursor.execute("SELECT name FROM Albums where owner_id= '{0}'".format(id))
	return cursor.fetchall()
	
def getAlbumPhotos(a_id):
	cursor = conn.cursor()
	cursor.execute("SELECT P.imgdata, P.picture_id, P.caption FROM (Pictures P, Album_Contents A) WHERE A.album_id = '{0}' AND P.picture_id = A.picture_id".format(a_id))
	return cursor.fetchall() 
	
def getAlbumName(a_id):
	cursor = conn.cursor()
	cursor.execute("SELECT name FROM Albums WHERE album_id= '{0}'".format(a_id))
	return cursor.fetchone()[0]
	
def getPhotoName(p_id):
	cursor = conn.cursor()
	cursor.execute("SELECT caption FROM Pictures WHERE picture_id= '{0}'".format(p_id))
	return cursor.fetchone()[0]
	
def getPhotoOwner(p_id):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id FROM Pictures WHERE picture_id= '{0}'".format(p_id))
	return cursor.fetchone()[0]
	
#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		imgfile = request.files['photo']
		caption = request.form.get('caption')
		album_name = request.form.get('album')
		print caption
		photo_data = base64.standard_b64encode(imgfile.read())
		cursor = conn.cursor()
		cursor.execute("SET FOREIGN_KEY_CHECKS=0")
		cursor.execute("INSERT INTO Pictures (imgdata, user_id, caption) VALUES ('{0}', '{1}', '{2}' )".format(photo_data, uid, caption))
		cursor.execute("SELECT picture_id FROM Pictures WHERE imgdata = '{0}' AND user_id = '{1}' AND caption = '{2}'".format(photo_data, uid, caption))
		p_id = cursor.fetchone()[0]
		cursor.execute("SELECT COUNT(*) FROM Albums WHERE owner_id = '{0}' AND name = '{1}'".format(uid, album_name))
		result = cursor.fetchone()[0]
		if (result < 1):
			cursor.execute("INSERT INTO Albums (owner_id, name, date_of_creation) VALUES ('{0}', '{1}', '{2}')".format(uid, album_name,datetime.datetime.today().strftime('%Y-%m-%d')))
		cursor.execute("SELECT album_id FROM Albums WHERE owner_id = '{0}' AND name = '{1}' AND date_of_creation = '{2}'".format(uid, album_name, datetime.datetime.today().strftime('%Y-%m-%d')))
		a_id = cursor.fetchone()[0]
		cursor.execute("INSERT INTO Album_Contents (album_id, picture_id) VALUES ('{0}', '{1}')".format(a_id, p_id))
		cursor.execute("SET FOREIGN_KEY_CHECKS=1")
		conn.commit()
		return render_template('album.html', name=album_name, aid = a_id, message='Photo uploaded!', photos=getAlbumPhotos(a_id))
	#The method is GET so we return a  HTML form to upload the a photo.
	else:
		return render_template('upload.html')
#end photo uploading code 


#default page  
@app.route("/", methods=['GET'])
def hello():
	return render_template('hello.html', message='Welecome to Photoshare')
	
@app.route('/profile')
@flask_login.login_required
def protected():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	albums=getUserAlbums(uid)
	albumnames = getUserAlbumNames(uid)
	friendNums = getUserFriendsList(uid)
	friendEmails = getUserFriendsListEmail(uid)
	return render_template('profile.html', name=flask_login.current_user.id, message="Your profile:", fullalbum = zip(albums,albumnames), friends = zip(friendNums,friendEmails))

@app.route('/user/<int:id>')
def other_user(id):
	if (flask_login.current_user.is_authenticated):
		if (id == getUserIdFromEmail(flask_login.current_user.id)):
			return protected()
	albums=getUserAlbums(id)
	albumnames = getUserAlbumNames(id)
	friendNums = getUserFriendsList(id)
	friendEmails = getUserFriendsListEmail(id)
	return render_template('other_user.html', user_id = id, name=getUserEmailFromId(id), fullalbum = zip(albums,albumnames), friends = zip(friendNums,friendEmails))
	
@app.route('/userbase')
def userbase():
	ids = getUserbaseId()
	emails=getUserbaseEmail()
	return render_template('userbase.html', url=zip(ids,emails))
	
@app.route('/added/<int:id>')
@flask_login.login_required
def addFriend(id):
	uid1 = getUserIdFromEmail(flask_login.current_user.id)
	cursor=conn.cursor()
	cursor.execute("SELECT COUNT(*) FROM Friends WHERE user1 = '{0}' AND user2 = '{1}'".format(uid1, id))
	result = cursor.fetchone()[0]
	if (result>0):
		return render_template('hello.html', message = "User is already your friend!")
	cursor.execute("INSERT INTO Friends(user1, user2) VALUES ('{0}', '{1}')".format(uid1, id))
	cursor.execute("INSERT INTO Friends(user1, user2) VALUES ('{0}', '{1}')".format(id, uid1))
	conn.commit()
	return render_template('other_user.html', user_id = id, name=getUserEmailFromId(id), message = 'Friend added!', albums=getUserAlbums(id) )

@app.route('/deletePhoto/<int:pid>')
@flask_login.login_required
def deletePhoto(pid):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor=conn.cursor()
	cursor.execute("SELECT caption FROM Pictures where picture_id = '{0}'".format(pid))
	caption = cursor.fetchone()[0]
	cursor.execute("SELECT user_id FROM pictures WHERE picture_id = '{0}'".format(pid))
	picture_owner = cursor.fetchone()[0]
	if (picture_owner == uid):
		cursor.execute("DELETE FROM album_contents WHERE picture_id = '{0}'".format(pid))
		cursor.execute("DELETE FROM pictures WHERE picture_id = '{0}' AND user_id = '{1}'".format(pid, uid))
		conn.commit()
		return render_template('deletePhotoSuccess.html')
	else:
		return render_template('deletePhotoFailure.html')
		
@app.route('/deleteAlbum/<int:aid>')
@flask_login.login_required
def deleteAlbum(aid):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor=conn.cursor()
	cursor.execute("SELECT owner_id FROM albums WHERE album_id = '{0}'".format(aid))
	album_owner = cursor.fetchone()[0]
	if (album_owner == uid):
		cursor.execute("SELECT picture_id FROM album_contents WHERE album_id = '{0}'".format(aid))
		pics = cursor.fetchall()
		cursor.execute("DELETE FROM album_contents WHERE album_id = '{0}'".format(aid))
		cursor.execute("DELETE FROM albums WHERE album_id = '{0}'".format(aid))
		for p in pics:
			cursor.execute("DELETE FROM pictures WHERE picture_id = '{0}'".format(p))
		conn.commit()
		return render_template('deleteAlbumSuccess.html')
	else:
		return render_template('deleteAlbumFailure.html')

@app.route('/album/<int:a_id>')
def album(a_id):
	return render_template('album.html', name=getAlbumName(a_id), aid = a_id, photos=getAlbumPhotos(a_id))

@app.route('/like/<int:p_id>')
@flask_login.login_required	
def like(p_id):
	u_id = getUserIdFromEmail(flask_login.current_user.id)
	cursor=conn.cursor()
	cursor.execute("SELECT COUNT(*) FROM Likes WHERE user_id = '{0}' AND picture_id = '{1}'".format(u_id, p_id))
	result = cursor.fetchone()[0]
	if (result > 0):
		return render_template('likeError.html')
	cursor.execute("INSERT INTO Likes(user_id, picture_id) VALUES ('{0}', '{1}')".format(u_id, p_id))
	cursor.execute("SELECT user_id FROM Likes WHERE picture_id = '{0}'".format(p_id))
	userids = cursor.fetchall()
	cursor.execute("SELECT email FROM Users INNER JOIN Likes ON Users.user_id = Likes.user_id WHERE Likes.picture_id = '{0}'".format(p_id))
	users = cursor.fetchall()
	cursor.execute("SELECT imgdata FROM Pictures WHERE picture_id = '{0}'".format(p_id))
	likedphoto = cursor.fetchall()
	conn.commit();
	return render_template('likes.html', message = "You have liked this photo!", name=getPhotoName(p_id), likedby = zip(userids, users), photo = likedphoto)
	
@app.route('/likes/<int:p_id>')	
def likes(p_id):
	cursor=conn.cursor()
	cursor.execute("SELECT user_id FROM Likes WHERE picture_id = '{0}'".format(p_id))
	userids = cursor.fetchall()
	cursor.execute("SELECT email FROM Users INNER JOIN Likes ON Users.user_id = Likes.user_id WHERE Likes.picture_id = '{0}'".format(p_id))
	users = cursor.fetchall()
	cursor.execute("SELECT imgdata FROM Pictures WHERE picture_id = '{0}'".format(p_id))
	likedphoto = cursor.fetchall()
	return render_template('likes.html', name=getPhotoName(p_id), likedby = zip(userids, users), photo = likedphoto)
	
@app.route('/comments/<int:p_id>')	
def comments(p_id):
	cursor=conn.cursor()
	cursor.execute("SELECT owner_id FROM Comments WHERE picture_id = '{0}'".format(p_id))
	userids = cursor.fetchall()
	cursor.execute("SELECT email FROM Users INNER JOIN Comments ON Users.user_id = Comments.owner_id WHERE Comments.picture_id = '{0}'".format(p_id))
	useremails = cursor.fetchall()
	cursor.execute("SELECT text FROM Comments WHERE picture_id = '{0}'".format(p_id))
	#comments = cursor.fetchall()
	return render_template('comments.html', comments = cursor.fetchall())

	
@app.route('/comment/<int:p_id>', methods=['GET', 'POST'])
def comment(p_id):
	if request.method == 'POST':
		if (flask_login.current_user.is_authenticated):
			u_id = getUserIdFromEmail(flask_login.current_user.id)
			if (getPhotoOwner(p_id) == u_id):
				return render_template('commentsError.html')
		text = request.form.get('text')
		if (flask_login.current_user.is_authenticated):
			u_id = getUserIdFromEmail(flask_login.current_user.id)
			print cursor.execute("INSERT INTO Comments(owner_id, picture_id, text, dateofcomment) VALUES ('{0}', '{1}', '{2}', '{3}')".format(u_id, p_id, text, datetime.datetime.today().strftime('%Y-%m-%d')))
		else:
			anonymous = User()
			anonymous.user_id=0
			#flask_login.login_user(anonymous)
			cursor.execute("SET FOREIGN_KEY_CHECKS=0")
			print cursor.execute("INSERT INTO Comments(owner_id, picture_id, text, dateofcomment) VALUES ('{0}', '{1}', '{2}', '{3}')".format(anonymous.user_id, p_id, text, datetime.datetime.today().strftime('%Y-%m-%d')))
			#flask_login.logout_user(anonymous)
			cursor.execute("SET FOREIGN_KEY_CHECKS=1")
		conn.commit()
		return render_template('hello.html', message = "Comment posted!")
	else:
		return render_template('leaveAComment.html', p_id=p_id)
	
@app.route('/tags/<int:p_id>')			
def tags (p_id):
	cursor=conn.cursor()
	cursor.execute("SELECT tag FROM Tags WHERE picture_id = '{0}'".format(p_id))
	return render_template('tags.html', tags = cursor.fetchall())
	
@app.route('/tag/<int:p_id>', methods=['GET', 'POST'])
@flask_login.login_required			
def tag (p_id):
	if request.method == 'POST':
		cursor=conn.cursor()
		tag = request.form.get('tag')
		
		cursor.execute("SELECT COUNT(*) FROM Tags WHERE tag = '{0}' AND picture_id = '{1}'".format(tag, p_id))
		result = cursor.fetchone()[0]
		if (result > 0):
			return render_template('tagError.html')
		else:
			print cursor.execute("INSERT INTO Tags(picture_id, tag) VALUES ('{0}', '{1}')".format(p_id, tag))
			conn.commit()
			return render_template('hello.html', message = "Tag added!")
	else:
		return render_template('EnterATag.html', p_id=p_id)
		
@app.route('/tagPage/<string:tag>')
def tagPage(tag):
	cursor=conn.cursor()
	cursor.execute("SELECT P.imgdata, P.picture_id, P.caption FROM (Pictures P, Tags T) WHERE T.tag = '{0}' AND P.picture_id = T.picture_id".format(tag))
	return render_template('tagPage.html', tag=tag, photos=cursor.fetchall())

@app.route('/tagPageUser/<string:tag>')
@flask_login.login_required	
def tagPageUser(tag):
	cursor=conn.cursor()
	u_id = getUserIdFromEmail(flask_login.current_user.id)
	cursor.execute("SELECT P.imgdata, P.picture_id, P.caption FROM (Pictures P, Tags T) WHERE T.tag = '{0}' AND P.picture_id = T.picture_id AND p.user_id = {1}".format(tag,u_id))
	return render_template('tagPage.html', tag=tag, photos=cursor.fetchall())
		
		
		
		
if __name__ == "__main__":
	#this is invoked when in the shell  you run 
	#$ python app.py 
	app.run(port=5000, debug=True)
