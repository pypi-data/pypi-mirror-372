from .core import CalcPlusInterpreter

def run(code_str):
    interpreter = CalcPlusInterpreter()
    return interpreter.interpret(code_str)

def run_file(path):
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()
    interpreter = CalcPlusInterpreter()
    return interpreter.interpret(code)