import asyncio
import datetime
import pandas as pd
import kasa
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def get_energy_cost(start: datetime, end: datetime):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager(log_level=40).install()))
    url = "https://tarifaluzhora.es/?tarifa=pcb&fecha="
    costs = {}
    dates = pd.date_range(start, end)
    for date in dates:
        modified_url = ('{}{}%2F{}%2F{}'.format(url, f"{date.day:02}", f"{date.month:02}", date.year))
        driver.get(modified_url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        costs[date.day] = soup.find_all('span', attrs={"class": "main_text"})[0].text[:6]
    driver.close()
    return costs


async def get_consumption(year: int = None, month: int = None):
    found_devices = await kasa.Discover.discover()
    devices = []
    for device in found_devices:
        temp = kasa.SmartDevice(device)
        await temp.update()
        daily = await temp.get_emeter_daily(year=year, month=month)
        devices.append(daily)
    return devices


def calc_total(kwh, eur):
    days = {}
    for day in eur:
        days[day] = kwh.get(day) * float(eur.get(day))
    return days


if __name__ == '__main__':
    print("Starting module...")
    energy_kwh = asyncio.run(get_consumption(year=2022, month=1))[0]  # we use only one KASA device
    energy_cost = get_energy_cost(datetime.date(2022, 1, 10), datetime.date(2022, 1, 11))
    money_cost = calc_total(energy_kwh, energy_cost)
    print(f'Energy consumption by day (kWh): {energy_kwh}')
    print(f'Energy cost by day (Euros/kWh): {energy_cost}')
    print(f'Cost in Euros/day: {money_cost}')
    print(f'Bitcoin produced(USD)/day: TBI')
