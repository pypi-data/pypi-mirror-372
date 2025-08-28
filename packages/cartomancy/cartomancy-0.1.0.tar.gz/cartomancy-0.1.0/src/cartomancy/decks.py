import random
from .constants import PIPS, SUITS, TAROT_TRUMPS, MINCHIATE_TRUMPS

def build_deck(query):
    minor_cards = [f"{pip} of {suit}" for pip in PIPS for suit in SUITS]

    if query.deck == "tarot":
        major_arcana = list(TAROT_TRUMPS.keys())
        return minor_cards + major_arcana

    elif query.deck == "minchiate":
        trump_cards = list(MINCHIATE_TRUMPS.keys())
        return minor_cards + trump_cards


def shuffle_and_pull(deck, query):
    random.shuffle(deck)
    pull=deck[:query.N]
    return pull
