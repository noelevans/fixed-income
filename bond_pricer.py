from decimal import Decimal
import math
import scipy.interpolate
from pprint import pprint

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
                 continuous_rate=None, compounding_rate=None, price_paid=None):
        if bool(continuous_rate) == bool(compounding_rate):
            raise Exception('Must specify continuous_rate OR compounding_rate')
        self.principal  = principal
        self.coupon_amt = coupon
        self.year_time  = year_time
        self.price_paid = price_paid
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
        
    def zero_rate(self, shorter_bonds=[]):
        if not self.coupon_amt:
            return math.log(self.principal/self._price) / self.year_time
        if not shorter_bonds:
            raise Exception('Cannot derive implied rate without constituent shorter bonds')
        for b in shorter_bonds:
            pass
        
    def treasury_zero_rate(self, maturity):
        maturities = [0.0, 0.500, 1.000, 1.500, 2.000]
        zero_rates = [0.0, 0.050, 0.058, 0.064, 0.068]
        zero_rate_curve = scipy.interpolate.interp1d(maturities, zero_rates)
        return zero_rate_curve(maturity)
        
    def market_price(self):
        return _price(self.compounding_freq, self.principal, self.coupon_amt,
                      self.year_time, self.treasury_zero_rate)
        
    def bond_yield(self):
        # Newton-Raphson: Use iterative _price calls. The result will approach
        # the market_price amount by varying the rate that are paid 
        # on the legs (a constant rate, not varying)
        market_price = self.market_price()
                
        def price_with_rate(rate, target=0.0):
            rates = lambda x: rate
            return _price(self.compounding_freq, self.principal, self.coupon_amt,
                    self.year_time, rates) - target
        
        def price_prime(r):
            # gradient at rate, r
            less = r - 0.0000001
            more = r + 0.0000001
            f_less = price_with_rate(less, market_price)
            f_more = price_with_rate(more, market_price)
            return (f_more - f_less) / (more - less)
        
        old_rate = 0.5
        while True:
            new_rate = old_rate - (price_with_rate(old_rate, market_price) / 
                                   price_prime(old_rate))
            if abs(new_rate - old_rate) < 0.0000001:
                break
            old_rate = new_rate
        return new_rate
        
    def par_yield_compounding_coupon(self):
        # Again use Newton-Raphson. Vary the coupon to reach a 
        # price equal to the **par** value (the principal amount)
        old_coupon = self.coupon_amt
        
        def price_with_coupon(coupon, target):
            return _price(self.compounding_freq, self.principal, coupon,
                    self.year_time, self.treasury_zero_rate) - target
                    
        def price_prime(c):
            # gradient at coupon, c
            less = c - 0.0000001
            more = c + 0.0000001
            f_less = price_with_coupon(less, self.principal)
            f_more = price_with_coupon(more, self.principal)
            return (f_more - f_less) / (more - less)
            
        while True:
            p_prime = price_prime(old_coupon)
            if p_prime == 0:
                return old_coupon
            new_coupon = old_coupon - (price_with_coupon(old_coupon, self.principal) / 
                                       p_prime)
            if abs(new_coupon - old_coupon) < 0.0000001:
                break
            old_coupon = new_coupon
        return new_coupon / self.principal
        
    def annualised_par_yield(self):
        par_yield_coupon  = self.par_yield_compounding_coupon()
        return self.compounding_freq * par_yield_coupon
        
    def continuous_par_yield(self):
        m = self.compounding_freq
        return math.log(math.pow(1 + self.annualised_par_yield() / m, m))
        

class ZeroCurve(object):
    
    def __init__(self, bonds):
        self.bonds = sorted(bonds, key=lambda b: b.year_time)
        self.rates = self.build_rates()
        
    def build_rates(self):
        rates = []
        for b in self.bonds:
            if not b.coupon_amt:
                r = math.log(b.principal/b.price_paid) / b.year_time
            else:
                mats_so_far  = [el[0] for el in rates]
                rates_so_far = [el[1] for el in rates]
                curve_so_far = scipy.interpolate.interp1d(mats_so_far, rates_so_far)
                
                n_coupons = int(b.compounding_freq * b.year_time)
                intervals = [c * (1.0 / b.compounding_freq) for c in xrange(1, n_coupons + 1)]
                legs = sum(b.coupon_amt * math.exp( -i * curve_so_far(i)) for i in intervals[:-1])
                tmp  = (b.price_paid - legs) / (b.principal + b.coupon_amt)
                r = math.log(tmp) / - b.year_time
            rates.append((b.year_time, r))
        return rates

        
if __name__ == '__main__':
    
    print 'Simple bond prices and yields'
    
    semi_annual = CompoundingFrequencies.SEMI_ANNUAL
    b0 = Bond(principal=100, coupon=3, compounding_freq=semi_annual, 
              year_time=2, compounding_rate=2.0)
    daily_rate       = b0.continuous_rate()
    compounded_rate  = b0.compounded_rate()
    market_price     = b0.market_price()
    bond_yield       = b0.bond_yield()
    annual_par_yield = b0.annualised_par_yield()
    continuous_par_yield = b0.continuous_par_yield()
    
    print 'Daily rate:           %.4f' % daily_rate
    print 'Quarterly rate:       %.4f' % compounded_rate
    print 'Market price:         %.4f' % market_price
    print 'Bond yield:           %.4f' % bond_yield
    print 'Par yield:            %.4f' % annual_par_yield
    #print 'Continuous par yield: %.4f    *** This still needs correction! ***' \
        % continuous_par_yield

    print 'Form treasury zero rate'
    # We have these bonds available in the market
    b1 = Bond(principal=100, coupon=0, compounding_freq=semi_annual,
              year_time=0.25, compounding_rate=1.0, price_paid=97.5)
    b2 = Bond(principal=100, coupon=0, compounding_freq=semi_annual,
              year_time=0.50, compounding_rate=1.0, price_paid=94.9)
    b3 = Bond(principal=100, coupon=0, compounding_freq=semi_annual,
              year_time=1.00, compounding_rate=1.0, price_paid=90.0)
    b4 = Bond(principal=100, coupon=4, compounding_freq=semi_annual,
              year_time=1.50, compounding_rate=1.0, price_paid=96.0)
    b5 = Bond(principal=100, coupon=6, compounding_freq=semi_annual,
              year_time=2.00, compounding_rate=1.0, price_paid=101.6)
    
    zc = ZeroCurve([b1, b2, b3, b4, b5])
    print 'ZeroCurve:'
    pprint(zc.rates)
