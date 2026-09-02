import matplotlib.pyplot as plt
import numpy as np
import math

# rocket setup
rocket_weight = 0.25 # kilogram
rocket_drag_coefficient = 0.6 # to be defined
rocket_motor_avg = 12 # newton
rocket_motor_max = 35 # newton
rocket_motor_brandtijd = 1.6 # seconden
rocket_surface = 4.42*10**-3 # vierkante meter

valversnelling = 9.81 # meter per seconde kwadraat
luchtdichtheid = 1.225 # kilogram per kubieke meter, bij 15C

zwaartekracht = valversnelling*rocket_weight
k_waarde = .5*luchtdichtheid*rocket_surface*rocket_drag_coefficient

def generate_moter_curve(force_max, brandtijd):
    tcalc = []
    ncalc = []
    looprange = int(brandtijd * 10 + 1)
    for i in range(0, looprange):
        x = i/10
        tcalc.append(x)
        ncalc.append(-(force_max/(0.5*brandtijd)**2)*(x-(0.5*brandtijd))**2+force_max)

    xpoints = np.array(tcalc)
    ypoints = np.array(ncalc)

    plt.plot(xpoints, ypoints)
    plt.xlabel("time (t)")
    plt.ylabel("force (N)")
    plt.show()

def calc_drag (k, speed):
    return k*(speed**2)

def plot_height (upforce_avg, mass, k, fz):
    hcalc = []
    tcalc = []
    h = 0
    v = 0
    t = 0
    while h >= 0:
        tcalc.append(t)
        hcalc.append(h)
        if t > 1.6:
            upforce_avg = 0
            fd = calc_drag(k, v)
            fn = upforce_avg - fz - fd
            a = fn / mass
            v = a * t
            h = v * t
            t += 0.1
        else:
            fd = calc_drag(k, v)
            fn = upforce_avg - fz - fd
            a = fn / mass
            v = a * t
            h = v * t
            t += 0.1

    xpoints = np.array(tcalc)
    ypoints = np.array(hcalc)

    plt.plot(xpoints, ypoints)

    plt.xlabel("time (t)")
    plt.ylabel("height (m)")

    plt.show()

plot_height(rocket_motor_avg, rocket_weight, k_waarde,zwaartekracht)
generate_moter_curve(rocket_motor_max,rocket_motor_brandtijd)
