# importing libraries
import os
import requests, json

from flask import Flask, request, Response, jsonify
from flask_mail import Mail, Message

from datetime import datetime
from werkzeug.security import safe_str_cmp

from db import db

from models.sessions import Session
from models.card import Card
from models.error_log import ErrorLog

from functions import validate_card, process_input
from credentials import headers, url, verify, mail_settings
# from bankcodes import bankcodes_alphabetic_order_1,bankcodes_alphabetic_order_2, bank_with_nuban_code

# from flask_bcrypt import Bcrypt

# creating an instance of the flask app
app = Flask(__name__)

#configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL','sqlite:///C:/Users/George/Desktop/build/data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'jose'

app.config.update(mail_settings)
mail = Mail(app)
# bcrypt = Bcrypt(app)

# will be used to send server response to user in text format
response = ""

@app.route('/delete', methods=['POST', 'GET'])
def delete():
    ErrorLog.__table__.drop(db.engine)
    return "deleted"


@app.route('/', methods=['POST', 'GET'])
def ussd_callback():
    global response
    session_id = request.values.get("sessionId", None)
    service_code = request.values.get("serviceCode", None)
    phone_number = request.values.get("phoneNumber", None)
    text = request.values.get("text", None) 
    # The value of text is set to None and not "default" because the cvv will be included in the initial ussd dial code

    try:
        # if the user added to 4 digit cvv to the ussd dial code
        if len(text) == 4:
            response  = "CON Please enter transfer card pin"
        
        # text variable should contain the cvv and the account number by now
        elif len(text) == 15:
            
            # check if card inputted is valid
            response = validate_card(text)
            
            # Continue the session if card is valid
            if response == "CON":
                response = response + " Please input account number"
   
        
        # Choose user bank - Page 1
        elif len(text) == 26:
            
            # check if card inputted is valid
            response = validate_card(text)
            
            # Continue the session if card is valid
            if response == "CON":
                response = response + " Choose bank name \n"
                response += "0. Access Bank\n"
                response += "1. Zenith Bank \n"
                response += "2. UBA \n"
                response += "3. Ecobank Nigeria \n"
                response += "4. Union Bank\n"
                response += "5. GTB \n"
                response += "6. First Bank \n"
                response += "7. FCMB \n"
                response += "8. Wema Bank \n"
                response += "9. Polaris Bank \n"
                response += "#. Next Page >>"
            
        # Choose user bank - Page 2 (if user can't find preferred bank in Page 1)
        elif text.split('*')[3] == "#" and len(text) == 28:
            
            # check if card inputted is valid
            response = validate_card(text)
            
            # Continue the session if card is valid
            if response == "CON":
                response = response + " Choose bank name \n"
                response += "0. Stanbic IBTC Bank \n"
                response += "1. Standard Chartered Bank \n"
                response += "2. Sterling Bank \n"
                response += "3. Enterprise Bank \n"
                response += "4. Fidelity Bank \n"
                response += "5. Keystone Bank \n"
                response += "6. MainStreet Bank \n"
                response += "7. Heritage Bank \n"
                response += "8. Unity Bank \n"
                response += "9. Citibank Nigeria "
            
        # if Page 1 or Page 2
        elif text.split('*')[3] != "#" and len(text) == 28:
            
            # check if card inputted is valid
            response = validate_card(text)
            
            if response == "CON":
            
                ' Get the validated card, receipient account number and bank code ' 
                ' that has been processed by the process_input function'
                card, receipient_account_number, bank_code, bank_name = process_input(text)
                
                # get the card unit as amount
                amount = card.card_unit
                
                # data to be sent to the verification api in json format
                data = {
                            "account_bank": bank_code,
                            "account_number": receipient_account_number
                        }
                
                # send request to verify account number from flutterwave api
                resp = requests.post(verify, headers=headers, data=json.dumps(data))
                # get the response status
                resp_status = json.loads(resp.content)['status']
                # get the response data
                resp_data = json.loads(resp.content)['data']
                
                # if account number verification was successful    
                if resp_status == "success":
                    
                    response = response + " Send ₦{} to {} with account number {} \n".format(amount,resp_data['account_name'],
                                                                                    receipient_account_number)
                    response += "1. Proceed \n"
                    response += "2. Cancel \n"
                else:
                    response = "END Account number and bank name does not match"
                
                
        # if Page 2
        elif text.split('*')[3] == "#" and len(text) == 30:
            
            # check if card inputted is valid
            response = validate_card(text)
            
            if response == "CON":
            
                ' Get the validated card, receipient account number and bank code ' 
                ' that has been processed by the process_input function'
                card, receipient_account_number, bank_code, bank_name = process_input(text)
                
                # get the card unit as amount
                amount = card.card_unit
                
                # data to be sent to the verification api in json format
                data = {
                            "account_bank": bank_code,
                            "account_number": receipient_account_number
                        }
                
                # send request to verify account number from flutterwave api
                resp = requests.post(verify, headers=headers, data=json.dumps(data))
                # get the response status
                resp_status = json.loads(resp.content)['status']
                # get the response data
                resp_data = json.loads(resp.content)['data']
                
                # if account number verification was successful    
                if resp_status == "success":
                    
                    response = response + " Send ₦{} to {} with account number {} \n".format(amount,resp_data['account_name'],
                                                                                    receipient_account_number)
                    response += "1. Proceed \n"
                    response += "2. Cancel \n"
                else:
                    response = "END Account number and bank name does not match"
                
            
        # if Page 1 and user has verified bank account
        elif text.split('*')[3] != "#" and len(text) == 30:
                
            # check if card inputted is valid
            response = validate_card(text)
            
            # put all user input in a list called user_input
            user_input = text.split('*')
            
            # if user chooses not to proceed after bank verification
            if user_input[4] == "2":
                response = "END Successfully cancelled. \n"
                response += "Please try again. Thank you"
            
            if response == "CON":
            
                ' Get the validated card, receipient account number and bank code ' 
                ' that has been processed by the process_input function'
                card, receipient_account_number, bank_code, bank_name = process_input(text)
                
                # get the card unit as amount
                amount = card.card_unit
            
                # data to be sent to the transfer api in json format
                data = {
                        "account_bank": bank_code,
                        "account_number": receipient_account_number,
                        "amount": amount,
                        "narration": "Easy Savings Transfer",
                        "currency": "NGN",
                        "callback_url": "https://e8b5c69aafd1.ngrok.io",
                        "debit_currency": "NGN"
                        }
                
                # send transfer details from data to the transfer api from flutterwave
                resp = requests.post(url, headers=headers, data=json.dumps(data))
                # get response message
                response_message = json.loads(resp.content)['message']
                # get the response status
                resp_status = json.loads(resp.content)['status']
                # get response data
                response_data = json.loads(resp.content)['data']   
                # get account name
                account_name = response_data['full_name']
                
                now = datetime.now() # current date and time
                date = now.strftime("%a %b %d, %Y") 
                time = now.strftime("%I:%M %p")
                
                # if account number verification was successful 
                if resp_status == "success":        
                    response = "END " + response_message + " to " + str(account_name) + "\n"
                    response += "Amount: " + str(response_data['amount']) + "\n"
                    response += "------------------------------------------ \n"
                    response += "Thank you for using Easy Savings Card"
                    complete_session = Session(session_id, service_code,
                                        phone_number, card.serial_number, 
                                        receipient_account_number,
                                        bank_name, account_name, amount,
                                        date, time)
                    complete_session.save_to_db()
                    
                    card.card_used = "True"
                    card.save_to_db()
                    
                else:
                    response = "END " + response_message + "\n"
                    response += "Please try again. We are sorry for any inconvenience"
        
        # if Page 2 and user has verified bank account
        elif text.split('*')[3] == "#" and len(text) == 32:
                
            # check if card inputted is valid
            response = validate_card(text)
            
            # put all user input in a list called user_input
            user_input = text.split('*')
            
            # if user chooses not to proceed after bank verification
            if user_input[4] == "2":
                response = "END Successfully cancelled. \n"
                response += "Please try again. Thank you"
            
            if response == "CON":
            
                ' Get the validated card, receipient account number and bank code ' 
                ' that has been processed by the process_input function'
                card, receipient_account_number, bank_code, bank_name = process_input(text)
                
                # get the card unit as amount
                amount = card.card_unit
            
                # data to be sent to the transfer api in json format
                data = {
                        "account_bank": bank_code,
                        "account_number": receipient_account_number,
                        "amount": amount,
                        "narration": "Easy Savings Transfer",
                        "currency": "NGN",
                        "callback_url": "https://e8b5c69aafd1.ngrok.io",
                        "debit_currency": "NGN"
                        }
                
                # send transfer details from data to the transfer api from flutterwave
                resp = requests.post(url, headers=headers, data=json.dumps(data))
                # get response message
                response_message = json.loads(resp.content)['message']
                # get the response status
                resp_status = json.loads(resp.content)['status']
                # get response data
                response_data = json.loads(resp.content)['data']   
                # get account name
                account_name = response_data['full_name']
                
                now = datetime.now() # current date and time
                date = now.strftime("%a %b %d, %Y") 
                time = now.strftime("%I:%M %p")
                
                # if account number verification was successful 
                if resp_status == "success":        
                    response = "END " + response_message + " to " + str(account_name) + "\n"
                    response += "Amount: " + str(response_data['amount']) + "\n"
                    response += "------------------------------------------ \n"
                    response += "Thank you for using Easy Savings Card"
                    complete_session = Session(session_id, service_code,
                                        phone_number, card.serial_number, 
                                        receipient_account_number,
                                        bank_name, account_name, amount,
                                        date, time)
                    complete_session.save_to_db()
                    
                    card.card_used = "True"
                    card.save_to_db()
                    
                else:
                    response = "END " + response_message + "\n"
                    response += "Please try again. We are sorry for any inconvenience"

            
        return response
    except IndexError as error:
        response = "END An error occurred. Please make sure of the following: \n"
        response += "- The ussd code you dialed is correct \n"
        response += "- The card pin is 10 digits \n"
        response += "- Your account number is 10 digits \n"
        response += "--------------------------------- \n"
        response += "Thank you and try again."
        
        now = datetime.now() # current date and time
        date = now.strftime("%a %b %d, %Y") 
        time = now.strftime("%I:%M %p")
        
        error_msg = ErrorLog(str(error),date,time,phone_number,"User Error")
        error_msg.save_to_db()
        
        return response, 400
        
    except Exception as error:
        response = "END A server error occurred. \n"
        response += "We are sorry for any incovenience this may cause. \n"
        response += "Please try again. Thank you"
      
        now = datetime.now() # current date and time
        date = now.strftime("%a %b %d, %Y") 
        time = now.strftime("%I:%M %p")
       
        error_msg = ErrorLog(str(error),date,time,phone_number,"Server Error")   
        error_msg.save_to_db()
        
        return response, 500


@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    db.init_app(app)
    app.run(port=1234,debug=True)  # important to mention debug=True