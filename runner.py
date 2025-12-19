import subprocess
import sys
import textwrap
import time

# given a string program (Add x y), generates 
# (let _ex (Ctx (set-of (Leaf (Par (Add (Var "x") (Var "y")) 0.0)))))
def generate_expr(s):
    def tokenize(s):
        return s.replace("(", " ( ").replace(")", " ) ").split()
    
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
    
    tokens = tokenize(s)
    parsed = parse(tokens)
    replaced = replace_vars(parsed)
    return "(let _ex (Ctx (set-of (Leaf (Par " + to_string(replaced) + " 0.0)))))"

# given [x, y] generates 
# (Ctx (set-of (Leaf (Par (Var "x") ?x_p)) (Leaf (Par (Var "y") ?y_p))))
def generate_rule(var_names):
    result = " ".join(f"(Leaf (Par (Var \"{var}\") ?{var}_p))" for var in var_names)
    return "(Ctx (set-of " + result + "))"

def run(test_name, expr, ctx):
    var_names = ctx.split()
    expr = generate_expr(expr)
    rule = generate_rule(var_names)

    bounds_type = " ".join(["String f64"] * len(var_names))
    bounds_query = " ".join(f"\"{var}\" ?{var}_p" for var in var_names)

    file = "tests/" + test_name + ".egg"
    with open(file, "w") as f:
        f.write(expr + "\n\n")
        f.write("(run-schedule (saturate (run)))\n\n")
        
        f.write(f"(relation bounds ({bounds_type}))\n\n")
        f.write(f"(rule ((-> {rule} _ex))\n      ((bounds {bounds_query})))\n\n")
        f.write("(run 1)\n\n")
        f.write("(print-function bounds 10)\n\n")

    src_names = ["Definitions", "Context", "Decombiners", "Operations"]
    src = " ".join(f"src/{name}.egg" for name in src_names)

    command = f"egglog {src} tests/{test_name}.egg"

    with open(file, "a") as f:
        start = time.perf_counter()
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        end = time.perf_counter()
        f.write(textwrap.indent(result.stdout, "; "))
        f.write(f"\n; Took {end - start} seconds")

# run("linear/linear2", "(Add x (Mul a x))", "x a")
# run("linear/linear3", "(Add x (Add (Mul a x) (Mul b x)))", "x a b")
# run("linear/linear4", "(Add x (Add (Mul a x) (Add (Mul b x) (Mul c x)))))", "x a b c")
# run("linear/linear5", "(Add x (Add (Mul a x) (Add (Mul b x) (Add (Mul c x) (Mul d x))))))", "x a b c d")
# run("linear/linear6", "(Add x (Add (Mul a x) (Add (Mul b x) (Add (Mul c x) (Add (Mul d x) (Mul e x)))))))", "x a b c d e")

# run("norm/norm1", "(Sqrt (Mul x x))", "x")
# run("norm/norm2", "(Sqrt (Add (Mul x x) (Mul y y)))", "x y")
# run("norm/norm3", "(Sqrt (Add (Mul x x) (Add (Mul y y) (Mul z z))))", "x y z")
# run("norm/norm4", "(Sqrt (Add (Mul x x) (Add (Mul y y) (Add (Mul z z) (Mul a a)))))", "x y z a")
# run("norm/norm5", "(Sqrt (Add (Mul x x) (Add (Mul y y) (Add (Mul z z) (Add (Mul a a) (Mul b b))))))", "x y z a b")
# run("norm/norm6", "(Sqrt (Add (Mul x x) (Add (Mul y y) (Add (Mul z z) (Add (Mul a a) (Add (Mul b b) (Mul c c)))))))", "x y z a b c")
# run("norm/norm7", "(Sqrt (Add (Mul x x) (Add (Mul y y) (Add (Mul z z) (Add (Mul a a) (Add (Mul b b) (Add (Mul c c) (Mul d d))))))))", "x y z a b c d")

# run("quad/quad2", "(Add x (Mul x (Mul x a)))", "x a")
# run("quad/quad3", "(Add x (Add (Mul x (Mul x a)) (Mul x (Mul x b))))", "x a b")
# run("quad/quad4", "(Add x (Add (Mul x (Mul x a)) (Add (Mul x (Mul x b)) (Mul x (Mul x c)))))", "x a b c")

run("ex1", "(Add x (Add (Mul a x) (Mul (Mul b x) x)))", "a b x")
run("ex2", "(Add a (Sqrt (Mul a b)))", "a b")
run("ex3", "(Mul (Add a b) (Add b a))", "a b")
run("ex4", "(Mul (Add a (Mul a b)) (Add c (Mul c d)))", "a b c d")
run("ex5", "(Add a (Mul a (Sqrt b)))", "a b")
run("ex6", "(Sqrt (Add (Mul a x) (Sqrt b)))", "a x b")
