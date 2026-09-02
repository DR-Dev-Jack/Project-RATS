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

def generate_moter_curve(brandtijd, d):
    tcalc = [0, brandtijd/4, brandtijd]
    ncalc = [0, d*2, 0]
        
    xpoints = np.array(tcalc)
    ypoints = np.array(ncalc)

    return xpoints, ypoints

def calc_drag (k, speed):
    return k*(speed**2)

def plot_height (x,y , mass, k, fz, dt=0.1):
    hcalc = []
    tcalc = []

    h = 0
    v = 0
    t = 0
    a = 0
    fzw = 0
    while h >= 0:

        h += v*dt

        tcalc.append(t)
        hcalc.append(h)
        
        fs = np.interp(t, x, y)
        fd = calc_drag(k, v)

        if fs > fz:
            fzw = fz

        fn = fs - fzw - fd

        if h <= 0:
            fn = fs

        a = fn / mass
        v += a*dt

        
        t += dt

    xpoints = np.array(tcalc)
    ypoints = np.array(hcalc)

    plt.subplot(1, 2, 1)
    plt.plot(xpoints, ypoints)
    plt.title("Rocket height curve")

    plt.xlabel("time (t)")
    plt.ylabel("height (m)")

    plt.subplot(2, 2, 2)
    plt.plot(x,y)
    plt.title("Rocket motor output curve")

    plt.xlabel("time (t)")
    plt.ylabel("power (N)")

    plt.show()

x_cords, y_cords = generate_moter_curve(rocket_motor_brandtijd, rocket_motor_avg)
plot_height(x_cords, y_cords, rocket_weight, k_waarde,zwaartekracht)
