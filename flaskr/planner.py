from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required

from flaskr.db import get_db

import time

import datetime

bp = Blueprint('planner', __name__)


@bp.route('/', methods=('GET',))
@login_required
def list_planners():
    u_id = g.user['user_id']
    db = get_db()
    planners = db.execute(
        'SELECT p.planner_id ,p.planner_name, p.created_date, p.user_id'
        ' FROM planner p JOIN user u USING (user_id)'
        ' WHERE p.user_id = (?)'
        ' ORDER BY p.created_date', (u_id,)
    ).fetchall()
    return render_template('home.html', planners=planners)


@bp.route('/newplanner', methods=('GET', 'POST'))
@login_required
def new_planner():
    if request.method == 'POST':
        planner_name = request.form['planner_name']
        error = None

        if not planner_name:
            error = "Planner name is required"

        if error is not None:
            flash(error)
        else:
            ts = time.time()
            timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            db = get_db()
            db.execute(
                'INSERT INTO planner (planner_name, created_date, user_id)'
                ' SELECT ?,?,?',
                (planner_name, timestamp, g.user['user_id'])
            )
            db.commit()
            return redirect(url_for('planner.list_planners'))

    return render_template('planner/createplanner.html')


def get_planner(id):
    planner = get_db().execute(
        'SELECT planner_id, planner_name, user_id'
        ' FROM planner p JOIN user u USING (user_id)'
        ' WHERE p.planner_id = ?',
        (id,)
    ).fetchone()

    if planner is None:
        abort(404, f"Planner id {id} doesn't exist.")

    return planner


@bp.route('/<int:id>/updateplanner', methods=('GET', 'POST'))
@login_required
def update_planner(id):
    planner = get_planner(id)

    if request.method == "POST":
        planner_name = request.form['planner_name']
        error = None

        if not planner_name:
            error = 'Planner name is required'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE planner SET planner_name = ?'
                ' WHERE planner_id = ?',
                (planner_name, id)
            )
            db.commit()
            return redirect(url_for('planner.list_planners'))

    return render_template('planner/updateplanner.html', planner=planner)


@bp.route('/<int:id>/removeplanner', methods=('POST',))
@login_required
def remove_planner(id):
    get_planner(id)
    db = get_db()
    db.execute('DELETE FROM planner WHERE planner_id = ?', (id,))
    db.commit()
    return redirect(url_for('planner.list_planners'))
