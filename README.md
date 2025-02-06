# Pokerbots Competition MIT 2025

Welcome to the Pokerbots Competition MIT 2025 repository. This project is designed for the MIT Pokerbots competition, where participants develop autonomous poker-playing bots. The competition involves creating a bot that can play a variant of Texas Hold'em with unique rules and strategies.

## Project Structure

The project is organized into several key components:

- **Engine**: The core game engine that simulates poker rounds and manages game states.
- **Player**: The bot logic that decides actions based on the current game state.
- **Skeleton**: Contains the base classes and interfaces for actions, states, and bot behavior.
- **Logs**: Game logs for analyzing bot performance and decision-making.

## Key Files and Directories

### Engine

The `engine.py` file contains the main game engine logic. It handles the game flow, including dealing cards, managing player actions, and determining the outcome of each round.

```python:engine.py
startLine: 1
endLine: 33
```

### Player

The `player.py` file contains the logic for the poker bot. It includes methods for preflop and postflop decision-making, hand evaluation, and board analysis.

```python:python_skeleton/player.py
startLine: 1
endLine: 16
```

### Actions and States

The `skeleton` directory includes definitions for actions (e.g., Fold, Call, Raise) and game states (e.g., GameState, RoundState). These are used to structure the bot's decision-making process.

```python:default/player.py
startLine: 1
endLine: 10
```

### Game Logs

The `gamelog.txt` file records detailed logs of each game round, including player actions, card distributions, and outcomes. This is useful for debugging and improving bot strategies.

```gamelog.txt
startLine: 1
endLine: 60
```

## Game Rules

The competition uses a variant of Texas Hold'em with the following rules:

- Each player is assigned a bounty rank, which affects the payout if their bounty card appears during the round.
- The starting stack for each round is 400 chips, with blinds set at 1 (small blind) and 2 (big blind).
- Players can perform actions such as Fold, Call, Raise, and Check based on the current game state.

For more detailed rules, refer to the `GAME_RULES` section in the `player_chatbot/player.py` file.

```python:player_chatbot/player.py
startLine: 35
endLine: 55
```

## Getting Started

To get started with the project, follow these steps:

1. **Clone the Repository**: Clone the repository to your local machine using `git clone`.
2. **Install Dependencies**: Ensure you have Python and necessary libraries installed. Use `pip install -r requirements.txt` if a requirements file is provided.
3. **Run the Bot**: Execute the main script to start the bot and simulate games. Use the provided scripts or create your own to test different strategies.

## Contributing

Contributions to the project are welcome. If you have ideas for improving the bot's strategy or optimizing the engine, feel free to submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## References

For more information on the algorithms and strategies used in this project, refer to the following papers:

- [1] Martin Zinkevich et al., "Regret minimization in games with incomplete information," 2008.
- [2] Marc Lanctot et al., "Monte Carlo sampling for regret minimization in extensive games," 2009.

```markdown:cpp_skeleton/cpp-cfr-master/README.md
startLine: 73
endLine: 77
```

We hope you enjoy participating in the Pokerbots Competition MIT 2025 and look forward to seeing your innovative strategies!



