import re

class CalcPlusInterpreter:
    def __init__(self):
        self.results = {}

    def interpret(self, code: str):
        lines = code.splitlines()
        numbers = []
        for line in lines:
            line = line.strip()
            matches = re.findall(r'[a-z~]+=\(([\d\.]+)\)', line)
            for match in matches:
                numbers.append(float(match))
        total = sum(numbers)
        self.results["resultado"] = total
        return self.results

def run(code: str):
    """Executa código CALC+ a partir de string"""
    return CalcPlusInterpreter().interpret(code)

def run_file(filename: str):
    """Executa código CALC+ a partir de arquivo .clc"""
    with open(filename, "r", encoding="utf-8") as f:
        code = f.read()
    return run(code)