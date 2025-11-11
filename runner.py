import subprocess
import sys
import textwrap
import time

# given a string program (Add (Mul x y) y)
# generates (let ex (Base 0.0 (Add (Mul (Var "x") (Var "y")) (Var "y"))))
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
    return "(let ex (Base 0.0 " + to_string(replaced) + " 0.0))"

# given a string x2 y3 z2
# generates (let ctx (Tens (Tens (Base 0.0 (Var "x") 2.0) (Base 0.0 (Var "y") 3.0)) (Base 0.0 (Var "z") 2.0)))
def generate_ctx(s):
    parts = s.strip().split()
    pairs = [(part[0], part[1:]) for part in parts]

    err = pairs[-1][1] if "." in pairs[-1][1] else pairs[-1][1] + ".0"
    result = f"(Base 0.0 (Var \"{pairs[-1][0]}\") {err})"
    
    for i in range(len(pairs) - 2, -1, -1):
        var, exp = pairs[i]
        err = exp if "." in exp else exp + ".0"
        base = f"(Base 0.0 (Var \"{var}\") {err})"
        result = f"(Tens {base} {result})"
    
    return f"(let ctx {result})"

def run(test_name, expr, ctx):
    expr = generate_expr(expr)
    ctx = generate_ctx(ctx)

    file = "tests/" + test_name + ".egg"
    with open(file, "w") as f:
        f.write(expr + "\n")
        f.write(ctx + "\n\n")
        f.write("(run-schedule (saturate (run)))\n")
        f.write("(check (-> ctx ex))\n\n")

    src_names = ["Definitions", "Context", "Decombiners", "Operations"]
    src = " ".join(f"src/{name}.egg" for name in src_names)

    command = f"egglog {src} tests/{test_name}.egg"

    with open(file, "a") as f:
        start = time.perf_counter()
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        end = time.perf_counter()
        if result.stderr:
            text = result.stderr
            last_error = text.rfind("[ERROR]")
            if last_error != -1:
                print(test_name + " failed")
            last_info = text.rfind("[INFO ]")
            last_pos = max(last_error, last_info)

            if last_pos != -1:
                text = text[last_pos:]
            f.write(textwrap.indent(text, "; "))
        f.write(f"\n; Took {end - start} seconds")

# if len(sys.argv) != 4:
#     print(f"Usage: {sys.argv[0]} <test name> <expr> <context>")
#     sys.exit(1)
    
# test_name = sys.argv[1]
# expr = generate_expr(sys.argv[2])
# ctx = generate_ctx(sys.argv[3])

run("ex1", "(Mul (Add a (Mul a b)) c)", "a1 c1 b1")
run("ex2", "(Add (Mul a a) (Mul b b))", "a1 b1")
run("ex3", "(Add (Add (Mul a b) (Mul (Mul a c) a)) a)", "a1 b2 c4")
run("ex4", "(Add a (Add b (Mul c (Add d e))))", "a1 b2 c1.5 d2.5 e2.5")
run("ex5", "(Add a (Sqrt (Mul a b)))", "a1 b4")
run("ex6", "(Add a (Mul a (Mul a b)))", "a1 b3")
