eggshel: a floating-point backward error analysis tool described in the paper **Synthesizing Backward Error Bounds, Backward**. This project is licensed under the MIT license.

## Getting started 
First, clone the repository. eggshel can be built manually or using the provided Docker image.

### Build with Docker

If you have [Docker](https://docs.docker.com/engine/install/), in the project root directory, run
```
docker build -t eggshel .
```
After the Docker image builds, you can enter a TTY with
```
docker run -it --rm eggshel
```

### Build manually

This manual build has been tested on `macOS 26.3.1`.
First, get `opam >= 2.3` [here](https://opam.ocaml.org/doc/Install.html). 
You need `ocaml >= 5.1` plus `dune >= 3.17` and `menhir >= 20240715`. 
Install them with 
```
opam install [package]
```
or, in the `bean` directory, you can obtain everything with
```
opam install --deps-only .
```

Build Bean via `dune`:
```
dune build
```

## Executing a program in eggshel

Run a 
```
dune exec -- bean examples/InnerProduct.be
```
- Turn on debug output with the flag `--debug` or `-d`.
- Disable unicode printing with the flag `--disable-unicode`.
- Set unit roundoff to `2^(-n)` with the flag `--unit-roundoff <n>` or `-u <n>`. Without this flag, we give the backward error bounds in terms of `ε`, where `ε = u / (1 - u)` and `u` is unit roundoff.

For example, run the `InnerProduct` Bean program with IEEE 754 double precision arithmetic as follows: 
```
dune exec -- bean examples/InnerProduct.be -u 53
```

The program looks like this:
```
{(u : (dnum, dnum))}
{(v : (num, num))}

/* 
    Computes the inner product of two vectors in R^2.
*/

dlet (u1, u2) = u;
let (v1, v2) = v;

let x = dmul u1 v1;
let y = dmul u2 v2;
add x y
```
Bean programs start with two lists of input variables: those that are *discrete* followed by those that are *linear*. The sole discrete input to `InnerProduct` is `u : (dnum, dnum)` while the sole linear input is `v : (num, num)`.
In a nutshell, this means that `u` and `v` are real vectors in ℝ²; however, `v` may have backward error while `u` may not.

The output is:
```
[General] Type of the program: ℝ
[General] Inferred linear context:
          v :[2.22e-16] (ℝ ⊗ ℝ)
Execution time: 0.000878s
```
The return type of `InnerProduct` is `ℝ`. 
The inferred context tells us that our input vector `v` has a backward error bound of `2.22e-16`.

**This means that there exists a vector $\tilde{v}$, where $\max_{i=1,2}|\ln(v_i/\tilde{v}_i)|\leq 2.22\cdot 10^{-16}$, such that $u\cdot\tilde{v}=$`InnerProduct u v`.**

Note that for vectors and matrices, we report the maximum componentwise backward error bound. 

## Running benchmarks
To run the benchmarks given in Section 5.2 of the paper, use the provided Makefile. Run 
```
make small
```
in the `bean` directory to run the benchmarks which take just a few seconds to run. The output will be piped to a file, `benchmarks.txt`. Run
```
make all
```
to run all the benchmarks. Note that this make take several minutes. The largest benchmark took us about 16 minutes to complete. Run
```
make clean
```
to remove the `benchmarks.txt` file and other generated Dune files.

## Writing an eggshel program
