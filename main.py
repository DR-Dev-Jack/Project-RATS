import numpy as np
import pandas as pd
import openmeteo_requests
import requests_cache
from retry_requests import retry
import math as m
import plotly.express as px

has_parachute = True #aanpasbaar

# locatie aanpasbaar
# school
latitude = 52.36
longitude = 4.92
# woestijn
# latitude = 24.58
# longitude = 13.21

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
    print("tempratuur: ", current_temperature_2m)
    print("wind speed: ", current_wind_speed_10m)
    print("wind direction: ", current_wind_direction_10m)
    print("pressure: ", current_surface_pressure)
    return temprature_in_kelvin, current_wind_speed_10m, pressure_in_pascal, current_wind_direction_10m

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

def calc_speed(fsd, rP, Fext, mass, goniometrie):
    if goniometrie == "sin":
        fn = fsd*m.sin(rP) + Fext
    else:
        fn = fsd*m.cos(rP) + Fext
    return fn/mass

def calc_pitch(rocket_pitch, angular_velocity, wind_speed, rocket_speed, wind_direction, axis, p, A, cd, mass, lenght, dt=0.01):
    d = lenght /2
    target_angle = m.atan2(rocket_speed, wind_speed)
    angle_error = rocket_pitch - target_angle
    k = calc_k(p, A, cd)
    if axis == "x":
        wind_speed *= m.sin(m.radians(wind_direction))
    elif axis == "y":
        wind_speed *= m.cos(m.radians(wind_direction))
    
    Fwind = wind_speed**2 * k * angle_error #special!!!
    I = 1/12*mass*lenght**2 # traagsheidsmoment
    Torque = -Fwind * d # d should be the distance from the center of mass to the point where the force is applied
    torque_dampening = angular_velocity * 0.3 # 0.3 is an estimate
    torque_total = Torque-torque_dampening
    angular_acceleration = torque_total/I
    angular_velocity += angular_acceleration*dt
    rocket_pitch += angular_velocity*dt
    return rocket_pitch, angular_velocity, Fwind

def calc_plot_values (mass, g, R, Ar, rcd, pcd, fuel, bt, delay, Ap, length, has_parachute, file_adres, color, skip_lines, dt=0.01):
    hcalc, xcalc, ycalc, tcalc = [], [], [], []
    t = h = x = y = vh = vx = vy = burned_weight = total = 0
    rP = rPx = rPy = aV = aVx = aVy = Fwindx = Fwindy = 0

    newton_time, newton = read_motor_curve_file(file_adres, skip_lines)
    T, current_wind, pressure, wind_direction = get_live_data(api_acces_point, location_and_etc)

    gravitatie_c = 6.67e-11
    mass_earth = 5.97e24
    radius_earth = 6.364844e6

    for i in range(int(newton_time[-1]/dt)):
        total += np.interp(i*dt, newton_time, newton)

    check = False
    while h >= 0:
        # using RK4 would be better than this simple version of eulors function
        h += vh*dt
        x += vx*dt
        y += vy*dt

        tcalc.append(t)
        hcalc.append(h)
        xcalc.append(x)
        ycalc.append(y)

        fs = np.interp(t, newton_time, newton)
        luchtdichtheid = calc_luchtdichtheid(R, T, h, g, pressure)
        if t > bt + delay and has_parachute:
            k = calc_k(luchtdichtheid, Ap, pcd)
        else:
            k = calc_k(luchtdichtheid, Ar, rcd)
        fd = calc_drag(k, vh)
        burned_weight += fs * dt
        minus_weight = burned_weight / total * fuel

        fz = gravitatie_c * (((mass - minus_weight) * mass_earth) / (radius_earth + h) ** 2)

        fnorm = fz
        if fs > fz:
            check = True

        if check:
            fnorm = 0

        vh += calc_speed(fs-fd, rP, fnorm-fz, mass-minus_weight, "cos")*dt
        vx += calc_speed(fs-fd, rPx, Fwindx, mass-minus_weight, "sin")*dt
        vy += calc_speed(fs-fd, rPy, Fwindy, mass-minus_weight, "sin")*dt

        rPy, aVy, Fwindy = calc_pitch(rPy, aVy, current_wind, vh, wind_direction,"y", luchtdichtheid, Ar, rcd, mass, length)
        rPx, aVx, Fwindx = calc_pitch(rPx, aVx, current_wind, vh, wind_direction,"x", luchtdichtheid, Ar, rcd, mass, length)
        rP, aV, trash = calc_pitch(rP, aV, current_wind, vh, wind_direction,"z", luchtdichtheid, Ar, rcd, mass, length)

        t += dt

    df = pd.DataFrame(dict(
        y=ycalc,
        x=xcalc,
        z=hcalc
    ))

    fig = px.line_3d(
        df, x="x", 
        y="y", 
        z="z", 
        title="Positie",
        color_discrete_sequence=[color],
    )

    df2 = pd.DataFrame(dict(
        t=tcalc,
        h=hcalc,
    ))

    fig2 = px.line(
        df2, x="t", 
        y="h", 
        title="Hoogte",
        color_discrete_sequence=[color],
    )

    return fig, fig2