from itertools import product


class Dimensionality:
    def __init__(self, unit_strings):
        self.unit_strings = unit_strings

    def __iter__(self):
        yield from self.unit_strings

    def __repr__(self):
        return f'Dimensionality({list(self)})'

    def __str__(self):
        return str(self.unit_strings)

    def __truediv__(self, other):
        return Dimensionality(unit_strings=[f'{a}/{b}' for a, b in product(self.unit_strings, other.unit_strings)])

    def __mul__(self, other):
        return Dimensionality(unit_strings=[f'{a}·{b}' for a, b in product(self.unit_strings, other.unit_strings)])

    def __len__(self):
        return len(self.unit_strings)


time = Dimensionality(['s', 'min', 'hour', 'day', 'week', 'year'])
mass = Dimensionality(['g', 'kg', 'tonne', 'lbs', 'ton'])
volume = Dimensionality(['l', 'm³', 'floz', 'gal'])
length = Dimensionality(['cm', 'm', 'km', 'ft', 'yd'])
energy = Dimensionality(['Wh', 'kWh', 'MWh', 'GWh', 'J', 'kJ', 'MJ', 'BTU'])
power = Dimensionality(['W', 'kW', 'MW', 'GW', 'BTU/h'])
temperature = Dimensionality(['°C', 'K', '°F'])
area = Dimensionality(['m²', 'ft²'])
pressure = Dimensionality(['bar', 'Pa', 'kPa', 'MPa', 'psi'])
angle = Dimensionality(['°', 'rad'])
bool = Dimensionality([""])
float = Dimensionality(["", "percent"])
