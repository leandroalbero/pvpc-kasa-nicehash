# PVPC + Kasa smart plugs + Nicehash

This script calculates the cost-effectiveness of mining. It queries historical data from a *TP-Link HS110* smart plug, queries average cost/day of the electricity (Spanish grid only for now, PVPC) and also queries Nicehash's API in order to get bitcoin and EUR produced per day by the miners.

## Getting started

You can install the most recent release using pip while in the project root:

`pip3 install .`

Then you'll need to install its dependencies using:

`pip3 install -r requirements.txt`

Finally, run it by:

```
(venv) fengdu:pvpc-kasa-nicehash leandroalbero$ python3 pvpc-knh
[L] Current power consumption (W): <EmeterStatus power=768.234271 voltage=226.976638 current=3.434955 total=642.583>
________________
Total energy cost in Euros: 203.18 
Total BTC produced: 0.00882312 EUR: 295.77
Average cost per day in Euros: 4.73
________________

```
Note: If using Nicehash API v2 you need to create a file named 'secrets' with org_id, api_key and api_secret on each line.
![](media/img.png)

## Requirements and supported devices

* TP-Link Kasa smart plug, this code has been tested with the HS110
* Nicehash API v2 org_id, api_key and api_secret

### Plugs

* HS100
* HS103
* HS105
* HS107
* HS110
* KP105
* KP115
* KP401

## TODO:

* We don't use 'ESIOS API' because it requires an API token, we use a web scraper on
  [https://tarifaluzhora.es/](https://tarifaluzhora.es/?tarifa=pcb&fecha=10%2F01%2F2022) instead. This is slower,
  but it is easier to set up. Will try to use ESIOS API by requesting a token on the CLI
* CLI doesn't have any parameters yet. Should have at least start_date and end_date or a default value for current month
* ~~Nicehash API~~
* Tidy the code for the plot function.
* Change start and end date to query data for the current month by default

## Resources

### Links

[Reverse engineering the TP-Link HS110](https://www.softscheck.com/en/reverse-engineering-tp-link-hs110/)

[TP-Link WiFi SmartPlug Client and Wireshark Dissector](https://github.com/softScheck/tplink-smartplug)

[Python-kasa GitHub repository](https://github.com/python-kasa/python-kasa)
