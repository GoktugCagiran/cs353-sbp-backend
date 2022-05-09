from flask import Flask
from flask_restful import Api
from tmpo.transaction_actions.transaction_actions import Transaction
from tmpo.account_actions.account_actions import Account, CreditCard

app = Flask(__name__)
api = Api(app)

api.add_resource(Transaction, '/transaction/<int:user_id>')
api.add_resource(CreditCard, '/credit_card/<string:card_number>')
api.add_resource(Account, '/accounts/<int:account_id>')