from db import db

class ErrorLog(db.Model):
    __tablename__ = 'errors'  # creating a table name
    
    id = db.Column(db.Integer, primary_key=True)  # this is the primary key
    
    # nullable is false so the column can't be empty
    error_text = db.Column(db.String(80), nullable=False)
    date = db.Column(db.String(80), nullable=False)
    time = db.Column(db.String(80), nullable=False)
    phone_number = db.Column(db.String(80), nullable=False)
    error_type = db.Column(db.String(80), default="Server Error", nullable=False)
    
    
    def __init__(self, error_text, date, time, phone_number, error_type):
        self.error_text = error_text
        self.date = date
        self.time = time
        self.phone_number = phone_number
        self.error_type = error_type
        
    def json(self):
        return {
            'error_text' : self.error_text,
            'date' : self.date,
            'time' : self.time,
            'phone_number': self.phone_number,
            'error_type' : self.error_type
        }   

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()