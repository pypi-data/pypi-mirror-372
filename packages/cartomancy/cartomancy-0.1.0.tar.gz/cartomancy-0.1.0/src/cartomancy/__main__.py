import random
from .query import parse_query
from .decks import build_deck, shuffle_and_pull

def main():
    query = parse_query()
    deck = build_deck(query)
    pull = shuffle_and_pull(deck, query)

    for i, card in enumerate(pull, start=1):
        if query.reversals and random.choice([True, False]):
            card = f"{card} Reversed"
        print(f"{i}. {card}")

if __name__ == "__main__":
    main()
