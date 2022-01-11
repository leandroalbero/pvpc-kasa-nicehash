import asyncio
import datetime
import pandas as pd
import kasa
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))


def get_energy_cost(start: datetime, end: datetime):
    url = "https://tarifaluzhora.es/?tarifa=pcb&fecha="
    costs = []
    dates = pd.date_range(start, end)
    for date in dates:
        modified_url = ('{}{}%2F{}%2F{}'.format(url, f"{date.day:02}", f"{date.month:02}", date.year))
        driver.get(modified_url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        costs.append({date.day: soup.find_all('span', attrs={"class": "main_text"})[0].text[:6]})
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


def get_nicehash():
    return 0


if __name__ == '__main__':
    print("Starting module...")
    print(f'Energy consumption by day (kWh): {asyncio.run(get_consumption(year=2022, month=1))}')
    print(f'Energy cost by day (Euros/kWh): {get_energy_cost(datetime.date(2022, 1, 10), datetime.date(2022, 1, 11))}')
