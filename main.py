import matplotlib.pyplot as plt
import numpy as np

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

def generate_moter_curve(power_max, brandtijd):
    xcalc = []
    ycalc = []
    looprange = int(brandtijd * 10 + 1)
    for i in range(0, looprange):
        x = i/10
        xcalc.append(x)
        ycalc.append(-(power_max/(0.5*brandtijd)**2)*(x-(0.5*brandtijd))**2+power_max)


    xpoints = np.array(xcalc)
    ypoints = np.array(ycalc)

    plt.plot(xpoints, ypoints)
    plt.show()

def calc_drag (k, speed):
    return k*(speed**2)

generate_moter_curve(rocket_motor_max,rocket_motor_brandtijd)
