from flask_sqlalchemy import SQLAlchemy
from tkinter import CASCADE
db = SQLAlchemy()


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Show(db.Model):
  __tablename__ = 'show'
  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id',ondelete=CASCADE), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id',ondelete=CASCADE), nullable=False)
  start_time = db.Column('start_time', db.DateTime, nullable=False)
  venue = db.relationship('Venue')
  artist = db.relationship('Artist')

class Venue(db.Model):
    __tablename__ = 'venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(120), nullable=False)
    website_link = db.Column(db.String(500))
    need_talents = db.Column(db.Boolean, nullable=True, default=False)
    talent_description = db.Column(db.String(600), nullable=True)


    # TODO: implement any missing fields, as a database migration using Flask-Migrate --DONE

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120)) 
    website_link = db.Column(db.String(500))
    need_venues = db.Column(db.Boolean, nullable=True, default=False)
    venue_description = db.Column(db.String(600), nullable=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate --DONE

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.