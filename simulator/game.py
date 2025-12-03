# game.py
import random
from collections import Counter, deque

# Action constants
A_DRAW = 0
A_PLAY_SKIP = 1
A_PLAY_ATTACK = 2
A_PLAY_SHUFFLE = 3
A_PLAY_NOPE = 4
A_PLAY_SEE_FUTURE = 5
A_PLAY_CAT = 6
A_PLAY_DEFUSE = 7

ACTION_NAMES = {
    A_DRAW: "DRAW",
    A_PLAY_SKIP: "PLAY_SKIP",
    A_PLAY_ATTACK: "PLAY_ATTACK",
    A_PLAY_SHUFFLE: "PLAY_SHUFFLE",
    A_PLAY_NOPE: "PLAY_NOPE",
    A_PLAY_SEE_FUTURE: "PLAY_SEE_FUTURE",
    A_PLAY_CAT: "PLAY_CAT",
    A_PLAY_DEFUSE: "PLAY_DEFUSE",
}

# Simplified card types
CARD_SKIP = "Skip"
CARD_ATTACK = "Attack"
CARD_SHUFFLE = "Shuffle"
CARD_NOPE = "Nope"
CARD_SEE_FUTURE = "SeeFuture"
CARD_CAT = "Cat"
CARD_DEFUSE = "Defuse"
CARD_BOMB = "Bomb"

ALL_ACTION_CARDS = [CARD_SKIP, CARD_ATTACK, CARD_SHUFFLE, CARD_NOPE, CARD_SEE_FUTURE, CARD_CAT]

class SimpleGame:
    """
    Minimal Exploding Kittens simulator suitable for generating transitions.
    - players: number of players
    - start_player: which index starts (default 0)
    """

    def __init__(self, players=5, rng=None):
        self.players = players
        self.rng = rng or random.Random()
        self.reset()

    def reset(self):
        # state containers
        self.hands = [[] for _ in range(self.players)]
        self.defuse_counts = [0] * self.players
        self.is_alive = [True] * self.players
        self.discard = []
        self.turn = 0  # current player index
        self.attack_counter = 0  # if attack used, next player must draw N times -> simplified handling in step
        self._build_and_deal()

    def _build_and_deal(self):
        # Build deck: lots of action cards, set aside bombs and defuses
        deck = []
        # add action cards copies
        for _ in range(6):  # 6 copies of each action card (adjustable)
            for c in ALL_ACTION_CARDS:
                deck.append(c)
        self.rng.shuffle(deck)

        # Pools
        bomb_pool = [CARD_BOMB + f"_{i}" for i in range(4)]  # 4 bombs
        defuse_pool = [CARD_DEFUSE + f"_{i}" for i in range(6)]  # 6 defuses total

        # Deal 7 regular cards to each player
        for i in range(7):
            for p in range(self.players):
                if deck:
                    self.hands[p].append(deck.pop())
                else:
                    # if deck empty (unlikely here), shuffle discard into deck
                    deck = list(self.discard)
                    self.discard = []
                    self.rng.shuffle(deck)
                    if deck:
                        self.hands[p].append(deck.pop())

        # Give 1 defuse to each player
        for p in range(self.players):
            if defuse_pool:
                card = defuse_pool.pop()
                self.hands[p].append(CARD_DEFUSE)
                self.defuse_counts[p] += 1

        # Per PDF: shuffle two extra defuses into deck (if available)
        extras_to_shuffle_back = min(2, len(defuse_pool))
        for _ in range(extras_to_shuffle_back):
            deck.append(CARD_DEFUSE)
            defuse_pool.pop()

        # Insert bombs = players - 1 randomly into the deck
        bombs_to_insert = max(0, self.players - 1)
        for _ in range(bombs_to_insert):
            if bomb_pool:
                b = bomb_pool.pop()
                pos = self.rng.randrange(len(deck) + 1)
                deck.insert(pos, CARD_BOMB)

        self.deck = deque(deck)
        # Discard is empty at start
        self.discard = []
        # reset turn to 0
        self.turn = 0

    def current_player(self):
        return self.turn

    def alive_count(self):
        return sum(1 for x in self.is_alive if x)

    def _next_alive(self, start):
        i = (start + 1) % self.players
        while not self.is_alive[i]:
            i = (i + 1) % self.players
        return i

    def _remove_if_empty_hand(self, p):
        # Not used now; placeholder
        pass

    def available_actions(self, player_index):
        """
        Returns list of available actions for the given player (we return the full fixed action space).
        Agents can choose actions they don't have in hand; game will treat invalid play as no-op.
        """
        return list(ACTION_NAMES.keys())

    def step(self, action):
        """
        Execute an action for current player.
        Returns: (reward, done, info)
        - reward is immediate reward for the acting player (0 normal, -1 exploded, +1 if they won)
        - done is True if game ended
        - info: dict with state info
        """
        p = self.turn
        reward = 0
        info = {}
        done = False

        if not self.is_alive[p]:
            # skip dead players
            self.turn = self._next_alive(p)
            return 0, False, {"skipped_dead": True}

        # Handle actions
        if action == A_DRAW:
            # Draw from top of deck (if deck empty, game ends in draw)
            if not self.deck:
                # deck depleted - we treat as draw (no winner)
                done = True
                info['reason'] = 'deck_empty'
                self.turn = self._next_alive(p)
                return 0, done, info

            card = self.deck.popleft()
            # If drawn defuse, add to hand/defuse count
            if card == CARD_DEFUSE:
                self.hands[p].append(CARD_DEFUSE)
                self.defuse_counts[p] += 1
                info['drawn'] = CARD_DEFUSE
            elif card == CARD_BOMB:
                # Exploding kitten
                info['drawn'] = CARD_BOMB
                if self.defuse_counts[p] > 0:
                    # Use a defuse (we simply decrement; preferentially remove a Defuse card from hand)
                    self.defuse_counts[p] -= 1
                    # remove one defuse card from hand if exists
                    try:
                        idx = self.hands[p].index(CARD_DEFUSE)
                        self.hands[p].pop(idx)
                    except ValueError:
                        pass
                    # reinsert bomb randomly into deck
                    pos = self.rng.randrange(len(self.deck) + 1) if self.deck else 0
                    self.deck.insert(pos, CARD_BOMB)
                    info['defused'] = True
                else:
                    # explode: player eliminated
                    self.is_alive[p] = False
                    reward = -1
                    self.hands[p] = []
                    self.defuse_counts[p] = 0
                    info['exploded'] = True
                    if self.alive_count() == 1:
                        # winner is last alive
                        winner = [i for i,alive in enumerate(self.is_alive) if alive][0]
                        # reward the winner later (not here)
                        done = True
                        info['winner'] = winner
            else:
                # Normal action card
                self.hands[p].append(card)
                info['drawn'] = card

            # After draw, drawing ends the player's turn (unless they exploded)
            if not info.get('exploded', False):
                # Advance to next alive
                self.turn = self._next_alive(p)
            else:
                # If exploded, skip to next alive (handled above)
                if self.alive_count() == 1:
                    done = True
                else:
                    self.turn = self._next_alive(p)

        else:
            # Play action: verify if player has card; if not treat as no-op
            played = False
            if action == A_PLAY_DEFUSE:
                if CARD_DEFUSE in self.hands[p]:
                    # use a defuse proactively (rare)
                    self.hands[p].remove(CARD_DEFUSE)
                    self.defuse_counts[p] = max(0, self.defuse_counts[p] - 1)
                    self.discard.append(CARD_DEFUSE)
                    played = True
                else:
                    played = False
            elif action == A_PLAY_SKIP:
                # If has Skip card, discard it and end turn (next player)
                if CARD_SKIP in self.hands[p]:
                    self.hands[p].remove(CARD_SKIP)
                    self.discard.append(CARD_SKIP)
                    played = True
                    # end turn without drawing: advance to next alive
                    self.turn = self._next_alive(p)
                else:
                    played = False
            elif action == A_PLAY_ATTACK:
                if CARD_ATTACK in self.hands[p]:
                    self.hands[p].remove(CARD_ATTACK)
                    self.discard.append(CARD_ATTACK)
                    played = True
                    # attack: next player must draw 2 times (we simulate by forcing next player to take two draws in their turn)
                    # We implement attack by recording attack_counter and advancing to next player
                    self.attack_counter = 2
                    self.turn = self._next_alive(p)
                else:
                    played = False
            elif action == A_PLAY_SHUFFLE:
                if CARD_SHUFFLE in self.hands[p]:
                    self.hands[p].remove(CARD_SHUFFLE)
                    self.discard.append(CARD_SHUFFLE)
                    self.rng.shuffle(self.deck)
                    played = True
                    # playing shuffle doesn't end your action-per-turn powers; you may continue; for simplicity we pass to next
                    self.turn = self._next_alive(p)
                else:
                    played = False
            elif action == A_PLAY_NOPE:
                if CARD_NOPE in self.hands[p]:
                    self.hands[p].remove(CARD_NOPE)
                    self.discard.append(CARD_NOPE)
                    played = True
                    # No-op behavior (cancels previous action) is complex in multi-agent sim; we simply treat as pass-to-next
                    self.turn = self._next_alive(p)
                else:
                    played = False
            elif action == A_PLAY_SEE_FUTURE:
                if CARD_SEE_FUTURE in self.hands[p]:
                    self.hands[p].remove(CARD_SEE_FUTURE)
                    self.discard.append(CARD_SEE_FUTURE)
                    # peek top 3 - we reveal to agent state (info)
                    peek = [self.deck[i] if i < len(self.deck) else None for i in range(3)]
                    info['peek'] = peek
                    played = True
                    # human may continue to play cards - to keep things simple, advance to next player
                    self.turn = self._next_alive(p)
                else:
                    played = False
            elif action == A_PLAY_CAT:
                if CARD_CAT in self.hands[p]:
                    self.hands[p].remove(CARD_CAT)
                    self.discard.append(CARD_CAT)
                    played = True
                    self.turn = self._next_alive(p)
                else:
                    played = False
            else:
                played = False

            # if played false (invalid play), we treat as no-op and do not advance turn
            if not played:
                info['invalid_play'] = True
                # to avoid infinite loops, advance to next player (treating invalid play as a pass)
                self.turn = self._next_alive(p)

        # After each action, check for terminal condition (only one alive)
        if self.alive_count() == 1:
            done = True
            winner = [i for i,alive in enumerate(self.is_alive) if alive][0]
            info['winner'] = winner
            # reward winner with +1 (we'll return that reward for action that caused terminal)
            if winner == p and reward == 0:
                # If acting player is also the winner (rare immediate win case), mark +1
                reward = 1

        return reward, done, info

    def get_canonical_state(self, player_index):
        """
        Return a small dict of features representing the state from `player_index` perspective.
        Includes:
            - current player's hand size
            - current player's defuse count
            - deck size
            - number of alive players
            - bitmask of alive players
            - top-3 deck peek
        Use this for encoding into integer state IDs.
        """
        top3 = tuple(list(self.deck)[:3])
        alive_mask = tuple(int(x) for x in self.is_alive)
        state = {
            "player": player_index,
            "hand_size": len(self.hands[player_index]),
            "defuse": self.defuse_counts[player_index],
            "deck_size": len(self.deck),
            "alive_count": self.alive_count(),
            "alive_mask": alive_mask,
            "top3": top3
        }
        return state
