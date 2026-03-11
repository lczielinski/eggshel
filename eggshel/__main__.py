import argparse, sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="eggshel", description="A backward error analysis tool.")
    parser.add_argument("expression", nargs="?", help="a single expression to evaluate")
    parser.add_argument("-f", "--file", help="file with list of expressions")

    args = parser.parse_args()

    if args.expression is not None and args.file is not None:
        parser.error("Cannot use both an expression and file")
    if args.expression is None and args.file is None:
        parser.error("Must provide an expression or file")

    if args.file:
        try:
            with open(args.file) as f:
                source = f.read()
        except FileNotFoundError:
            parser.error(f"file not found: {args.file}")
        
    else:
        source = args.expression

    print(f"Got: {source}")
