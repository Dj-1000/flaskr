import functools, re
from flask import (
    Blueprint,flash,g,redirect,render_template,request,session,url_for, Response, jsonify,json, 
)
from werkzeug.security import check_password_hash,generate_password_hash
from flask_httpauth import HTTPBasicAuth
from flaskr.db import get_db

bp = Blueprint('auth',__name__,url_prefix='/auth')
auth = HTTPBasicAuth()
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method=="POST":
        username = request.form['username']
        password = request.form['password']
        errors = []
        if username.isspace():  # Check if name consists only of spaces
            errors.append('Username cannot be empty spaces only.') 
            
        if password.isspace():  # Check if password consists only of spaces
            errors.append('Password cannot be empty spaces only.')
        db = get_db()
        
        
        if not username:
            errors.append('Username is required.')
        elif not password:
            errors.append('Password is required.')
            
        if len(username) < 3:
            errors.append('Username must be at least 3 characters long')
            
        # Regex for allowed characters: alphanumeric, underscore, and period
        username_regex = r'^[a-zA-Z0-9_.]+$'
        if not re.match(username_regex, username):
            errors.append('Username can only contain letters, numbers, underscores (_), and periods (.)')
        
        if errors:    
            flash('Registration failed:', category='error')
            for error in errors:
                flash(error)
        else:
            try:
                db.execute(
                    "INSERT INTO user (username,password) VALUES (?,?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
                flash('Registration successful!', category='success')
            except db.IntegrityError as e:
                error=f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))
        
    return render_template('auth/register.html')
        
        
        
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(f"username: {username} password: {password}")
        db = get_db()
        error = None
        user = db.execute(
            "SELECT * FROM user WHERE username = ?",(username,)
        ).fetchone()
        
        
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'],password):
            error = "Incorrect password."
        
        if error is None:
            session.clear()
            print("USER_ID :",user['id'])
            session["user_id"] = user['id']
            return redirect(url_for("index"))
        
        flash(error)
        # return jsonify({
        #     "error_message": error
        # }) , 200
        
    return render_template("auth/login.html")     
        

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")
    
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            "SELECT * FROM user WHERE id = ?",(user_id,)
        ).fetchone()
        
        
@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))



def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))
        
        return view(**kwargs)
    return wrapped_view
