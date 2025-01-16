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

        print(f"\n=== Action Decision ===", file=sys.stderr)
        print(f"Street: {street}", file=sys.stderr)
        print(f"Position: {'SB' if not bool(active) else 'BB'}", file=sys.stderr)
        print(f"Continue cost: {continue_cost}", file=sys.stderr)
        print(f"Legal actions: {legal_actions}", file=sys.stderr)
        print(f"My cards: {my_cards}", file=sys.stderr)
        print(f"Board cards: {board_cards}", file=sys.stderr)
        print(f"My bounty: {my_bounty}", file=sys.stderr)
       
        # Evaluate hand strength
        if street == 0:  # Preflop
            # Get absolute rank and range percentile from hand_strength
            # Convert face cards to consistent format
            card_ranks = []
            for card in my_cards:
                rank = card[0]
                if rank == 'T': rank = '10'
                if rank == 'J': rank = '11'
                if rank == 'Q': rank = '12'
                if rank == 'K': rank = '13'
                if rank == 'A': rank = '14'
                card_ranks.append(rank)
            
            # Sort ranks in descending order and convert back to original format
            ranks = sorted(card_ranks, key=int, reverse=True)
            ranks = ['T' if r == '10' else 'J' if r == '11' else 'Q' if r == '12' else 'K' if r == '13' else 'A' if r == '14' else r for r in ranks]
            
            suited = my_cards[0][1] == my_cards[1][1]
            hand_key = ''.join(ranks) + ('s' if suited else 'o')
            
            hand_stats = self.hand_strength.get(hand_key, [30.0, 169, 99.0])
            absolute_rank = hand_stats[1]
            range_percentile = hand_stats[2]  # Use the third index for range percentile
            
            # Check if we have a bounty card
            has_bounty = my_bounty in [card[0] for card in my_cards]
            
            # Print debug information
            print(f"Range percentile: {range_percentile}", file=sys.stderr)
            print(f"Absolute rank: {absolute_rank}, Has bounty: {has_bounty}", file=sys.stderr)
            
            if RaiseAction in legal_actions:
                min_raise, max_raise = round_state.raise_bounds()
                pot = my_contribution + opp_contribution
                
                # Define raise sizes based on number of previous raises
                raise_sizes = {
                    0: 2.5,  # First raise: 2.5x pot
                    1: 2.7,  # First reraise: 2.7x pot
                    2: 2.2,  # Second reraise: 2.2x pot
                    3: 4.0,  # Third+ reraise: 4x pot
                }
                
                # Calculate number of raises this street
                num_raises = (my_contribution + opp_contribution - 3) // 2  # -3 accounts for blinds
                num_raises = min(num_raises, 3)  # Cap at 3+ raises
                
                # Calculate raise amount
                multiplier = raise_sizes.get(num_raises, 4.0)  # Default to 4x for any further raises
                raise_amount = int(np.ceil(pot * multiplier))
                
                # Ensure raise is within bounds
                raise_amount = max(min_raise, min(max_raise, raise_amount))
                
                # Always raise with bounty cards or top 90% of hands
                if has_bounty or range_percentile <= 90:
                    print(f"Raising with bounty/strong hand to {raise_amount}", file=sys.stderr)
                    return RaiseAction(raise_amount)
                    
            elif CheckAction in legal_actions:
                print(f"Checking when given the option", file=sys.stderr)
                return CheckAction()
            
            elif CallAction in legal_actions:
                if has_bounty or range_percentile <= 90:
                    print(f"Calling with bounty/strong hand", file=sys.stderr)
                    return CallAction()
            
            print(f"Folding weak hand", file=sys.stderr)
            return FoldAction()

        else:  # Postflop streets
            # Evaluate our hand strength
            hole_cards = my_cards
            board = board_cards
            
            # Check for pair or better
            ranks_in_hand = [card[0] for card in hole_cards]
            ranks_on_board = [card[0] for card in board]
            all_ranks = ranks_in_hand + ranks_on_board
            
            # Convert face cards to numbers for proper comparison
            rank_values = {'2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, 'T':10, 'J':11, 'Q':12, 'K':13, 'A':14}
            numeric_ranks = [rank_values[r] for r in all_ranks]
            
            # Count rank frequencies
            rank_counts = {}
            for rank in numeric_ranks:
                rank_counts[rank] = rank_counts.get(rank, 0) + 1
            
            has_pair_or_better = any(count >= 2 for count in rank_counts.values())
            should_bet = has_pair_or_better and random.random() < 0.5
            
            print(f"Hand evaluation - Ranks: {all_ranks}, Has pair or better: {has_pair_or_better}", file=sys.stderr)
            
            # First handle checking if available
            if CheckAction in legal_actions:
                if not should_bet:
                    print(f"Checking with {ranks_in_hand} on {ranks_on_board}", file=sys.stderr)
                    return CheckAction()
            
            # Then handle betting if we want to bet
            if RaiseAction in legal_actions and should_bet:
                min_raise, max_raise = round_state.raise_bounds()
                pot = my_contribution + opp_contribution
                bet_amount = min(max_raise, int(pot * 0.5))  # Bet half pot
                print(f"Betting {bet_amount} with pair or better", file=sys.stderr)
                return RaiseAction(bet_amount)
            
            # If we can't check and don't want to bet, fold
            if FoldAction in legal_actions:
                print(f"Folding", file=sys.stderr)
                return FoldAction()
            
            # If we can't fold, call
            if CallAction in legal_actions:
                print(f"Calling - can't fold", file=sys.stderr)
                return CallAction()
            
            # If we get here somehow, check if possible
            if CheckAction in legal_actions:
                print(f"Checking by default", file=sys.stderr)
                return CheckAction()
            
            print(f"Defaulting to fold", file=sys.stderr)
            print("=====================\n", file=sys.stderr)
            return FoldAction()

    def evaluate_hand(self, hole_cards, community_cards, bounty_rank):
        import eval7
        import sys
        
        # Combine hole cards and community cards into a deck
        deck = hole_cards + community_cards
        deck_cards = [eval7.Card(card) for card in deck]
        
        # Log initial hand information
        print(f"\n=== Hand Evaluation ===", file=sys.stderr)
        print(f"Hole cards: {hole_cards}", file=sys.stderr)
        print(f"Community cards: {community_cards}", file=sys.stderr)
        print(f"Bounty rank: {bounty_rank}", file=sys.stderr)
        
        # Get the base strength from eval7
        base_strength = eval7.evaluate(deck_cards)
        print(f"Raw eval7 strength: {base_strength}", file=sys.stderr)
        
        # Normalize base strength to a 1-100 scale
        normalized_strength = int((np.log(base_strength) - np.log(344847)) / (np.log(135004160) - np.log(344847)) * 100)
        print(f"Normalized strength (0-100): {normalized_strength}", file=sys.stderr)
        
        # Check if bounty rank affects multiplier
        bounty_cards = [card[0] for card in hole_cards + community_cards]
        bounty_multiplier = 1.5 if bounty_rank in bounty_cards else 1.0
        print(f"Card ranks: {bounty_cards}", file=sys.stderr)
        print(f"Bounty multiplier: {bounty_multiplier}", file=sys.stderr)
        
        # Apply bounty multiplier
        adjusted_strength = normalized_strength * bounty_multiplier
        print(f"Adjusted strength: {adjusted_strength}", file=sys.stderr)
        
        # Final normalization
        final_strength = min(100, adjusted_strength)
        print(f"Final strength: {final_strength}", file=sys.stderr)
        print("=====================\n", file=sys.stderr)
        
        return final_strength


    def evaluate_preflop_hand(self, cards, bounty_rank):
        """
        Evaluates preflop hand strength considering bounty
        Returns win percentage adjusted for bounty cards
        """
        import sys
        
        # Sort cards by rank for easier comparison
        ranks = sorted([card[0] for card in cards], reverse=True)
        suited = cards[0][1] == cards[1][1]  # Check if cards share the same suit
        
        # Construct hand key (e.g., 'AKs' or 'AKo')
        hand_key = ''.join(ranks) + ('s' if suited else 'o')
        
        print(f"\n=== Preflop Hand Evaluation ===", file=sys.stderr)
        print(f"Hand: {cards}", file=sys.stderr)
        print(f"Constructed key: {hand_key}", file=sys.stderr)
        print(f"Bounty rank: {bounty_rank}", file=sys.stderr)
        
        # Get base strength [win_percentage, range_percentile]
        # Default to [30.0, 99.0] for unmapped hands (slightly better than worst hand)
        base_stats = self.hand_strength.get(hand_key, [30.0, 99.0])
        win_percentage = base_stats[0]
        range_percentile = base_stats[1]
        
        print(f"Base win percentage: {win_percentage}%", file=sys.stderr)
        print(f"Range percentile: {range_percentile} (lower is better)", file=sys.stderr)
        
        # Bounty multiplier if we have bounty card
        if bounty_rank in ranks:
            win_percentage *= 1.2  # Increase win percentage by 20% with bounty card
            print(f"Bounty card found! Adjusted win percentage: {win_percentage}%", file=sys.stderr)
        
        print("=====================\n", file=sys.stderr)
        
        # Return both win percentage and range percentile for better preflop decision making
        return win_percentage, range_percentile


if __name__ == '__main__':
    run_bot(Player(), parse_args())
    
