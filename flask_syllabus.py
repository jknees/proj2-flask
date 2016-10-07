"""
Very simple Flask web site, with one page
displaying a course schedule.

"""

import flask
from flask import render_template
from flask import request
from flask import url_for

import json
import logging

# Date handling 
import arrow # Replacement for datetime, based on moment.js
import datetime # But we still need time
from dateutil import tz  # For interpreting local times

# Our own module
import pre  # Preprocess schedule file


###
# Globals
###
app = flask.Flask(__name__)
import CONFIG


###
# Pages
###

@app.route("/")
@app.route("/index")
@app.route("/schedule")
def index():
  prevWeek = arrow.now().replace(weeks=-1).format('MM/DD/YYYY') #The date as of a week ago
  currentWeek = arrow.now().format('MM/DD/YYYY') #The current date
  app.logger.debug("Main page entry")
  if 'schedule': not in flask.session:
      app.logger.debug("Processing raw schedule file")
      raw = open(CONFIG.schedule)
      flask.session['schedule'] = pre.process(raw)

  return flask.render_template('syllabus.html', currentWeek=currentWeek, prevWeek=prevWeek ) #Sends off the current date and the prev week to help determine the week to highlight.


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    flask.session['linkback'] =  flask.url_for("index")
    return flask.render_template('page_not_found.html'), 404

#################
#
# Functions used within the templates
#
#################

@app.template_filter( 'fmtdate' )
def format_arrow_date( date ):
    try: 
        normal = arrow.get( date )
        return normal.format("ddd MM/DD/YYYY")
    except:
        return "(bad date)"


#############
#    
# Set up to run from cgi-bin script, from
# gunicorn, or stand-alone.
#
app.secret_key = CONFIG.secret_key
app.debug=CONFIG.DEBUG
app.logger.setLevel(logging.DEBUG)
if __name__ == "__main__":
    print("Opening for global access on port {}".format(CONFIG.PORT))
    app.run(port=CONFIG.PORT, host="0.0.0.0")

