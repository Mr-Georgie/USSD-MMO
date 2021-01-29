from db import db

class Session(db.Model):
    __tablename__ = 'sessions'  # creating a table name
    
    id = db.Column(db.Integer, primary_key=True)  # this is the primary key
    
    # nullable is false so the column can't be empty
    session_id = db.Column(db.String(80), nullable=False)
    service_code = db.Column(db.Integer, nullable=False)
    phone_number = db.Column(db.String(80), nullable=False)
    serial_number = db.Column(db.String(80), nullable=False)
    bank_name = db.Column(db.String(80), nullable=False)
    account_number = db.Column(db.String(80), nullable=False)
    account_name = db.Column(db.String(80), nullable=False)
    amount = db.Column(db.String(80), nullable=False)
    date = db.Column(db.String(80), nullable=False)
    time = db.Column(db.String(80), nullable=False)
    
    
    def __init__(self, session_id, 
                 service_code, phone_number,
                 serial_number, account_number, 
                 bank_name, account_name, 
                 amount, date, time):
        self.session_id = session_id
        self.service_code = service_code
        self.phone_number = phone_number
        self.serial_number = serial_number
        self.account_number = account_number
        self.bank_name = bank_name
        self.account_name = account_name
        self.amount = amount
        self.date = date
        self.time = time
        
    def json(self):
        return {
            'session_id' : self.session_id,
            'service_code' :self.service_code,
            'phone_number': self.phone_number,
            'serial_number' : self.serial_number,
            'account_number': self.account_number,
            'bank_name' : self.bank_name,
            'account_name' : self.account_name,
            'amount' : self.amount,
            'date' : self.date,
            'time' : self.time
        }   

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()