import argparse

def parse_query():
    querent = argparse.ArgumentParser(
            description="cartomancy in the terminal 🃏"
            )
    querent.add_argument("deck", choices=['tarot', 'minchiate'], default='tarot', help="pick a deck")
    querent.add_argument("N", type=int, help="# of cards to draw")
    querent.add_argument("-r", "--reversals", action="store_true", help="allow reversals")
    query = querent.parse_args()
    return query
