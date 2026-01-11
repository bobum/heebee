# Mini-Games System for Ren'Py Visual Novel
# This module provides a collection of mini-games with score tracking,
# difficulty levels, and reward system integration.

init python:
    import random
    import time

    #############################################
    # MINIGAME BASE CLASS
    #############################################

    class MinigameBase:
        """Base class for all mini-games with score tracking and difficulty."""

        # Difficulty levels
        EASY = 1
        MEDIUM = 2
        HARD = 3

        def __init__(self, name="Minigame"):
            self.name = name
            self.score = 0
            self.high_score = 0
            self.difficulty = self.MEDIUM
            self.is_active = False
            self.result = None  # "win", "lose", or None
            self.attempts = 0
            self.wins = 0
            self.losses = 0

        def start(self):
            """Start the minigame."""
            self.is_active = True
            self.result = None
            self.attempts += 1

        def end(self, won=False):
            """End the minigame and record result."""
            self.is_active = False
            if won:
                self.result = "win"
                self.wins += 1
                if self.score > self.high_score:
                    self.high_score = self.score
            else:
                self.result = "lose"
                self.losses += 1

        def reset(self):
            """Reset the current game state."""
            self.score = 0
            self.result = None

        def set_difficulty(self, level):
            """Set difficulty level (1=Easy, 2=Medium, 3=Hard)."""
            if level in [self.EASY, self.MEDIUM, self.HARD]:
                self.difficulty = level

        def get_difficulty_name(self):
            """Get human-readable difficulty name."""
            names = {1: "Easy", 2: "Medium", 3: "Hard"}
            return names.get(self.difficulty, "Medium")

        def add_score(self, points):
            """Add points to current score."""
            self.score += points

        def get_win_rate(self):
            """Calculate win rate percentage."""
            if self.attempts == 0:
                return 0
            return int((self.wins / self.attempts) * 100)


    #############################################
    # REWARD SYSTEM
    #############################################

    class RewardSystem:
        """Handles rewards for minigame completion."""

        @staticmethod
        def calculate_reward(minigame, base_gold=10, base_xp=5):
            """Calculate rewards based on game result and difficulty."""
            if minigame.result != "win":
                return {"gold": 0, "xp": 0, "items": []}

            multiplier = minigame.difficulty
            score_bonus = minigame.score // 10

            gold = (base_gold * multiplier) + score_bonus
            xp = (base_xp * multiplier) + (score_bonus // 2)

            # Chance for bonus items on higher difficulties
            items = []
            if minigame.difficulty >= 2 and random.random() < 0.3:
                items.append("Health Potion")
            if minigame.difficulty == 3 and random.random() < 0.2:
                items.append("Rare Token")

            return {"gold": gold, "xp": xp, "items": items}

        @staticmethod
        def apply_rewards(rewards):
            """Apply rewards to player (integrate with your game's systems)."""
            # These should connect to your game's inventory/stats system
            if hasattr(store, 'player_gold'):
                store.player_gold += rewards.get("gold", 0)
            if hasattr(store, 'player_xp'):
                store.player_xp += rewards.get("xp", 0)
            if hasattr(store, 'inventory') and rewards.get("items"):
                for item in rewards["items"]:
                    store.inventory.append(item)


    #############################################
    # NUMBER GUESSING GAME
    #############################################

    class NumberGuessingGame(MinigameBase):
        """Guess a number with hints (higher/lower)."""

        def __init__(self):
            super().__init__("Number Guessing")
            self.target = 0
            self.min_num = 1
            self.max_num = 100
            self.guesses_left = 7
            self.max_guesses = 7
            self.last_hint = ""
            self.guess_history = []

        def start(self):
            super().start()
            # Adjust range and guesses based on difficulty
            if self.difficulty == self.EASY:
                self.min_num, self.max_num = 1, 50
                self.max_guesses = 10
            elif self.difficulty == self.MEDIUM:
                self.min_num, self.max_num = 1, 100
                self.max_guesses = 7
            else:  # HARD
                self.min_num, self.max_num = 1, 200
                self.max_guesses = 6

            self.target = random.randint(self.min_num, self.max_num)
            self.guesses_left = self.max_guesses
            self.guess_history = []
            self.last_hint = "Guess a number between {} and {}!".format(self.min_num, self.max_num)

        def make_guess(self, guess):
            """Process a guess and return hint."""
            if not self.is_active:
                return "Game not active!"

            self.guesses_left -= 1
            self.guess_history.append(guess)

            if guess == self.target:
                points = (self.guesses_left + 1) * 10 * self.difficulty
                self.add_score(points)
                self.end(won=True)
                self.last_hint = "Correct! The number was {}!".format(self.target)
                return self.last_hint
            elif self.guesses_left <= 0:
                self.end(won=False)
                self.last_hint = "Out of guesses! The number was {}.".format(self.target)
                return self.last_hint
            elif guess < self.target:
                diff = self.target - guess
                if diff > 20:
                    self.last_hint = "Much higher!"
                elif diff > 10:
                    self.last_hint = "Higher!"
                else:
                    self.last_hint = "A little higher..."
            else:
                diff = guess - self.target
                if diff > 20:
                    self.last_hint = "Much lower!"
                elif diff > 10:
                    self.last_hint = "Lower!"
                else:
                    self.last_hint = "A little lower..."

            return self.last_hint


    #############################################
    # MEMORY CARD GAME
    #############################################

    class MemoryCardGame(MinigameBase):
        """Match pairs of cards by memory."""

        CARD_SYMBOLS = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]

        def __init__(self):
            super().__init__("Memory Match")
            self.grid_size = 4  # 4x4 grid
            self.cards = []
            self.revealed = []
            self.matched = []
            self.first_pick = None
            self.second_pick = None
            self.moves = 0
            self.pairs_found = 0
            self.total_pairs = 0
            self.can_pick = True

        def start(self):
            super().start()
            # Adjust grid size based on difficulty
            if self.difficulty == self.EASY:
                self.grid_size = 3  # 3x4 = 12 cards, 6 pairs
                num_pairs = 6
            elif self.difficulty == self.MEDIUM:
                self.grid_size = 4  # 4x4 = 16 cards, 8 pairs
                num_pairs = 8
            else:  # HARD
                self.grid_size = 4  # 4x5 = 20 cards, 10 pairs
                num_pairs = 10

            self.total_pairs = num_pairs
            self.pairs_found = 0
            self.moves = 0
            self.first_pick = None
            self.second_pick = None
            self.can_pick = True

            # Create card pairs
            symbols = self.CARD_SYMBOLS[:num_pairs]
            self.cards = symbols * 2
            random.shuffle(self.cards)

            # Track revealed and matched cards
            self.revealed = [False] * len(self.cards)
            self.matched = [False] * len(self.cards)

        def pick_card(self, index):
            """Pick a card at the given index."""
            if not self.is_active or not self.can_pick:
                return None
            if index < 0 or index >= len(self.cards):
                return None
            if self.revealed[index] or self.matched[index]:
                return None

            self.revealed[index] = True

            if self.first_pick is None:
                self.first_pick = index
                return self.cards[index]
            else:
                self.second_pick = index
                self.moves += 1
                self.can_pick = False
                return self.cards[index]

        def check_match(self):
            """Check if the two picked cards match."""
            if self.first_pick is None or self.second_pick is None:
                return None

            card1 = self.cards[self.first_pick]
            card2 = self.cards[self.second_pick]

            if card1 == card2:
                self.matched[self.first_pick] = True
                self.matched[self.second_pick] = True
                self.pairs_found += 1
                self.add_score(10 * self.difficulty)

                if self.pairs_found >= self.total_pairs:
                    # Bonus for fewer moves
                    min_moves = self.total_pairs
                    if self.moves <= min_moves * 2:
                        self.add_score(50 * self.difficulty)
                    self.end(won=True)

                self.first_pick = None
                self.second_pick = None
                self.can_pick = True
                return True
            else:
                return False

        def hide_unmatched(self):
            """Hide cards that didn't match."""
            if self.first_pick is not None:
                self.revealed[self.first_pick] = False
            if self.second_pick is not None:
                self.revealed[self.second_pick] = False
            self.first_pick = None
            self.second_pick = None
            self.can_pick = True

        def get_card_display(self, index):
            """Get display value for a card."""
            if self.matched[index] or self.revealed[index]:
                return self.cards[index]
            return "?"


    #############################################
    # ROCK-PAPER-SCISSORS GAME
    #############################################

    class RockPaperScissorsGame(MinigameBase):
        """Rock-Paper-Scissors against NPC."""

        ROCK = "rock"
        PAPER = "paper"
        SCISSORS = "scissors"
        CHOICES = [ROCK, PAPER, SCISSORS]

        def __init__(self):
            super().__init__("Rock-Paper-Scissors")
            self.rounds_to_win = 3
            self.player_wins = 0
            self.npc_wins = 0
            self.current_round = 0
            self.player_choice = None
            self.npc_choice = None
            self.round_result = None
            self.npc_name = "Opponent"
            self.npc_pattern = []  # For AI personality

        def start(self):
            super().start()
            # Adjust rounds based on difficulty
            if self.difficulty == self.EASY:
                self.rounds_to_win = 2
            elif self.difficulty == self.MEDIUM:
                self.rounds_to_win = 3
            else:  # HARD
                self.rounds_to_win = 4

            self.player_wins = 0
            self.npc_wins = 0
            self.current_round = 0
            self.npc_pattern = []

        def play_round(self, player_choice):
            """Play one round of RPS."""
            if not self.is_active:
                return None

            self.current_round += 1
            self.player_choice = player_choice

            # NPC choice - harder difficulties have smarter AI
            if self.difficulty == self.HARD and len(self.npc_pattern) >= 2:
                # Try to predict player's pattern
                if self.npc_pattern[-1] == self.npc_pattern[-2]:
                    # Player repeating? Counter their last choice
                    self.npc_choice = self._get_counter(self.npc_pattern[-1])
                else:
                    self.npc_choice = random.choice(self.CHOICES)
            else:
                self.npc_choice = random.choice(self.CHOICES)

            self.npc_pattern.append(player_choice)

            # Determine winner
            if player_choice == self.npc_choice:
                self.round_result = "tie"
            elif self._beats(player_choice, self.npc_choice):
                self.round_result = "win"
                self.player_wins += 1
                self.add_score(10 * self.difficulty)
            else:
                self.round_result = "lose"
                self.npc_wins += 1

            # Check for game end
            if self.player_wins >= self.rounds_to_win:
                self.add_score(25 * self.difficulty)  # Bonus for winning
                self.end(won=True)
            elif self.npc_wins >= self.rounds_to_win:
                self.end(won=False)

            return self.round_result

        def _beats(self, a, b):
            """Check if choice a beats choice b."""
            return (a == self.ROCK and b == self.SCISSORS) or \
                   (a == self.PAPER and b == self.ROCK) or \
                   (a == self.SCISSORS and b == self.PAPER)

        def _get_counter(self, choice):
            """Get the choice that beats the given choice."""
            counters = {
                self.ROCK: self.PAPER,
                self.PAPER: self.SCISSORS,
                self.SCISSORS: self.ROCK
            }
            return counters.get(choice, random.choice(self.CHOICES))

        def get_choice_emoji(self, choice):
            """Get display character for choice."""
            emojis = {
                self.ROCK: "[Rock]",
                self.PAPER: "[Paper]",
                self.SCISSORS: "[Scissors]"
            }
            return emojis.get(choice, "?")


    #############################################
    # SLIDING PUZZLE GAME
    #############################################

    class SlidingPuzzleGame(MinigameBase):
        """Classic sliding tile puzzle."""

        def __init__(self):
            super().__init__("Sliding Puzzle")
            self.size = 3  # 3x3 grid
            self.tiles = []
            self.empty_pos = 0
            self.moves = 0
            self.target_moves = 0

        def start(self):
            super().start()
            # Adjust size based on difficulty
            if self.difficulty == self.EASY:
                self.size = 3
                self.target_moves = 20
            elif self.difficulty == self.MEDIUM:
                self.size = 3
                self.target_moves = 15
            else:  # HARD
                self.size = 4
                self.target_moves = 30

            self.moves = 0
            total_tiles = self.size * self.size

            # Create solved state
            self.tiles = list(range(1, total_tiles)) + [0]  # 0 is empty
            self.empty_pos = total_tiles - 1

            # Shuffle with valid moves
            self._shuffle_puzzle()

        def _shuffle_puzzle(self):
            """Shuffle puzzle using valid moves."""
            shuffle_moves = 50 * self.difficulty
            for _ in range(shuffle_moves):
                valid_moves = self._get_valid_moves()
                if valid_moves:
                    move = random.choice(valid_moves)
                    self._swap(move)

        def _get_valid_moves(self):
            """Get positions that can move into empty space."""
            valid = []
            row, col = divmod(self.empty_pos, self.size)

            if row > 0:
                valid.append(self.empty_pos - self.size)  # Above
            if row < self.size - 1:
                valid.append(self.empty_pos + self.size)  # Below
            if col > 0:
                valid.append(self.empty_pos - 1)  # Left
            if col < self.size - 1:
                valid.append(self.empty_pos + 1)  # Right

            return valid

        def _swap(self, pos):
            """Swap tile at pos with empty space."""
            self.tiles[self.empty_pos], self.tiles[pos] = \
                self.tiles[pos], self.tiles[self.empty_pos]
            self.empty_pos = pos

        def move_tile(self, pos):
            """Try to move tile at position."""
            if not self.is_active:
                return False
            if pos not in self._get_valid_moves():
                return False

            self._swap(pos)
            self.moves += 1

            if self._is_solved():
                # Bonus for fewer moves
                if self.moves <= self.target_moves:
                    self.add_score(100 * self.difficulty)
                else:
                    self.add_score(50 * self.difficulty)
                self.end(won=True)

            return True

        def _is_solved(self):
            """Check if puzzle is in solved state."""
            total = self.size * self.size
            return self.tiles == list(range(1, total)) + [0]

        def get_tile(self, pos):
            """Get tile value at position."""
            return self.tiles[pos] if self.tiles[pos] != 0 else ""

        def can_move(self, pos):
            """Check if tile at position can be moved."""
            return pos in self._get_valid_moves()


    #############################################
    # PATTERN MATCHING GAME
    #############################################

    class PatternMatchGame(MinigameBase):
        """Simon-says style pattern matching."""

        COLORS = ["red", "blue", "green", "yellow"]

        def __init__(self):
            super().__init__("Pattern Match")
            self.pattern = []
            self.player_input = []
            self.current_length = 0
            self.max_length = 10
            self.showing_pattern = False
            self.current_show_index = 0

        def start(self):
            super().start()
            # Adjust based on difficulty
            if self.difficulty == self.EASY:
                self.max_length = 6
            elif self.difficulty == self.MEDIUM:
                self.max_length = 10
            else:  # HARD
                self.max_length = 15

            self.pattern = []
            self.player_input = []
            self.current_length = 0
            self._add_to_pattern()

        def _add_to_pattern(self):
            """Add a new color to the pattern."""
            self.pattern.append(random.choice(self.COLORS))
            self.current_length = len(self.pattern)
            self.player_input = []
            self.showing_pattern = True
            self.current_show_index = 0

        def get_next_pattern_color(self):
            """Get next color to show in pattern display."""
            if self.current_show_index < len(self.pattern):
                color = self.pattern[self.current_show_index]
                self.current_show_index += 1
                if self.current_show_index >= len(self.pattern):
                    self.showing_pattern = False
                return color
            return None

        def input_color(self, color):
            """Player inputs a color."""
            if not self.is_active or self.showing_pattern:
                return None

            self.player_input.append(color)
            index = len(self.player_input) - 1

            # Check if input matches pattern
            if self.player_input[index] != self.pattern[index]:
                self.end(won=False)
                return "wrong"

            # Check if pattern complete
            if len(self.player_input) >= len(self.pattern):
                self.add_score(self.current_length * 5 * self.difficulty)

                if self.current_length >= self.max_length:
                    self.add_score(50 * self.difficulty)  # Bonus
                    self.end(won=True)
                    return "complete"
                else:
                    self._add_to_pattern()
                    return "next_round"

            return "correct"


    #############################################
    # QUICK-TIME EVENT (QTE) SYSTEM
    #############################################

    class QTESystem(MinigameBase):
        """Quick-time events for action sequences."""

        KEYS = ["up", "down", "left", "right", "action"]

        def __init__(self):
            super().__init__("Quick-Time Event")
            self.sequence = []
            self.current_index = 0
            self.time_limit = 2.0  # Seconds per input
            self.start_time = 0
            self.successes = 0
            self.failures = 0
            self.max_failures = 3
            self.current_key = None
            self.sequence_length = 5
            self.is_waiting = False

        def start(self):
            super().start()
            # Adjust based on difficulty
            if self.difficulty == self.EASY:
                self.time_limit = 3.0
                self.sequence_length = 4
                self.max_failures = 4
            elif self.difficulty == self.MEDIUM:
                self.time_limit = 2.0
                self.sequence_length = 6
                self.max_failures = 3
            else:  # HARD
                self.time_limit = 1.5
                self.sequence_length = 8
                self.max_failures = 2

            self.sequence = [random.choice(self.KEYS) for _ in range(self.sequence_length)]
            self.current_index = 0
            self.successes = 0
            self.failures = 0
            self._next_prompt()

        def _next_prompt(self):
            """Move to next QTE prompt."""
            if self.current_index >= len(self.sequence):
                if self.failures < self.max_failures:
                    self.add_score(self.successes * 15 * self.difficulty)
                    self.end(won=True)
                else:
                    self.end(won=False)
                return

            self.current_key = self.sequence[self.current_index]
            self.start_time = time.time()
            self.is_waiting = True

        def check_input(self, key_pressed):
            """Check player's input against current QTE."""
            if not self.is_active or not self.is_waiting:
                return None

            elapsed = time.time() - self.start_time

            if elapsed > self.time_limit:
                self.failures += 1
                self.is_waiting = False
                if self.failures >= self.max_failures:
                    self.end(won=False)
                    return "fail_timeout"
                self.current_index += 1
                self._next_prompt()
                return "timeout"

            if key_pressed == self.current_key:
                self.successes += 1
                self.add_score(10 * self.difficulty)
                # Bonus for quick response
                if elapsed < self.time_limit / 2:
                    self.add_score(5 * self.difficulty)
                self.is_waiting = False
                self.current_index += 1
                self._next_prompt()
                return "success"
            else:
                self.failures += 1
                self.is_waiting = False
                if self.failures >= self.max_failures:
                    self.end(won=False)
                    return "fail_wrong"
                self.current_index += 1
                self._next_prompt()
                return "wrong"

        def get_time_remaining(self):
            """Get remaining time for current prompt."""
            if not self.is_waiting:
                return 0
            elapsed = time.time() - self.start_time
            return max(0, self.time_limit - elapsed)

        def get_key_display(self, key):
            """Get display text for a key."""
            displays = {
                "up": "[UP]",
                "down": "[DOWN]",
                "left": "[LEFT]",
                "right": "[RIGHT]",
                "action": "[ACTION]"
            }
            return displays.get(key, key.upper())


    #############################################
    # GLOBAL MINIGAME INSTANCES
    #############################################

    # Create global instances for use in game
    number_game = NumberGuessingGame()
    memory_game = MemoryCardGame()
    rps_game = RockPaperScissorsGame()
    puzzle_game = SlidingPuzzleGame()
    pattern_game = PatternMatchGame()
    qte_system = QTESystem()

    reward_system = RewardSystem()


#############################################
# MINIGAME SCREENS
#############################################

# Difficulty Selection Screen
screen minigame_difficulty(game):
    modal True

    frame:
        xalign 0.5
        yalign 0.5
        xpadding 50
        ypadding 30

        vbox:
            spacing 20

            text "Select Difficulty" size 36 xalign 0.5

            null height 10

            textbutton "Easy" action [Function(game.set_difficulty, 1), Return("easy")] xalign 0.5
            textbutton "Medium" action [Function(game.set_difficulty, 2), Return("medium")] xalign 0.5
            textbutton "Hard" action [Function(game.set_difficulty, 3), Return("hard")] xalign 0.5

            null height 10

            textbutton "Cancel" action Return("cancel") xalign 0.5


# Reward Display Screen
screen minigame_rewards(rewards):
    modal True

    frame:
        xalign 0.5
        yalign 0.5
        xpadding 50
        ypadding 30

        vbox:
            spacing 15

            text "Rewards!" size 36 xalign 0.5 color "#FFD700"

            null height 10

            if rewards["gold"] > 0:
                text "Gold: +[rewards[gold]]" xalign 0.5
            if rewards["xp"] > 0:
                text "XP: +[rewards[xp]]" xalign 0.5
            if rewards["items"]:
                text "Items:" xalign 0.5
                for item in rewards["items"]:
                    text "  - [item]" xalign 0.5

            null height 10

            textbutton "Collect" action Return() xalign 0.5


# Number Guessing Game Screen
screen number_guessing_game():
    modal True

    default guess_input = ""

    frame:
        xalign 0.5
        yalign 0.5
        xpadding 50
        ypadding 30
        xminimum 400

        vbox:
            spacing 15

            text "Number Guessing Game" size 30 xalign 0.5
            text "Difficulty: [number_game.get_difficulty_name()]" size 18 xalign 0.5

            null height 10

            text "Guesses Left: [number_game.guesses_left]" xalign 0.5
            text "[number_game.last_hint]" xalign 0.5

            null height 10

            if number_game.is_active:
                hbox:
                    xalign 0.5
                    spacing 10

                    for num in range(1, 11):
                        textbutton "[num]0" action Return(num * 10)

                hbox:
                    xalign 0.5
                    spacing 10

                    for num in range(1, 11):
                        $ display_num = num if num < 10 else 10
                        textbutton "[display_num]" action Return(num)
            else:
                text "Score: [number_game.score]" size 24 xalign 0.5
                textbutton "Close" action Return("close") xalign 0.5


# Memory Card Game Screen
screen memory_card_game():
    modal True

    frame:
        xalign 0.5
        yalign 0.5
        xpadding 30
        ypadding 30

        vbox:
            spacing 15

            text "Memory Match" size 30 xalign 0.5
            text "Pairs: [memory_game.pairs_found]/[memory_game.total_pairs] | Moves: [memory_game.moves]" xalign 0.5

            null height 10

            if memory_game.is_active:
                # Card grid
                $ cols = 4 if memory_game.difficulty >= 2 else 3
                $ rows = (len(memory_game.cards) + cols - 1) // cols

                grid cols rows:
                    spacing 10
                    xalign 0.5

                    for i in range(len(memory_game.cards)):
                        $ card_text = memory_game.get_card_display(i)
                        $ is_matched = memory_game.matched[i]
                        $ can_click = memory_game.can_pick and not memory_game.revealed[i] and not is_matched

                        textbutton "[card_text]":
                            xminimum 50
                            yminimum 50
                            if can_click:
                                action Return(("pick", i))
                            else:
                                action NullAction()

                    # Fill empty grid spaces
                    for i in range(rows * cols - len(memory_game.cards)):
                        null

                null height 10

                if not memory_game.can_pick and memory_game.first_pick is not None:
                    textbutton "Check Match" action Return(("check", None)) xalign 0.5
            else:
                text "Game Over!" size 24 xalign 0.5
                text "Score: [memory_game.score]" xalign 0.5
                textbutton "Close" action Return(("close", None)) xalign 0.5


# Rock-Paper-Scissors Screen
screen rps_game_screen():
    modal True

    frame:
        xalign 0.5
        yalign 0.5
        xpadding 50
        ypadding 30
        xminimum 400

        vbox:
            spacing 15

            text "Rock-Paper-Scissors" size 30 xalign 0.5
            text "First to [rps_game.rounds_to_win] wins!" size 18 xalign 0.5

            null height 10

            hbox:
                xalign 0.5
                spacing 30
                text "You: [rps_game.player_wins]"
                text "Opponent: [rps_game.npc_wins]"

            null height 10

            if rps_game.is_active:
                if rps_game.round_result:
                    text "You chose: [rps_game.get_choice_emoji(rps_game.player_choice)]" xalign 0.5
                    text "Opponent chose: [rps_game.get_choice_emoji(rps_game.npc_choice)]" xalign 0.5
                    if rps_game.round_result == "win":
                        text "You win this round!" color "#00FF00" xalign 0.5
                    elif rps_game.round_result == "lose":
                        text "You lose this round!" color "#FF0000" xalign 0.5
                    else:
                        text "It's a tie!" xalign 0.5
                    null height 10

                text "Choose your move:" xalign 0.5

                hbox:
                    xalign 0.5
                    spacing 20
                    textbutton "Rock" action Return("rock")
                    textbutton "Paper" action Return("paper")
                    textbutton "Scissors" action Return("scissors")
            else:
                if rps_game.result == "win":
                    text "Victory!" size 28 color "#00FF00" xalign 0.5
                else:
                    text "Defeat!" size 28 color "#FF0000" xalign 0.5
                text "Score: [rps_game.score]" xalign 0.5
                textbutton "Close" action Return("close") xalign 0.5


# Sliding Puzzle Screen
screen sliding_puzzle_screen():
    modal True

    frame:
        xalign 0.5
        yalign 0.5
        xpadding 30
        ypadding 30

        vbox:
            spacing 15

            text "Sliding Puzzle" size 30 xalign 0.5
            text "Moves: [puzzle_game.moves]" xalign 0.5

            null height 10

            if puzzle_game.is_active:
                grid puzzle_game.size puzzle_game.size:
                    spacing 5
                    xalign 0.5

                    for i in range(puzzle_game.size * puzzle_game.size):
                        $ tile_val = puzzle_game.get_tile(i)
                        $ can_click = puzzle_game.can_move(i)

                        if tile_val:
                            textbutton "[tile_val]":
                                xminimum 60
                                yminimum 60
                                if can_click:
                                    action Return(("move", i))
                                else:
                                    action NullAction()
                        else:
                            frame:
                                xminimum 60
                                yminimum 60
                                background "#333333"
            else:
                text "Puzzle Solved!" size 24 color "#00FF00" xalign 0.5
                text "Score: [puzzle_game.score]" xalign 0.5
                textbutton "Close" action Return(("close", None)) xalign 0.5


# Pattern Match Screen
screen pattern_match_screen():
    modal True

    frame:
        xalign 0.5
        yalign 0.5
        xpadding 50
        ypadding 30
        xminimum 450

        vbox:
            spacing 15

            text "Pattern Match" size 30 xalign 0.5
            text "Level: [pattern_game.current_length]" xalign 0.5

            null height 10

            if pattern_game.is_active:
                if pattern_game.showing_pattern:
                    text "Watch the pattern!" size 20 xalign 0.5
                    textbutton "Show Next" action Return(("show", None)) xalign 0.5
                else:
                    text "Repeat the pattern!" size 20 xalign 0.5
                    text "Input: [len(pattern_game.player_input)]/[len(pattern_game.pattern)]" xalign 0.5

                    null height 10

                    hbox:
                        xalign 0.5
                        spacing 15

                        textbutton "Red":
                            action Return(("input", "red"))
                            background "#FF0000"
                        textbutton "Blue":
                            action Return(("input", "blue"))
                            background "#0000FF"
                        textbutton "Green":
                            action Return(("input", "green"))
                            background "#00FF00"
                        textbutton "Yellow":
                            action Return(("input", "yellow"))
                            background "#FFFF00"
            else:
                if pattern_game.result == "win":
                    text "Pattern Complete!" size 24 color "#00FF00" xalign 0.5
                else:
                    text "Wrong Pattern!" size 24 color "#FF0000" xalign 0.5
                text "Score: [pattern_game.score]" xalign 0.5
                textbutton "Close" action Return(("close", None)) xalign 0.5


# QTE Screen
screen qte_screen():
    modal True

    frame:
        xalign 0.5
        yalign 0.5
        xpadding 50
        ypadding 30
        xminimum 400

        vbox:
            spacing 15

            text "Quick-Time Event!" size 30 xalign 0.5

            hbox:
                xalign 0.5
                spacing 20
                text "Success: [qte_system.successes]" color "#00FF00"
                text "Failures: [qte_system.failures]/[qte_system.max_failures]" color "#FF0000"

            null height 10

            if qte_system.is_active and qte_system.is_waiting:
                $ current_display = qte_system.get_key_display(qte_system.current_key)
                text "Press:" size 24 xalign 0.5
                text "[current_display]" size 40 xalign 0.5 color "#FFD700"

                $ time_left = qte_system.get_time_remaining()
                bar value time_left range qte_system.time_limit xalign 0.5 xmaximum 300

                null height 10

                hbox:
                    xalign 0.5
                    spacing 10

                    textbutton "UP" action Return("up")
                    textbutton "DOWN" action Return("down")
                    textbutton "LEFT" action Return("left")
                    textbutton "RIGHT" action Return("right")
                    textbutton "ACTION" action Return("action")

            elif not qte_system.is_active:
                if qte_system.result == "win":
                    text "Success!" size 28 color "#00FF00" xalign 0.5
                else:
                    text "Failed!" size 28 color "#FF0000" xalign 0.5
                text "Score: [qte_system.score]" xalign 0.5
                textbutton "Close" action Return("close") xalign 0.5


# Minigame Selection Menu
screen minigame_menu():
    modal True

    frame:
        xalign 0.5
        yalign 0.5
        xpadding 50
        ypadding 30

        vbox:
            spacing 20

            text "Mini-Games" size 36 xalign 0.5

            null height 10

            textbutton "Number Guessing" action Return("number") xalign 0.5
            textbutton "Memory Match" action Return("memory") xalign 0.5
            textbutton "Rock-Paper-Scissors" action Return("rps") xalign 0.5
            textbutton "Sliding Puzzle" action Return("puzzle") xalign 0.5
            textbutton "Pattern Match" action Return("pattern") xalign 0.5
            textbutton "Quick-Time Event" action Return("qte") xalign 0.5

            null height 10

            textbutton "Back" action Return("back") xalign 0.5


#############################################
# MINIGAME LABELS (Entry Points)
#############################################

label play_minigame_menu:
    $ selected_game = renpy.call_screen("minigame_menu")

    if selected_game == "number":
        jump play_number_game
    elif selected_game == "memory":
        jump play_memory_game
    elif selected_game == "rps":
        jump play_rps_game
    elif selected_game == "puzzle":
        jump play_puzzle_game
    elif selected_game == "pattern":
        jump play_pattern_game
    elif selected_game == "qte":
        jump play_qte_game

    return


label play_number_game:
    $ diff = renpy.call_screen("minigame_difficulty", number_game)
    if diff == "cancel":
        return

    $ number_game.start()

    while number_game.is_active:
        $ guess = renpy.call_screen("number_guessing_game")
        if guess == "close":
            jump number_game_end
        $ number_game.make_guess(guess)

    label number_game_end:
    $ result = renpy.call_screen("number_guessing_game")

    if number_game.result == "win":
        $ rewards = reward_system.calculate_reward(number_game)
        $ reward_system.apply_rewards(rewards)
        call screen minigame_rewards(rewards)

    return


label play_memory_game:
    $ diff = renpy.call_screen("minigame_difficulty", memory_game)
    if diff == "cancel":
        return

    $ memory_game.start()

    while memory_game.is_active:
        $ action = renpy.call_screen("memory_card_game")
        $ action_type, index = action

        if action_type == "close":
            jump memory_game_end
        elif action_type == "pick":
            $ memory_game.pick_card(index)
            if memory_game.first_pick is not None and memory_game.second_pick is not None:
                $ matched = memory_game.check_match()
                if matched == False:
                    pause 0.5
                    $ memory_game.hide_unmatched()
        elif action_type == "check":
            $ matched = memory_game.check_match()
            if matched == False:
                pause 0.5
                $ memory_game.hide_unmatched()

    label memory_game_end:
    $ result = renpy.call_screen("memory_card_game")

    if memory_game.result == "win":
        $ rewards = reward_system.calculate_reward(memory_game)
        $ reward_system.apply_rewards(rewards)
        call screen minigame_rewards(rewards)

    return


label play_rps_game:
    $ diff = renpy.call_screen("minigame_difficulty", rps_game)
    if diff == "cancel":
        return

    $ rps_game.start()

    while rps_game.is_active:
        $ choice = renpy.call_screen("rps_game_screen")
        if choice == "close":
            jump rps_game_end
        if choice in ["rock", "paper", "scissors"]:
            $ rps_game.play_round(choice)

    label rps_game_end:
    $ result = renpy.call_screen("rps_game_screen")

    if rps_game.result == "win":
        $ rewards = reward_system.calculate_reward(rps_game)
        $ reward_system.apply_rewards(rewards)
        call screen minigame_rewards(rewards)

    return


label play_puzzle_game:
    $ diff = renpy.call_screen("minigame_difficulty", puzzle_game)
    if diff == "cancel":
        return

    $ puzzle_game.start()

    while puzzle_game.is_active:
        $ action = renpy.call_screen("sliding_puzzle_screen")
        $ action_type, index = action

        if action_type == "close":
            jump puzzle_game_end
        elif action_type == "move":
            $ puzzle_game.move_tile(index)

    label puzzle_game_end:
    $ result = renpy.call_screen("sliding_puzzle_screen")

    if puzzle_game.result == "win":
        $ rewards = reward_system.calculate_reward(puzzle_game)
        $ reward_system.apply_rewards(rewards)
        call screen minigame_rewards(rewards)

    return


label play_pattern_game:
    $ diff = renpy.call_screen("minigame_difficulty", pattern_game)
    if diff == "cancel":
        return

    $ pattern_game.start()

    while pattern_game.is_active:
        $ action = renpy.call_screen("pattern_match_screen")
        $ action_type, value = action

        if action_type == "close":
            jump pattern_game_end
        elif action_type == "show":
            $ color = pattern_game.get_next_pattern_color()
            if color:
                "[color]"
        elif action_type == "input":
            $ result = pattern_game.input_color(value)

    label pattern_game_end:
    $ result = renpy.call_screen("pattern_match_screen")

    if pattern_game.result == "win":
        $ rewards = reward_system.calculate_reward(pattern_game)
        $ reward_system.apply_rewards(rewards)
        call screen minigame_rewards(rewards)

    return


label play_qte_game:
    $ diff = renpy.call_screen("minigame_difficulty", qte_system)
    if diff == "cancel":
        return

    $ qte_system.start()

    while qte_system.is_active:
        $ key = renpy.call_screen("qte_screen")
        if key == "close":
            jump qte_game_end
        $ qte_system.check_input(key)

    label qte_game_end:
    $ result = renpy.call_screen("qte_screen")

    if qte_system.result == "win":
        $ rewards = reward_system.calculate_reward(qte_system)
        $ reward_system.apply_rewards(rewards)
        call screen minigame_rewards(rewards)

    return


# Quick QTE for action scenes (can be called from dialogue)
label quick_qte(sequence_length=3, difficulty=2):
    $ qte_system.set_difficulty(difficulty)
    $ qte_system.sequence_length = sequence_length
    $ qte_system.start()

    while qte_system.is_active:
        $ key = renpy.call_screen("qte_screen")
        if key != "close":
            $ qte_system.check_input(key)

    $ qte_success = qte_system.result == "win"
    return qte_success
