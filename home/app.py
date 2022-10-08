#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
#\DTapp.config('SQLALCHEMY_DATABASE_URI')='postgresql://postgres:admin@localhost:5432/example'
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:12345@localhost:5432/fyyur'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
migrate=Migrate(app,db)
class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    location=db.Column(db.String(100))
    seeking_talent=db.Column(db.Boolean,default=True)
    seeking_description=db.Column(db.String(40))
    description=db.Column(db.String(500))
    num_upcoming_shows=db.Column(db.Integer,default=0)
    shows=db.relationship('Show',backref='Venue',lazy=False)
class Artist(db.Model):
    __tablename__ = 'Artist'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    age=db.Column(db.Integer)
    description=db.Column(db.String(500))
    seeking_venue=db.Column(db.Boolean,default=True)
    seeking_description=db.Column(db.String(40))
    shows=db.relationship('Show',backref='Artist',lazy=False)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    date=db.Column(db.DateTime,nullable=False)
    youtube_link=db.Column(db.String(50),unique=True)
    venue_id=db.Column(db.Integer,db.ForeignKey('Venue.id'))
    artist_id=db.Column(db.Integer,db.ForeignKey('Artist.id'))
    venue_name=db.Column(db.Integer,db.ForeignKey('Venue.name'))
    artist_name=db.Column(db.Integer,db.ForeignKey('Artist.name'))
    artist_image_link=db.Column(db.Integer,db.ForeignKey('Artist.image_link'))
    venue_image_link=db.Column(db.Integer,db.ForeignKey('Venue.image_link'))
    start_time=db.Column(db.DateTime,nullable=False)
    past_shows_count=db.Column(db.DateTime)
 
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
    data=[]
    venues=Venue.query.distinct(Venue.state,Venue.city).all()
    for num in venues:
        venue_shows=db.session.query(Venue).filter(Venue.state==num.state,               Venue.city==num.city).all()
        city_state={
          'city':num.city,
          'state':num.state
        }
        venue_details=[]
        for ven in venue_shows:
              venue_details.append({
                'id':ven.id,
                'name':ven.name,
                  'num_upcoming_shows':len(Venue.shows.filter(Show.start_time>DateTime.now).all())
              })
        city_state['venues']=venue_details
        data.append(city_state)
    return render_template('pages/venues.html', areas=data)
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term=request.form.get('search_term', '')
    results=Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
    data=[]
    for result in results:
        data.append({'id': result.id,
               'name': result.name,
               'num_upcoming_shows': result.num_upcoming_shows})
    results_count=len(results)
    response={
    'count':results_count,
    'data':data
    }
    return render_template('pages/search_venues.html', results=response, 
search_term=request.form.get('search_term', ''))
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
   
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue_info=Venue.query.get(venue_id)
    past_shows=[]
    past_shows.append({
    'artist_id':venue_info.shows.artist_id,
    'artist_name':venue_info.shows.artist_name,
    'artist_image_link':venue_info.shows.artist_image_link,
    'start_time':venue_info.shows.start_time
    })
    upcoming_show=[]
    upcoming_show.append({
    'Upcoming_shows':venue_info.shows.name
    })
    data={
    'id':venue_info.id,
    'name':venue_info.name,
    'genres':venue_info.genres,
    'address':venue_info.address,
    'city':venue_info.city,
    'state':venue_info.state,
    'phone':venue_info.phone,
    'website':venue_info.website,
    'facebook_link':venue_info.facebook_link,
    'seeking_talent':venue_info.seeking_talent,
    'seeking_description':venue_info.seeking_description,
    'image_link':venue_info.image_link,
    'past_shows': past_show,
    'upcoming_shows': upcoming_show,
    'past_shows_count':venue_info.shows.past_shows_count,
    'upcoming_shows_count':venue_info.shows.upcoming_shows_count
  }
    return render_template('pages/show_venue.html', venue=data)
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
 # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    try:
        new_venue_details=Venue(
        name=request.form['name'],
        city=request.form['city'],
        state=request.form['state'],
        address=request.form['address'],
        phone=request.form['phone'],
        image_link=request.form['image_link'],
        facebook_link=request.form['facebook_link'],
        location=request.form['location'],
        description=request.form['description'],
        )
        db.session.add(new_venue_details)
        db.session.commit()
    # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        print(sys.exc_info)
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')
  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    venue_id=Venue.query.get(venue_id)
    try:
        db.session.query(Venue).filter(Venue.id==venue_id).delete()
        db.session.commit()
        flash('Venue ' + venue_id + ' was successfully deleted!')
    except:
        db.session.rollback()
        print(sys.exc_info)
        flash('An error occurred. Venue ' + venue_id + ' could not be deleted.')
    finally:
        db.session.close()
    return None  
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    data=[]
    for artist in Artist.query.all():
        data.append({
            'id':artist.id,
            'name':artist.name
          })
    return render_template('pages/artists.html', artists=data)
  # TODO: replace with real data returned from querying the database
@app.route('/artists/search', methods=['POST'])
def search_artists():
    search=request.form['search_term']
    search_results=Artist.query.filter(Artist.name.ilike('%' +search+ '%'))
    info=[]
    for each_search in search_results:
        info.append({
          'id': each_search.id,
          'name':each_search.name,
          'num_upcoming_shows': len(each_search.shows.filter(Show.date>DateTime.now).all())
          })
    response={
    'count':len(search_results),
    'data': info
  }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist_info=Artist.query.get(artist_id)
    past_shows=[]
    past_shows.append({
      'venue_id':artist_info.shows.venue_id,
      'venue_name':artist_info.shows.venue_name,
      'venue_image_link':artist_info.shows.venue_image_link,
      'start_time':artist_info.shows.start_time
    })
    upcoming_show=[]
    upcoming_show.append({
    'Upcoming_shows':artist_info.shows.name
  })
    data={
    'id':artist_info.id,
    'name':artist_info.name,
    'genres':artist_info.genres,
    'address':artist_info.address,
    'city':artist_info.city,
    'state':artist_info.state,
    'phone':artist_info.phone,
    'website':artist_info.website,
    'facebook_link':artist_info.facebook_link,
    'seeking_talent':artist_info.seeking_talent,
    'seeking_description':artist_info.seeking_description,
    'image_link':artist_info.image_link,
    'past_shows': past_shows,
    'upcoming_shows': upcoming_show,
    'past_shows_count':artist_info.shows.past_shows_count,
    'upcoming_shows_count':artist_info.shows.upcoming_shows_count
  }
    return render_template('pages/show_artist.html', artist=data)
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  
 # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm(request.form)
    artist_id=request.args.get('artist_id')
    db.session.query(Artist).get(artist_id)
    artist={
   "id": Artist.id,
    "name": Artist.name,
    "genres": Artist.genres,
    "city": Artist.city,
    "state": Artist.state,
    "phone": Artist.phone,
    "website": Artist.website,
    "facebook_link": Artist.facebook_link,
    "seeking_venue": Artist.seeking_venue,
    "seeking_description": Artist.seeking_description,
    "image_link": Artist.image_link
  } 
    return render_template('forms/edit_artist.html',form=form,artist=artist)
@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    artist_id=Artist.query.get(artist_id)
    try:
        artist=db.session.query(Artist).filter(Artist.id==artist_id).all()
        artist.name=request.form['name']
        artist.state=request.form['state']
        artist.phone=request.form['phone']
        artist.genres=request.form['genres']
        artist.image_link=request.form['image_link']
        artist.facebook_link=request.form['facebook_link']
        artist.age=request.form['age']
        artist.description=request.form['description']
        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + artist_id + ' was successfully Updated!')
    except:
        db.session.rollback()
        print(sys.exc_info)
        flash('An error occurred. Artist ' + artist_id + ' could not be edited.')
    finally:
        db.session.close()
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
    return redirect(url_for('show_artist', artist_id=artist_id))
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm(request.form)
    venue_datails=Venue.query.get(venue_id)
    form.name.data=venue_details['name']
    form.genres.data=venue_details['genres']
    form.address.data=venue_details['address']
    form.city.data=venue_details['city']
    form.state.data=venue_details['state']
    form.phone.data=venue_details['phone']
    form.website.data=venue_details['website']
    form.facebook_link.data=venue_details['facebook_link']
    form.seeking_talent.data=venue_details['seeking_talent']
    form.seeking_description.data=venue_details['seeking_description']
    form.image_link.data=venue_details['image_link']

  # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form=VenueForm(request.form)
    venue_info=Venue.query.get(venue_id)
    if form.validate():
        try:
            venue_info.name=form.name.data
            venue_info.genres=form.genres.data
            venue_info.address=form.address.data
            venue_info.city=form.city.data
            venue_info.state=form.state.data
            venue_info.phone=form.phone.data
            venue_info.website=form.website.data
            venue_info.facebook_link=form.facebook_link.data
            venue_info.image_link=form.image_link.data
            db.session.add(venue_info)
            db.session.commit()
            flash('Venue ' + venue_id + ' was successfully edited!')
        except:
            db.session.rollback()
            print(sys.exc_info)
            flash('An error occurred. Venue ' + venue_id + ' could not be edited.')
        finally:
            db.session.close()
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
    try:
        artist=Artist(
        name=request.form['name'],
        genres=request.form['genres'],
        city=request.form['city'],
        state=request.form['state'],
        phone=request.form['phone'],
        website=request.form['website'],
        image_link=request.form['image_link'],
        facebook_link=request.form['facebook_link'])
        db.session.add(artist)
        db.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        print(sys.exc_info)
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()
    return render_template('pages/home.html')
         
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
 
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')



#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    shows=db.session.query(Show).all()
    data=[]
    for show in shows:
        data.append({
            'venue_id':show.venue_id,
            'venue_name':show.venue_name,
            'artist_id':show.artist_id,
            'artist_name':show.artist_name,
            'artist_image_link':show.artist_image_link,
            'start_time':show.start_time
            })
    return render_template('pages/shows.html', shows=data)
  # displays list of shows at /shows
  # TODO: replace with real venues data.

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    try:
        show=Show(
        name=request.form['name'],
        date=request.form['date'],
        youtube_link=request.form['youtube_link'],
        venue_id=request.form['venue_id'],
        artist_id=request.form['artist_id'],
        venue_name=request.form['venue_name'],
        artist_name=request.form['artist_name'],
        artist_image_link=request.form['artist_image_link'],
        start_time=request.form['start_time'])
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
    except:
        db.session.rollback()
        print(sys.exc_info)
        flash('An error occurred. Show could not be listed.')
    finally:
        db.session.close()
    return render_template('pages/home.html')
      
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

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
    app.run(host='0.0.0.0', port=port,debug=True)
'''
