from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.db import get_db
from flaskr.auth import login_required

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db=get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html',posts=posts)


@bp.route('/create',methods=('GET', 'POST'))
def create():
    if request.method=='POST':
        title = request.form['title']
        body = request.form['body']
        errors=[]
        
        ##Validation on title and body
        if title.isspace():
            errors.append("Title can not be empty.")
        if len(title)<3:
            errors.append("Title must be at least 3 characters long.")
        if body.isspace():
            errors.append("Body cannot be empty.")
        if not title:
            errors.append('Title is required')
        if not body:
            errors.append('Body is required')
            
        
        if errors:    
            flash('Posts creation failed:', category='error')
            for error in errors:
                flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO post (title,body,author_id) VALUES(?,?,?)",
                (title,body,g.user['id'])
            )
            db.commit()
            flash("Post created successfully")
            return redirect(url_for('blog.index'))
        
    return render_template('blog/create.html')    

def get_post(id,check_author=True):
    post = get_db().execute(
        "SELECT p.id, p.title, p.body, p. author_id, p.created, u.username"
        " FROM post p JOIN user u ON p.author_id = u.user_id"
        " WHERE p.id = ?",
        (id,)
    ).fetchone()
    
    if post in None:
        abort(404, "Post id {0} doesn't exist.".format(id))
    
    if check_author and post['author_id'] != g.user_id:
        abort(403)
    
    return post

@login_required
@bp.route("/update",methods=["GET","POST"])
def update(id):
    post = get_post(id)
    if request.method == "POST":
        title = request.form['title']
        body = request.form['body']
        errors = []
        
         ##Validation on title and body
        if title.isspace():
            errors.append("Title can not be empty.")
        if len(title)<3:
            errors.append("Title must be at least 3 characters long.")
        if body.isspace():
            errors.append("Body cannot be empty.")
        if not title:
            errors.append('Title is required')
        if not body:
            errors.append('Body is required')
        
        if errors:
            for error in errors:
                flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE post SET title =?, body =? WHERE id =?",
                (title,body,id)
            )
            db.commit()
            return redirect(url_for('blog.index'))
    
    return render_template("blog/update.html",post=post)        


@login_required
@bp.route('/delete',methods=["POST"])
def delete(id):
    post = get_post(id)
    db = get_db()
    db.execute("DELETE FROM post WHERE id =?",(id,))
    db.commit()
    return redirect(url_for('blog.index'))