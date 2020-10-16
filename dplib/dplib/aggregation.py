class Aggregation:
    name = 'constant'
    def __init__(self, ds, value):
        self.ds = ds
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

    def get_dataseries(self):
        return self.ds

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
    def __init__(self, ds, lhs, rhs):
        self.ds = ds
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
    def __init__(self, ds, average, count):
        self.ds = ds
        self.average = average
        self.count = count

    def __eq__(self, other):
        return isinstance(other, type(self)) and \
               self.average == other.average and \
               self.count == other.count

    def __repr__(self):
        return f'AverageAggregation({self.average}, {self.count})'

    @staticmethod
    def from_dataseries(ds):
        return AverageAggregation.from_sum_and_count(ds, sum(ds), len(ds))

    @staticmethod
    def from_dataseries(ds):
        sum = 0
        count = 0
        for x in ds:
            sum += x
            count += 1
        return AverageAggregation.from_sum_and_count(ds, sum, count)

    @staticmethod
    def from_sum_and_count(ds, sum, count):
        agg = AverageAggregation(ds, sum / count, count)
        return agg

    def merge(self, other):
        count = self.count + other.count
        # Take the other DataSeries, it would be pricy to keep a copy of all DataSeries (by combining them)
        # We take the other.ds because it should be the newer one
        return AverageAggregation(other.ds,
                                  ((self.average * self.count) + (other.average * other.count)) / count,
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
        return MaxAggregation(other.ds, max(self.value, other.value))
    
class MinAggregation(Aggregation):
    name = 'min'    
    def merge(self, other):
        return MinAggregation(other.ds, min(self.value, other.value))
