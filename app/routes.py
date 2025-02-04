from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from wtforms import FormField, SelectField, SubmitField, validators, StringField
from flask_wtf import FlaskForm
from models import Reservation, Court, Player
from database import db
from datetime import datetime, timedelta

app_blueprint = Blueprint('app', __name__)

class ReservationForm(FlaskForm):
    title = StringField('Title', validators=[validators.DataRequired()])
    num_courts = SelectField(
        'Number of Courts',
        choices=[(str(i), str(i)) for i in range(1, 11)],
        validators=[validators.DataRequired()]
    )
    participants_per_court = SelectField(
        'Players per Court',
        choices=[(str(i), str(i)) for i in range(2, 7)],
        validators=[validators.DataRequired()]
    )
    submit = SubmitField('Create')

@app_blueprint.route('/')
def home():
    # Get current date and time
    now = datetime.now()
    today = now.date()
    
    # Query upcoming reservations
    upcoming_reservations = Reservation.query.filter(
        (Reservation.date > today) | 
        ((Reservation.date == today) & (Reservation.start_time > now.time()))
    ).order_by(Reservation.date, Reservation.start_time).all()
    
    return render_template('home.html', upcoming_reservations=upcoming_reservations)

@app_blueprint.route('/create_reservation', methods=['GET', 'POST'])
def create_reservation():
    if request.method == 'POST':
        title = request.form.get('title')
        num_courts = int(request.form.get('num_courts'))
        participants_per_court = int(request.form.get('participants_per_court'))
        date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
        start_time = datetime.strptime(request.form.get('start_time'), '%H:%M').time()
        duration = int(request.form.get('duration'))  # Duration in minutes
        end_time = (datetime.combine(date, start_time) + timedelta(minutes=duration)).time()

        # Create reservation
        reservation = Reservation(
            title=title,
            num_courts=num_courts,
            participants_per_court=participants_per_court,
            date=date,
            start_time=start_time,
            end_time=end_time
        )
        db.session.add(reservation)
        db.session.commit()

        # Create the specified number of courts
        for i in range(1, num_courts + 1):
            court = Court(court_number=i, reservation_id=reservation.id)
            db.session.add(court)

        db.session.commit()  # Commit the courts to the database

        # Redirect to the reservation details page
        return redirect(url_for('app.view_reservation', reservation_id=reservation.id))

    return render_template('create_reservation.html')

@app_blueprint.route('/submit_reservation', methods=['POST'])
def submit_reservation():
    title = request.form.get('title')
    num_courts = int(request.form.get('num_courts'))
    participants_per_court = int(request.form.get('participants_per_court'))
    date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
    start_time = datetime.strptime(request.form.get('start_time'), '%H:%M').time()
    duration = int(request.form.get('duration'))  # Duration in minutes
    end_time = (datetime.combine(date, start_time) + timedelta(minutes=duration)).time()

    # Create reservation
    reservation = Reservation(
        title=title,
        num_courts=num_courts,
        participants_per_court=participants_per_court,
        date=date,
        start_time=start_time,
        end_time=end_time
    )
    db.session.add(reservation)
    db.session.commit()
    return jsonify({'success': True, 'reservation_id': reservation.id})

@app_blueprint.route('/submit_players', methods=['POST'])
def submit_players():
    reservation_id = request.form.get('reservation_id')
    reservation = Reservation.query.get_or_404(reservation_id)
    
    for i in range(1, reservation.num_courts + 1):
        court = Court(court_number=i, reservation_id=reservation_id)
        db.session.add(court)
        db.session.flush()  # Get court ID
        
        for j in range(1, reservation.participants_per_court + 1):
            player_name = request.form.get(f'court_{i}_player_{j}')
            if player_name:
                player = Player(name=player_name, court_id=court.id)
                db.session.add(player)
    
    db.session.commit()
    return redirect(url_for('app.view_reservations'))

@app_blueprint.route('/view_reservations')
def view_reservations():
    reservations = Reservation.query.all()
    return render_template('reservations_list.html', reservations=reservations)

@app_blueprint.route('/reservation/<int:reservation_id>')
def view_reservation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    return render_template('reservation_detail.html', reservation=reservation)

@app_blueprint.route('/reservation/<int:reservation_id>/close', methods=['POST'])
def close_reservation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    reservation.is_closed = True
    db.session.commit()
    return jsonify({'success': True})

@app_blueprint.route('/reservation/<int:reservation_id>/delete', methods=['DELETE'])
def delete_reservation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    
    # Delete related courts and players first
    for court in reservation.courts:
        Player.query.filter_by(court_id=court.id).delete()  # Remove players associated with the court
        db.session.delete(court)  # Delete the court
    
    db.session.delete(reservation)  # Delete the reservation
    db.session.commit()  # Commit the changes
    return jsonify({'success': True})

@app_blueprint.route('/reservation/<int:reservation_id>/add-court', methods=['POST'])
def add_court(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    # Get the highest court number and add 1, or start at 1 if no courts exist
    highest_court = Court.query.filter_by(reservation_id=reservation_id).order_by(Court.court_number.desc()).first()
    new_court_number = (highest_court.court_number + 1) if highest_court else 1
    
    court = Court(court_number=new_court_number, reservation_id=reservation_id)
    reservation.num_courts += 1
    db.session.add(court)
    db.session.commit()
    return jsonify({'success': True})

@app_blueprint.route('/reservation/<int:reservation_id>/update-players', methods=['POST'])
def update_players(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    
    # Clear existing players
    for court in reservation.courts:
        Player.query.filter_by(court_id=court.id).delete()
    
    # Add new players
    for court in reservation.courts:
        court_players = []
        for j in range(1, reservation.participants_per_court + 1):
            player_name = request.form.get(f'court_{court.court_number}_player_{j}')
            if player_name:
                player = Player(name=player_name, court_id=court.id)
                court_players.append(player)
                db.session.add(player)
    
        # If this is the last court and it's full, add a new court
        if (court.court_number == reservation.num_courts and 
            len(court_players) == reservation.participants_per_court and 
            not reservation.is_closed):
            new_court = Court(
                court_number=reservation.num_courts + 1,
                reservation_id=reservation.id
            )
            reservation.num_courts += 1
            db.session.add(new_court)
    
    db.session.commit()
    return redirect(url_for('app.view_reservation', reservation_id=reservation_id))

@app_blueprint.route('/reservation/<int:reservation_id>/remove-court', methods=['DELETE'])
def remove_court(reservation_id):
    court_id = request.args.get('court_id', type=int)
    court = Court.query.get_or_404(court_id)
    
    # Check if court belongs to this reservation
    if court.reservation_id != reservation_id:
        return jsonify({'error': 'Court does not belong to this reservation'}), 403
    
    # Check if court has players
    if len(court.players) > 0:
        return jsonify({'error': 'Cannot remove court with players'}), 400
    
    removed_court_number = court.court_number
    
    # Remove the court
    db.session.delete(court)
    
    # Update the court numbers for remaining courts
    remaining_courts = Court.query.filter(
        Court.reservation_id == reservation_id,
        Court.court_number > removed_court_number
    ).order_by(Court.court_number).all()
    
    for i, court in enumerate(remaining_courts, start=removed_court_number):
        court.court_number = i
    
    # Update reservation court count
    reservation = Reservation.query.get(reservation_id)
    reservation.num_courts -= 1
    
    db.session.commit()
    return jsonify({'success': True})

@app_blueprint.route('/reservation/<int:reservation_id>/update', methods=['POST'])
def update_reservation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    if reservation.is_closed:
        return jsonify({'error': 'Cannot update closed reservation'}), 400
        
    reservation.title = request.form.get('title')
    reservation.date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
    reservation.start_time = datetime.strptime(request.form.get('start_time'), '%H:%M').time()
    reservation.end_time = datetime.strptime(request.form.get('end_time'), '%H:%M').time()
    
    db.session.commit()
    return redirect(url_for('app.view_reservation', reservation_id=reservation_id))

# Error handlers
@app_blueprint.errorhandler(404)
def not_found(error):
    return render_template('error_404.html'), 404

@app_blueprint.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error_500.html'), 500