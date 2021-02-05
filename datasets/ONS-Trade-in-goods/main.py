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

# # ONS Trade in goods: country-by-commodity, imports and exports<br>
# <br>
# This data is split into two distributions, one for imports and the other for exports:

from gssutils import *

for script in ['exports.py', 'imports.py']:
    %run $script
    print(landingPage)
    
    cubes.add_cube(scraper, table, title)
    cubes.output_all()

# +
