# eggshel: a floating-point backward error analysis tool
`eggshel` is the tool described in Section 6 of the paper **Synthesizing Backward Error Bounds, Backward**. This project is licensed under the MIT license.

## Getting started 
First, clone the repository. eggshel can be built manually or using the provided Docker image.

### Build with Docker

If you have [Docker](https://docs.docker.com/engine/install/), in the project root directory, run
```
make docker
```
to enter a pseudo-terminal. **To run the large benchmarks, make sure you allow Docker containers at least 16GB of memory.**

### Build manually

This manual build has been tested on `macOS 26.3.1`.

**Requirements:** `python >= 3.13` and `rust/cargo >= 1.90`

Install `egglog` (tested with v2.0):
```
cargo install egglog
```

## Executing a program

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
And run it like this:
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
You can also pass in multiple files. By default, programs will be executed in parallel, unless the `-j 1` flag is passed.

## Options
Use the flag `-t` or `--timeout` to set the timeout in seconds per program (default one hour). 
Use the flag `-j` or `--jobs` to set the maximum number of parallel jobs (default CPU count). 
If you are having memory issues, we recommend setting `-j 1`.

## Running benchmarks
To run the benchmarks given in Section 6.3 of the paper, use the provided Makefile.
**Warning: `eggshel` can be memory-intensive. We recommend at least 16GB of memory to run large benchmarks.** Run 
```
make benchmarks
```
to run small benchmarks, which should complete within a few minutes. The results will be found in the `benchmarks` directory in the `.txt.results` files. To decrease the number of parallel jobs, run
```
make benchmarks JOBS=<n>
```
Run
```
make benchmarks-large
```
to run the large benchmarks that several minutes each and find the results in `benchmarks/large`. 
Note that the large benchmarks are run sequentially, not in parallel.
Finally, run
```
make clean
```
to remove the `.results` files.
