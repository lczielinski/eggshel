import argparse, sys, tempfile, os
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import groupby
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
    parser.add_argument("-f", "--files", nargs="+", help="files with list of expressions")
    parser.add_argument("-t", "--timeout", type=int, default=3600, help="set timeout")

    args = parser.parse_args()

    if args.expression is not None and args.files is not None:
        parser.error("Cannot use both an expression and file")
    if args.expression is None and args.files is None:
        parser.error("Must provide an expression or file")

    if args.files:
        jobs = []  # (filepath, name, expr)
        for filepath in args.files:
            try:
                with open(filepath) as f:
                    source = f.read()
            except FileNotFoundError:
                parser.error(f"file not found: {filepath}")
            for line in source.splitlines():
                line = line.strip()
                if not line:
                    continue
                name, expr = line.split(None, 1)
                jobs.append((filepath, name, expr))

        results = [None] * len(jobs)
        with ThreadPoolExecutor() as pool:
            futures = {pool.submit(generate_and_run, expr, args.timeout): i for i, (_, name, expr) in enumerate(jobs)}
            for future in as_completed(futures):
                i = futures[future]
                filepath, name, expr = jobs[i]
                output = f"Name: {name}\nExpression: {expr}\nResults:\n"
                output += future.result()
                results[i] = output

        sep = "\n\n" + ("=" * 40) + "\n\n"
        # group results by source file and write each .results file
        for filepath, group in groupby(range(len(jobs)), key=lambda i: jobs[i][0]):
            group_results = [results[i] for i in group]
            with open(filepath + ".results", "w") as f:
                f.write(sep.join(group_results))
    else:
        # just print results in terminal
        print(generate_and_run(args.expression, args.timeout))
