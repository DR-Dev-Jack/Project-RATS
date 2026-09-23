import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import openmeteo_requests
import requests_cache
from retry_requests import retry
import math as m

# rocket setup
rocket_weight = 0.6 # kilogram of 0.15 voor de cartoon rocket
rocket_drag_coefficient = 0.5 # to be defined
parachute_drag_coefficient = 0.8 # approximatly
rocket_surface = 4.42e-3 # vierkante meter, bij diameter van 75mm
parachute_surface = 1.59*10**-1 # vierkante meter, bij diameter van 45cm

#fuel setup
fuel_weight = 0.028 # still in kilograms and 0.024 for the D12
brandtijd = 2.2 # seconden
delaytime = 5.0 # seconden

#natuur constante
valversnelling = 9.81 # meter per seconde kwadraat
#temperatuur = 288.15 # kelvin, Celcuis is T - 273.15
gasconstante = 287.05 # joule per kilogram kelvin

# locatie
# school
latitude = 52.36
longitude = 4.92
# woestijn
# latitude = 24.58
# longitude = 13.21

file_adres = "TSP_E20.csv"# or 'TSP_D12.csv'
skip_lines = 4

api_acces_point = "https://api.open-meteo.com/v1/forecast"
location_and_etc = {
    "latitude": latitude,
    "longitude": longitude,
    "current": ["temperature_2m", "wind_speed_10m", "wind_direction_10m", "surface_pressure"],
    "wind_speed_unit": "ms",
}

def get_live_data(url, params):
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)
    responses = openmeteo.weather_api(url, params = params)
    response = responses[0]
    current = response.Current()
    current_temperature_2m = current.Variables(0).Value()
    current_wind_speed_10m = current.Variables(1).Value()
    current_wind_direction_10m = current.Variables(2).Value()
    current_surface_pressure = current.Variables(3).Value()
    temprature_in_kelvin = current_temperature_2m + 273.15
    pressure_in_pascal = current_surface_pressure * 100
    print("tempratuur: ", temprature_in_kelvin)
    print("wind speed: ", current_wind_speed_10m)
    print("wind direction: ", current_wind_direction_10m)
    print("pressure: ", current_surface_pressure)
    return temprature_in_kelvin, current_wind_speed_10m, pressure_in_pascal

def read_motor_curve_file(adress, skip):
    data = pd.read_csv(adress, skiprows=skip)

    time = data['Time (s)'].to_numpy()
    thrust = data['Thrust (N)'].to_numpy()

    return time, thrust

def calc_luchtdichtheid(R, T, h, g, Po):
    M = float(2.9*10**-2)
    t_op_hoogte = T-(6.5e-3*h)
    presure_at_height = Po * m.e**((-1.0 * M*g*h)/(R*t_op_hoogte))
    luchtdichtheid = presure_at_height/(R*t_op_hoogte)

    return luchtdichtheid

def calc_k (p, A, cd):
    return .5*p*A*cd #p is luchtdichtheid, A is oppervlak, cd is drag coefficient

def calc_drag (k, speed):
    return k * speed * abs(speed)

def calc_angels(rocket_pitch, angular_velocity, wind_speed, rocket_speed, p=1.2, A=4.42e-3, cd=0.5, mass=0.6, lenght=0.6, d=0.2, dt=0.01):
    target_angle = m.atan2(rocket_speed, wind_speed)
    angle_error = rocket_pitch - target_angle
    k = calc_k(p, A, cd)
    Fwind = wind_speed**2 * k * angle_error
    I = 1/12*mass*lenght**2
    Torque = -Fwind * d # d should be the distance from the center of mass to the point where the force is applied
    torque_dampening = angular_velocity * 0.3 # 0.3 is an estimate
    torque_total = Torque-torque_dampening
    angular_acceleration = torque_total/I
    angular_velocity += angular_acceleration*dt
    rocket_pitch += angular_velocity*dt
    return rocket_pitch, angular_velocity

def plot_height (x, y , mass, g, R, T, current_wind, Ar, rcd, pcd, fuel, bt, delay, Ap, pressure, rocket_angle_x=0, dt=0.01):
    hcalc = []
    tcalc = []

    vcalc = []
    t2calc = []

    h = 0
    v = 0
    t = 0
    burned_weight = 0
    total = 0

    rP = 0
    aV = 0
    counter = 0
    for i in range(int(x[-1]/dt)):
        total += np.interp(i*dt, x, y)

    check = False
    while h >= 0:
        # using RK4 would be better than this simple version of eulors function
        h += v*dt

        tcalc.append(t)
        hcalc.append(h)
        t2calc.append(rP*57.3)
        vcalc.append(t)

        fs = np.interp(t, x, y)
        luchtdichtheid = calc_luchtdichtheid(R, T, h, g, pressure)
        if t > bt+delay:
            k = calc_k(luchtdichtheid, Ap, pcd)
        else:
            k = calc_k(luchtdichtheid, Ar, rcd)
        fd = calc_drag(k, v)
        burned_weight += fs*dt
        minus_weight = burned_weight/total * fuel

        fz = 6.67e-11*(((mass - minus_weight)*5.97e24)/(6.364844e6+h)**2) #Fz=gravitatieconstante⋅(massa van de aarde⋅massa van het object)/afstand tot het midden van de aarde

        fnorm = fz
        if fs > fz:
            check = True

        if check:
            fnorm = 0

        fn = fs*m.cos(rocket_angle_x) + fnorm - fz - fd*m.cos(rocket_angle_x)

        a = fn / (mass-minus_weight)
        v += a*dt

        t += dt

        rP, aV= calc_angels(rP, aV, current_wind, v)

    xpoints = np.array(tcalc)
    ypoints = np.array(hcalc)

    x2points = np.array(t2calc)
    y2points = np.array(vcalc)
    

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

    plt.xlabel("degree from orgin")
    plt.ylabel("time in seconds")

    plt.show()

temperatuur, wind_speed, druk_aan_oppervlakte = get_live_data(api_acces_point, location_and_etc)
x_cords, y_cords = read_motor_curve_file(file_adres, skip_lines)
plot_height(x_cords, y_cords, rocket_weight, valversnelling, gasconstante, temperatuur, wind_speed, rocket_surface, rocket_drag_coefficient, parachute_drag_coefficient, fuel_weight, brandtijd, delaytime, parachute_surface, druk_aan_oppervlakte)
