from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

class Sensor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    value = db.Column(db.Integer)

    network_id = db.Column(db.Integer, db.ForeignKey('network.id'))
    added = db.Column(db.DateTime)

    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.added = datetime.datetime.now()
    
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'value': self.value,
            'added': self.added
        }

class Network(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    sensors = db.relationship('Sensor', backref='network', lazy=True)

    def __init__(self, name):
        self.name = name
    