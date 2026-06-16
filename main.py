# global imports ---------------------------------------------------
import argparse

# local imports ----------------------------------------------------
from src.search import run


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Automatiza búsquedas en Bing/Edge para Microsoft Rewards"
    )
    parser.add_argument(
        "-n", "--num",
        type=int,
        default=45,
        help="Número total de búsquedas (por defecto: 45)"
    )
    args = parser.parse_args()
    run(total=args.num)
