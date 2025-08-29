import argparse
import asyncio
from pathlib import Path

from .json_utils import load_json, save_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Invaders synchronizer")
    parser.add_argument(
        "-u",
        "--users",
        type=Path,
        required=True,
        help="Path to the JSON users file",
    )
    return parser.parse_args()


async def async_main() -> None:
    args = parse_args()
    users = load_json(args.users)
    await asyncio.gather(*[user.run() for user in users], return_exceptions=True)
    save_json(args.users, users)


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
