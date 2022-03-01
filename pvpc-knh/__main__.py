import asyncio
import datetime
import os.path
import sqlite3
import sqlite3 as sql
import matplotlib.pyplot
import pandas as pd
import kasa
import requests
import nicehash
import selenium.common.exceptions
from bs4 import BeautifulSoup
from numpy import datetime64
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import argparse


def __initialize_database():
    db = sql.connect('test.db')
    db.execute('CREATE TABLE precios_energia(fecha DATETIME PRIMARY KEY, eur_kwh FLOAT)')
    db.execute('CREATE TABLE consumos(plug_id TEXT, fecha DATETIME PRIMARY KEY, kwh FLOAT)')
    db.execute('CREATE TABLE nicehash(id TEXT PRIMARY KEY, date DATETIME, amount FLOAT, fee_amount FLOAT)')
    db.close()


def update_energy_cost(start: datetime, end: datetime):
    if not os.path.exists('test.db'):
        __initialize_database()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager(log_level=40).install()))
    url = "https://tarifaluzhora.es/?tarifa=pcb&fecha="
    db = sql.connect('test.db')
    cursor = db.cursor()
    dates = pd.date_range(start, end)

    for date in dates:
        texto = f"SELECT * FROM precios_energia WHERE fecha IS \'{date.year}-{date.month:02}-{date.day:02}\'"
        query_results = cursor.execute(texto).fetchall()
        if len(query_results) == 0:
            modified_url = ('{}{}%2F{}%2F{}'.format(url, f"{date.day:02}", f"{date.month:02}", date.year))
            try:
                driver.get(modified_url)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                cost_eur = float(soup.find_all('span', attrs={"class": "main_text"})[0].text[:6])
                try:
                    cursor.execute('INSERT INTO precios_energia (fecha, eur_kwh) VALUES '
                                   '(\'{}-{}-{}\',{})'.format(date.year, str(date.month).zfill(2),
                                                              str(date.day).zfill(2), cost_eur))
                except sqlite3.IntegrityError:
                    pass
            except selenium.common.exceptions.UnexpectedAlertPresentException:
                print(f'[E] Query failed due to data not available for that date: {date}\n----------------')
                break
            else:
                pass
    db.commit()
    db.close()
    driver.close()


async def update_power(year: int = None, month: int = None):
    if not os.path.exists('test.db'):
        __initialize_database()
    found_devices = await kasa.Discover.discover()
    db = sql.connect('test.db')
    cursor = db.cursor()
    days_kwh = []
    if len(found_devices) == 0:
        print("[E] No Kasa devices found...")
    for device in found_devices:
        if found_devices.get(device).device_type.name == 'Plug':
            temp = kasa.SmartDevice(device)
            await temp.update()
            daily = await temp.get_emeter_daily(year=year, month=month)
            print(f'[L] Current power consumption (W): {await temp.get_emeter_realtime()}')
            for day in daily.items():
                if day[0] == datetime.date.today().day:
                    break
                query = f"INSERT INTO consumos (plug_id, fecha, kwh) VALUES ('{found_devices.get(device).device_id}'" \
                        f", '{year}-{str(month).zfill(2)}-{str(day[0]).zfill(2)}',{day[1]}) "
                try:
                    cursor.execute(query)
                except sqlite3.IntegrityError:
                    pass
            days_kwh.append(daily)
    db.commit()
    db.close()


def update_nicehash():
    endpoint = 'https://api2.nicehash.com'
    if not os.path.exists('test.db'):
        __initialize_database()
    try:
        secrets_file = open('secrets', 'r')
        secrets = secrets_file.readlines()
        organisation_id = secrets[0].rstrip('\n')
        key = secrets[1].rstrip('\n')
        secret = secrets[2].rstrip('\n')
    except FileNotFoundError:
        print("[E] Secrets file not found, please create one with org_id, api_key and api_secret on each line.")
        return
    private_api = nicehash.private_api(endpoint, organisation_id, key, secret)
    payouts = private_api.get_payouts(size=10000, page=0)['list']
    db = sql.connect('test.db')
    cursor = db.cursor()
    for transaction in payouts:
        formatted_date = datetime.datetime.fromtimestamp(transaction['created']/1000).strftime('%Y-%m-%d %H:%M:%S')
        query = f"INSERT INTO nicehash (id, date, amount, fee_amount) " \
                f"VALUES ('{transaction['id']}','{formatted_date}',{transaction['amount']},{transaction['feeAmount']})"
        try:
            cursor.execute(query)
        except sqlite3.IntegrityError:
            pass
    db.commit()
    db.close()


def calc_metrics(start: datetime, end: datetime):
    db = sql.connect('test.db')
    _metrics = {}
    cursor = db.cursor()
    sum_query = f"SELECT sum(kwh * eur_kwh) FROM  consumos, precios_energia " \
                f"WHERE consumos.fecha = precios_energia.fecha " \
                f"AND consumos.fecha BETWEEN \'{start}\' AND \'{end}\'"
    _metrics['total_cost'] = cursor.execute(sum_query).fetchone()[0]
    avg_query = f"SELECT avg(kwh * eur_kwh) FROM  consumos, precios_energia " \
                f"WHERE consumos.fecha = precios_energia.fecha " \
                f"AND consumos.fecha BETWEEN \'{start}\' AND \'{end}\'"
    _metrics['avg_cost'] = cursor.execute(avg_query).fetchone()[0]
    btc_sum_query = f"SELECT sum(amount) FROM nicehash WHERE date BETWEEN '{start}' AND '{end}'"
    _metrics['btc_produced'] = cursor.execute(btc_sum_query).fetchone()[0]
    btc_price = requests.get("https://api.coingecko.com/api/v3/exchange_rates")
    _metrics['btc_eur'] = btc_price.json()['rates']['eur']['value']
    btc_avg_day_query = f"SELECT avg(av) from (" \
                        f"SELECT sum(amount) as av, STRFTIME('%Y-%m-%d', date) AS date FROM nicehash " \
                        f"WHERE date BETWEEN '{start}' AND '{end}' GROUP BY strftime('%Y-%m-%d', date))"
    _metrics['btc_avg_day'] = cursor.execute(btc_avg_day_query).fetchone()[0]
    db.close()
    return _metrics


def plot_data(start: datetime, end: datetime, save_file=True, plot_3=True, profitability=True):
    db = sql.connect('test.db')
    cursor = db.cursor()
    query = f"SELECT consumos.fecha, consumos.kwh, precios_energia.eur_kwh, kwh * eur_kwh AS eur_cost " \
            f"FROM consumos, precios_energia " \
            f"WHERE consumos.fecha = precios_energia.fecha " \
            f"AND consumos.fecha BETWEEN \'{start}\' AND \'{end}\'"
    table = cursor.execute(query).fetchall()
    dataframe = pd.DataFrame(table, columns=["Date", "kWh", "EUR/kWh", "EUR/day"]).astype({"Date": datetime64})
    if plot_3:
        dataframe.plot(x="Date", y=["EUR/day", "kWh", "EUR/kWh"], kind='line', subplots=True)
    else:
        dataframe.plot(x="Date", y=["EUR/day"], kind='line')

    if save_file:
        matplotlib.pyplot.savefig('plot.png')
    if profitability:
        btc_production = cursor.execute(f"SELECT sum(amount), STRFTIME('%Y-%m-%d', date) AS date FROM nicehash "
                                        f"WHERE DATE(date) BETWEEN '{start}' AND '{end}' "
                                        f"GROUP BY strftime('%Y-%m-%d', date) ORDER BY DATE(date)").fetchall()
        btc_dataframe = pd.DataFrame(btc_production, columns=["amount", "date"]).astype({"date": datetime64})
        btc_dataframe.plot(x="date", y=["amount"], kind='scatter')
        matplotlib.pyplot.savefig('nicehash.png')
    matplotlib.pyplot.show()


if __name__ == '__main__':
    all_args = argparse.ArgumentParser()
    all_args.add_argument('-s', '--startdate', required=False, help='starting date in Y-M-D')
    all_args.add_argument('-e', '--enddate', required=False, help='ending date in Y-M-D')
    args = vars(all_args.parse_args())
    energy_kwh = asyncio.run(update_power(year=2022, month=2))
    update_energy_cost(datetime.date(2022, 1, 1), datetime.date.today())
    metrics = calc_metrics(datetime.date(2022, 1, 1), datetime.date.today())
    print(f"________________\nTotal energy cost: {metrics.get('total_cost'):.2f} EUR")
    print(f"Total produced BTC: {metrics.get('btc_produced'):.8f} EUR: "
          f"{metrics.get('btc_produced') * metrics.get('btc_eur'):.2f}")
    print(f"Average produced per day BTC: {metrics.get('btc_avg_day'):.8f} EUR: {metrics.get('btc_avg_day') * metrics.get('btc_eur'):.2f}")
    print(f"Average energy cost per day: {metrics.get('avg_cost'):.2f} EUR\n________________")
    plot_data(datetime.date(2022, 1, 1), datetime.date.today(), plot_3=True)
    update_nicehash()
