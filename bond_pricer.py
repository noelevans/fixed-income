from decimal import Decimal
import math
import scipy.interpolate


class CompoundingFrequencies(object):
    
    ANNUAL      =   1
    SEMI_ANNUAL =   2
    QUARTERLY   =   4
    MONTHLY     =  12
    WEEKLY      =  52
    DAILY       = 365
    

def _price(compounding_freq, principal, coupon_amt, length, rates):
    total   = 0.0
    coupons = int(compounding_freq * length)
    intervals = [c * (1.0 / compounding_freq) for c in xrange(1, coupons + 1)]
    legs = [coupon_amt * math.exp( -rates(i) * i) for i in intervals]
    total = sum(legs)

    # add returned principal
    total += principal * math.exp( -rates(length) * length)
    return total


class Bond(object):
    
    def __init__(self, principal, coupon, compounding_freq, year_time, 
                 continuous_rate=None, compounding_rate=None):
        if bool(continuous_rate) == bool(compounding_rate):
            raise Exception('Must specify continuous_rate OR compounding_rate')
        self.principal  = principal
        self.coupon_amt = coupon
        self.year_time  = year_time
        self._continuous_rate  = continuous_rate 
        self._compounding_rate = compounding_rate 
        self.compounding_freq  = compounding_freq
        
    def continuous_rate(self):
        if self._continuous_rate:
            return self._continuous_rate
        m = self.compounding_freq
        return math.log(math.pow(1 + self._compounding_rate / m, m))
        
    def compounded_rate(self):
        if self._compounding_rate:
            return self._compounding_rate
        m = self.compounding_freq
        return m * (math.exp(self._continuous_rate / m) - 1)
        
    def n_year_zero_rate(self):
        return self.principal * math.exp(self.continuous_rate() * self.year_time)
        
    def treasury_zero_rate(self, maturity):
        maturities = [0.500, 1.000, 1.500, 2.000]
        zero_rates = [0.050, 0.058, 0.064, 0.068]
        zero_rate_curve = scipy.interpolate.interp1d(maturities, zero_rates)
        return zero_rate_curve(maturity)
        
    def market_price(self):
        return _price(self.compounding_freq, self.principal, self.coupon_amt,
                      self.year_time, self.treasury_zero_rate)
        
    def newton_raphson_bond_yield(self):
        # using the iterative _price call, the result will approach the market_price amount
        market_price = self.market_price()
                
        def price_with_rate(rate, target=0.0):
            rates = lambda x: rate
            return _price(self.compounding_freq, self.principal, self.coupon_amt,
                    self.year_time, rates) - target
        
        def price_prime(r):
            # gradient at r
            less = r - 0.0000001
            more = r + 0.0000001
            f_less = price_with_rate(less, market_price)
            f_more = price_with_rate(more, market_price)
            return (f_more - f_less) / (more - less)
        
        old_rate = 0.5
        while True:
            new_rate = old_rate - (price_with_rate(old_rate, market_price) / price_prime(old_rate))
            if abs(new_rate - old_rate) < 0.0000001:
                break
            old_rate = new_rate
        return new_rate
        
        
if __name__ == '__main__':
    b1 = Bond(principal=100, coupon=3, compounding_freq=CompoundingFrequencies.SEMI_ANNUAL, 
              year_time=2, compounding_rate=2.0)
    daily_rate      = b1.continuous_rate()
    compounded_rate = b1.compounded_rate()
    market_price    = b1.market_price()
    bond_yield      = b1.newton_raphson_bond_yield()
    
    print 'Daily rate:       %.5f' % daily_rate
    print 'Quarterly rate:   %.5f' % compounded_rate
    print 'Market price:    %.5f' % market_price
    print 'Bond yield:       %.5f' % bond_yield
