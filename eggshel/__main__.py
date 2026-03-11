import argparse, sys, tempfile, os
from .runner import run_program
from .generate import generate_program

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

        results = []
        for line in source.splitlines():
            line = line.strip()
            if not line:
                continue
            file, expr = line.split(None, 1)
            output = f"File: {file}\nExpression: {expr}\nResults:\n"
            generate_program(file, expr)
            output += run_program(file)
            results.append(output)
        # write in .results file
        sep = "\n\n" + ("=" * 40) + "\n\n"
        with open(args.file + ".results", "w") as f:
            f.write(sep.join(results))
    else:
        expr = args.expression
        tmp = tempfile.mktemp(dir=".", suffix=".egg")
        generate_program(tmp, expr)
        output = run_program(tmp)
        print(output)
        os.remove(tmp)
