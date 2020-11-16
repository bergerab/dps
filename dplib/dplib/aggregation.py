class Aggregation:
    name = 'constant'
    def __init__(self, series, value):
        self.series = series
        self.value = value

    def __add__(self, other):
        return AddAggregation(None, self, other)
    
    def __radd__(self, other):
        return AddAggregation(None, self, other)
    
    def __sub__(self, other):
        return SubAggregation(None, self, other)
    
    def __rsub__(self, other):
        return SubAggregation(None, other, self)
    
    def __mul__(self, other):
        return MulAggregation(None, self, other)
    
    def __rmul__(self, other):
        return MulAggregation(None, self, other)
    
    def __truediv__(self, other):
        return DivAggregation(None, self, other)
    
    def __rtruediv__(self, other):
        return DivAggregation(None, other, self)        
    
    def __floordiv__(self, other):
        return FloorDivAggregation(None, self, other)        
    
    def __rfloordiv__(self, other):
        return FloorDivAggregation(None, other, self)

    def __eq__(self, other):
        return isinstance(other, type(self)) and \
               self.value == other.value

    def __repr__(self):
        return f'Aggregation({self.name}, {self.value})'

    def merge(self, other):
        return other
    
    def get_value(self):
        return self.value

    def get_series(self):
        return self.series

    @staticmethod
    def lift(x):
        if isinstance(x, Aggregation):
            return x
        return Aggregation(None, x)

    def to_dict(self):
        return {
            'name': self.name,
            'value': self.value,
        }

    @staticmethod
    def from_dict(d):
        name = d['name']
        if name == Aggregation.name:
            return Aggregation(None, d['value'])
        elif name == MinAggregation.name:
            return MinAggregation(None, d['value'])
        elif name == MaxAggregation.name:
            return MaxAggregation(None, d['value'])
        elif name == ValuesAggregation.name:
            return ValuesAggregation(None, d['value'])
        elif name == AverageAggregation.name:
            return AverageAggregation(None, d['average'], d['count'])
        elif name == AddAggregation.name:
            return AddAggregation(None,
                                  Aggregation.from_dict(d['lhs']),
                                  Aggregation.from_dict(d['rhs']))
        elif name == SubAggregation.name:
            return SubAggregation(None,
                                  Aggregation.from_dict(d['lhs']),
                                  Aggregation.from_dict(d['rhs']))
        elif name == MulAggregation.name:
            return MulAggregation(None,
                                  Aggregation.from_dict(d['lhs']),
                                  Aggregation.from_dict(d['rhs']))
        elif name == DivAggregation.name:
            return DivAggregation(None,
                                  Aggregation.from_dict(d['lhs']),
                                  Aggregation.from_dict(d['rhs']))
        elif name == FloorDivAggregation.name:
            return FloorDivAggregation(None,
                                       Aggregation.from_dict(d['lhs']),
                                       Aggregation.from_dict(d['rhs']))
        else:
            raise Exception('Invalid aggregation dictionary.')

class OperatorAggregation(Aggregation):
    def __init__(self, series, lhs, rhs):
        self.series = series
        self.lhs = Aggregation.lift(lhs)
        self.rhs = Aggregation.lift(rhs)

    def op(self, x, y):
        raise Exception('Unimplemented `op` for OperatorAggregation.')

    def merge(self, other):
        return self.__class__(None, self.lhs.merge(other.lhs), self.rhs.merge(other.rhs))

    def __eq__(self, other):
        return isinstance(other, type(self)) and \
               self.lhs == other.lhs and \
               self.rhs == other.rhs

    def __repr__(self):
        return f'Operator({self.name}, {self.lhs}, {self.rhs})'

    def get_value(self):
        return self.op(self.lhs.get_value(), self.rhs.get_value())

    def to_dict(self):
        return {
            'name': self.name,
            'lhs': self.lhs.to_dict(),
            'rhs': self.rhs.to_dict(),
        }

class AddAggregation(OperatorAggregation):
    name = 'add'
    def op(self, x, y):
        return x + y

class SubAggregation(OperatorAggregation):
    name = 'sub'
    def op(self, x, y):
        return x - y

class MulAggregation(OperatorAggregation):
    name = 'mul'
    def op(self, x, y):
        return x * y

class DivAggregation(OperatorAggregation):
    name = 'div'
    def op(self, x, y):
        return x / y

class FloorDivAggregation(OperatorAggregation):
    name = 'floordiv'
    def op(self, x, y):
        return x // y

class AverageAggregation(Aggregation):
    name = 'average'        
    def __init__(self, series, average, count):
        self.series = series
        self.average = average
        self.count = count

    def __eq__(self, other):
        return isinstance(other, type(self)) and \
               self.average == other.average and \
               self.count == other.count

    def __repr__(self):
        return f'AverageAggregation({self.average}, {self.count})'

    @staticmethod
    def from_series(series):
        return AverageAggregation.from_sum_and_count(series, sum(series), len(series))

    @staticmethod
    def from_sum_and_count(series, sum, count):
        average = None # An average of "None" means there was no data to average over
        if count != 0:
            average = sum / count
        agg = AverageAggregation(series, average, count)
        return agg

    def merge(self, other):
        count = self.count + other.count
        average = None
        if self.count == 0:
            average = other.average
        elif other.average is None:
            average = (self.average * self.count) / count
        else:
            average = ((self.average * self.count) + (other.average * other.count)) / count
        # Take the other Series, it would be pricy to keep a copy of all Series (by combining them)
        # We take the other.series because it should be the newer one
        return AverageAggregation(other.series,
                                  average,
                                  count)

    def get_value(self):
        return self.average

    def to_dict(self):
        return {
            'name': self.name,
            'average': self.average,
            'count': self.count,
        }

class MaxAggregation(Aggregation):
    name = 'max'
    def merge(self, other):
        return MaxAggregation(other.series, max(self.value, other.value))
    
class MinAggregation(Aggregation):
    name = 'min'    
    def merge(self, other):
        return MinAggregation(other.series, min(self.value, other.value))

class ValuesAggregation(Aggregation):
    name = 'values'
    def merge(self, other):
        value = self.value
        for key in other.value:
            value[key] = value[key].merge(other.value[key])
        return ValuesAggregation(other.series, value)

    def get_value(self):
        d = {}
        for key in self.value:
            d[key] = self.value[key].get_value()
        return d
