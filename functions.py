import hashlib
from models.card import Card
from bankcodes import bankcodes_alphabetic_order_1,bankcodes_alphabetic_order_2, bank_with_nuban_code
# from credentials import headers, url, verify, mail_settings

salt = '$2b$12'

def validate_card(text_input):
    
    # create a list of all user inputted data
    split_input = text_input.split('*')
    
    cvv = split_input[0] # get the cvv from user input
    card_pin = split_input[1] # get the card pin from user input
    
    # compare the hashed pin with the pin in the database
    card_hashed = hashlib.blake2s((card_pin+salt).encode()).hexdigest()
    
    card = Card.query.filter_by(card_pin=card_hashed).first()
    
    if card is None:
        response = "END The card you entered is invalid"
    elif card.card_used == "True":
        response = "END This card has already been used."
    elif card and str(card.cvv) != cvv:    
        response = "END The card pin you entered is not correct.\n"
        response += "Please confirm card pin and redial"
    else:
        response = "CON"
    
    return response


def process_input(text_input):
    # create a list of all user inputted data
    split_input = text_input.split('*')
    
    receipient_acc_num = split_input[2] # inputted account number
    if split_input[3] == "#":
        receipient_bank = split_input[4] # index for inputted bank name
        bank_name = bankcodes_alphabetic_order_2[receipient_bank] # get bank name by index from dict
    else:
        receipient_bank = split_input[3] # index for inputted bank name
        bank_name = bankcodes_alphabetic_order_1[receipient_bank] # get bank name by index from dict
    
    bank_code = bank_with_nuban_code[bank_name] # get bank code with bank name from dict
    
    cvv = split_input[0] # get the cvv from user input
    card_pin = split_input[1] # get the card pin from user input
    
    # compare the hashed pin with the pin in the database
    card_hashed = hashlib.blake2s((card_pin+salt).encode()).hexdigest()
    
    card = Card.query.filter_by(card_pin=card_hashed).first()
    
    return card, receipient_acc_num, bank_code, bank_name