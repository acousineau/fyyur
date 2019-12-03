from app import db

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    start_time = db.Column(db.DateTime)

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    genres = db.Column(db.String(), nullable=False)
    address = db.Column(db.String(120))
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120), unique=True)
    facebook_link = db.Column(db.String(120), unique=True)
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500), unique=True)

    shows = db.relationship('Show', backref='venue', lazy=True)

    # past_shows: [{
    #   artist_id
    #   artist_name
    #   artist_image_link
    #   start_time
    # }]
    # upcoming_shows: []
    # past_shows_count: 1
    # upcoming_shows_count: 0

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    genres = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120), unique=True)
    facebook_link = db.Column(db.String(120), unique=True)
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500), unique=True)

    shows = db.relationship('Show', backref='artist', lazy=True)

    # past_shows: [{
    #   venue_id
    #   venue_name
    #   venue_image_link
    #   start_time
    # }]
    # upcoming_shows: []
    # past_shows_count: 1
    # upcoming_shows_count: 0
