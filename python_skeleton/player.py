'''
Simple example pokerbot, written in Python.
'''
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot

import random
import eval7


class Player(Bot):
    '''
    A pokerbot.
    '''

    def __init__(self):
        '''
        Called when a new game starts. Called exactly once.

        Arguments:
        Nothing.

        Returns:
        Nothing.
        '''
        # Store hand strength as [win_percentage, range_percentile]
        # win_percentage: % chance to win against random hand (84.90 = wins 84.90% of the time)
        # range_percentile: position in range (0.6 = top 0.6% of hands, 100 = bottom 100%)
        self.hand_strength = {
            # Pocket Pairs
            'AA': [84.90, 0.6], 'KK': [82.10, 1.2], 'QQ': [79.60, 1.8], 'JJ': [77.10, 2.4], 'TT': [74.70, 3.0],
            '99': [71.70, 3.6], '88': [68.70, 4.1], '77': [65.70, 4.7], '66': [62.70, 5.3], '55': [59.60, 5.9],
            '44': [56.30, 6.5], '33': [52.90, 7.1], '22': [49.30, 7.7],

            # Suited Hands
            'AKs': [66.20, 8.3], 'AQs': [65.40, 8.9], 'AJs': [64.40, 9.5], 'ATs': [63.40, 10.1], 'A9s': [61.40, 10.7], 'A8s': [60.30, 11.2], 'A7s': [59.10, 11.8], 'A6s': [57.80, 12.4], 'A5s': [57.70, 13.0], 'A4s': [56.70, 13.6], 'A3s': [55.90, 14.2], 'A2s': [55.00, 14.8],
            'KQs': [62.40, 15.4], 'KJs': [61.40, 16.0], 'KTs': [60.40, 16.6], 'K9s': [58.40, 17.2], 'K8s': [56.40, 17.8], 'K7s': [55.40, 18.3], 'K6s': [54.30, 18.9], 'K5s': [53.30, 19.5], 'K4s': [52.30, 20.1], 'K3s': [51.40, 20.7], 'K2s': [50.50, 21.3],
            'QJs': [59.10, 21.9], 'QTs': [58.10, 22.5], 'Q9s': [56.10, 23.1], 'Q8s': [54.20, 23.7], 'Q7s': [52.10, 24.3], 'Q6s': [51.30, 24.9], 'Q5s': [50.20, 25.4], 'Q4s': [49.30, 26.0], 'Q3s': [48.40, 26.6], 'Q2s': [47.50, 27.2],
            'JTs': [56.20, 27.8], 'J9s': [54.20, 28.4], 'J8s': [52.30, 29.0], 'J7s': [50.30, 29.6], 'J6s': [48.30, 30.2], 'J5s': [47.50, 30.8], 'J4s': [46.50, 31.4], 'J3s': [45.70, 32.0], 'J2s': [44.70, 32.5],
            'T9s': [52.40, 33.1], 'T8s': [50.40, 33.7], 'T7s': [48.40, 34.3], 'T6s': [46.50, 34.9], 'T5s': [44.50, 35.5], 'T4s': [43.70, 36.1], 'T3s': [42.80, 36.7], 'T2s': [42.00, 37.3],
            '98s': [48.90, 37.9], '97s': [46.90, 38.5], '96s': [44.90, 39.1], '95s': [42.90, 39.6], '94s': [40.90, 40.2], '93s': [40.30, 40.8], '92s': [39.40, 41.4],
            '87s': [45.70, 42.0], '86s': [43.70, 42.6], '85s': [41.70, 43.2], '84s': [39.70, 43.8], '83s': [37.80, 44.4], '82s': [37.20, 45.0],
            '76s': [42.90, 45.6], '75s': [40.90, 46.2], '74s': [38.90, 46.7], '73s': [37.00, 47.3], '72s': [35.10, 47.9],
            '65s': [40.30, 48.5], '64s': [38.30, 49.1], '63s': [36.40, 49.7], '62s': [34.40, 50.3],
            '54s': [38.50, 50.9], '53s': [36.50, 51.5], '52s': [34.50, 52.1],
            '43s': [35.70, 52.7], '42s': [33.70, 53.3],
            '32s': [33.10, 53.8],

            # Offsuit Hands
            'AKo': [64.50, 54.4], 'AQo': [63.70, 55.0], 'AJo': [62.70, 55.6], 'ATo': [61.70, 56.2], 'A9o': [59.70, 56.8], 'A8o': [58.60, 57.4], 'A7o': [57.40, 58.0], 'A6o': [56.10, 58.6], 'A5o': [56.00, 59.2], 'A4o': [55.00, 59.8], 'A3o': [54.20, 60.4], 'A2o': [53.30, 60.9],
            'KQo': [60.50, 61.5], 'KJo': [59.50, 62.1], 'KTo': [58.50, 62.7], 'K9o': [56.50, 63.3], 'K8o': [54.50, 63.9], 'K7o': [53.50, 64.5], 'K6o': [52.40, 65.1], 'K5o': [51.40, 65.7], 'K4o': [50.40, 66.3], 'K3o': [49.50, 66.9], 'K2o': [48.60, 67.5],
            'QJo': [57.00, 68.0], 'QTo': [56.00, 68.6], 'Q9o': [54.00, 69.2], 'Q8o': [52.10, 69.8], 'Q7o': [50.10, 70.4], 'Q6o': [49.30, 71.0], 'Q5o': [48.20, 71.6], 'Q4o': [47.30, 72.2], 'Q3o': [46.40, 72.8], 'Q2o': [45.50, 73.4],
            'JTo': [53.80, 74.0], 'J9o': [51.80, 74.6], 'J8o': [49.90, 75.1], 'J7o': [47.90, 75.7], 'J6o': [45.90, 76.3], 'J5o': [45.10, 76.9], 'J4o': [44.10, 77.5], 'J3o': [43.30, 78.1], 'J2o': [42.30, 78.7],
            'T9o': [49.80, 79.3], 'T8o': [47.80, 79.9], 'T7o': [45.80, 80.5], 'T6o': [43.90, 81.1], 'T5o': [41.90, 81.7], 'T4o': [41.10, 82.2], 'T3o': [40.20, 82.8], 'T2o': [39.40, 83.4],
            '98o': [46.10, 84.0], '97o': [44.10, 84.6], '96o': [42.10, 85.2], '95o': [40.10, 85.8], '94o': [38.10, 86.4], '93o': [37.50, 87.0], '92o': [36.60, 87.6],
            '87o': [42.70, 88.2], '86o': [40.70, 88.8], '85o': [38.70, 89.3], '84o': [36.70, 89.9], '83o': [34.80, 90.5], '82o': [34.20, 91.1],
            '76o': [39.70, 91.7], '75o': [37.70, 92.3], '74o': [35.70, 92.9], '73o': [33.80, 93.5], '72o': [31.90, 94.1],
            '65o': [37.00, 94.7], '64o': [35.00, 95.3], '63o': [33.10, 95.9], '62o': [31.10, 96.4],
            '54o': [35.10, 97.0], '53o': [33.10, 97.6], '52o': [31.10, 98.2],
            '43o': [32.10, 98.8], '42o': [30.10, 99.4],
            '32o': [29.30, 100.0]
        }
        # Track opponent tendencies
        self.opponent_stats = {
            'preflop_raise_count': 0,
            'total_hands': 0,
            'fold_to_3bet': 0,
            'three_bet_opportunities': 0
        }

    def handle_new_round(self, game_state, round_state, active):
        '''
        Called when a new round starts. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        my_bankroll = game_state.bankroll  # the total number of chips you've gained or lost from the beginning of the game to the start of this round
        game_clock = game_state.game_clock  # the total number of seconds your bot has left to play this game
        round_num = game_state.round_num  # the round number from 1 to NUM_ROUNDS
        my_cards = round_state.hands[active]  # your cards
        big_blind = bool(active)  # True if you are the big blind
        my_bounty = round_state.bounties[active]  # your current bounty rank
        pass

    def handle_round_over(self, game_state, terminal_state, active):
        '''
        Called when a round ends. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        terminal_state: the TerminalState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        my_delta = terminal_state.deltas[active]  # your bankroll change from this round
        previous_state = terminal_state.previous_state  # RoundState before payoffs
        street = previous_state.street  # 0, 3, 4, or 5 representing when this round ended
        my_cards = previous_state.hands[active]  # your cards
        opp_cards = previous_state.hands[1-active]  # opponent's cards or [] if not revealed
        opponent_bounty = terminal_state.bounty_hits # True if opponent hit bounty

    def get_action(self, game_state, round_state, active):
        '''
        Where the magic happens - your code should implement this function.
        Called any time the engine needs an action from your bot.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Your action.
        '''
        # Get basic info
        street = round_state.street  # 0, 3, 4, or 5 representing pre-flop, flop, turn, or river respectively
        my_cards = round_state.hands[active]  # your cards
        board_cards = round_state.deck[:street]  # the board cards
        opp_pip = round_state.pips[1-active]  # the number of chips your opponent has contributed to the pot this round of betting
        my_stack = round_state.stacks[active]  # the number of chips you have remaining
        opp_stack = round_state.stacks[1-active]  # the number of chips your opponent has remaining
        my_pip = round_state.pips[active]  # the number of chips you have contributed to the pot this round of betting

        continue_cost = opp_pip - my_pip  # the number of chips needed to stay in the pot
        my_bounty = round_state.bounties[active]  # your current bounty rank
        my_contribution = STARTING_STACK - my_stack  # the number of chips you have contributed to the pot
        opp_contribution = STARTING_STACK - opp_stack  # the number of chips your opponent has contributed to the pot
        legal_actions = round_state.legal_actions()  # the actions you are allowed to take
        street = round_state.street
        my_cards = round_state.hands[active]
   
        
        
        # Evaluate hand strength
        if street == 0:  # Preflop
            hand_value = self.evaluate_preflop_hand(my_cards, my_bounty)
        else:
            board_cards = round_state.deck[:street]
            hand_value = self.evaluate_hand(my_cards, board_cards, my_bounty)
        
        
        # Calculate pot odds
        if (continue_cost + opp_pip + my_pip) > 0:
            pot_odds = continue_cost / (continue_cost + opp_pip + my_pip)
        else:
            pot_odds = 1
        
        # Basic preflop strategy
        if street == 0:
            if RaiseAction in legal_actions:
                min_raise, max_raise = round_state.raise_bounds()
                # If we're small blind (button)
                if not bool(active):  # active == 0 means small blind
                    if hand_value > 65:  # Premium hand
                        return RaiseAction(min(max_raise, int(2.5 * BIG_BLIND)))
                # If we're big blind
                else:
                    if continue_cost > 0:  # Facing a raise
                        if hand_value > 75:  # Very strong hand
                            return RaiseAction(min(max_raise, int(4.4 * continue_cost)))
                        elif hand_value > 60:  # Decent hand
                            return CallAction()
            
            elif CheckAction in legal_actions:
                return CheckAction()
            
            elif CallAction in legal_actions and hand_value > 50:
                return CallAction()
            
            return FoldAction()
        
        if street >= 1: #flop
            if RaiseAction in legal_actions:
                min_raise, max_raise = round_state.raise_bounds()
                if hand_value > 80:
                    return RaiseAction(min(max_raise, int(3/4*(opp_pip + my_pip))))
                elif hand_value > 65:
                    return RaiseAction(min(max_raise, 1/2*(opp_pip + my_pip)))
            elif CheckAction in legal_actions:
                return CheckAction()
            
            elif CallAction in legal_actions:
                if hand_value > 55:
                    return CallAction()
            
            else:
                return FoldAction()


            

    def evaluate_hand(self, hole_cards, community_cards, bounty_rank):
        print(f'{hole_cards=}, {community_cards=}')
        deck = hole_cards + community_cards
        deck = [eval7.Card(card) for card in deck]
        base_strength = eval7.evaluate(deck)
        bounty_multiplier = 1.5 if bounty_rank in [card[0] for card in hole_cards + community_cards] else 1.0
        return base_strength * bounty_multiplier 

    def evaluate_preflop_hand(self, cards, bounty_rank):
        """
        Evaluates preflop hand strength considering bounty
        Returns win percentage adjusted for bounty cards
        """
        # Sort cards by rank for easier comparison
        ranks = sorted([card[0] for card in cards], reverse=True)
        suited = cards[0][1] == cards[1][1]  # Check if cards share the same suit
        
        # Construct hand key (e.g., 'AKs' or 'AKo')
        hand_key = ''.join(ranks) + ('s' if suited else 'o')
        
        # Get base strength [win_percentage, range_percentile]
        # Default to [30.0, 99.0] for unmapped hands (slightly better than worst hand)
        base_stats = self.hand_strength.get(hand_key, [30.0, 99.0])
        win_percentage = base_stats[0]
        
        # Bounty multiplier if we have bounty card
        if bounty_rank in ranks:
            win_percentage *= 1.2  # Increase win percentage by 20% with bounty card
        
        return win_percentage 


if __name__ == '__main__':
    run_bot(Player(), parse_args())
    
