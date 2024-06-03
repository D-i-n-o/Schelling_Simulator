
import ast, math

locals =  {key: value for (key,value) in vars(math).items() if key[0] != '_'}
locals.update({"abs": abs, "complex": complex, "min": min, "max": max, "pow": pow, "round": round})

class Visitor(ast.NodeVisitor):
    def visit(self, node):
       if not isinstance(node, self.whitelist):
           raise ValueError(node)
       return super().visit(node)

    whitelist = (ast.Module, ast.Expr, ast.Load, ast.Expression, ast.Add, ast.Sub, ast.UnaryOp, ast.Num, ast.BinOp,
            ast.Mult, ast.Div, ast.Pow, ast.BitOr, ast.BitAnd, ast.BitXor, ast.USub, ast.UAdd, ast.FloorDiv, ast.Mod,
            ast.LShift, ast.RShift, ast.Invert, ast.Call, ast.Name)

def evaluate(expr, extra_locals):
    if any(elem in expr for elem in '\n#') : raise ValueError(expr)
    try:
        node = ast.parse(expr.strip(), mode='eval')
        Visitor().visit(node)
        locals.update(extra_locals)
        return eval(compile(node, "<string>", "eval"), {'__builtins__': None}, locals)
    except Exception: raise ValueError(expr)


class CustomUtility():
    def __init__(self, code):
        self.code = code
    def __call__(self, f_i):
        try:
            return float(evaluate(self.code, {"frac":f_i}))
        except:
            return 0.0

class SinglePeakedUtility():
    def __init__(self, peak):
        self.peak = peak
        
    def __call__(self, f_i):
        if f_i > self.peak:
            f_i = self.peak / (1.0-self.peak) * (1.0-f_i)
        return f_i / self.peak
    
class TauUtility():
    def __init__(self, tau):
        self.tau = tau
        
    def __call__(self, f_i):
        return min(f_i, self.tau)
    
class TauNoSegUtility():
    def __init__(self, tau):
        self.tau = tau
        
    def __call__(self, f_i):
        if f_i == 1.0:
            return 0.0
        return min(f_i, self.tau)
    

