class ZeroCurve():

	def __init__(self, maturity_rates):
		self.maturity_rates = maturity_rates
	
	def addMaturityRate(self, maturity_rate):
		self.maturity_rates.append(maturity_rate)
		
	def get(self, maturity):
		return self.maturity_rates[maturity]


class Bond():

	def __init__(self, principle, maturity, coupon, pay_freq):
		self.principle = principle
		self.maturity = maturity
		self.coupon = coupon
		self.pay_freq = pay_freq
		
	def rate(zero_curve, interval):
		return Math.exp(-interval * zero_curve.get(interval))
	
	def getCleanPrice(self, zero_curve):
		summation = 0
		interval = 0
		while interval < maturity:
			summation += coupon * rate()
			interval += pay_freq
		summation += (principle + coupon) * rate()
		return summation
	
