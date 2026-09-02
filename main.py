import matplotlib.pyplot as plt
import numpy as np

# rocket setup
rocket_weight = 0.25 # in kilogram
rocket_drag_coefficient = 0.6 # to be defined
rocket_motor_avg = 12 # in newton
rocket_motor_max = 35 # in newton
rocket_motor_brandtijd = 1.6 # in seconden

valversnelling = 9.81 # in meter per seconde kwadraat
zwaartekracht = valversnelling*rocket_weight

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


def calculate_newton():
    print("something")

calculate_newton()
generate_moter_curve(rocket_motor_max,rocket_motor_brandtijd)




