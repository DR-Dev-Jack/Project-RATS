import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math

# rocket setup
rocket_weight = 0.25 # kilogram
fuel_weight = 0.024 # still in kilograms
rocket_drag_coefficient = 0.6 # to be defined
rocket_motor_avg = 12 # newton
rocket_motor_max = 35 # still in newton
rocket_motor_brandtijd = 1.6 # seconden
rocket_surface = 4.42e-3 # vierkante meter

valversnelling = 9.81 # meter per seconde kwadraat
# luchtdichtheid = 1.225 # kilogram per kubieke meter, bij 15C    !!!Add changing air density by height!!!
temperatuur = 288.15 # kelvin, 15c
gasconstante = 287.05 # joule per kilogram kelvin. in droge lucht, misschien aanpasbaar met luchtvochtigheid?

#zwaartekracht = valversnelling*rocket_weight
# k_waarde = .5*luchtdichtheid*rocket_surface*rocket_drag_coefficient

file_adres = 'TSP_D12.csv'
skip_lines = 4

def generate_moter_curve(file_adres, skip_lines):  # !!!Average is 12 Ns, about 7N ): so not right!!!
    data = pd.read_csv(file_adres, skiprows=skip_lines)

    time = data['Time (s)'].to_numpy()
    thrust = data['Thrust (N)'].to_numpy()

    return time, thrust

def calc_luchtdichtheid(R, T, h, g):
    M = float(2.9*10**-2)
    Po= 101325.0
    presure_at_height = Po * math.e**((-1.0 * M*g*h)/(R*T))
    luchtdichtheid = presure_at_height/(R*T)

    return luchtdichtheid

def calc_k (p, A, cd):
    return .5*p*A*cd

def calc_drag (k, speed):
    return k * speed * abs(speed)

def plot_height (x, y , mass, g, d1, t1, R, T, A, cd, dt=0.1, ):
    hcalc = []
    tcalc = []

    h = 0
    v = 0
    t = 0
    burned_weight = 0
    total = d1*t1
    check = False
    while h >= 0:
        # using RK4 would be better than this simple version of eulors function
        h += v*dt

        tcalc.append(t)
        hcalc.append(h)

        fs = np.interp(t, x, y)
        luchtdichtheid = calc_luchtdichtheid(R, T, h, g)
        k = calc_k(luchtdichtheid, A, cd)
        fd = calc_drag(k, v)
        burned_weight += fs*dt
        minus_weight = burned_weight/total*0.024
        fz = g*(mass - minus_weight)

        fnorm = fz
        if fs > fz:
            check = True

        if check:
            fnorm = 0

        fn = fs + fnorm - fz - fd

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

x_cords, y_cords = generate_moter_curve(file_adres, skip_lines)
plot_height(x_cords, y_cords, rocket_weight, valversnelling, rocket_motor_avg, rocket_motor_brandtijd, gasconstante, temperatuur, rocket_surface, rocket_drag_coefficient)
