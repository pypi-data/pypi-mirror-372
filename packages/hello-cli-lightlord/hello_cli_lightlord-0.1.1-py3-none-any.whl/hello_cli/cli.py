import argparse

def main() -> None:
    parser = argparse.ArgumentParser(description="Say hello.")
    parser.add_argument("-n", "--name", default="World",
                        help="Name to greet (default: World)")
    parser.add_argument("--caps", action="store_true",
                        help="ALL CAPS")
    args = parser.parse_args()

    msg = f"Hello, {args.name}!!!"
    if args.caps:
        msg = msg.upper()
    print(msg)

if __name__ == "__main__":
    main()