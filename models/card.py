from db import db

class Card(db.Model):
    __tablename__ = 'cards'  # creating a table name
    
    id = db.Column(db.Integer, primary_key=True)  # this is the primary key
    
    # nullable is false so the column can't be empty
    serial_number = db.Column(db.String(80), nullable=False, unique=True)
    card_pin = db.Column(db.String(80), nullable=False)
    cvv = db.Column(db.Integer, nullable=False)
    card_unit = db.Column(db.Integer, nullable=False)
    card_used = db.Column(db.String(80), default="False", nullable=False)
    
    def __init__(self, serial_number, card_pin, cvv, card_unit, card_used):
        self.serial_number = serial_number
        self.card_pin = card_pin
        self.cvv = cvv
        self.card_unit = card_unit
        self.card_used = card_used
        
    def json(self):
        return {
            'serial_number' : self.serial_number,
            'card_pin' :self.card_pin,
            'cvv': self.cvv,
            'card_unit': self.card_unit,
            'card_used' :self.card_used
        }   
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
        
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
