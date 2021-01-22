# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.6.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# # UK trade in goods by industry, country and commodity
#
# This data is split into two distributions, one for imports and the other for exports:
# https://www.ons.gov.uk/economy/nationalaccounts/balanceofpayments/datasets/uktradeingoodsbyindustrycountryandcommodityimports
#
# https://www.ons.gov.uk/economy/nationalaccounts/balanceofpayments/datasets/uktradeingoodsbyindustrycountryandcommodityexports

for script in ['exports.py', 'imports.py']:
    %run $script
    print(landingPage)
    print()
    
    cubes.add_cube(scraper, table, title)
    cubes.output_all()


