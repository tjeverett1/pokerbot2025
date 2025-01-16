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
import numpy as np
import sys


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
        # Store hand strength as [win_percentage, absolute_rank, range_percentile]
        # absolute_rank: 1-169 (1 = best, 169 = worst)
        # range_percentile: position in range (0.6 = top 0.6% of hands, 100 = bottom 100%)
        self.hand_strength = {
            # Premium hands
            'AA': [84.90, 1, 0.59],     'KK': [82.10, 2, 1.18],     'QQ': [79.60, 3, 1.77],     'AKs': [66.20, 4, 2.37],
            'JJ': [77.10, 5, 2.96],     'AQs': [65.40, 6, 3.55],    'KQs': [62.40, 7, 4.14],    'AJs': [64.40, 8, 4.73],
            'KJs': [61.40, 9, 5.33],    'TT': [74.70, 10, 5.92],    'AKo': [64.50, 11, 6.51],   'ATs': [63.40, 12, 7.10],
            'QJs': [59.10, 13, 7.69],   'KTs': [60.40, 14, 8.28],   'QTs': [58.10, 15, 8.88],   'JTs': [56.20, 16, 9.47],
            '99': [71.70, 17, 10.06],   'AQo': [63.70, 18, 10.65],  
            
            # Very Strong hands
            'A9s': [61.40, 19, 11.24],  'KQo': [60.50, 20, 11.83],
            '88': [68.70, 21, 12.43],   'K9s': [58.40, 22, 13.02],  'T9s': [52.40, 23, 13.61],  'A8s': [60.30, 24, 14.20],
            'Q9s': [56.10, 25, 14.79],  'J9s': [54.20, 26, 15.38],  'AJo': [62.70, 27, 15.98],  'A5s': [57.70, 28, 16.57],
            '77': [65.70, 29, 17.16],   'A7s': [59.10, 30, 17.75],  'KJo': [59.50, 31, 18.34],  'A4s': [56.70, 32, 18.93],
            'A3s': [55.90, 33, 19.53],  'A6s': [57.80, 34, 20.12],  'QJo': [57.00, 35, 20.71],  '66': [62.70, 36, 21.30],
            'K8s': [56.40, 37, 21.89],  'T8s': [50.40, 38, 22.49],  'A2s': [55.00, 39, 23.08],  '98s': [48.90, 40, 23.67],
            'J8s': [52.30, 41, 24.26],  'ATo': [61.70, 42, 24.85],  
            
            # Solid hands
            'Q8s': [54.20, 43, 25.44],  'K7s': [55.40, 44, 26.04],
            'KTo': [58.50, 45, 26.63],  '55': [59.60, 46, 27.22],   'JTo': [53.80, 47, 27.81],  '87s': [45.70, 48, 28.40],
            'QTo': [56.00, 49, 29.59],  '44': [56.30, 50, 29.59],   '33': [52.90, 51, 30.18],   '22': [49.30, 52, 30.77],
            'K6s': [54.30, 53, 31.36],  '97s': [46.90, 54, 31.95],  'K5s': [53.30, 55, 32.54],  '76s': [42.90, 56, 33.14],
            'T7s': [48.40, 57, 33.73],  'K4s': [52.30, 58, 34.32],  'K3s': [51.40, 59, 34.91],  'K2s': [50.50, 60, 35.50],
            'Q7s': [52.10, 61, 36.09],  '86s': [43.70, 62, 36.69],  '65s': [40.30, 63, 37.28],  'J7s': [50.30, 64, 37.87],
            '54s': [38.50, 65, 38.46],  'Q6s': [51.30, 66, 39.05],  '75s': [40.90, 67, 39.64],  '96s': [44.90, 68, 40.24],
            'Q5s': [50.20, 69, 40.83],  '64s': [38.30, 70, 41.42],  'Q4s': [49.30, 71, 42.01],  'Q3s': [48.40, 72, 42.60],
            'T9o': [52.40, 73, 43.20],  'T6s': [46.50, 74, 43.79],  'Q2s': [47.50, 75, 44.38],  'A9o': [61.40, 76, 44.97],
            '53s': [36.50, 77, 45.56],  '85s': [41.70, 78, 46.15],  'J8o': [52.30, 79, 46.75],  'J9o': [54.20, 80, 47.34],
            'K9o': [58.40, 81, 47.93],  
            
            # Marginal hands
            'J5s': [47.50, 82, 48.52],  'Q9o': [56.10, 83, 49.11],  '43s': [35.70, 84, 49.70],
            '74s': [38.90, 85, 50.30],  'J4s': [46.50, 86, 50.89],  'J3s': [45.70, 87, 51.48],  '95s': [42.90, 88, 52.07],
            'J2s': [44.70, 89, 52.66],  '63s': [36.40, 90, 53.25],  'A8o': [60.30, 91, 53.85],  '52s': [34.50, 92, 54.44],
            'T5s': [44.50, 93, 55.03],  '84s': [39.70, 94, 55.62],  'T4s': [43.70, 95, 56.21],  'T3s': [42.80, 96, 56.80],
            '42s': [33.70, 97, 57.40],  'T2s': [42.00, 98, 57.99],  '98o': [48.90, 99, 58.58],  'T8o': [50.40, 100, 59.17],
            'A5o': [57.70, 101, 59.76], 'A7o': [59.10, 102, 60.36], '73s': [37.00, 103, 60.95], 'A4o': [56.70, 104, 61.54],
            '32s': [33.10, 105, 62.13], '94s': [40.90, 106, 62.72], '93s': [40.30, 107, 63.31], 'J8o': [52.30, 108, 63.91],
            'A3o': [55.90, 109, 64.50], '62s': [34.40, 110, 65.09], '92s': [39.40, 111, 65.68], 'K8o': [56.40, 112, 66.27],
            'A6o': [57.80, 113, 66.86], '87o': [45.70, 114, 67.46], 'Q8o': [54.20, 115, 68.05], '83s': [37.80, 116, 68.64],
            'A2o': [55.00, 117, 69.23], '82s': [37.20, 118, 69.82], '97o': [46.90, 119, 70.41], '72s': [35.10, 120, 71.01],
            '76o': [42.90, 121, 71.60], 'K7o': [55.40, 122, 72.19], '65o': [40.30, 123, 72.78], 'T7o': [48.40, 124, 73.37],
            'K6o': [54.30, 125, 73.96], '86o': [43.70, 126, 74.56], '54o': [38.50, 127, 75.15], 'K5o': [53.30, 128, 75.74],
            'J7o': [50.30, 129, 76.33], '75o': [40.90, 130, 76.92], 'Q7o': [52.10, 131, 77.51], 'K4o': [52.30, 132, 78.11],
            'K3o': [51.40, 133, 78.70], '96o': [44.90, 134, 79.29], 
            
            # Pretty bad hands
            'K2o': [50.50, 135, 79.88], '64o': [38.30, 136, 80.47],
            'Q6o': [51.30, 137, 81.07], '53o': [36.50, 138, 81.66], '85o': [41.70, 139, 82.25], 'T6o': [46.50, 140, 82.84],
            'Q5o': [50.20, 141, 83.43], '43o': [35.70, 142, 84.02], 'Q4o': [49.30, 143, 84.62], 'Q3o': [48.40, 144, 85.21],
            '74o': [38.90, 145, 85.80], 'Q2o': [47.50, 146, 86.39], 'J6o': [48.30, 147, 86.98], '63o': [36.40, 148, 87.57],
            'J5o': [47.50, 149, 88.17], '95o': [42.90, 150, 88.76], '52o': [34.50, 151, 89.35], 'J4o': [46.50, 152, 89.94],
            'J3o': [45.70, 153, 90.53],
            
            # Garbage hands (always fold unless there's bounty)
            '42o': [33.70, 154, 91.12], 'J2o': [44.70, 155, 91.71], '84o': [39.70, 156, 92.31],
            'T5o': [44.50, 157, 92.90], 'T4o': [43.70, 158, 93.49], '32o': [33.10, 159, 94.08], 'T3o': [42.80, 160, 94.67],
            '73o': [37.00, 161, 95.26], 'T2o': [42.00, 162, 95.85], '62o': [34.40, 163, 96.45], '94o': [40.90, 164, 97.04],
            '93o': [40.30, 165, 97.63], '92o': [39.40, 166, 98.22], '83o': [37.80, 167, 98.81], '82o': [37.20, 168, 99.40],
            '72o': [35.10, 169, 100.0]
        }

        # Define raise sizes based on number of previous raises
        self.preflop_raise_sizes = {
            0: 2.0,  
            1: 2.2,
            2: 2.3, 
            3: 2.4, 
            4: 2.7,
            5: float('inf') 
        }

        # Track opponent tendencies
        self.opponent_stats = {
            'preflop_raise_count': 0,
            'total_hands': 0,
            'fold_to_3bet': 0,
            'three_bet_opportunities': 0
        }

        # Add raise tracking
        self.current_round_raises = 0
        self.current_round_num = 0

    def handle_new_round(self, game_state, round_state, active):
        '''
        Called when a new round starts.
        '''
        # Reset raise counter at start of each round
        if self.current_round_num != game_state.round_num:
            self.current_round_raises = 0
            self.current_round_num = game_state.round_num

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
        '''
        street = round_state.street
        print(f"\n=== Action Decision ===", file=sys.stderr)
        print(f"Round: {game_state.round_num}/{NUM_ROUNDS}", file=sys.stderr)  # Added round number
        print(f"Street: {street}", file=sys.stderr)
        print(f"Position: {'SB' if not bool(active) else 'BB'}", file=sys.stderr)
        print(f"Legal actions: {round_state.legal_actions()}", file=sys.stderr)
        print(f"My cards: {round_state.hands[active]}", file=sys.stderr)
        print(f"Board cards: {round_state.deck[:street]}", file=sys.stderr)
        print(f"My bounty: {round_state.bounties[active]}", file=sys.stderr)
       
        if street == 0:  
            return self.get_preflop_action(game_state, round_state, active)
        else:  
            return self.get_postflop_action(game_state, round_state, active)

    def get_preflop_action(self, game_state, round_state, active):
        """
        Helper function to determine preflop action based on position and pot odds
        Returns: Action object (RaiseAction, CallAction, CheckAction, or FoldAction)
        """
        def get_hand_stats():
            """
            Helper function to evaluate hand strength
            Returns: (range_percentile, has_bounty)
            """
            cards = round_state.hands[active]
            bounty_rank = round_state.bounties[active]

            # Convert face cards to consistent format
            card_ranks = []
            for card in cards:
                rank = card[0]
                card_ranks.append(rank)
            
            # Check if suited
            suited = cards[0][1] == cards[1][1]
            
            # Handle pocket pairs first
            if card_ranks[0] == card_ranks[1]:
                hand_key = card_ranks[0] + card_ranks[1]
            # Handle Ace hands - Ace must always be first
            elif 'A' in card_ranks:
                other_card = [r for r in card_ranks if r != 'A'][0]
                hand_key = 'A' + other_card + ('s' if suited else 'o')
            # Handle King hands - King must be first if no Ace
            elif 'K' in card_ranks:
                other_card = [r for r in card_ranks if r != 'K'][0]
                hand_key = 'K' + other_card + ('s' if suited else 'o')
            # Handle Queen hands - Queen must be first if no Ace or King
            elif 'Q' in card_ranks:
                other_card = [r for r in card_ranks if r != 'Q'][0]
                hand_key = 'Q' + other_card + ('s' if suited else 'o')
            # Handle Jack hands - Jack must be first if no Ace, King, or Queen
            elif 'J' in card_ranks:
                other_card = [r for r in card_ranks if r != 'J'][0]
                hand_key = 'J' + other_card + ('s' if suited else 'o')
            # Handle Ten hands - Ten must be first if no face cards
            elif 'T' in card_ranks:
                other_card = [r for r in card_ranks if r != 'T'][0]
                hand_key = 'T' + other_card + ('s' if suited else 'o')
            else:
                # For remaining hands, sort numerically
                ranks = sorted(card_ranks, reverse=True)
                hand_key = ranks[0] + ranks[1] + ('s' if suited else 'o')
            
            print(f"Hand key: {hand_key}", file=sys.stderr)  # Debug print
            
            # Get hand stats from dictionary
            hand_stats = self.hand_strength.get(hand_key, [30.0, 169, 99.0])
            range_percentile = hand_stats[2]
            
            has_bounty = bounty_rank in [card[0] for card in cards]
            
            print(f"Range percentile: {range_percentile}", file=sys.stderr)
            print(f"Has bounty: {has_bounty}", file=sys.stderr)
            return range_percentile, has_bounty

        def calculate_pot_odds(my_contrib, opp_contrib, call_amount):
            """
            Calculate pot odds and total pot size
            Returns: (pot_odds, total_pot)
            """
            if call_amount == 0:
                return float('inf'), my_contrib + opp_contrib
                
            current_pot = my_contrib + opp_contrib  # What's already in the pot
            total_pot = current_pot + call_amount  # Total after we call
            
            # Pot odds = what we can win / what we need to risk
            # When facing a raise, we can win the current pot plus their raise
            pot_odds = total_pot / call_amount
            
            print(f"Pot Odds Calculation:", file=sys.stderr)
            print(f"My contribution: {my_contrib}", file=sys.stderr)
            print(f"Opponent contribution: {opp_contrib}", file=sys.stderr)
            print(f"Call amount: {call_amount}", file=sys.stderr)
            print(f"Current pot: {current_pot}", file=sys.stderr)
            print(f"Total pot after call: {total_pot}", file=sys.stderr)
            print(f"Pot odds: {pot_odds:.2f}:1", file=sys.stderr)
            
            return pot_odds, total_pot

        def adjust_range_percentile(base_percentile):
            """
            Dynamically adjust range percentile based on pot odds
            Returns: adjusted_percentile
            """
            # Skip adjustments if no raises yet
            if self.current_round_raises == 0:
                print(f"  No raises yet - using base percentile: {base_percentile:.1f}", file=sys.stderr)
                return base_percentile
            
            # Calculate required equity from pot odds
            my_stack = round_state.stacks[active]
            opp_stack = round_state.stacks[1-active]
            my_contribution = STARTING_STACK - my_stack
            opp_contribution = STARTING_STACK - opp_stack
            call_amount = max(0, opp_contribution - my_contribution)
            
            if call_amount == 0:
                return base_percentile
                
            total_pot = my_contribution + opp_contribution + call_amount
            pot_odds = total_pot / call_amount
            
            # Required equity = 1 / (1 + pot_odds)
            # Example: 4:1 pot odds means we need 20% equity
            required_equity = 1 / (1 + pot_odds)
            
            # Convert to percentile (multiply by 100 since equity is 0-1)
            # We continue with hands BETTER than required equity
            max_continue_percentile = (1 - required_equity) * 100
            
            print(f"Range adjustment:", file=sys.stderr)
            print(f"  Base percentile: {base_percentile:.1f}", file=sys.stderr)
            print(f"  Pot odds: {pot_odds:.2f}:1", file=sys.stderr)
            print(f"  Required equity: {required_equity:.1%}", file=sys.stderr)
            print(f"  Max continue: {max_continue_percentile:.1f}%", file=sys.stderr)
            
            # If our hand is worse than the continuing range, adjust it to 100%
            if base_percentile > max_continue_percentile:
                print(f"  Final percentile: 100.0 (hand not in continuing range)", file=sys.stderr)
                return 100.0
                
            # Otherwise, rescale our hand to the new range
            adjusted_percentile = (base_percentile / max_continue_percentile) * 100
            print(f"  Final percentile: {adjusted_percentile:.1f}", file=sys.stderr)
            
            return adjusted_percentile

        # Get base hand evaluation and position info
        base_percentile, has_bounty = get_hand_stats()
        is_sb = not bool(active)
        legal_actions = round_state.legal_actions()
        my_stack = round_state.stacks[active]
        opp_stack = round_state.stacks[1-active]
        my_contribution = STARTING_STACK - my_stack
        opp_contribution = STARTING_STACK - opp_stack

        # SB specific logic - only raise or fold, never call
        if is_sb and my_contribution <= 1 and opp_contribution <= 2:
            if RaiseAction in legal_actions:
                if base_percentile <= 83 or has_bounty:  # Open top 83% or bounty hands
                    min_raise, max_raise = round_state.raise_bounds()
                    pot = my_contribution + opp_contribution
                    raise_multiplier = random.uniform(2.0, 2.50)
                    raise_amount = int(pot * raise_multiplier)
                    raise_amount = max(min_raise, min(max_raise, raise_amount))
                    self.current_round_raises += 1  # Increment raise counter
                    print(f"Opening from SB with {'bounty hand' if has_bounty else 'top 83%'} - Raising {raise_amount} ({raise_multiplier:.1f}x pot)", file=sys.stderr)
                    return RaiseAction(raise_amount)
            print(f"Folding from SB - hand too weak", file=sys.stderr)
            return FoldAction()

        # Adjust percentile based on number of raises
        range_percentile = adjust_range_percentile(base_percentile)

        # Calculate pot odds for non-SB decisions
        call_amount = 0
        if CallAction in legal_actions:
            call_amount = max(0, opp_contribution - my_contribution)
        pot_odds, total_pot = calculate_pot_odds(my_contribution, opp_contribution, call_amount)

        if CallAction in legal_actions:
            # Call with good pot odds or strong hands
            if has_bounty:
                print(f"Calling with bounty card", file=sys.stderr)
                return CallAction()
            elif pot_odds >= 3 and range_percentile <= 60:
                print(f"Calling with good pot odds", file=sys.stderr)
                return CallAction()
            elif pot_odds >= 2 and range_percentile <= 40:
                print(f"Calling with decent pot odds and strong hand", file=sys.stderr)
                return CallAction()

        # Rest of decision making (for BB or facing raises)
        if RaiseAction in legal_actions:
            min_raise, max_raise = round_state.raise_bounds()
            pot = my_contribution + opp_contribution
            
            # Randomize between raising top 10-20% of hands when facing action
            raise_threshold = random.uniform(10.0, 20.0)
            if range_percentile <= raise_threshold:  
                # Get raise size multiplier based on number of raises
                raise_multiplier = self.preflop_raise_sizes.get(self.current_round_raises, float('inf'))
                
                # Calculate raise amount
                raise_amount = int(pot * raise_multiplier)
                raise_amount = max(min_raise, min(max_raise, raise_amount))
                self.current_round_raises += 1
                
                print(f"Raising with strong hand (top {raise_threshold:.1f}%) - Raising {raise_amount} ({raise_multiplier:.1f}x pot)", file=sys.stderr)
                return RaiseAction(raise_amount)

        if CallAction in legal_actions:
            # Call with good pot odds or strong hands
            if has_bounty:
                print(f"Calling with bounty card", file=sys.stderr)
                return CallAction()
            elif pot_odds >= 3 and range_percentile <= 60:
                print(f"Calling with good pot odds", file=sys.stderr)
                return CallAction()
            elif pot_odds >= 2 and range_percentile <= 40:
                print(f"Calling with decent pot odds and strong hand", file=sys.stderr)
                return CallAction()

        if CheckAction in legal_actions:
            print(f"Checking when given the option", file=sys.stderr)
            return CheckAction()
        
        print(f"Folding - insufficient pot odds or weak hand", file=sys.stderr)
        return FoldAction()

    def get_postflop_action(self, game_state, round_state, active):
        """
        Helper function to determine postflop action based on hand strength
        Returns: Action object (RaiseAction, CallAction, CheckAction, or FoldAction)
        """
        def evaluate_hand_strength():
            """
            Helper function to evaluate postflop hand strength using eval7
            Returns: (hand_value, hand_type)
            """
            hole_cards = [eval7.Card(card) for card in round_state.hands[active]]
            board_cards = [eval7.Card(card) for card in round_state.deck[:round_state.street]]
            
            # Evaluate the hand
            all_cards = hole_cards + board_cards
            hand_value = eval7.evaluate(all_cards)
            
            # Convert hand value to hand type
            hand_types = {
                0: 'High Card',
                1: 'Pair',
                2: 'Two Pair',
                3: 'Three of a Kind',
                4: 'Straight',
                5: 'Flush',
                6: 'Full House',
                7: 'Four of a Kind',
                8: 'Straight Flush'
            }
            
            hand_type = hand_types[hand_value >> 24]
            print(f"Hand evaluation - Type: {hand_type}, Value: {hand_value}", file=sys.stderr)
            return hand_value, hand_type

        # Get hand evaluation
        hand_value, hand_type = evaluate_hand_strength()

        # Rest of postflop logic
        legal_actions = round_state.legal_actions()
        my_stack = round_state.stacks[active]
        opp_stack = round_state.stacks[1-active]
        my_contribution = STARTING_STACK - my_stack
        opp_contribution = STARTING_STACK - opp_stack
        pot = my_contribution + opp_contribution
        
        # Define betting strategy based on hand strength
        if hand_type in ['Straight Flush', 'Four of a Kind', 'Full House', 'Flush', 'Straight']:
            # Very strong hands - bet big or raise
            if RaiseAction in legal_actions:
                min_raise, max_raise = round_state.raise_bounds()
                bet_amount = min(max_raise, pot)  # Pot-sized bet
                print(f"Value betting {bet_amount} with {hand_type}", file=sys.stderr)
                return RaiseAction(bet_amount)
            
        elif hand_type in ['Three of a Kind', 'Two Pair']:
            # Strong hands - bet medium or call
            if RaiseAction in legal_actions and random.random() < 0.8:  # 80% bet frequency
                min_raise, max_raise = round_state.raise_bounds()
                bet_amount = min(max_raise, int(pot * 0.75))  # 3/4 pot bet
                print(f"Value betting {bet_amount} with {hand_type}", file=sys.stderr)
                return RaiseAction(bet_amount)
                
        elif hand_type == 'Pair':
            # Medium strength - bet small or call
            if RaiseAction in legal_actions and random.random() < 0.5:  # 50% bet frequency
                min_raise, max_raise = round_state.raise_bounds()
                bet_amount = min(max_raise, int(pot * 0.5))  # Half pot bet
                print(f"Value betting {bet_amount} with {hand_type}", file=sys.stderr)
                return RaiseAction(bet_amount)
        
        # Default actions based on hand strength
        if CheckAction in legal_actions:
            print(f"Checking with {hand_type}", file=sys.stderr)
            return CheckAction()
            
        if CallAction in legal_actions:
            if hand_type != 'High Card':  # Call with any pair or better
                print(f"Calling with {hand_type}", file=sys.stderr)
                return CallAction()
        
        if FoldAction in legal_actions:
            print(f"Folding {hand_type}", file=sys.stderr)
            return FoldAction()
        
        # Fallback actions
        if CheckAction in legal_actions:
            return CheckAction()
        
        return FoldAction()


if __name__ == '__main__':
    run_bot(Player(), parse_args())
    
