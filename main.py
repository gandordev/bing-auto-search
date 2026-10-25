# global imports ---------------------------------------------------
import argparse
import logging

# local imports ----------------------------------------------------
from src.search import run

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    parser = argparse.ArgumentParser(
        description="Automate Bing searches"
    )
    parser.add_argument(
        "-n",
        "--num",
        type=int,
        default=45,
        help="Total number of searches (default: 45)",
    )
    args = parser.parse_args()
    run(total=args.num)