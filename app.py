from flask import Flask
from flask_restful import Api
from actions.transaction_actions.transaction_actions import DepositingTransaction, WithdrawingTransaction
from actions.account_actions.account_actions import Account, CreditCard
from actions.bet_actions.bet_actions import Bet, BetSlip, MonetizedBetSlip
from actions.team_actions.team_actions import Team, TeamBase, Player


app = Flask(__name__)
api = Api(app)

api.add_resource(DepositingTransaction, '/depositing_transaction/<int:account_id>')
api.add_resource(WithdrawingTransaction, '/withdrawing_transaction/<int:account_id>')
api.add_resource(CreditCard, '/credit_card/<int:account_id>')
api.add_resource(Account, '/accounts/<int:account_id>')
api.add_resource(Team, '/teams/<int:team_id>')
api.add_resource(TeamBase, '/team_bases/<int:team_id>')
api.add_resource(Player, '/players/<int:player_id>')
api.add_resource(Bet, '/bets/<int:bet_id>')
api.add_resource(BetSlip, '/bet_slips/<int:bet_slip_id>')
api.add_resource(MonetizedBetSlip, '/monetized_bet_slips/<int:monetized_bet_slip_id>')

if __name__ == '__main__':
    app.run(debug=True)