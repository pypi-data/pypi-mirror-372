class CalcPlusInterpreter:
    def __init__(self):
        self.results = {}
        self.calc_count = 0

    def interpret(self, code):
        # aqui vai todo seu código do interpretador
        # exemplo mínimo:
        lines = code.split('\n')
        numbers = []
        for line in lines:
            if '=' in line:
                try:
                    number = float(line.split('=')[1].strip('()'))
                    numbers.append(number)
                except:
                    pass
        total = sum(numbers)
        self.results['resultado'] = total
        return self.results