from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    db = get_db()
    posts = db.execute("""
        SELECT  
            p.id, p.title, p.body, p.created, p.author_id, u.username
        FROM
            post p INNER JOIN user u 
            ON p.author_id = u.id
        ORDER BY p.created DESC            
    """).fetchall()

    return render_template('index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
def create():
    if request.method != 'POST':
        return render_template('create.html')

    title = request.form['title']
    body = request.form['body']
    error = None

    if not title:
        error = 'You must have a title'
    if error is not None:
        flash(error)
        return render_template('create.html')

    db = get_db()
    db.execute("""
        INSERT INTO 
            post (title, body, author_id)
        VALUES 
            (?, ?, ?)       
    """, (title, body, g.user['id'])
               )
    db.commit()

    return redirect(url_for('blog.index'))


def get_post(id, check_author=True):
    post = get_db().execute("""
        SELECT 
            p.id, title, body, created, author_id, username
        FROM post p INNER JOIN user u
        ON p.author_id = u.id
        WHERE p.id = ?
    """, (id,)).fetchone()

    if post is None:
        abort(404, f'No post with id {id} exists')
    if post['author_id'] != g.user['id']:
        abort(403, 'You may not edit someone else\'s post')

    return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
def update(id):

    post = get_post(id)
    if request.method != 'POST':
        return render_template('update.html', post=post)

    title = request.form['title']
    body = request.form['body']
    error = None
    if title is None:
        error = "You must provide a title"

    if error is not None:
        flash(error)
        return render_template('update.html')

    db = get_db()
    db.execute("""
        UPDATE post
        SET title = ?, body = ?
        WHERE id = ?
    """, (title, body, id))
    db.commit()
    return redirect(url_for('blog.index'))


@bp.route('/<int:id>/delete', methods=('POST',))
# @login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))
