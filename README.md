eggshel: a floating-point backward error analysis tool described in Section 6 of the paper **Synthesizing Backward Error Bounds, Backward**. This project is licensed under the MIT license.

## Getting started 
First, clone the repository. eggshel can be built manually or using the provided Docker image.

### Build with Docker

If you have [Docker](https://docs.docker.com/engine/install/), in the project root directory, run
```
make docker
```
to enter a pseudo-terminal. **To run benchmarks, make sure you allow Docker containers 16GB of memory.**

### Build manually

This manual build has been tested on `macOS 26.3.1`.

**Requirements:** `python >= 3.13` and `rust/cargo >= 1.90`

Install `egglog` (tested with v2.0):
```
cargo install egglog
```

## Executing a program in eggshel

Run a single program (an S-expression with operators Sqrt, Add, and Mul) like this:
```
python3 -m eggshel "(Sqrt (Add x y))"
```
This program sums two floating-point variables, `x` and `y`, then takes their square root. 
The result looks like:
```
(1) Found bounds: x with 3.0ε, y with 3.0ε
Took 0.02878616697853431 seconds
```
This is a backward error result for the program with respect to `x` and `y` individually.
The error is given in terms of $\varepsilon$, where $\varepsilon = u / (1 - u)$ and $u$ is unit roundoff ($2^{-53}$ for IEEE 754 double precision).

**Theorem.** For any floating-point inputs `x` and `y`, there exist real numbers $\tilde{x}$ and $\tilde{y}$ such that $\sqrt{\tilde{x}+\tilde{y}}=$`(Sqrt (Add x y))`. The backward error bounds tell us that $|\ln(x/\tilde{x})|\leq 3\varepsilon$ and $|\ln(y/\tilde{y})|\leq 3\varepsilon$.

It is possible that no bounds are found, many bounds are found, or the program times out. If no bounds are found, then either the program is not backward stable, or `eggshel` was unable to find a proof. If many bounds are found (up to 10 will be returned), this means there were multiple valid ways to distribute the backward error. 

## Running many programs
To run many programs, create a `.txt` file containing the programs like this:
```
myprogram1 (Add a b)
myprogram2 (Add a (Sqrt b))
```
Run it like this:
```
python3 -m eggshel -f myprograms.txt
```
A file `myprograms.txt.results` will be created summarizing the results:
```
Name: myprogram1
Expression: (Add a b)
Results:
(1) Found bounds: a with 1.0ε, b with 1.0ε
Took 0.03328920801868662 seconds

========================================

Name: myprogram2
Expression: (Add a (Sqrt b))
Results:
(1) Found bounds: a with 1.0ε, b with 4.0ε
Took 0.026194458012469113 seconds
```
You can also pass in multiple files. All programs will be executed in parallel.

## Options
Use the flag `-t` or `--timeout` to set the timeout in seconds (default one hour). 
Use the flag `-j` or `--jobs` to set the maximum number of parallel jobs (default CPU count).

## Running benchmarks
**We recommend 16GB of memory to run the benchmarks. If you are having issues with benchmarks being killed, try passing in the -j flag to use fewer cores.** To run the benchmarks given in Section 6.3 of the paper, use the provided Makefile. Run 
```
make benchmarks TIMEOUT=300
```
to run all the benchmarks with five minutes of timeout per program. 
**Warning: this may take a few hours to complete.**
The results will be found in the `benchmarks` directory in the `.txt.results` files. Run 
```
make benchmarks TIMEOUT=3600
```
to achieve the full results. Run
```
make clean
```
to remove the `.results` files.
