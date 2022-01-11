import asyncio
import datetime
import pandas as pd
import kasa
import selenium.common.exceptions
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import argparse
import matplotlib.pyplot as plt


def get_energy_cost(start: datetime, end: datetime):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager(log_level=40).install()))
    url = "https://tarifaluzhora.es/?tarifa=pcb&fecha="
    costs = {}
    dates = pd.date_range(start, end)
    for date in dates:
        modified_url = ('{}{}%2F{}%2F{}'.format(url, f"{date.day:02}", f"{date.month:02}", date.year))
        try:
            driver.get(modified_url)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            costs[date.day] = float(soup.find_all('span', attrs={"class": "main_text"})[0].text[:6])
        except selenium.common.exceptions.UnexpectedAlertPresentException:
            print(f'Query failed due to data not available for that date: {date}\n----------------')
            break
    driver.close()
    return costs


async def get_consumption(year: int = None, month: int = None):
    found_devices = await kasa.Discover.discover()
    devices = []
    for device in found_devices:
        temp = kasa.SmartDevice(device)
        await temp.update()
        daily = await temp.get_emeter_daily(year=year, month=month)
        print(f'Current power consumption (W): {await temp.get_emeter_realtime()}')
        devices.append(daily)
    return devices


def calc_total(kwh, eur):
    days = {}
    sum_eur = 0
    for day in eur:
        try:
            days[day] = kwh.get(day) * float(eur.get(day))
            sum_eur += days[day]
        except TypeError:
            pass
    days["sum"] = sum_eur
    return days


if __name__ == '__main__':
    all_args = argparse.ArgumentParser()
    all_args.add_argument('-s', '--startdate', required=False, help='starting date in Y-M-D')
    all_args.add_argument('-e', '--enddate', required=False, help='ending date in Y-M-D')
    args = vars(all_args.parse_args())
    energy_kwh = asyncio.run(get_consumption(year=2022, month=1))[0]  # we use only one KASA device
    energy_cost = get_energy_cost(datetime.date(2022, 1, 1), datetime.date(2022, 1, 31))
    money_cost = calc_total(energy_kwh, energy_cost)
    print(f'Energy consumption by day (kWh): {energy_kwh}')
    print(f'Energy cost by day (Euros/kWh): {energy_cost}')
    print(f'Cost in Euros/day: {money_cost}\n________________')
    print(f'Total cost in Euros: {money_cost["sum"]}')

    x, y = zip(*energy_cost.items())
    z, t = zip(*energy_kwh.items())
    # Create Plot

    fig, ax1 = plt.subplots()

    ax1.set_xlabel(f'Day of the month. Total Cost (EUR): {money_cost["sum"]}')
    ax1.set_ylabel('Energy cost €/kWh)', color='black')
    plot_1 = ax1.plot(x, y, color='black')
    ax1.tick_params(axis='y', labelcolor='black')

    # Adding Twin Axes

    ax2 = ax1.twinx()

    ax2.set_ylabel('Energy consumption (kWh)', color='green')
    plot_2 = ax2.plot(z, t, color='green')
    ax2.tick_params(axis='y', labelcolor='green')

    # Show plot

    plt.show()
