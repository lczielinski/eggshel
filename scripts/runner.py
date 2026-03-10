import subprocess, sys, textwrap, time

# running eggshel programs

src_files = ["definitions", "context", "share", "operations"]

src = " ".join(f"src/{name}.egg" for name in src_files)

def run_program(name):
    file = name + ".egg"
    command = f"egglog {src} {file}"

    with open(file, "a") as f:
        start = time.perf_counter()
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        end = time.perf_counter()
        # write output in file
        output = textwrap.indent(result.stdout, "; ") + f"; Took {end - start} seconds"
        f.write(output)
        # return output