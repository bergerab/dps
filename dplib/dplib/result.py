class AggregationCache:
    def __init__(self):
        self.cache = []
        self.precache = []
    
    def add(self, x):
        self.precache.append(x)

    def commit(self):
        self.cache = self.precache
        self.precache = []

    def pop(self):
        return self.cache.pop()

    def is_empty(self):
        return bool(self.cache)

class Result:
    def __init__(self, value):
        self.value = value
    
    def __add__(self, other):
        return self.value + other.value
    
    def __radd__(self, other):
        return other.value + self.value        
    
    def __sub__(self, other):
        return self.value - other.value
    
    def __rsub__(self, other):
        return other.value - self.value        
    
    def __mul__(self, other):
        return self.value * other.value
    
    def __rmul__(self, other):
        return other.value * self.value
    
    def __truediv__(self, other):
        return self.value / other.value
    
    def __rtruediv__(self, other):
        return other.value / self.value
    
    def __floordiv__(self, other):
        return self.value // other.value
    
    def __rfloordiv__(self, other):
        return other.value // self.value
