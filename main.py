from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import datetime
import os

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fleet_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class VehicleData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    speed = db.Column(db.Float, nullable=False)
    steering_angle = db.Column(db.Float, nullable=False)
    force = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return send_from_directory('templates', 'dashboard.html')

@app.route('/update_location', methods=['POST'])
def update_location():
    data = request.json
    lat = data.get('lat')
    lng = data.get('lng')
    speed = data.get('speed')
    steering_angle = data.get('steering_angle')
    force = data.get('force')

    if not (lat and lng and speed and steering_angle and force):
        return jsonify({'status': 'error', 'message': 'Invalid data'}), 400

    new_data = VehicleData(
        lat=lat,
        lng=lng,
        speed=speed,
        steering_angle=steering_angle,
        force=force
    )
    db.session.add(new_data)
    db.session.commit()

    return jsonify({'status': 'success'}), 200

@app.route('/get_data', methods=['GET'])
def get_data():
    data = VehicleData.query.order_by(VehicleData.timestamp.desc()).all()
    result = [{
        'lat': item.lat,
        'lng': item.lng,
        'speed': item.speed,
        'steering_angle': item.steering_angle,
        'force': item.force,
        'timestamp': item.timestamp.isoformat()
    } for item in data]
    return jsonify(result), 200

if __name__ == '__main__':
    app.run(debug=True)
