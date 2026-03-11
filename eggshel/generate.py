import re, os

# generating runnable eggshel programs

ops = ["Add", "Mul", "Sqrt"]

# given a string program "(Add (Mul x y) y)"
# generates "(Base 0.0 (Add (Mul (Var "x") (Var "y")) (Var "y")) 0.0)"
def generate_expr(s):
    def parse(tokens):
        token = tokens.pop(0)
        if token == "(":
            expr = []
            while tokens[0] != ")":
                expr.append(parse(tokens))
            tokens.pop(0) # remove the ")"
            return expr
        else:
            return token
    
    def replace_vars(expr):
        if isinstance(expr, str):
            if expr in ops:
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

# given "(Add (Mul x y) y)"
# returns ["x", "y"]
def extract_vars(s):
    tokens = re.findall(r'[A-Za-z_]\w*', s)
    return sorted(set(t for t in tokens if t not in ops))

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

# generate full eggshel program
def generate_program(name, expr):
    var_names = extract_vars(expr)
    expr = generate_expr(expr)
    bases = generate_bases(var_names)
    ctx = generate_ctx(bases)

    bounds_type = " ".join(["String f64"] * len(var_names))
    bounds_query = " ".join(f"\"{var}\" {var}_p" for var in var_names)

    file = name + ".egg"
    os.makedirs(os.path.dirname(file), exist_ok=True)
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
