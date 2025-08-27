from scipy import stats
import sys

class Initializer(object):
    """Weight distributions for custom initializations."""
    def __init__(self, distribution=None, low=0.0, high=1.0, mean=0.0, std=1.0):
        self.distribution = distribution
        if distribution is None:
            self.distribution = self.normal
        self.low = low
        self.high = high
        self.mean = mean
        self.std = std

    def __call__(self, shape):
        return self.distribution(self, shape)

    def normal(self, shape):
        """bell shaped distribution"""
        return stats.truncnorm.rvs(self.low, self.high, loc=self.mean, scale=self.std, size=shape)

    def uniform(self, shape):
        """plateau shaped distribution"""
        return stats.uniform.rvs(loc=self.low, scale=self.high-self.low, size=shape)

    def xavier(self, shape):
        """for tanh or sigmoid activation function"""
        return stats.truncnorm.rvs(self.low, self.high, scale=1.0/shape[0]**0.5, size=shape)

    def he(self, shape):
        """for relu activation function"""
        return stats.truncnorm.rvs(self.low, self.high, scale=2.0/shape[0]**0.5, size=shape)

if __name__ == '__main__':
    shape = (3, 3)
    low,high,mean,std = (
        0.0, 1.0, 0.0, 1.0
    )
    if len(sys.argv) >= 3:
        low = sys.argv[1]
        high = sys.argv[2]
    if len(sys.argv) >= 5:
        mean = sys.argv[3]
        std = sys.argv[4]
    print("shape %s low %s high %s mean %s std %s" % (shape, low, high, mean, std))
    print("normal")
    intl = Initializer(distribution=Initializer.normal, low=low, high=high, mean=mean, std=std)
    print(intl.normal(shape))
    print("uniform")
    intl = Initializer(distribution=Initializer.uniform, low=low, high=high, mean=mean, std=std)
    print(intl.uniform(shape))
    print("xavier")
    intl = Initializer(distribution=Initializer.xavier, low=low, high=high, mean=mean, std=std)
    print(intl.xavier(shape))
    print("he")
    intl = Initializer(distribution=Initializer.he, low=low, high=high, mean=mean, std=std)
    print(intl.he(shape))
