#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import sys
from tkinter import CASCADE
import dateutil.parser
import babel
from flask import Flask, render_template, jsonify, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import db, Venue, Show, Artist
import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
#db = SQLAlchemy(app)
db.init_app(app)
migrate = Migrate(app,db)

# TODO: connect to a local postgresql database --DONE

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
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue. --DONE

    # gets the current date time 
    current_date = datetime.datetime.now()

    # gets all unique locations from venue
    locations = db.session.query(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()

    # initialize an empty array object would hold the data to be fed to the view
    data = []

    # looping through the locations
    for location in locations:
      
      # holds the object template
      body = {"city": "", "state": "", "venues":[]}

      # for each location, gets the 'city' and 'state' and inserts into the object template created in 'body' 
      body['city'] = location.city
      body['state'] = location.state

      # gets the venues for each location
      venues = Venue.query.filter_by(state=location.state, city=location.city).all()
      print(venues)
      
      # looping through the venues to get each venue attributes
      for venue in venues:
        
        # gets the upcoming shows for each venue
        upcoming_shows = Show.query.filter_by(venue_id = venue.id).filter(Show.start_time > current_date).all()

        venues = {}
     
        venues["id"] = venue.id
        venues["name"] = venue.name
        venues["num_upcoming_shows"] = len(upcoming_shows)

        body["venues"].append(venues)
      data.append(body)
    #return data
    return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive. --DONE
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  # gets the current date time 
  current_date = datetime.datetime.now()

  # gets the searched word from the form
  search_word = request.form.get('search_term', '')

  # prepares the search word by formatting it
  search = "%{}%".format(search_word)

  # queries the venue table based on the search word
  venues = Venue.query.filter(Venue.name.ilike(search))

  response = {"count": venues.count(), "data": []}

  for venue in venues:

    # gets the upcoming shows for each venue
    upcoming_shows = Show.query.filter_by(venue_id = venue.id).filter(Show.start_time > current_date).all()

    
    response["data"].append({
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": len(upcoming_shows),
        })
  #return response

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id -- DONE

  # gets the current date time 
  current_date = datetime.datetime.now()

  # get the row for the venue id
  venue_info = Venue.query.get(venue_id)

  # data template object for the view consumption 
  body = {
    "id": venue_info.id,
    "name": venue_info.name,
    "genres": venue_info.genres.replace('{','').replace('}','').replace('"','').split(','), # data clean up for the view --removes the unwanted characters and spilt into list
    "address": venue_info.address,
    "city": venue_info.city,
    "state": venue_info.state,
    "phone": venue_info.phone,
    "website": venue_info.website_link,
    "facebook_link": venue_info.facebook_link,
    "seeking_talent": venue_info.need_talents,
    "seeking_description": venue_info.talent_description,
    "image_link": venue_info.image_link,
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": "",
    "upcoming_shows_count": "",
  }


  # gets the upcoming shows for each venue
  upcoming_shows = Show.query.filter_by(venue_id = venue_id).filter(Show.start_time > current_date).all()

  # looping through the upcoming shows
  for show in upcoming_shows:
    upcoming_shows_obj = {}

    upcoming_shows_obj["artist_id"] = show.artist.id
    upcoming_shows_obj["artist_name"] = show.artist.name
    upcoming_shows_obj["artist_image_link"] = show.artist.image_link
    upcoming_shows_obj["start_time"] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S") # converts the datetime to string for the view consumption

    body["upcoming_shows"].append(upcoming_shows_obj)
    body["upcoming_shows_count"] = (str(len(upcoming_shows)))

  # gets the past shows for each venue
  past_shows = Show.query.filter_by(venue_id = venue_id).filter(Show.start_time < current_date).all()
  for show in past_shows:
    past_shows_obj = {}

    past_shows_obj["artist_id"] = show.artist.id
    past_shows_obj["artist_name"] = show.artist.name
    past_shows_obj["artist_image_link"] = show.artist.image_link
    past_shows_obj["start_time"] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")  # converts the datetime to string for the view consumption

    body["past_shows"].append(past_shows_obj)
    body["past_shows_count"] = (str(len(past_shows)))

  data = body
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  # TODO: insert form data as a new Venue record in the db, instead --DONE
  # TODO: modify data to be the data object returned from db insertion --DONE

  # on successful db insert, flash success --DONE
  
  # TODO: on unsuccessful db insert, flash an error instead. --DONE
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.') --DONE
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  error = False
  body = {}
  try:
    print('***Inserting venue record***')

    # creates an instance of the 'Venue' class object
    venue = Venue(name = form.name.data,
                  city = form.city.data,
                  state = form.state.data, 
                  address = form.address.data,
                  phone = form.phone.data, 
                  image_link = form.image_link.data,
                  facebook_link = form.facebook_link.data, 
                  genres = form.genres.data, 
                  website_link = form.website_link.data,
                  need_talents = form.seeking_talent.data, 
                  talent_description = form.seeking_description.data)

    # adds the instance created to the db session and commits/inserts new record to the database              
    db.session.add(venue)
    db.session.commit()

    # computes the JSON object from the commited/inserted venue record
    body['name'] = venue.name
    body['city'] = venue.city
    body['state'] = venue.state
    body['address'] = venue.address
    body['phone'] = venue.phone
    body['image_link'] = venue.image_link
    body['facebook_link'] = venue.facebook_link
    body['genre'] = venue.genres
    body['website_link'] = venue.website_link
    body['seeking_talent'] = venue.need_talents
    body['seeking_description'] = venue.talent_description
  except:
    # in case an error occurs, the error variable is set to True and transaction is rolled back
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    # closes the session
    db.session.close()
  # if there isn't any error, show a success message and branch to homepage
  if not error:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')
   # return jsonify(body)
  # if an error occurs, show the error message and branch to error page
  else:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    abort(500)
    

@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail. --DONE

  venue_info = Venue.query.get(venue_id)
  print(venue_id)
  error = False
  try:
    venue = Venue.query.filter_by(id=venue_id).one()
    db.session.delete(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if not error:
    flash('Venue ' + venue_info.name + ' was successfully deleted!')
    return render_template('pages/home.html')
  else:
    flash('An error occurred. Venue ' + venue_info.name + ' could not be deleted!.')
    abort(500)
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage --DONE
  

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database --DONE

  data = []
  artists = Artist.query.all()
  
  for artist in artists:
    data.append({
      "id": artist.id,
    "name": artist.name,
    })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive. --DONE
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  # gets the current date time 
  current_date = datetime.datetime.now()

  # gets the searched word from the form
  search_word = request.form.get('search_term', '')

  # prepares the search word by formatting it
  search = "%{}%".format(search_word)

  # queries the artist table based on the search word
  artists = Artist.query.filter(Artist.name.ilike(search))

  response = {"count": artists.count(), "data": []}
  for artist in artists:

    # gets the upcoming shows for each artist
    upcoming_shows = Show.query.filter_by(artist_id = artist.id).filter(Show.start_time > current_date).all()

    
    response["data"].append({
          "id": artist.id,
          "name": artist.name,
          "num_upcoming_shows": len(upcoming_shows),
        })
  #return response
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id --DONE

  # gets the current date time 
  current_date = datetime.datetime.now()

  # get the row for the venue id
  artist_info = Artist.query.get(artist_id)

  # data template object for the view consumption 
  body = {
    "id": artist_info.id,
    "name": artist_info.name,
    "genres": artist_info.genres.replace('{','').replace('}','').replace('"','').split(','), # data clean up for the view --removes the unwanted characters and spilt into list
    "city": artist_info.city,
    "state": artist_info.state,
    "phone": artist_info.phone,
    "website": artist_info.website_link,
    "facebook_link": artist_info.facebook_link,
    "seeking_venue": artist_info.need_venues,
    "seeking_description": artist_info.venue_description,
    "image_link": artist_info.image_link,
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": "",
    "upcoming_shows_count": "",
  }


  # gets the upcoming shows for each venue
  upcoming_shows = Show.query.filter_by(artist_id = artist_id).filter(Show.start_time > current_date).all()

  # looping through the upcoming shows
  for show in upcoming_shows:
    upcoming_shows_obj = {}

    upcoming_shows_obj["venue_id"] = show.venue.id
    upcoming_shows_obj["venue_name"] = show.venue.name
    upcoming_shows_obj["venue_image_link"] = show.venue.image_link
    upcoming_shows_obj["start_time"] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S") # converts the datetime to string for the view consumption

    body["upcoming_shows"].append(upcoming_shows_obj)
    body["upcoming_shows_count"] = (str(len(upcoming_shows)))

  # gets the past shows for each venue
  past_shows = Show.query.filter_by(artist_id = artist_id).filter(Show.start_time < current_date).all()
  for show in past_shows:
    past_shows_obj = {}

    past_shows_obj["venue_id"] = show.venue.id
    past_shows_obj["venue_name"] = show.venue.name
    past_shows_obj["venue_image_link"] = show.venue.image_link
    past_shows_obj["start_time"] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")  # converts the datetime to string for the view consumption

    body["past_shows"].append(past_shows_obj)
    body["past_shows_count"] = (str(len(past_shows)))

  data = body
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

   # get the row for the venue id
  artist_info = Artist.query.get(artist_id)

  # data template object for the view consumption 
  body = {
    "id": artist_info.id,
    "name": artist_info.name,
    "genres": artist_info.genres.replace('{','').replace('}','').replace('"','').split(','), # data clean up for the view --removes the unwanted characters and spilt into list
    "city": artist_info.city,
    "state": artist_info.state,
    "phone": artist_info.phone,
    "website": artist_info.website_link,
    "facebook_link": artist_info.facebook_link,
    "seeking_venue": artist_info.need_venues,
    "seeking_description": artist_info.venue_description,
    "image_link": artist_info.image_link,
  }

  form.name.data = artist_info.name
  form.city.data = artist_info.city
  form.state.data = artist_info.state
  form.phone.data = artist_info.phone
  form.image_link.data = artist_info.image_link
  form.facebook_link.data = artist_info.facebook_link
  form.genres.data = artist_info.genres.replace('{','').replace('}','').replace('"','').split(','), # data clean up for the view --removes the unwanted characters and spilt into list
  form.website_link.data = artist_info.website_link
  form.seeking_venue.data = artist_info.need_venues
  form.seeking_description.data = artist_info.venue_description             

  artist = body
  #return artist

  # TODO: populate form with fields from artist with ID <artist_id> --DONE
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing --DONE
  # artist record with ID <artist_id> using the new attributes

  form = ArtistForm(request.form)
  error = False
  artist_info = Artist.query.get(artist_id)
  try:
    print('***Updating Artist record***')

    # updates the artist_info data with the new info changes
    artist_info.name = form.name.data
    artist_info.city = form.city.data
    artist_info.state = form.state.data
    artist_info.phone = form.phone.data 
    artist_info.image_link = form.image_link.data
    artist_info.facebook_link = form.facebook_link.data 
    artist_info.genres = form.genres.data 
    artist_info.website_link = form.website_link.data
    artist_info.need_venues = form.seeking_venue.data 
    artist_info.venue_description = form.seeking_description.data

    # adds the instance created to the db session and commits updated record to the database  
    db.session.commit()
  except:
    # in case an error occurs, the error variable is set to True and transaction is rolled back
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    # closes the session
    db.session.close()
  # if there isn't any error, show a success message and branch to homepage
  if not error:
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
    return redirect(url_for('show_artist', artist_id=artist_id))
  # if an error occurs, show the error message and branch to error page
  else:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated!.')
    abort(500)
    

  

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

   # get the row for the venue id
  venue_info = Venue.query.get(venue_id)

  # data template object for the view consumption 
  body = {
    "id": venue_info.id,
    "name": venue_info.name,
    "genres": venue_info.genres.replace('{','').replace('}','').replace('"','').split(','), # data clean up for the view --removes the unwanted characters and spilt into list
    "address": venue_info.address,
    "city": venue_info.city,
    "state": venue_info.state,
    "phone": venue_info.phone,
    "website": venue_info.website_link,
    "facebook_link": venue_info.facebook_link,
    "seeking_talent": venue_info.need_talents,
    "seeking_description": venue_info.talent_description,
    "image_link": venue_info.image_link,
  }

  form.name.data = venue_info.name
  form.city.data = venue_info.city
  form.state.data = venue_info.state
  form.address.data = venue_info.address
  form.phone.data = venue_info.phone
  form.image_link.data = venue_info.image_link
  form.facebook_link.data = venue_info.facebook_link
  form.genres.data = venue_info.genres.replace('{','').replace('}','').replace('"','').split(','), # data clean up for the view --removes the unwanted characters and spilt into list
  form.website_link.data = venue_info.website_link
  form.seeking_talent.data = venue_info.need_talents
  form.seeking_description.data = venue_info.talent_description             

  venue = body
  #return venue

  # TODO: populate form with values from venue with ID <venue_id> --DONE
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing --DONE
  # venue record with ID <venue_id> using the new attributes 
  form = VenueForm(request.form)
  error = False
  body = {}
  venue_info = Venue.query.get(venue_id)
  try:
    print('***Updating Venue record***')

    # updates the venue_info data with the new info changes
    venue_info.name = form.name.data
    venue_info.city = form.city.data
    venue_info.state = form.state.data 
    venue_info.address = form.address.data
    venue_info.phone = form.phone.data 
    venue_info.image_link = form.image_link.data
    venue_info.facebook_link = form.facebook_link.data 
    venue_info.genres = form.genres.data 
    venue_info.website_link = form.website_link.data
    venue_info.need_talents = form.seeking_talent.data 
    venue_info.talent_description = form.seeking_description.data

    # adds the instance created to the db session and commits updated record to the database  
    db.session.commit()
  except:
    # in case an error occurs, the error variable is set to True and transaction is rolled back
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    # closes the session
    db.session.close()
  # if there isn't any error, show a success message and branch to homepage
  if not error:
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
    return redirect(url_for('show_venue', venue_id=venue_id))
  # if an error occurs, show the error message and branch to error page
  else:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated!.')
    abort(500)
    

  

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead --DONE
  # TODO: modify data to be the data object returned from db insertion --DONE

  # on successful db insert, flash success 
  # TODO: on unsuccessful db insert, flash an error instead. --DONE
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')

  # variables initialization
  error = False
  body = {}
  try:
    print('***Inserting artist record***')

    # creates an instance of the 'Artist' class object
    artist = Artist(name = form.name.data,
                    city = form.city.data,
                    state = form.state.data,
                    phone = form.phone.data, 
                    image_link = form.image_link.data,
                    facebook_link = form.facebook_link.data, 
                    genres = form.genres.data, 
                    website_link = form.website_link.data,
                    need_venues = form.seeking_venue.data, 
                    venue_description = form.seeking_description.data)

    # adds the instance created to the db session and commits/inserts new record to the database               
    db.session.add(artist)
    db.session.commit()

    # computes the JSON object from the commited/inserted artist record
    body['name'] = artist.name
    body['city'] = artist.city
    body['state'] = artist.state
    body['phone'] = artist.phone
    body['image_link'] = artist.image_link
    body['facebook_link'] = artist.facebook_link
    body['genre'] = artist.genres
    body['website_link'] = artist.website_link
    body['seeking_venue'] = artist.need_venues
    body['seeking_description'] = artist.venue_description
  except:
    # in case an error occurs, the error variable is set to True and transaction is rolled back
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    # closes the session
    db.session.close()
  # if there isn't any error, show a success message and branch to homepage
  if not error:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')
   # return jsonify(body)
  # if an error occurs, show the error message and branch to error page
  else:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    abort(500)

  


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data. --DONE
  data =[]
  shows = Show.query.all()
  for show in shows:
    
    data.append({
      "venue_id" : show.venue_id,
      "venue_name" : show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link" : show.artist.image_link,
      "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    })

 
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm(request.form)
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead --DONE

  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead. --DONE
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  #return render_template('pages/home.html')
  error = False
  try:
    print('***Inserting show record***')

    print('venue id: ' + form.venue_id.data)
    print('artist id: ' + form.artist_id.data)

    # converts the string input to integer
    venue_id = int(form.venue_id.data)
    artist_id = int(form.artist_id.data)

    show = Show(
    venue_id = venue_id,
    artist_id = artist_id,
    start_time = form.start_time.data
    ) 
    # adds the instance created to the db session and commits/inserts new record to the database              
    db.session.add(show)
    db.session.commit()
  except:
    # in case an error occurs, the error variable is set to True and transaction is rolled back
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    # closes the session
    db.session.close()
  # if there isn't any error, show a success message and branch to homepage
  if not error:
    flash('Show was successfully listed!')
    return render_template('pages/home.html')
  # if an error occurs, show the error message and branch to error page
  else:
    flash('An error occurred.Show could not be listed.')
    abort(500)
    


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
    //port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0')
'''
