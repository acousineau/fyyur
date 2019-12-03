#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
from datetime import datetime
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import re
from pprint import pprint

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

migrate = Migrate(app, db)

from models import *

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  venues = Venue.query.all() # do a group by instead?
  modified_venues = []
  for venue in venues:
    # if city/state are part of object in modified_venues
    if any(mv['city'] == venue.city for mv in modified_venues) and any(mv['state'] == venue.state for mv in modified_venues):
      modified_venue = next(mv for mv in modified_venues if mv['city'] == venue.city and mv['state'] == venue.state)
      # add venue to that object
      modified_venue['venues'].append({
        'id': venue.id,
        'name': venue.name,
        'num_upcoming_shows': Show.query
          .filter_by(venue_id=venue.id)
          .filter(Show.start_time > datetime.now())
          .count()
      })
    # else create a new area with that city state combination
    else:
      modified_venues.append({
        'city': venue.city,
        'state': venue.state,
        'venues': [{
          'id': venue.id,
          'name': venue.name,
          'num_upcoming_shows': Show.query
            .filter_by(venue_id=venue.id)
            .filter(Show.start_time > datetime.now())
            .count()
        }]
      })
  return render_template('pages/venues.html', areas=modified_venues)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  base = Venue.query.filter(Venue.name.ilike(f'%{request.form["search_term"]}%'))
  venues = base.all()
  modified_venues = []
  venues_count = base.count()
  for venue in venues:
    modified_venues.append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": Show.query.filter_by(venue_id=venue.id).filter(Show.start_time > datetime.now()).count()
    })
  return render_template('pages/search_venues.html', results={ 'count': venues_count, 'data': modified_venues }, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  modified_genres = venue.genres[1:-1].split(',')
  modified_venue = {
    'id': venue.id,
    'name': venue.name,
    'genres': modified_genres,
    'address': venue.address,
    'city': venue.city,
    'state': venue.state,
    'phone': venue.phone,
    'website': venue.website,
    'facebook_link': venue.facebook_link,
    'seeking_talen': venue.seeking_talent,
    'seeking_description': venue.seeking_description,
    "image_link": venue.image_link
  }
  show_base = Show.query.filter_by(venue_id=venue_id).join('artist')
  past_show_base = show_base.filter(Show.start_time < datetime.now())
  upcoming_show_base = show_base.filter(Show.start_time > datetime.now())
  modified_venue['past_shows_count'] = past_show_base.count()
  modified_venue['upcoming_shows_count'] = upcoming_show_base.count()
  past_shows = past_show_base.all()
  modified_past_shows = []
  upcoming_shows = upcoming_show_base.all()
  modified_upcoming_shows = []

  for show in past_shows:
    modified_past_shows.append({
      'artist_id': show.artist_id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': str(show.start_time),
    })
  for show in upcoming_shows:
    modified_upcoming_shows.append({
      'artist_id': show.artist_id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': str(show.start_time),
    })
  
  modified_venue['past_shows'] = modified_past_shows
  modified_venue['upcoming_shows'] = modified_upcoming_shows
  return render_template('pages/show_venue.html', venue=modified_venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  body = {}
  body['name'] = request.form['name']
  try:
    new_venue = Venue(
      name=request.form['name'],
      city=request.form['city'],
      state=request.form['state'],
      address=request.form['address'],
      phone=request.form['phone'],
      genres=request.form.getlist('genres'),
      facebook_link=request.form['facebook_link'],
      image_link=request.form['image_link']
    )
    db.session.add(new_venue)
    db.session.commit()
    # on successful db insert, flash success
    flash(f'Venue {body["name"]} was successfully listed!')
  except:
    db.session.rollback()
    flash(f'An error occurred. Venue {body["name"]} could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist.query.all()
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  base = Artist.query.filter(Artist.name.ilike(f'%{request.form["search_term"]}%'))
  artists = base.all()
  modified_artists = []
  artists_count = base.count()
  for artist in artists:
    modified_artists.append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": Show.query.filter_by(artist_id=artist.id).filter(Show.start_time > datetime.now()).count()
    })

  return render_template('pages/search_artists.html', results={ 'data': modified_artists, 'count': artists_count }, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  artist = Artist.query.get(artist_id)
  modified_genres = artist.genres[1:-1].split(',')
  modified_artist = {
    'id': artist.id,
    'name': artist.name,
    'genres': modified_genres,
    'city': artist.city,
    'state': artist.state,
    'phone': artist.phone,
    'website': artist.website,
    'facebook_link': artist.facebook_link,
    'seeking_venue': artist.seeking_venue,
    'seeking_description': artist.seeking_description,
    "image_link": artist.image_link
  }
  show_base = Show.query.filter_by(artist_id=artist_id).join('venue')
  past_show_base = show_base.filter(Show.start_time < datetime.now())
  upcoming_show_base = show_base.filter(Show.start_time > datetime.now())
  modified_artist['past_shows_count'] = past_show_base.count()
  modified_artist['upcoming_shows_count'] = upcoming_show_base.count()
  past_shows = past_show_base.all()
  modified_past_shows = []
  upcoming_shows = upcoming_show_base.all()
  modified_upcoming_shows = []

  for show in past_shows:
    modified_past_shows.append({
      'venue_id': show.venue_id,
      'venue_name': show.venue.name,
      'venue_image_link': show.venue.image_link,
      'start_time': str(show.start_time),
    })
  for show in upcoming_shows:
    modified_upcoming_shows.append({
      'venue_id': show.venue_id,
      'venue_name': show.venue.name,
      'venue_image_link': show.venue.image_link,
      'start_time': str(show.start_time),
    })
  
  modified_artist['past_shows'] = modified_past_shows
  modified_artist['upcoming_shows'] = modified_upcoming_shows
  return render_template('pages/show_artist.html', artist=modified_artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with values from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  body = {}
  body['name'] = request.form['name']
  try:
    new_artist = Artist(
      name=request.form['name'],
      city=request.form['city'],
      state=request.form['state'],
      phone=request.form['phone'],
      genres=request.form.getlist('genres'),
      facebook_link=request.form['facebook_link'],
      image_link=request.form['image_link']
    )
    db.session.add(new_artist)
    db.session.commit()
    # on successful db insert, flash success
    flash(f'Artist {body["name"]} was successfully listed!')
  except:
    db.session.rollback()
    flash(f'An error occurred. Artist {body["name"]} could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  shows = Show.query.join('artist').join('venue').all()
  def modify_show(show):
    return {
      'venue_id': show.venue.id,
      'venue_name': show.venue.name,
      'artist_id': show.artist.id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': str(show.start_time)
    }
  modified_shows = map(modify_show, shows)
  return render_template('pages/shows.html', shows=modified_shows)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  try:
    new_show = Show(
      artist_id=request.form['artist_id'],
      venue_id=request.form['venue_id'],
      start_time=request.form['start_time']
    )
    db.session.add(new_show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash(f'An error occurred. Artist {body["name"]} could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
