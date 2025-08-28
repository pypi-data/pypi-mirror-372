import math

class Average:
    def __init__(self, arg=[0, 0]):
        self._sum = arg[0]
        self._count = arg[1]
    def __add__(self, other):
        return Average([self._sum + other._sum, self._count + other._count])
        # return HyperLogLog(bytearray(max(a,b) for a, b in zip(self._rmem, other._rmem)))

    def __radd__(self, other):
        return Average([self._sum + other._sum, self._count + other._count])
        # return HyperLogLog(bytearray(max(a,b) for a, b in zip(self._rmem, other._rmem)))

    def __iadd__(self, other):
        self._sum += other._sum
        self._count += other._count
        return self

    def __str__(self):
        return f'{self.value()}'

    def __repr__(self):
        return f'$avg(sum={self._sum}, count={self._count})'

    def value(self):
        if self._count == 0:
            return math.nan
        return self._sum / self._count

if __name__ == '__main__':
    x = Average([10, 2])
    y = Average([10, 5])
    print('x = ', x)
    print('y = ', y)
    print('x + y = ', x + y)
    print('repr(x) = ', repr(x))
    print('repr(y) = ', repr(y))