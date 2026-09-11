import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math

# rocket setup
rocket_weight = 0.6 # kilogram of 0.15 voor de cartoon rocket
fuel_weight = 0.028 # still in kilograms and 0.024 for the D12
rocket_drag_coefficient = 0.5 # to be defined
parachute_drag_coefficient = 0.8 # approximatly
rocket_surface = 4.42e-3 # vierkante meter

valversnelling = 9.81 # meter per seconde kwadraat
temperatuur = 288.15 # kelvin, Celcuis is T - 273.15
gasconstante = 287.05 # joule per kilogram kelvin

file_adres = "TSP_E20.csv"# or 'TSP_D12.csv'
skip_lines = 4

def generate_moter_curve(adress, skip):
    data = pd.read_csv(adress, skiprows=skip)

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

def plot_height (x, y , mass, g, R, T, A, rcd, pcd,fuel, dt=0.01):
    hcalc = []
    tcalc = []

    h2calc = []
    t2calc = []

    h = 0
    v = 0
    t = 0
    burned_weight = 0
    total = 0
    for i in range(int(x[-1]/dt)):
        total += np.interp(i*dt, x, y)
    print(total)
    check = False
    while h >= 0:
        # using RK4 would be better than this simple version of eulors function
        h += v*dt

        tcalc.append(t)
        hcalc.append(h)
        t2calc.append(t)
        h2calc.append(v)

        fs = np.interp(t, x, y)
        luchtdichtheid = calc_luchtdichtheid(R, T, h, g)
        if t > 6.8:
            k = calc_k(luchtdichtheid, A, pcd)
        else:
            k = calc_k(luchtdichtheid, A, rcd)
        fd = calc_drag(k, v)
        burned_weight += fs*dt
        minus_weight = burned_weight/total * fuel
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

    x2points = np.array(t2calc)
    y2points = np.array(h2calc)
    

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

    plt.subplot(2, 2, 4)
    plt.plot(x2points, y2points)
    plt.title("Rocket velocity curve")

    plt.xlabel("time (t)")
    plt.ylabel("velocity (m/s)")

    plt.show()

x_cords, y_cords = generate_moter_curve(file_adres, skip_lines)
plot_height(x_cords, y_cords, rocket_weight, valversnelling, gasconstante, temperatuur, rocket_surface, rocket_drag_coefficient, parachute_drag_coefficient, fuel_weight)
