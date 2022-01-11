import setuptools
with open('requirements.txt', 'r') as f:
    install_requires = f.read().splitlines()
setuptools.setup(
    name='pvpc-knh',
    version="0.0.3",
    author="leandroalbero",
    description="Queries cost of energy from Red Electrica Española, kWh used from 'TP-Link Kasa' and data from "
                "Nicehash to calculate the efficiency of mining in a monthly basis",
    packages=setuptools.find_packages()

)