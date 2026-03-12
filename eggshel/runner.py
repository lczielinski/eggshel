import subprocess, sys, time

# running eggshel programs

lib_files = ["definitions", "context", "share", "operations"]
lib = " ".join(f"lib/{name}.egg" for name in lib_files)

# format an egglog output given as 
# (
#   (bounds "a" 1.0 "b" 2.0)
# )
def parse_output(output, seconds):
    lines = [l.strip() for l in output.strip().strip("()").strip().splitlines() if l.strip()]
    message = ""
    if not lines:
        message = "No bounds found.\n"
    for i, line in enumerate(lines, 1):
        tokens = line.strip("()").split()
        tokens = tokens[1:]

        pairs = []
        for j in range(0, len(tokens), 2):
            name = tokens[j].strip("\"")
            value = tokens[j + 1]
            pairs.append(f"{name} with {value}ε")

        message += f"({i}) Found bounds: {', '.join(pairs)}\n"
    return message + f"Took {seconds} seconds"

def run_program(file, timeout):
    command = f"egglog {lib} {file}"

    start = time.perf_counter()
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
        end = time.perf_counter()
        if result.returncode != 0:
            output = f"Error:\n{result.stderr}"
        else:
            output = parse_output(result.stdout, end - start)
    except subprocess.TimeoutExpired:
        output = f"Timed out after {timeout} seconds"
    return output
