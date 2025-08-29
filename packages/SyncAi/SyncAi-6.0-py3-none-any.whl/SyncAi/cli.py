import argparse
import asyncio
from .main import HackerGpt


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments and return known/unknown."""
    parser = argparse.ArgumentParser(
        description="HackerGpt CLI — AI Prompting & Image Generation",
        add_help=False
    )
    parser.add_argument("-p", "--prompt", type=str, help="Send a prompt to HackerGpt")
    parser.add_argument("-img", "--imager", type=str, help="Generate image from prompt")
    parser.add_argument("-v", "--version", action="store_true", help="Display version info")
    parser.add_argument("-h", "--help", action="store_true", help="Display help message")
    parser.add_argument("-l" , "--language" , type=str, default="english" , help= "Set Language for HackerGpt")

    args, unknown = parser.parse_known_args()

    # Handle unknown arguments gracefully
    if unknown:
        for arg in unknown:
            print(f"[ERROR] Argument `{arg}` not recognized.")
        exit(1)

    return args


async def run_cli():
    """Execute CLI logic based on parsed arguments."""
    args = parse_args()

    try:
        if args.prompt:
            print(HackerGpt.chat(args.prompt , language=args.language))

        elif args.imager:
            HackerGpt.generate_image(args.imager)
            print(f"[INFO] Image saved as: {args.imager}.png")

        elif args.version:
            print(HackerGpt().version())

        elif args.help:
            print(HackerGpt().help())

        else:
            print("[ERROR] No valid arguments provided. Use `-h` for help.")
    except Exception as e:
        print(f"[FATAL] Unexpected error: {e}")


def console():
    """CLI entry point for `syncai` command."""
    asyncio.run(run_cli())
    return 0


if __name__ == "__main__":
    console()
