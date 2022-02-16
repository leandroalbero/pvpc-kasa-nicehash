# PVPC + Kasa smart plugs + Nicehash

This script calculates the cost-effectiveness of mining. It queries historical data from a *TP-Link HS110* smart plug, queries average cost/day of the electricity (Spanish grid only for now, PVPC) and also queries Nicehash's API in order to get bitcoin produced per day on my machines.

## Getting started

You can install the most recent release using pip while in the project root:

`pip3 install .`

Then you'll need to install its dependencies using:

`pip3 install -r requirements.txt`

Finally, run it by:

```
(venv) fengdu:pvpc-kasa-nicehash leandroalbero$ python3 pvpc-knh
[L] Current power consumption (W): <EmeterStatus power=756.361601 voltage=235.435793 current=3.266415 total=526.996>
[E] Query failed due to data not available for that date: 2022-02-17 00:00:00
----------------
Total cost in Euros: 96.84 
Average cost in Euros: 4.40
________________
[('2022-01-19', 18.151, 0.3099, 5.6249949), ('2022-01-20', 17.519, 0.2843, 4.980651699999999), ('2022-01-21', 17.538, 0.27, 4.73526), ('2022-01-22', 17.602, 0.246, 4.330092), ('2022-01-23', 17.836, 0.2605, 4.646278), ('2022-01-24', 17.783, 0.3287, 5.8452721), ('2022-01-25', 17.788, 0.3238, 5.759754399999999), ('2022-01-26', 17.829, 0.3389, 6.0422481), ('2022-01-27', 16.594, 0.3346, 5.5523524), ('2022-01-28', 18.766, 0.325, 6.098949999999999), ('2022-01-29', 18.352, 0.2879, 5.2835408), ('2022-01-30', 18.39, 0.2988, 5.494932), ('2022-01-31', 18.312, 0.3247, 5.9459064)]
```

![](media/img.png)

## Requirements and supported devices

* TP-Link Kasa smart plug, this code has been tested with the HS110
* Nicehash API private token

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
* Nicehash API
* Tidy the code for the plot function.

## Resources

### Links

[Reverse engineering the TP-Link HS110](https://www.softscheck.com/en/reverse-engineering-tp-link-hs110/)

[TP-Link WiFi SmartPlug Client and Wireshark Dissector](https://github.com/softScheck/tplink-smartplug)

[Python-kasa GitHub repository](https://github.com/python-kasa/python-kasa)
