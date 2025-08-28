from __future__ import division, print_function

import sys
sys

def all_equal(iterator, test=None):
    """
    If test is None do a straight equality test.
    """
    it = iter(iterator)
    if test is None:
        try:
            target = next(it)
            test = lambda x: x == target
        except StopIteration:
            return True
    return all(test(x) for x in it)


def grouped(it, size):
    'yield chunks of it in groups of size'
    if size < 1:
        raise ValueError('size must be greater than 0 (not %r)' % size)
    result = []
    count = 0
    for ele in it:
        result.append(ele)
        count += 1
        if count == size:
            yield tuple(result)
            count = 0
            result = []
    if result:
        yield tuple(result)

def grouped_by_column(it, size):
    'yield chunks of it in groups of size columns'
    if size < 1:
        raise ValueError('size must be greater than 0 (not %r)' % size)
    elements = list(it)
    iters = []
    rows, remainder = divmod(len(elements), size)
    if remainder:
        rows += 1
    for column in grouped(elements, rows):
        iters.append(column)
    return zip_longest(*iters, fillvalue='')

class xrange(object):
    """
    Accepts arbitrary objects to use to produce sequence iterators.
    """
    def __init__(self, start, stop=None, step=None, count=None, epsilon=None):
        """
        range(7) -> start=0, stop=7, step=1, count=None
        range(5, count=3) -> start=0, stop=5, step=1, count=3 (raises)
        range(start=5, count=3) -> start=5, stop=None, step=1, count=3
        range(1, 3, step=2) -> start=1, stop=3, step=2, count=None
        """
        if stop is None and count is None:
            # `start` value is actually `stop`
            start, stop = None, start
        if count is not None and count < 0:
            raise ValueError('count must be a non-negative number')
        # valid combinations:
        # start  stop  step  count    notes
        #          x                  start=0, step=1
        #          x     x            start=0, step=1
        #   x                         step=1, infinite
        #   x      x                  step=1
        #   x            x            infinite
        #   x                   x     step=1
        #   x      x     x
        #   x      x            x     step=1
        #   x            x      x
        #   x      x     x      x
        #
        combo = [1 if a is not None else 0 for a in (start, stop, step, count)]
        if combo not in (
                [0, 1, 0, 0],
                [0, 1, 1, 0],
                [1, 0, 0, 0],
                [1, 1, 0, 0],
                [1, 0, 1, 0],
                [1, 0, 0, 1],
                [1, 1, 1, 0],
                [1, 1, 0, 1],
                [1, 0, 1, 1],
                [1, 1, 1, 1],
                ):
            args = [name for (name, present) in zip(('start','stop','step','count'), combo) if present]
            raise TypeError('invalid combination of arguments: %s' % ', '.join(args))
        if start is not None:
            ref = type(start)
        else:
            ref = type(stop)
            start = ref(0)
        if step is None:
            try:
                step = ref(1)
                if stop is not None and stop < start:
                    step = ref(-1)
            except TypeError:
                raise ValueError("step must be specified for type %r" % type(stop))
        try:
            if callable(step):
                start + step(start, 1, start)
            else:
                start + step
        except TypeError:
            raise TypeError('unable to add %r to %r' % (step, start))
        self.start = start
        self.stop = stop
        self.step = step
        self.count = count
        self.epsilon = epsilon
        self.values = None

    def __contains__(self, value):
        if self.values is None:
            self.values = list(self)
        return value in self.values

    def __iter__(self):
        if self.values is not None:
            return iter(self.values)
        else:
            return self._generate_values()

    def __repr__(self):
        values = []
        if self.start:
            values.append(repr(self.start))
        if self.stop is not None:
            values.append(repr(self.stop))
        values.extend([
            '%s=%r' % (k,v)
            for k,v in (
                ('step', self.step),
                ('count', self.count),
                ('epsilon', self.epsilon),
                )
            if v is not None
            ])
        return '%s(%s)' % (self.__class__.__name__, ', '.join(values))

    def _generate_values(self):
        start, stop, step, count, epsilon = self.start, self.stop, self.step, self.count, self.epsilon
        i = -1
        target = None
        if stop is not None and epsilon is not None:
            target = stop - epsilon, stop + epsilon
        reverse = None
        if stop is not None:
            reverse = stop < start
        while 'more values to yield':
            if count is not None:
                if count < 1:
                    break
                count -= 1
            i += 1
            if i == 0:
                value = start
            else:
                if callable(step):
                    value = step(start, i, value)
                else:
                    value = start + i * step
            if stop is not None:
                if value == stop:
                    break
                if reverse:
                    if value <= stop:
                        break
                else:
                    if value >= stop:
                        break
                if target is not None and target[0] <= value <= target[1]:
                    break
            yield value


