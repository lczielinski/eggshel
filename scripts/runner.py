# import subprocess
# import sys
# import textwrap
# import time
src_files = ["definitions", "context", "share", "operations"]

src = " ".join(f"src/{name}.egg" for name in src_files)
command = f"egglog {src} tests/{test_name}.egg"

    with open(file, "a") as f:
        start = time.perf_counter()
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        end = time.perf_counter()
        f.write(textwrap.indent(result.stdout, "; "))
        f.write(f"; Took {end - start} seconds")