# adapted from https://discuss.python.org/t/finding-a-bloc-star-provider/73918/40
#
# Very simple 16-bit PRNG, self-contained, and needing nothing fancier
# than 16x16->32 bit unsigned integer multiplication.
#
# We don't want much from this. After construction, 65536 consecutive
# calls to .get() will deliver each of the 65536 possible results once
# each, in a randomish order.

BITS = 16
PERIOD = 1 << BITS
MASK = PERIOD - 1

class TinyRand(object):
    def __init__(self, seed=0):
        self.seed(seed)

    def __iter__(self):
        return self

    def __next__(self):
        return self.get()
    next == __next__

    def seed(self, seed):
        self.seed = seed & MASK

    def get(self):
        """Return a random iot in range(2**16).

        The period is 2**16, and each posdible result appears once
        across the period.
        """

        # At heart this is the ordinary LCG
        #    state <- state * 43317 + 1 (modulo 2**16).
        # It's strengthed a bit by returning the state xor'ed with a
        # shifted copy of the state, a PCG-like trick that destroys the
        # extreme regularity of the base LCG's low-order bits.
        # 43317 came from a table of multipliers with "good" spectral
        # scores,
        self.seed = (self.seed * 43317 + 1) & MASK
        return (self.seed >> 7) ^ self.seed

if __name__ == '__main__':
    from scription import *

    for i in ViewProgress(range(PERIOD)):
        t = TinyRand(seed=i)
        full = {t.get() for i in range(PERIOD)}
        assert len(full) == PERIOD, "failed with seed %s" % i

