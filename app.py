#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from crypt import methods
from email.policy import default
from encodings import search_function
import json
import re
from urllib import response
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys, os
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
db.init_app(app)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))
    genres = db.Column("genres",db.ARRAY(db.String()), nullable=False)
    seeking_talent = db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.String(200))

    shows_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    #shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
       return f'<Venue {self.id} {self.name}>'
    

    #fat models logics
    @property
    def upcoming_shows(self):
      return list(filter(lambda show: show.start_time >= datetime.utcnow(), self.shows))
    
    @property
    def past_shows(self):
      return list(filter(lambda show: show.start_time < datetime.utcnow(), self.shows))

    @property
    def upcoming_shows_count(self):
      return len(self.upcoming_shows)

    @property
    def past_shows_count(self):
      return len(self.past_shows)





#implementing artist model

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column("genres", db.ARRAY(db.String()), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.String(200))

    shows_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)


    def __repr__(self):
       return f'<Artist {self.id} {self.name}>'

    #implement fat model logics
    @property
    def upcoming_shows(self):
      return list(filter(lambda show: show.start_time >= datetime.utcnow(), self.shows))
    
    @property
    def past_shows(self):
      return list(filter(lambda show: show.start_time < datetime.utcnow(), self.shows))

    @property
    def upcoming_shows_count(self):
      return len(self.upcoming_shows)

    @property
    def past_shows_count(self):
      return len(self.past_shows)
    

class Show(db.Model):
  __tablename__='Show'

  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.relationship('Artist', backref='artist', lazy=True)
  venue_id = db.relationship('Venue', backref='venue', lazy=True)
  start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

  def __repr__(self):
    return f'<Show {self.id}, Artist{self.artist_id}, Venue{self.venue_id}>'

  #implement fat model logics

  @property
  def venue_name(self):
    return self.venue.name

  @property
  def artist_name(self):
    return self.artist.name

  @property
  def artist_image_link(self):
    return self.artist.image_link


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

  #setting empty for storing data

  data=[]

  #retrieve all data related to venues and their respective cities

  venues = Venue.query.all()
  print(venues)

  #linking venues to cities
  venue_cities = set()

  #use loops to set city data
  for venue in venues:
    venue_cities.add((venue.city, venue.state))  #this adds city/state tuples

  #traversing unique address or location and adding venues
  
  for address in venue_cities:
    data.append({
      "state": address[0],
      "city": address[1],
      "venues": []
    })

  #interating to obtain the number of upcoming shows in every venue
  for venue in venues:
    num_upcoming_shows = 0
    shows = Show.query.filter_by(venue_id=venue.id).all()

    #checking show start time

    for show in shows:
      if show.start_time > datetime.now():
        num_upcoming_shows = num_upcoming_shows + 1

    for i in data:
      #i denotes number of entries
      if venue.city == i['city'] and venue.state == i['state']:
        i['venues'].append({
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": num_upcoming_shows
      }) 

  return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  search_item = request.form.get('search_item', '')

  venues = Venue.query.filter(Venue.name.ilike('%s' + '%s')).all()
  venue_data = []

  for venue in venues:
    venue_data.append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": 0, #set as null value

    })
  
  response={
    "count": len(venues),
    "data": venue_data
  }

  return render_template('pages/search_venues.html',\
     results=response, search_item=request.form.get('search_item', ''))

  #try def





@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id

  venue = Venue.query.get(venue_id)
  shows = Show.query.filter_by(venue_id=venue_id)

  #setting venue_data entry

  venue_data = {
    "id": venue.id,
    "name": venue.name,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "genres": venue.genres,
    "city": venue.city,
    "state": venue.state,
    "address": venue.address,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "upcoming_shows": venue.upcoming_shows(shows),
    "past_shows": venue.past_shows(shows),
    "upcoming_shows_count" : len(venue.upcoming_shows(shows)),
    "past_shows_count": len(venue.past_shows(shows))
  }

  return render_template('pages/show_venue.html', venue=venue_data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  
  try:
    #setting form data
    form = VenueForm()
    name = request.form['name']
    phone = request.form['phone']
    facebook_link = request.form['facebook_link']
    website = ""
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    genres = request.form['genres']
    image_link = ""
    seeking_talent = True
    seeking_description = True

    #creating venue db instances

    venue = Venue(name=name, city=city, state=state, address=address,\
      phone=phone, website=website, genres=genres, facebook_link=facebook_link,\
        seeking_description=seeking_description, seeking_talent=seeking_talent,\
          image_link=image_link)

    db.session.add(venue)
    db.session.commit()
    flash('congratulation, Venue' + request.form['name'] + 'was successfully listed ')

  except:
    flash('Sorry, an error occured. Venue'\
       + request.form['name'] + 'could not be listed! Try Again.')
    db.session.rollback()
    print(sys.exc_info())

  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('Venue' + Venue.query.get(venue_id) + 'has been successfully deleted.')

  except:
    flash('Sorry, an erro occurred. Venue' + Venue.query.get(venue_id) + 'could not be deleted')
    db.session.rollback()

  finally:
    db.session.close()
  
  return redirect(url_for('venues'))

  
#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists =Artist.query.all()
  return render_template('pages/artists.html', artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_query = request.form.get(search_query)

  artists = Artist.query.filter(Artist.name.ilike('%s' + search_query + '%s')).all()

  artist_data = []

  #interating artist as  in artists entries

  for a in artists:
    artist_data.append({
      "id": a.id,
      "name": a.name,
      "num-upcoming_shows": 0
    })
  
  response = {
    "count": len(artists),
    "data": artist_data
  }
  return render_template('pages/search_artists.html', results=response, search_query=request.form.get('search_query', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  
  artist = Artist.query.filter_by(id=artist_id).all()

  shows = Show.query.filter_by(artist_id=artist_id).all()

  artist_data ={
    "id": artist.id,
    "name": artist.name,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "address": artist.address,
    "seeking_talent": artist.seeking_talent,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "upcoming_shows": artist.upcoming_shows(shows),
    "past_shows": artist.past_shows(shows),
    "upcoming_shows_count" : len(artist.upcoming_shows(shows)),
    "past_shows_count": len(artist.past_shows(shows))
  }
  
  return render_template('pages/show_artist.html', artist=artist_data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  
  artist = Artist.query.filter_by(id=artist_id).first()

  artist ={
    "id": artist_id,
    "name": artist.name,
    "phone": artist.phone,
    "genres": artist.genres,
    "address": artist.address,
    "city": artist.city,
    "state": artist.state,
    "facebook_link": artist.facebook_link,
    "website": artist.website,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_venue,
    "image_link": artist.image_link
  }

  #populate form with fields from artist with ID<artist_id>

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  try:
    form = ArtistForm()

    artist = Artist.query.fileter_by(id=artist_id).first()

    #insert data from user input

    artist.name = request.form['name']
    artist.phone = request.form['phone']
    artist.website = ""
    artist.image_link = ""
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.address = request.form['address']
    artist.genres = request.form['genres']
    artist.facebook_link = request.form['facebook-link']
    artist.seeking_venue = False
    artist.seeking_description = ""

    db.session.commit()

    flash('Artist' + request.form['name'] + 'has been successfully update.')

  except:
    db.session.rollback()
    flash('Sorry, an error has occurred. Artist' + request.form['name'] + 'failed to update!')

  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  
  venue = Venue.query.filter_by(id=venue_id).all()

  venue_data = {
    "id": venue_id,
    "name": venue.name,
    "phone": venue.phone,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "facebook_link": venue.facebook_link,
    "website": venue.website,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_venue,
    "image_link": venue.image_link
  }

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  try:
    form = VenueForm()

    venue = Venue.query.filter_by(id=venue_id).first()

    #pointing data to venue

    venue.name = request.form['name']
    venue.phone = request.form['phone']
    venue.website = ""
    venue.image_link = ""
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.genres = request.form['genres']
    venue.facebook_link = request.form['facebook-link']
    venue.seeking_talent = True
    venue.seeking_description = ""

    db.session.commit()
    flash('Congratulations, Venue' + request.form['name'] +\
       'has been successfully update')

  except:
    db.session.rollback()
    flash('Sorry, an error occured. Venue' +\
       request.form['name'] + 'could not be updated')

  finally:
    db.session.close()

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
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  try:
    form = VenueForm()
    name = request.form['name']
    phone = request.form['phone']
    facebook_link = request.form['facebook_link']
    website = ""
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    genres = request.form['genres']
    image_link = ""
    seeking_venue = False
    seeking_description = ""

    #creating venue db instances

    artist = Venue(name=name, city=city, state=state, address=address,\
      phone=phone, website=website, genres=genres, facebook_link=facebook_link,\
        seeking_description=seeking_description, seeking_talent=seeking_venue,\
          image_link=image_link)

    db.session.add(artist)
    db.session.commit()
    flash('congratulation, Venue' + request.form['name'] + 'was successfully listed ')

  except:
    flash('Sorry, an error occured. Venue'\
       + request.form['name'] + 'could not be listed.')
    db.session.rollback()
    print(sys.exc_info())

  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.route('/artists/<artist-id>', methods=['DELETE'])
def delete_artist(artist_id):

  try:

    artist = Artist.query.get(artist_id)
    db.session.delete(artist)
    db.session.commit()
    flash('Artist' + Artist.query.get(artist) + 'has been successfully deleted.')

  except:
    flash('sorry, an erro occurred. Artist' + Artist.query.get(artist_id)\
      + 'could not be deleted!')
    db.session.rollback()

  finally:
    db.session.close()

  return redirect(url_for('artist'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  
  data = []

  shows = Show.query.all()

  for show in shows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
      "artist_id": show.artist-id,
      "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
      "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
      "start_time": str(show.start_time)
    })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  try:
    artist_id = request.form['artist']
    venue_id = request.form['venue_id']
    start_time =request.form['start_time']

    #creating a new show
    show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)

    db.session.add(show)
    db.session.commit()

    flash('Show was successfully listed')  #success message

  except:

    db.session.rollback()
    flash('sorry, an error occurred. Show could not be created')

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
