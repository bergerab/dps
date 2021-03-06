import numpy as np

class Aggregation:
    name = 'constant'
    def __init__(self, series, value, skip_merge=False):
        self.series = series
        self.value = value
        self.skip_merge = skip_merge # used when referencing aggregations from other aggregations - the sub aggregations have already been merged so the parent should skip

    def clone(self):
        return Aggregation(self.series, self.value, self.skip_merge)
        
    def __add__(self, other):
        if not isinstance(other, Aggregation):
            other = Aggregation.lift(other)
        return AddAggregation(None, self, other)

    # If you do any operations on an aggregation, you lose the ability to
    # chart it. Because at that point, the chart will be different than
    # what the aggregation says.
    #
    # For example if we allowed plotting and doing operations on aggregations, the
    # KPI of "avg(Va) * 1234" would plot the Va signal (untouched), but the aggregation
    # would be the average of Va times 1234. This would cause great confusion for users.
    # They would see the plot, and they wouldn't know how the plot corresponds with the
    # aggregation.
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

    def __gt__(self, other):
        return GreaterThanAggregation(None, self, other)

    def __lt__(self, other):
        return LessThanAggregation(None, self, other)

    def __ge__(self, other):
        return GreaterThanOrEqualAggregation(None, self, other)

    def __le__(self, other):
        return LessThanOrEqualAggregation(None, self, other)

    def __eq__(self, other):
        return EqualAggregation(None, self, other)

    def __ne__(self, other):
        return NotEqualAggregation(None, self, other)

    def equals(self, other):
        return isinstance(other, type(self)) and \
               self.value == other.value

    def __repr__(self):
        return f'Aggregation({self.name}, {self.value})'

    def merge(self, other):
        if self.skip_merge:
            return other
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
        elif name == CumSumAggregation.name:
            return CumSumAggregation(None, d['value'])
        elif name == AbsAggregation.name:
            return AbsAggregation(None, d['value'])
        elif name == SumAggregation.name:
            return SumAggregation(None, d['value'])
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
        elif name == GreaterThanAggregation.name:
            return GreaterThanAggregation(None,
                                       Aggregation.from_dict(d['lhs']),
                                       Aggregation.from_dict(d['rhs']))
        elif name == GreaterThanOrEqualAggregation.name:
            return GreaterThanOrEqualAggregation(None,
                                       Aggregation.from_dict(d['lhs']),
                                       Aggregation.from_dict(d['rhs']))
        elif name == LessThanAggregation.name:
            return LessThanAggregation(None,
                                       Aggregation.from_dict(d['lhs']),
                                       Aggregation.from_dict(d['rhs']))
        elif name == LessThanOrEqualAggregation.name:
            return LessThanOrEqualAggregation(None,
                                       Aggregation.from_dict(d['lhs']),
                                       Aggregation.from_dict(d['rhs']))
        elif name == EqualAggregation.name:
            return EqualAggregation(None,
                                       Aggregation.from_dict(d['lhs']),
                                       Aggregation.from_dict(d['rhs']))
        elif name == NotEqualAggregation.name:
            return NotEqualAggregation(None,
                                       Aggregation.from_dict(d['lhs']),
                                       Aggregation.from_dict(d['rhs']))
        elif name == IfAggregation.name:
            return IfAggregation(None,
                                 Aggregation.from_dict(d['body']),
                                 Aggregation.from_dict(d['test']),
                                 Aggregation.from_dict(d['orelse']))
        elif name == TableAggregation.name:
            return TableAggregation(None, d['sub_aggregation'], d['table'])
        else:
            raise Exception('Invalid aggregation dictionary.')

class TableAggregation(Aggregation):
    name = 'table'
    def __init__(self, series, sub_aggregation='avg', table=None): # row counts must be the same between table aggregations that are merged
        self.series = series
        self.sub_aggregation = sub_aggregation # can only be 'min', 'max', or 'avg'
        self.value = self.table = table if table != None else {}
        self.lift_table() # ensure all values in the table are aggregations

    def lift_agg(self, x):
        if isinstance(x, Aggregation):
            return x
        if self.sub_aggregation == 'avg':
            return AverageAggregation.from_sum_and_count(None, x, 1)
        elif self.sub_aggregation == 'min':
            return MinAggregation(None, x)
        elif self.sub_aggregation == 'max':
            return MaxAggregation(None, x)
        raise Exception(f'TableAggregation: invalid sub aggregation {self.sub_aggregation}')

    def lift_table(self):
        for col in self.table:
            self.table[col] = list(map(lambda x: self.lift_agg(x), self.table[col]))

    def append(self, row):
        for key in row:
            if key in self.table:
                self.table[key].append(self.lift_agg(row[key]))
            else:
                self.table[key] = [self.lift_agg(row[key])]

    def merge(self, other):
        table = {}
        for col in self.table:
            table[col] = []
            for i, cell in enumerate(self.table[col]):
                table[col].append(cell.merge(other.table[col][i]))
        return TableAggregation(self.series, self.sub_aggregation, table)

    def get_value(self):
        table = {}
        for col in self.table:
            table[col] = list(map(lambda x: x.get_value(), self.table[col]))
        return table

    def to_dict(self):
        table = {}
        for col in self.table:
            table[col] = list(map(lambda x: x.to_dict(), self.table[col]))
        return {
            'name': self.name,
            'sub_aggregation': self.sub_aggregation,
            'table': table,
        }

class IfAggregation(Aggregation):
    name = 'if'
    def __init__(self, series, body, test, orelse):
        self.series = series
        self.body = body
        self.test = test
        self.orelse = orelse

    def merge(self, other):
        return self.__class__(None, self.body.merge(other.body), self.test.merge(other.test), self.orelse.merge(other.orelse))

    def equals(self, other):
        return isinstance(other, type(self)) and \
               self.body.equals(other.body) and \
               self.test.equals(other.rhs) and \
                   self.orelse.equals(other.orelse)

    def __repr__(self):
        return f'If({self.body} if {self.test} else {self.orelse})'

    def get_value(self):
        body = self.body.get_value()
        test = self.test.get_value()
        orelse = self.orelse.get_value()
        if test:
            return body
        return orelse

    def to_dict(self):
        return {
            'name': self.name,
            'body': self.body.to_dict(),
            'test': self.test.to_dict(),
            'orelse': self.orelse.to_dict(),
        }

class OperatorAggregation(Aggregation):
    def __init__(self, series, lhs, rhs, skip_merge=False):
        self.series = series
        self.lhs = Aggregation.lift(lhs)
        self.rhs = Aggregation.lift(rhs)
        self.skip_merge = skip_merge

    def op(self, x, y):
        raise Exception('Unimplemented `op` for OperatorAggregation.')

    def merge(self, other):
        if self.skip_merge:
            return other
        return self.__class__(None, self.lhs.merge(other.lhs), self.rhs.merge(other.rhs))
    
    def clone(self):
        return self.__class__(None, self.lhs, self.rhs, self.skip_merge)

    def equals(self, other):
        return isinstance(other, type(self)) and \
               self.lhs == other.lhs and \
               self.rhs == other.rhs

    def __repr__(self):
        return f'Operator({self.name}, {self.lhs}, {self.rhs})'

    def get_value(self):
        x = self.lhs.get_value()
        y = self.rhs.get_value()
        # If either are None this means we have an average aggregation or something that didn't provide a value. So we cannot provide a value either
        if x is None or y is None:
            return None
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
        return x * y

class GreaterThanAggregation(OperatorAggregation):
    name = 'gt'
    def op(self, x, y):
        return x > y

class LessThanAggregation(OperatorAggregation):
    name = 'lt'
    def op(self, x, y):
        return x < y

class LessThanOrEqualAggregation(OperatorAggregation):
    name = 'lte'
    def op(self, x, y):
        return x <= y

class GreaterThanOrEqualAggregation(OperatorAggregation):
    name = 'gte'
    def op(self, x, y):
        return x >= y

class EqualAggregation(OperatorAggregation):
    name = 'eq'
    def op(self, x, y):
        return x == y

class NotEqualAggregation(OperatorAggregation):
    name = 'ne'
    def op(self, x, y):
        return x != y

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
    def __init__(self, series, average, count, skip_merge=False):
        self.series = series
        self.average = average
        self.count = count
        self.skip_merge = skip_merge

    def __eq__(self, other):
        return isinstance(other, type(self)) and \
               self.average == other.average and \
               self.count == other.count

    def __repr__(self):
        return f'AverageAggregation({self.average}, {self.count})'

    def clone(self):
        return AverageAggregation(self.series, self.average, self.count, self.skip_merge)

    @staticmethod
    def from_series(series):
        xs = series.series.sum()
        return AverageAggregation.from_sum_and_count(series, xs, series.series.size)

    @staticmethod
    def from_sum_and_count(series, sum, count):
        average = None # An average of "None" means there was no data to average over
        if count != 0:
            average = sum / count
        agg = AverageAggregation(series, average, count)
        return agg

    def merge(self, other):
        if self.skip_merge:
            return other
        count = self.count + other.count
        if other.average is None:
            ret = AverageAggregation(other.series, self.average, self.count)
        elif self.average is None:
            ret = AverageAggregation(other.series, other.average, other.count)
        else:
            # Take the other Series, it would be pricy to keep a copy of all Series (by combining them)
            # We take the other.series because it should be the newer one
            ret = AverageAggregation(other.series,
                                      ((self.average * self.count) + (other.average * other.count)) / count,
                                      count)
        return ret

    def get_value(self):
        return self.average

    def to_dict(self):
        return {
            'name': self.name,
            'average': self.average,
            'count': self.count,
        }

class SumAggregation(Aggregation):
    name = 'sum'
    def merge(self, other):
        return SumAggregation(other.series, self.value + other.value)

class AbsAggregation(Aggregation):
    name = 'abs'
    def merge(self, other):
        # Always take latest
        return AbsAggregation(other.series, other.value)

    def get_value(self):
        return abs(self.value.get_value())

class MaxAggregation(Aggregation):
    name = 'max'
    def merge(self, other):
        return MaxAggregation(other.series, max(self.value, other.value))
    
class MinAggregation(Aggregation):
    name = 'min'    
    def merge(self, other):
        return MinAggregation(other.series, min(self.value, other.value))

class CumSumAggregation(Aggregation):
    name = 'cumsum'
    def merge(self, other):
        cumsum = other.series.series + self.value
        other.series.series = cumsum
        return CumSumAggregation(other.series, cumsum[-1])

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
