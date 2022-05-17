from flask import Flask
from flask_restful import Resource, Api
from flask_cors import CORS
from blueprints.auth.blueprint_authentication import blueprint_authentication
from blueprints.scratch_off.blueprint_scratch_off import blueprint_scratch_off
from blueprints.admin.blueprint_admin import blueprint_admin
from actions.account_actions.account_actions import Account, CreditCard
from actions.team_actions.team_actions import Team, TeamBase, Player
from actions.game_actions.game_actions import Game, League
from actions.bet_actions.bet_actions import Bet, BetSlip, MonetizedBetSlip
from actions.transaction_actions.transaction_actions import DepositingTransaction, WithdrawingTransaction
from blueprints.roulette.blueprint_roulette import blueprint_roulette
from blueprints.sharable.blueprints_sharable import blueprint_sharable
from blueprints.reward.blueprint_reward import blueprint_reward
app = Flask(__name__)
api = Api(app)
CORS(app)

api.add_resource(Game, '/game/<int:game_id>')
api.add_resource(League, '/league/<int:league_id>')
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


app.register_blueprint(blueprint_authentication)
app.register_blueprint(blueprint_scratch_off)
app.register_blueprint(blueprint_admin)
app.register_blueprint(blueprint_roulette)
app.register_blueprint(blueprint_reward)
app.register_blueprint(blueprint_sharable)

if __name__ == "__main__":
    app.run(debug=True)
    print('name == __main__')


