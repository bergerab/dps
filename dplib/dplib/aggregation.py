class Aggregation:
    name = 'constant'
    def __init__(self, series, value):
        self.series = series
        self.value = value

    def __add__(self, other):
        if not isinstance(other, Aggregation):
            raise Exception('other', type(other))
        return AddAggregation(choose_series(self, other), self, other)
    
    def __radd__(self, other):
        return AddAggregation(choose_series(self, other), self, other)
    
    def __sub__(self, other):
        return SubAggregation(choose_series(self, other), self, other)
    
    def __rsub__(self, other):
        return SubAggregation(choose_series(self, other), other, self)
    
    def __mul__(self, other):
        return MulAggregation(choose_series(self, other), self, other)
    
    def __rmul__(self, other):
        return MulAggregation(choose_series(self, other), self, other)
    
    def __truediv__(self, other):
        return DivAggregation(choose_series(self, other), self, other)
    
    def __rtruediv__(self, other):
        return DivAggregation(choose_series(self, other), other, self)        
    
    def __floordiv__(self, other):
        return FloorDivAggregation(choose_series(self, other), self, other)        
    
    def __rfloordiv__(self, other):
        return FloorDivAggregation(choose_series(self, other), other, self)

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
        x = self.lhs.get_value()
        y = self.rhs.get_value()
        value = self.op(x, y)
        return value

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
        # Important for weighted average where an operand could be null
        if x is None or y is None:
            return 0
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
        xs = series.series.sum()
        if isinstance(xs, Aggregation):
            raise Exception('WHY3 ? ')
        return AverageAggregation.from_sum_and_count(series, xs, series.size)

    @staticmethod
    def from_sum_and_count(series, sum, count):
        if isinstance(sum, Aggregation):
            raise Exception('SUMISANAGG ' + str(type(sum)))
        if isinstance(count, Aggregation):
            raise Exception('COUNTISANAGG ')
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
        if isinstance(average, Aggregation):
            raise Exception('WHY ? ' + str(average))
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
        value = {}
        for key in other.value:
            value[key] = self.value[key].merge(other.value[key])
        return ValuesAggregation(other.series, value)

    def to_dict(self):
        return {
            'name': self.name,
            'value': list(map(lambda x: x.to_dict(), self.value)),
        }

    def __repr__(self):
        value = ', '.join(map(lambda x: repr(x), self.value))
        return f'Aggregation({self.name}, [{value}])'

    def get_value(self):
        d = {}
        for key in self.value:
            d[key] = self.value[key].get_value()
        return d

def choose_series(x, y):
    return x.series if x.series is not None else y.series
