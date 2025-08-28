import re

class CalcPlusInterpreter:
    def __init__(self):
        self.results = {}
        self.calc_count = 0

    def interpret(self, code: str):
        lines = code.splitlines()
        numbers = []
        current_result = f"resultado{self.calc_count+1}"
        for line in lines:
            line = line.strip()
            match_normal = re.findall(r'^[a-bA-B]=\(([\d\.]+)\)', line)
            for match in match_normal:
                numbers.append(float(match))
            match_extra = re.findall(r'~[c-zC-Z]=\(([\d\.]+)\)', line)
            for match in match_extra:
                numbers.append(float(match))
        total = sum(numbers)
        self.results[current_result] = total
        return self.results