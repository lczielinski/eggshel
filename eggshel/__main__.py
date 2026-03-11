import argparse, sys, tempfile, os
from concurrent.futures import ThreadPoolExecutor, as_completed
from .runner import run_program
from .generate import generate_program

def generate_and_run(expr, timeout):
    fd, tmp = tempfile.mkstemp()
    os.close(fd)
    try:
        generate_program(tmp, expr)
        output = run_program(tmp, timeout)
    finally:
        os.remove(tmp)
    return output

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="eggshel", description="A backward error analysis tool.")
    parser.add_argument("expression", nargs="?", help="a single expression to evaluate")
    parser.add_argument("-f", "--file", help="file with list of expressions")
    parser.add_argument("-t", "--timeout", type=int, default=3600, help="set timeout")

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

        # run all programs in file concurrently
        jobs = []
        for line in source.splitlines():
            line = line.strip()
            if not line:
                continue
            name, expr = line.split(None, 1)
            jobs.append((name, expr))

        results = [None] * len(jobs)
        with ThreadPoolExecutor() as pool:
            futures = {pool.submit(generate_and_run, expr, args.timeout): i for i, (name, expr) in enumerate(jobs)}
            for future in as_completed(futures):
                i = futures[future]
                name, expr = jobs[i]
                output = f"Name: {name}\nExpression: {expr}\nResults:\n"
                output += future.result()
                results[i] = output
        # write to a .results file
        sep = "\n\n" + ("=" * 40) + "\n\n"
        with open(args.file + ".results", "w") as f:
            f.write(sep.join(results))
    else:
        # just print results in terminal
        print(generate_and_run(args.expression, args.timeout))
