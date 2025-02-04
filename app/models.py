from database import db

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    num_courts = db.Column(db.Integer, nullable=False)
    participants_per_court = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    is_closed = db.Column(db.Boolean, default=False)
    courts = db.relationship('Court', backref='reservation', lazy=True)

    def __repr__(self):
        return f"Reservation('{self.title}', '{self.num_courts}', '{self.participants_per_court}')"

class Court(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    court_number = db.Column(db.Integer, nullable=False)
    reservation_id = db.Column(db.Integer, db.ForeignKey('reservation.id'), nullable=False)
    players = db.relationship('Player', backref='court', lazy=True)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    court_id = db.Column(db.Integer, db.ForeignKey('court.id'), nullable=False)