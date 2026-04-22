from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash
from db.connection import getconn
import uuid

events_bp = Blueprint('events', __name__)

# links events search HTML page
@events_bp.route("/events")
def events():
    # conn = None
    # cursor = None

    return render_template('events_search.html')
