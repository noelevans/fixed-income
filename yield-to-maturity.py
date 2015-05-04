import math

def returnRate(pv,fv,y):
	return math.pow( fv / pv, 1.0 / y ) - 1


def dfYTM(z, p, c, b, y):
	return ( y + 1 ) * ( c + b ) * math.pow( z, y ) - y * b * math.pow( z, y - 1) - ( c + p )


def fYTM(z, p, c, b, y):
	return ( c + b ) * math.pow( z, y+1 ) - b * math.pow( z, y ) - ( c + p ) * z + p


def bondYTM(current_value, rate, par_value, years_to_mat):
	
	z = rate
	coupon = rate * par_value
	error_margin = 0.00001

	if rate == 0:
		return returnRate(current_value, par_value, years_to_mat)

		
	for i in range( 0, 100 ):

		if math.fabs(fYTM( z, current_value, coupon, par_value, years_to_mat)) < error_margin:
			break
		
		while math.fabs(dfYTM(z, current_value, coupon, par_value, years_to_mat)) < error_margin:
			z+= .1
		z = z - (fYTM(z, current_value, coupon, par_value, years_to_mat) 
			/ dfYTM(z, current_value, coupon, par_value, years_to_mat))

	if math.fabs(fYTM(z, current_value, coupon, par_value, years_to_mat)) >= error_margin:
		return -1  # error

	return (1/z) - 1


def doCalc():
	
	current_value = 1100
	coupon_value = 3.75
	par_value = 1000
	years_to_mat = 5
	rate = coupon_value/100
	
	current_yield = rate * par_value * 100 / current_value
	
	ytm = bondYTM(current_value, rate, par_value, years_to_mat)
	if ytm >= 0:
		ytm = ytm * 100
	else:
		ytm = "error"

	print current_yield
	print ytm


doCalc()
