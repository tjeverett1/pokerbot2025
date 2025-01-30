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
        super().__init__()
        
        # Add rank conversion dictionary
        self.rank_to_numeric = {
            'A': 14, 'K': 13, 'Q': 12, 'J': 11, 'T': 10,
            '9': 9, '8': 8, '7': 7, '6': 6, '5': 5,
            '4': 4, '3': 3, '2': 2
        }
        
        # Store hand strength as [win_percentage, absolute_rank, range_percentile]
        # absolute_rank: 1-169 (1 = best, 169 = worst)
        # range_percentile: position in range (0.6 = top 0.6% of hands, 100 = bottom 100%)
        # Calculation of range percentile: combos of hand / 1326
        # combos of hand: {pocket pairs: 6, suited cards: 4, offsuit cards: 12}
        self.hand_strength = {
            # Premium hands
            'AA': [84.90, 1, 0.45],      'KK': [82.10, 2, 0.90],      'QQ': [79.60, 3, 1.36],      'AKs': [66.20, 4, 1.66],
            'JJ': [77.10, 5, 2.11],      'AQs': [65.40, 6, 2.41],     'KQs': [62.40, 7, 2.71],     'AJs': [64.40, 8, 3.02],
            'KJs': [61.40, 9, 3.32],     'TT': [74.70, 10, 3.77],     'AKo': [64.50, 11, 4.67],    'ATs': [63.40, 12, 4.98],
            'QJs': [59.10, 13, 5.28],    'KTs': [60.40, 14, 5.58],    'QTs': [58.10, 15, 5.88],    'JTs': [56.20, 16, 6.18],
            '99': [71.70, 17, 6.64],     'AQo': [63.70, 18, 7.54],    'A9s': [61.40, 19, 7.84],    'KQo': [60.50, 20, 8.75],
            '88': [68.70, 21, 9.20], 
              
            # Very Strong hands
            'K9s': [58.40, 22, 9.50],    'T9s': [52.40, 23, 9.80],    'A8s': [60.30, 24, 10.11],
            'Q9s': [56.10, 25, 10.41],   'J9s': [54.20, 26, 10.71],   'AJo': [62.70, 27, 11.61],   'A5s': [57.70, 28, 11.92],
            '77': [65.70, 29, 12.37],    'A7s': [59.10, 30, 12.67],   'KJo': [59.50, 31, 13.57],   'A4s': [56.70, 32, 13.88],
            'A3s': [55.90, 33, 14.18],   'A6s': [57.80, 34, 14.48],   'QJo': [57.00, 35, 15.38],   '66': [62.70, 36, 15.84],
            'K8s': [56.40, 37, 16.14],   'T8s': [50.40, 38, 16.44],   'A2s': [55.00, 39, 16.74],   '98s': [48.90, 40, 17.04],
            'J8s': [52.30, 41, 17.35],   'ATo': [61.70, 42, 18.25],   
            
            # Solid hands
            'Q8s': [54.20, 43, 18.55],   'K7s': [55.40, 44, 18.85],
            'KTo': [58.50, 45, 19.76],   '55': [59.60, 46, 20.21],    'JTo': [53.80, 47, 21.12],   '87s': [45.70, 48, 21.42],
            'QTo': [56.00, 49, 22.32],   '44': [56.30, 50, 22.78],    '33': [52.90, 51, 23.23],    '22': [49.30, 52, 23.68],
            'K6s': [54.30, 53, 23.98],   '97s': [46.90, 54, 24.28],   'K5s': [53.30, 55, 24.59],   '76s': [42.90, 56, 24.89],
            'T7s': [48.40, 57, 25.19],   'K4s': [52.30, 58, 25.49],   'K3s': [51.40, 59, 25.79],   'K2s': [50.50, 60, 26.09],
            'Q7s': [52.10, 61, 26.40],   '86s': [43.70, 62, 26.70],   '65s': [40.30, 63, 27.00],   'J7s': [50.30, 64, 27.30],
            '54s': [38.50, 65, 27.60],   'Q6s': [51.30, 66, 27.90],   '75s': [40.90, 67, 28.21],   '96s': [44.90, 68, 28.51],
            'Q5s': [50.20, 69, 28.81],   '64s': [38.30, 70, 29.11],   'Q4s': [49.30, 71, 29.41],   'Q3s': [48.40, 72, 29.71],
            'T9o': [52.40, 73, 30.62],   'T6s': [46.50, 74, 30.92],   'Q2s': [47.50, 75, 31.22],   'A9o': [61.40, 76, 32.13],
            '53s': [36.50, 77, 32.43],   '85s': [41.70, 78, 32.73],   'J9o': [54.20, 79, 33.63],   'K9o': [58.40, 80, 34.54],
            
            # Marginal Hands
            'J5s': [47.50, 81, 34.84],   'Q9o': [56.10, 82, 35.75],   '43s': [35.70, 83, 36.05],   '74s': [38.90, 84, 36.35],
            'J4s': [46.50, 85, 36.65],   'J3s': [45.70, 86, 36.95],   '95s': [42.90, 87, 37.25],   'J2s': [44.70, 88, 37.56],
            '63s': [36.40, 89, 37.86],   'A8o': [60.30, 90, 38.76],   '52s': [34.50, 91, 39.06],   'T5s': [44.50, 92, 39.37],
            '84s': [39.70, 93, 39.67],   'T4s': [43.70, 94, 39.97],   'T3s': [42.80, 95, 40.27],   '42s': [33.70, 96, 40.57],
            'T2s': [42.00, 97, 40.87],   '98o': [48.90, 98, 41.78],   'T8o': [50.40, 99, 42.68],   'A5o': [57.70, 100, 43.59],
            'A7o': [59.10, 101, 44.49],  '73s': [37.00, 102, 44.80],  'A4o': [56.70, 103, 45.70],  '32s': [33.10, 104, 46.00],
            '94s': [40.90, 105, 46.30],  '93s': [40.30, 106, 46.61],  'J8o': [52.30, 107, 47.51],  'A3o': [55.90, 108, 48.42],
            '62s': [34.40, 109, 48.72],  '92s': [39.40, 110, 49.02],  'K8o': [56.40, 111, 49.92],  'A6o': [57.80, 112, 50.83],
            '87o': [45.70, 113, 51.73],  'Q8o': [54.20, 114, 52.64],  '83s': [37.80, 115, 52.94],  'A2o': [55.00, 116, 53.85],
            '82s': [37.20, 117, 54.15],  '97o': [46.90, 118, 55.05],  '72s': [35.10, 119, 55.35],  '76o': [42.90, 120, 56.26],
            'K7o': [55.40, 121, 57.16],  '65o': [40.30, 122, 58.07],  'T7o': [48.40, 123, 58.97],  'K6o': [54.30, 124, 59.88],
            '86o': [43.70, 125, 60.78],  '54o': [38.50, 126, 61.69],  'K5o': [53.30, 127, 62.59],  'J7o': [50.30, 128, 63.50],
            '75o': [40.90, 129, 64.40],  'Q7o': [52.10, 130, 65.31],  'K4o': [52.30, 131, 66.21],  'K3o': [51.40, 132, 67.12],
            '96o': [44.90, 133, 68.02],  

            # Bad Hands
            'K2o': [50.50, 134, 68.93],  '64o': [38.30, 135, 69.83],  'Q6o': [51.30, 136, 70.74],
            '53o': [36.50, 137, 71.64],  '85o': [41.70, 138, 72.55],  'T6o': [46.50, 139, 73.45],  'Q5o': [50.20, 140, 74.36],
            '43o': [35.70, 141, 75.26],  'Q4o': [49.30, 142, 76.17],  'Q3o': [48.40, 143, 77.07],  '74o': [38.90, 144, 77.98],
            'Q2o': [47.50, 145, 78.88],  'J6o': [48.30, 146, 79.79],  '63o': [36.40, 147, 80.69],  'J5o': [47.50, 148, 81.60],
            '95o': [42.90, 149, 82.50],  '52o': [34.50, 150, 83.41],  'J4o': [46.50, 151, 84.31],  'J3o': [45.70, 152, 85.22],
            
            # Trash Hands
            '42o': [33.70, 153, 86.12],  'J2o': [44.70, 154, 87.03],  '84o': [39.70, 155, 87.93],  'T5o': [44.50, 156, 88.84],
            'T4o': [43.70, 157, 89.74],  '32o': [33.10, 158, 90.65],  'T3o': [42.80, 159, 91.55],  '73o': [37.00, 160, 92.46],
            'T2o': [42.00, 161, 93.36],  '62o': [34.40, 162, 94.27],  '94o': [40.90, 163, 95.17],  '93o': [40.30, 164, 96.08],
            '92o': [39.40, 165, 96.98],  '83o': [37.80, 166, 97.89],  '82o': [37.20, 167, 98.79],  '72o': [35.10, 168, 100.0]
        }

        # Define raise sizes based on number of previous raises
        self.preflop_raise_sizes = {
            0: 2.0,  
            1: 2.2,
            2: 2.3, 
            3: 2.4, 
            4: 2.0,
            5: float('inf') 
        }

        # Define opening ranges
        self.sb_open_range = 86.0  # Percentage of hands to open from SB

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

        self.is_preflop_aggressor = False

        self.previous_street_strength = 0.0  # Add this line

    def handle_new_round(self, game_state, round_state, active):
        '''
        Called when a new round starts.
        '''
        # Reset raise counter at start of each round
        if self.current_round_num != game_state.round_num:
            self.current_round_raises = 0
            self.current_round_num = game_state.round_num

        # Reset the aggressor status at the start of each round
        self.is_preflop_aggressor = False

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
                if base_percentile <= self.sb_open_range or has_bounty:
                    min_raise, max_raise = round_state.raise_bounds()
                    pot = my_contribution + opp_contribution
                    raise_multiplier = random.uniform(2.0, 2.50)
                    raise_amount = int(pot * raise_multiplier)
                    raise_amount = max(min_raise, min(max_raise, raise_amount))
                    self.current_round_raises += 1  # Increment raise counter
                    self.is_preflop_aggressor = True  # Add this line
                    print(f"Opening from SB with {'bounty hand' if has_bounty else f'top {self.sb_open_range}%'} - Raising {raise_amount} ({raise_multiplier:.1f}x pot)", file=sys.stderr)
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

        # MOVED: Only check for calling after we've decided not to raise
        if CallAction in legal_actions:
            # Reset preflop aggressor status if we're calling a 3bet
            if round_state.street == 0:
                self.is_preflop_aggressor = False
                
            # Call with good pot odds or strong hands
            if has_bounty:
                print(f"Calling with bounty card", file=sys.stderr)
                return CallAction()
            
            # Calculate required equity from pot odds
            my_stack = round_state.stacks[active]
            opp_stack = round_state.stacks[1-active]
            my_contribution = STARTING_STACK - my_stack
            opp_contribution = STARTING_STACK - opp_stack
            call_amount = max(0, opp_contribution - my_contribution)
            
            if call_amount > 0:
                total_pot = my_contribution + opp_contribution + call_amount
                pot_odds = total_pot / call_amount
                required_equity = 1 / (1 + pot_odds)
                required_percentile = required_equity * 100
                
                print(f"Pot odds: {pot_odds:.2f}:1", file=sys.stderr)
                print(f"Required equity: {required_equity:.1%}", file=sys.stderr)
                print(f"Required percentile: {required_percentile:.1f}", file=sys.stderr)
                print(f"Hand percentile: {range_percentile:.1f}", file=sys.stderr)
                
                # If our hand is better than required percentile, call
                if range_percentile <= 100 - required_percentile:
                    print(f"Calling - hand meets required strength threshold", file=sys.stderr)
                    return CallAction()

        if CheckAction in legal_actions:
            print(f"Checking when given the option", file=sys.stderr)
            return CheckAction()
        
        print(f"Folding - insufficient pot odds or weak hand", file=sys.stderr)
        return FoldAction()
    

    def get_postflop_action(self, game_state, round_state, active):
        """
        GTO-based postflop strategy using pot odds and board texture
        """
        # Get street and position info
        street = round_state.street
        is_sb = not bool(active)
        street_name = ['Flop', 'Turn', 'River'][street-3]
        
        # Calculate stack sizes and contributions
        my_stack = round_state.stacks[active]
        opp_stack = round_state.stacks[1-active]
        my_contrib = STARTING_STACK - my_stack
        opp_contrib = STARTING_STACK - opp_stack
        pot = my_contrib + opp_contrib
        
        def analyze_previous_action(my_contrib, opp_contrib, is_sb, street):
            """
            Analyzes previous betting patterns to inform decision making
            Returns: (is_opponent_capped, previous_streets_checked)
            """
            # Use the stored preflop aggressor status instead of contributions
            hero_preflop_aggressor = self.is_preflop_aggressor
            
            # Check if previous streets had action
            previous_streets_checked = True
            if street > 3:  # On turn or river
                previous_streets_checked = self.current_round_raises == 0
            return hero_preflop_aggressor, previous_streets_checked

        def evaluate_hand_and_board():
            """
            Evaluates hand strength and board texture
            Returns: (hand_value, hand_type, board_type, relative_strength, board_favor)
            """
            hole_cards = [eval7.Card(card) for card in round_state.hands[active]]
            board_cards = [eval7.Card(card) for card in round_state.deck[:round_state.street]]
            
            # Basic hand strength
            all_cards = hole_cards + board_cards
            hand_value = eval7.evaluate(all_cards)
            
            # Calculate relative hand strength
            # Generate all possible two card combinations
            deck = []
            ranks = '23456789TJQKA'
            suits = 'hdcs'
            for rank in ranks:
                for suit in suits:
                    card_str = rank + suit
                    if eval7.Card(card_str) not in all_cards:  # Skip cards we can see
                        deck.append(eval7.Card(card_str))
            
            # Generate all possible opponent hands
            possible_hands = 0
            better_hands = 0
            for i in range(len(deck)):
                for j in range(i + 1, len(deck)):
                    possible_hands += 1
                    opp_value = eval7.evaluate(board_cards + [deck[i], deck[j]])
                    if opp_value > hand_value:
                        better_hands += 1
            
            relative_strength = 1 - (better_hands / possible_hands) if possible_hands > 0 else 1
            
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
            
            # Board texture analysis
            suits = [card.suit for card in board_cards]
            ranks = [card.rank for card in board_cards]
            
            # Check for draws
            flush_draw = len(set(suits)) == 3 and any(suits.count(s) >= 3 for s in suits)
            straight_draw = len(set(ranks)) >= 3 and max(ranks) - min(ranks) <= 4
            paired_board = len(set(ranks)) < len(ranks)
            
            # Categorize board type
            if paired_board:
                board_type = 'paired'
            elif flush_draw and straight_draw:
                board_type = 'very_draw_heavy'
            elif flush_draw or straight_draw:
                board_type = 'draw_heavy'
            else:
                board_type = 'dry'
            
            print(f"Hand evaluation - Type: {hand_type}, Value: {hand_value}", file=sys.stderr)
            print(f"Board type: {board_type}", file=sys.stderr)
            print(f"Relative strength: {relative_strength:.2%}", file=sys.stderr)
            
            # New board texture analysis for aggressor vs caller
            def analyze_board_favor(board_cards):
                """
                Analyzes if board texture favors preflop aggressor or caller
                Returns: 'aggressor', 'caller', or 'neutral'
                """
                # Convert eval7 ranks to our numeric system
                # eval7 uses: 2=0, 3=1, 4=2, ..., T=8, J=9, Q=10, K=11, A=12
                def convert_eval7_rank(rank):
                    if isinstance(rank, int):
                        return rank + 2  # Convert eval7's 0-12 to our 2-14
                    return self.rank_to_numeric[rank]

                ranks = [card.rank for card in board_cards]
                suits = [card.suit for card in board_cards]
                
                # Convert ranks to numeric values (2-14)
                numeric_ranks = []
                for rank in ranks:
                    numeric_rank = convert_eval7_rank(rank)
                    numeric_ranks.append(numeric_rank)
                
                # Sort ranks for analysis
                numeric_ranks.sort(reverse=True)
                print(f"Sorted numeric ranks: {numeric_ranks}", file=sys.stderr)
                
                # Calculate characteristics
                high_cards = sum(1 for r in numeric_ranks if r >= 10)
                connected_cards = sum(1 for i in range(len(numeric_ranks)-1) if numeric_ranks[i] - numeric_ranks[i+1] == 1)
                suited_cards = max([suits.count(s) for s in set(suits)])
                avg_rank = sum(numeric_ranks) / len(numeric_ranks)
                
                print(f"Average calculation: {sum(numeric_ranks)} / {len(numeric_ranks)} = {avg_rank:.2f}", file=sys.stderr)
                
                # Calculate gaps between unique ranks
                unique_ranks = sorted(set(numeric_ranks), reverse=True)
                gaps = 0
                for i in range(len(unique_ranks)-1):
                    gap = unique_ranks[i] - unique_ranks[i+1] - 1
                    gaps += gap
                
                # Analyze board texture
                factors = {
                    'aggressor': 0,
                    'caller': 0
                }
                
                # Factors favoring aggressor
                if high_cards >= 2: factors['aggressor'] += 2
                if gaps >= 3: factors['aggressor'] += 1
                if avg_rank > 10: factors['aggressor'] += 1
                if connected_cards == 0: factors['aggressor'] += 1
                
                # Factors favoring caller
                if connected_cards >= 2: factors['caller'] += 2
                if suited_cards >= 2: factors['caller'] += 1
                if avg_rank < 8: factors['caller'] += 1
                if high_cards == 0: factors['caller'] += 1
                
                # Determine overall favor
                favor = 'neutral'
                if factors['aggressor'] > factors['caller'] + 1:
                    favor = 'aggressor'
                elif factors['caller'] > factors['aggressor'] + 1:
                    favor = 'caller'
                
                # Debug prints
                print(f"\nBoard texture analysis:", file=sys.stderr)
                print(f"High cards: {high_cards}", file=sys.stderr)
                print(f"Connected cards: {connected_cards}", file=sys.stderr)
                print(f"Suited cards: {suited_cards}", file=sys.stderr)
                print(f"Average rank: {avg_rank:.1f}", file=sys.stderr)
                print(f"Gaps: {gaps}", file=sys.stderr)
                print(f"Aggressor points: {factors['aggressor']}", file=sys.stderr)
                print(f"Caller points: {factors['caller']}", file=sys.stderr)
                print(f"Board favors: {favor}", file=sys.stderr)
                
                return favor

            board_favor = analyze_board_favor(board_cards)
            
            return hand_value, hand_type, board_type, relative_strength, board_favor

        # Get hand evaluation and board analysis
        hand_value, hand_type, board_type, relative_strength, board_favor = evaluate_hand_and_board()
        hero_preflop_aggressor, previous_streets_checked = analyze_previous_action(my_contrib, opp_contrib, is_sb, street)
        
        legal_actions = round_state.legal_actions()
        
        print(f"\nDecision point analysis:", file=sys.stderr)
        print(f"Street: {street_name}", file=sys.stderr)
        print(f"Position: {'SB (OOP)' if is_sb else 'BB (IP)'}", file=sys.stderr)
        print(f"Pot size: {pot}", file=sys.stderr)
        print(f"Hero was preflop aggressor: {hero_preflop_aggressor}", file=sys.stderr)
        print(f"Previous streets checked through: {previous_streets_checked}", file=sys.stderr)    
        print(f"Relative strength: {relative_strength:.2%}", file=sys.stderr)
        
        # Store current strength for next street
        self.previous_street_strength = relative_strength
        
        # FLOP STRATEGY
        if street == 3:
            # Always check raise bounds before attempting a raise
            can_raise = RaiseAction in legal_actions
            min_raise, max_raise = round_state.raise_bounds() if can_raise else (0, 0)
            
            if hero_preflop_aggressor:
                if relative_strength > 0.85:  # Increase threshold for strong hands
                    if can_raise and min_raise <= int(pot * 0.75) <= max_raise:
                        bet_amount = int(pot * 0.75)  # Larger bet size for strong hands
                        print(f"Betting flop as preflop aggressor: {bet_amount} into {pot}", file=sys.stderr)
                        return RaiseAction(bet_amount)
            
            if not is_sb:  # In position
                if can_raise and relative_strength > 0.70:
                    bet_size = int(pot * random.uniform(0.33, 0.5))
                    if min_raise <= bet_size <= max_raise:
                        print(f"IP flop bet with strong hand: {bet_size} into {pot}", file=sys.stderr)
                        return RaiseAction(bet_size)
                
                if CallAction in legal_actions and relative_strength > 0.30:
                    print(f"Calling flop IP with decent hand", file=sys.stderr)
                    return CallAction()
                
                if CheckAction in legal_actions:
                    print(f"Checking flop IP with weak hand", file=sys.stderr)
                    return CheckAction()
            else:  # Out of position
                if CallAction in legal_actions and relative_strength > 0.35:
                    print(f"Calling flop OOP with decent hand", file=sys.stderr)
                    return CallAction()
                
                if CheckAction in legal_actions:
                    print(f"Checking flop OOP", file=sys.stderr)
                    return CheckAction()
            
            # Default actions
            if CheckAction in legal_actions:
                print(f"Checking flop by default", file=sys.stderr)
                return CheckAction()
            elif CallAction in legal_actions:
                call_amount = max(0, opp_contrib - my_contrib)
                if pot / call_amount >= 3:  # Getting 3:1 or better
                    print(f"Calling flop by default with good odds", file=sys.stderr)
                    return CallAction()
            
            print(f"Folding flop by default", file=sys.stderr)
            return FoldAction()

        # TURN STRATEGY
        elif street == 4:
            # Calculate pot odds and stack sizes
            call_amount = max(0, opp_contrib - my_contrib)
            my_stack = round_state.stacks[active]
            opp_stack = round_state.stacks[1-active]
            
            # Always check raise bounds before attempting raises
            can_raise = RaiseAction in legal_actions
            min_raise, max_raise = round_state.raise_bounds() if can_raise else (0, 0)
            
            # Log the raise bounds for debugging
            if can_raise:
                print(f"Turn stacks - Me: {my_stack}, Opp: {opp_stack}", file=sys.stderr)
                print(f"Contributions - Me: {my_contrib}, Opp: {opp_contrib}", file=sys.stderr)
                print(f"Raise bounds - Min: {min_raise}, Max: {max_raise}", file=sys.stderr)
            
            # If facing a raise of our bet
            if self.current_round_raises >= 2:
                if can_raise and relative_strength > 0.8:  # Increase threshold for strong hands
                    # Calculate a 2.5x raise
                    intended_raise = min(max_raise, opp_contrib + (opp_contrib - my_contrib))
                    if min_raise <= intended_raise <= max_raise:
                        print(f"Re-raising turn with strong hand: {intended_raise}", file=sys.stderr)
                        return RaiseAction(intended_raise)
                
                # If we can't raise but can call and have decent equity
                if CallAction in legal_actions and relative_strength > 0.6:
                    print(f"Calling turn raise with good hand", file=sys.stderr)
                    return CallAction()
                
                # If we can only check, do that instead of folding
                if CheckAction in legal_actions:
                    print(f"Checking turn - can't fold", file=sys.stderr)
                    return CheckAction()
                
                # Only fold if it's actually legal
                if FoldAction in legal_actions:
                    print(f"Folding to turn raise", file=sys.stderr)
                    return FoldAction()
            
            # If we can only check or raise
            if CheckAction in legal_actions:
                if can_raise and relative_strength > 0.8:  # Strong hand
                    bet_amount = min(max_raise, int(pot * 0.75))  # Larger bet size for strong hands
                    if min_raise <= bet_amount:
                        print(f"Turn value bet: {bet_amount}", file=sys.stderr)
                        return RaiseAction(bet_amount)
                print(f"Checking turn by default", file=sys.stderr)
                return CheckAction()
            
            # If we must call or fold
            if CallAction in legal_actions and relative_strength > 0.5:
                print(f"Calling turn with decent hand", file=sys.stderr)
                return CallAction()
            
            # Only fold if it's legal
            if FoldAction in legal_actions:
                print(f"Folding turn by default", file=sys.stderr)
                return FoldAction()
            
            # Final fallback - must check
            print(f"Checking turn - no other legal action", file=sys.stderr)
            return CheckAction()

        # RIVER STRATEGY
        elif street == 5:
            # Calculate pot odds and stack sizes
            call_amount = max(0, opp_contrib - my_contrib)
            my_stack = round_state.stacks[active]
            opp_stack = round_state.stacks[1-active]
            effective_stack = min(my_stack, opp_stack)
            
            if call_amount > 0:
                pot_odds = pot / call_amount
                required_equity = 1 / (1 + pot_odds)
                print(f"River pot odds: {pot_odds:.2f}:1 (need {required_equity:.1%} equity)", file=sys.stderr)
                print(f"Effective stack: {effective_stack}, Pot: {pot}", file=sys.stderr)
            
            # Always check raise bounds and stack sizes before attempting raises
            can_raise = RaiseAction in legal_actions
            min_raise, max_raise = round_state.raise_bounds() if can_raise else (0, 0)
            
            # Ensure we never try to raise more than our stack
            max_raise = min(max_raise, my_stack)
            
            # Always bet/raise with the nuts (>95% equity)
            if relative_strength > 0.95:
                if can_raise and min_raise <= max_raise:
                    # Size up with the nuts - bet pot or max available
                    bet_amount = min(pot, max_raise)
                    print(f"Value betting river with nuts: {bet_amount} into {pot}", file=sys.stderr)
                    return RaiseAction(bet_amount)
                elif CallAction in legal_actions:
                    print(f"Calling river with nuts", file=sys.stderr)
                    return CallAction()
            
            # If facing a bet, check if we have sufficient pot odds to call
            if CallAction in legal_actions and call_amount > 0:
                if relative_strength < required_equity:
                    print(f"Folding river - insufficient equity ({relative_strength:.1%} < {required_equity:.1%})", file=sys.stderr)
                    return FoldAction()
            
            # Betting strategy based on previous street action
            if can_raise and min_raise <= max_raise:
                previous_bets = self.current_round_raises
                
                # Calculate bet sizes safely
                def get_safe_bet_size(pot_fraction):
                    intended_bet = int(pot * pot_fraction)
                    return min(intended_bet, max_raise)
                
                # No previous betting - polarized range (bet bottom 10% and top 40%)
                if previous_bets == 0:
                    if relative_strength > 0.60 or relative_strength < 0.10:
                        bet_amount = get_safe_bet_size(0.75)
                        if min_raise <= bet_amount:
                            print(f"River bet with {'strong value' if relative_strength > 0.60 else 'bluff'}: {bet_amount} into {pot}", file=sys.stderr)
                            return RaiseAction(bet_amount)
                
                # One street bet - tighter range (bet bottom 8% and top 25%)
                elif previous_bets == 1:
                    if relative_strength > 0.75 or relative_strength < 0.08:
                        bet_amount = get_safe_bet_size(0.66)
                        if min_raise <= bet_amount:
                            print(f"River bet after 1 street: {bet_amount} into {pot}", file=sys.stderr)
                            return RaiseAction(bet_amount)
                
                # Two streets bet - very tight range (bet bottom 5% and top 15%)
                elif previous_bets == 2:
                    if relative_strength > 0.85 or relative_strength < 0.05:
                        bet_amount = get_safe_bet_size(0.5)
                        if min_raise <= bet_amount:
                            print(f"River bet after 2 streets: {bet_amount} into {pot}", file=sys.stderr)
                            return RaiseAction(bet_amount)
            
            # If we have a decent hand and facing a bet, call
            if CallAction in legal_actions and relative_strength >= required_equity:
                print(f"Calling river with sufficient equity ({relative_strength:.1%} >= {required_equity:.1%})", file=sys.stderr)
                return CallAction()
            
            # Default to checking if possible
            if CheckAction in legal_actions:
                print(f"Checking river by default", file=sys.stderr)
                return CheckAction()
            
            # Bluffing opportunity
            if relative_strength < 0.3 and board_favor == 'aggressor':
                if can_raise and min_raise <= int(pot * 0.5) <= max_raise:
                    bet_amount = int(pot * 0.5)
                    print(f"Bluffing river: {bet_amount} into {pot}", file=sys.stderr)
                    return RaiseAction(bet_amount)
            
            print(f"Folding river by default", file=sys.stderr)
            return FoldAction()


if __name__ == '__main__':
    run_bot(Player(), parse_args())
    
