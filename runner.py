import subprocess
import sys
import textwrap
import time

# given a string program (Add (Mul x y) y)
# generates "(Base 0.0 (Add (Mul (Var "x") (Var "y")) (Var "y")) 0.0)"
def generate_expr(s):
    def parse(tokens):
        token = tokens.pop(0)
        if token == "(":
            expr = []
            while tokens[0] != ")":
                expr.append(parse(tokens))
            tokens.pop(0) # Remove the ")"
            return expr
        else:
            return token
    
    def replace_vars(expr):
        if isinstance(expr, str):
            if expr in ["Add", "Mul", "Sqrt"]:
                return expr
            else:
                return ["Var", "\"" + expr + "\""]
        elif isinstance(expr, list):
            return [replace_vars(item) for item in expr]
        return expr
    
    def to_string(expr):
        if isinstance(expr, str):
            return expr
        elif isinstance(expr, list):
            return "(" + " ".join(to_string(item) for item in expr) + ")"
        return str(expr)
    
    tokens = s.replace("(", " ( ").replace(")", " ) ").split()
    parsed = parse(tokens)
    replaced = replace_vars(parsed)
    return "(Base 0.0 " + to_string(replaced) + " 0.0)"

# given ["x", "y"]
# generates ["(Base 0.0 (Var "x") x_p)", "(Base 0.0 (Var "y") y_p)"]
def generate_bases(var_names):
    return [f"(Base 0.0 (Var \"{var}\") {var}_p)" for var in var_names]

# given ["(Base 0.0 (Var "x") x_p)", "(Base 0.0 (Var "y") y_p)"]
# generates "(Tens (Base 0.0 (Var "x") x_p) (Base 0.0 (Var "y") y_p))"
def generate_ctx(bases):
    result = bases[-1]
    for i in range(len(bases) - 2, -1, -1):
        result = f"(Tens {bases[i]} {result})"
    return result

def run(test_name, expr, ctx):
    expr = generate_expr(expr)
    var_names = ctx.split()
    bases = generate_bases(var_names)
    ctx = generate_ctx(bases)

    bounds_type = " ".join(["String f64"] * len(var_names))
    bounds_query = " ".join(f"\"{var}\" {var}_p" for var in var_names)

    file = "tests/" + test_name + ".egg"
    with open(file, "w") as f:
        f.write(f"(let ex {expr})\n\n")
        f.write(f"(rule ({" ".join(bases)})\n      ({ctx}))\n\n")

        f.write(f"(ruleset trans)\n\n")
        f.write(f"(rule ((-> ctx2 ex) (-> ctx1 ctx2))\n      ((-> ctx1 ex)) :ruleset trans)\n\n")
        
        f.write(f"(relation bounds ({bounds_type}))\n\n")
        f.write("(ruleset post)\n\n")
        f.write(f"(rule ((-> {ctx} ex))\n      ((bounds {bounds_query})) :ruleset post)\n\n")
        
        f.write("(run-schedule (seq (saturate (seq (run) (run trans))) (run post)))\n\n")
        f.write("(print-function bounds 10)\n\n")

    src_names = ["Definitions", "Context", "Decombiners", "Operations"]
    src = " ".join(f"src/{name}.egg" for name in src_names)

    command = f"egglog {src} tests/{test_name}.egg"

    with open(file, "a") as f:
        start = time.perf_counter()
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        end = time.perf_counter()
        f.write(textwrap.indent(result.stdout, "; "))
        f.write(f"; Took {end - start} seconds")

run("linear/linear2", "(Add x (Mul a x))", "x a")
run("linear/linear3", "(Add x (Add (Mul a x) (Mul b x)))", "x a b")
run("linear/linear4", "(Add x (Add (Mul a x) (Add (Mul b x) (Mul c x)))))", "x a b c")
run("linear/linear5", "(Add x (Add (Mul a x) (Add (Mul b x) (Add (Mul c x) (Mul d x))))))", "x a b c d")
run("linear/linear6", "(Add x (Add (Mul a x) (Add (Mul b x) (Add (Mul c x) (Add (Mul d x) (Mul e x)))))))", "x a b c d e")

run("norm/norm1", "(Sqrt (Mul x x))", "x")
run("norm/norm2", "(Sqrt (Add (Mul x x) (Mul y y)))", "x y")
run("norm/norm3", "(Sqrt (Add (Mul x x) (Add (Mul y y) (Mul z z))))", "x y z")
run("norm/norm4", "(Sqrt (Add (Mul x x) (Add (Mul y y) (Add (Mul z z) (Mul a a)))))", "x y z a")
run("norm/norm5", "(Sqrt (Add (Mul x x) (Add (Mul y y) (Add (Mul z z) (Add (Mul a a) (Mul b b))))))", "x y z a b")
run("norm/norm6", "(Sqrt (Add (Mul x x) (Add (Mul y y) (Add (Mul z z) (Add (Mul a a) (Add (Mul b b) (Mul c c)))))))", "x y z a b c")
run("norm/norm7", "(Sqrt (Add (Mul x x) (Add (Mul y y) (Add (Mul z z) (Add (Mul a a) (Add (Mul b b) (Add (Mul c c) (Mul d d))))))))", "x y z a b c d")

run("quad/quad2", "(Add x (Mul x (Mul x a)))", "x a")
run("quad/quad3", "(Add x (Add (Mul x (Mul x a)) (Mul x (Mul x b))))", "x a b")
run("quad/quad4", "(Add x (Add (Mul x (Mul x a)) (Add (Mul x (Mul x b)) (Mul x (Mul x c)))))", "x a b c")

run("ex1", "(Add x (Add (Mul a x) (Mul (Mul b x) x)))", "a b x")
run("ex2", "(Add a (Sqrt (Mul a b)))", "a b")
run("ex3", "(Mul (Add a b) (Add b a))", "a b")
run("ex4", "(Mul (Add a (Mul a b)) (Add c (Mul c d)))", "a b c d")
run("ex5", "(Add a (Mul a (Sqrt b)))", "a b")
run("ex6", "(Sqrt (Add (Mul a x) (Sqrt b)))", "a x b")
