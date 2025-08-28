from .core import CalcPlusInterpreter

def run(code_str):
    interpreter = CalcPlusInterpreter()
    return interpreter.interpret(code_str)

def run_file(path):
    with open(path) as f:
        code = f.read()
    interpreter = CalcPlusInterpreter()
    return interpreter.interpret(code)