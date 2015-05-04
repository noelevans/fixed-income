from math import sqrt, exp, pi, log
import sys


"""
def compute(form):
    B_S_c = B_S_call(price,strike,remTime,vol,intRate)
    B_S_p = B_S_put(price,strike,remTime,vol,intRate)
    form.call.value = roundToPennies(B_S_c)
    form.put.value = roundToPennies(B_S_p)
"""

class Operator():
    def __init__(self, inSpot=0, inStrike=0, inRemTime=0, inVol=0, inIntRate=0):
        self.spot = inSpot
        self.strike = inStrike
        self.remTime = inRemTime
        self.vol = inVol
        self.intRate = inIntRate
    def roundToPennies(n):
        pennies = n*10000
        pennies = round(pennies)
        return pennies / 10000
    def erf(self, d):
        step = 0.01
        sum = 0
        x = -5 + step / 2
        while ( (x < d) and (x < 4) ):
            sum = sum + exp(- x * x / 2) * step
            x = x + step
        return sum / sqrt(2 * pi)
    def B_S_call(self, price, strike, remTime, vol, intRate):
        d1 = ( log( price / strike) + ( intRate + vol*vol / 2 ) * remTime ) / ( vol * sqrt( remTime) )
        d2 = d1 - vol * sqrt( remTime )
        return price * erf(d1) - strike * exp( - (intRate*remTime) ) * erf(d2)
    def B_S_put(price, strike, remTime, vol, intRate):
        d1 = ( log( price / strike) + ( intRate + vol*vol / 2 ) * remTime ) / ( vol * sqrt( remTime) )
        d2 = d1 - vol * sqrt( remTime )
        return strike * exp( - (intRate*remTime) ) * erf(-d2) - price * erf(-d1)
    def calc():
        d1 = ( log( price / strike) + ( intRate + vol*vol / 2 ) * remTime ) / ( vol * sqrt( remTime) )
        d2 = d1 - vol * sqrt( remTime )
        erfprimed1 = exp( -(d1*d1)/2 ) / sqrt( 2*pi )

class DeltaCall(Operator):
    def calc():
        return erf(d1)

class DeltaPut(Operator):
    def calc():
        return erf(d1) - 1


class ThetaCall(Operator):
    def calc():
        theta_c = - price * erfprimed1 * vol / ( 2 * sqrt( remTime ) ) - intRate * strike * exp( - intRate * remTime ) * erf(d2)
        return theta_c / 365


class ThetaPut(Operator):
    def calc():
        theta_p = - price * erfprimed1 * vol / ( 2 * sqrt( remTime ) ) + intRate * strike * exp( - intRate * remTime ) * erf(-d2)
        return theta_p / 365


class RhoCall(Operator):
    def calc():
        return strike * remTime * exp( - intRate * remTime ) * erf(d2) / 100


class RhoPut(Operator):
    def calc():
        return - strike * remTime * exp( - intRate * remTime ) * erf(-d2) / 100


class Vega(Operator):
    def calc():
        return price * sqrt( remTime ) * erfprimed1 / 100


class Gamma(Operator):
    def calc():
        return erfprimed1 / ( price * vol * sqrt( remTime) )


def getUserInput():
    print("Enter the following inputs...")
    price = float(raw_input(   "Spot price:        "))
    strike = float(raw_input(  "Strike price:      "))
    remTime = float(raw_input("Duration (days):   "))
    remTime = remTime / 365
    vol = float(raw_input(     "Volatility (%):    "))
    vol = vol / 100
    intRate = float(raw_input("Interest rate (%): "))
    intRate = intRate / 100


def displayCalcs():
    print()
    print()
    print("Spot price:   " + spot)
    print("Strike price: " + strike)
    print("Duration:     " + remTime)
    print("Volitility:   " + vol)
    print("Interest rate:" + intRate)
    print()
    print("Delta call:   " + DeltaCall.calc())
    """
    form.delta_call.value = roundToPennies(delta_c)
    form.delta_put.value = roundToPennies(delta_p)
    form.theta_call.value = roundToPennies(theta_c)
    form.theta_put.value = roundToPennies(theta_p)
    form.rho_call.value = roundToPennies(rho_c)
    form.rho_put.value = roundToPennies(rho_p)
    form.vega.value = roundToPennies(vega)
    form.gamma.value = roundToPennies(gamma)
    """


# main
getUserInput()
doCalc()
displayCalcs()
