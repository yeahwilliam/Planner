from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required

from flaskr.db import get_db

from flaskr.planner import get_planner

from datetime import datetime

bp = Blueprint('planner_item', __name__)


@bp.route('/<int:p_id>/myplanner', methods=('GET',))
@login_required
def myplanner(p_id):
    planner = get_planner(p_id)
    db = get_db()
    planner_items = db.execute(
        'SELECT planner_item_id, title, due_date, is_done, notes'
        ' FROM planner_item i JOIN planner p USING (planner_id)'
        ' WHERE p.user_id = ? AND p.planner_id = ?'
        ' ORDER BY due_date', (planner['user_id'], planner['planner_id'])
    ).fetchall()
    return render_template('planner_item/myplanner.html', planner_items=planner_items, planner=planner)


@bp.route('/<int:p_id>/myplanner/newtask', methods=('GET', 'POST'))
@login_required
def create_task(p_id):
    planner = get_planner(p_id)
    if request.method == 'POST':
        title = request.form['title']
        due_date = request.form['due_date']
        is_done = request.form['is_done']
        notes = request.form['notes']
        error = None

        if not title:
            error = 'Title is required.'
        elif not due_date:
            error = 'Due date is required'

        if error is not None:
            flash(error)
        else:
            due_date_obj = datetime.strptime(due_date, '%Y-%m-%dT%H:%M')
            db = get_db()
            db.execute(
                'INSERT INTO planner_item (title, due_date, is_done, notes, planner_id)'
                ' SELECT ?,?,?,?, planner_id FROM planner p JOIN user u ON u.user_id=p.user_id '
                ' WHERE u.user_id=? AND p.planner_id = ?',
                (title, due_date_obj, is_done, notes, g.user['user_id'], p_id)
            )
            db.commit()
            return redirect(url_for('planner_item.myplanner', p_id=planner['planner_id']))

    return render_template('planner_item/newtasks.html', planner=planner)


def get_planner_item(id):
    planner_task = get_db().execute(
        'SELECT planner_item_id, title, due_date, is_done, notes'
        ' FROM planner_item i JOIN planner p USING (planner_id)'
        ' WHERE i.planner_item_id = ? ',
        (id,)
    ).fetchone()

    if planner_task is None:
        abort(404, f"Planner task id {id} doesn't exist.")

    return planner_task


@bp.route('/<int:p_id>/<int:id>/updatetask', methods=('GET', 'POST'))
@login_required
def update_task(p_id, id):
    planner_item = get_planner_item(id)
    planner = get_planner(p_id)
    if request.method == "POST":
        title = request.form['title']
        due_date = request.form['due_date']
        is_done = request.form['is_done']
        notes = request.form['notes']
        error = None

        if not title:
            error = 'Title is required'
        elif not due_date:
            error = 'Due date is required'

        if error is not None:
            flash(error)
        else:
            due_date_obj = datetime.strptime(due_date, '%Y-%m-%dT%H:%M')
            db = get_db()
            db.execute(
                'UPDATE planner_item SET title = ?, due_date = ?, is_done = ?, notes = ?'
                ' WHERE planner_item_id = ?',
                (title, due_date_obj, is_done, notes, planner_item['planner_item_id'])
            )
            db.commit()
            return redirect(url_for('planner_item.myplanner', p_id=planner['planner_id'], id=planner_item['planner_item_id']))

    return render_template('planner_item/updatetasks.html', planner=planner, planner_item=planner_item)


@bp.route('/<int:p_id>/<int:id>/deletetask', methods=('POST',))
@login_required
def delete_task(p_id, id):
    planner = get_planner(p_id)
    planner_item = get_planner_item(id)
    db = get_db()
    db.execute('DELETE FROM planner_item WHERE planner_item_id = ?', (id,))
    db.commit()
    return redirect(url_for('planner_item.myplanner', p_id = planner['planner_id'], id=planner_item['planner_item_id']))
