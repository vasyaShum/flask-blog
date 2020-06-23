from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from blog.auth import login_required
from blog.db import get_db


bp = Blueprint('site', __name__)


def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, text, date, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()
    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))
    if check_author and post['author_id'] != g.user['id']:
        abort(403)
    return post


@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, text, date, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY date DESC'
    ).fetchall()

    return render_template('site/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        text = request.form['text']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, text, author_id)'
                ' VALUES (?, ?, ?)',
                (title, text, g.user['id'])
            )
            db.commit()
            return redirect(url_for('site.index'))

    return render_template('site/create.html')


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        text = request.form['text']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, text = ?'
                ' WHERE id = ?',
                (title, text, id)
            )
            db.commit()
            return redirect(url_for('site.index'))

    return render_template('site/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('GET',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('site.index'))