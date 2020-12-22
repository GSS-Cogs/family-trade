# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
from gssutils import *

scraper = Scraper(seed="info.json")
scraper.distributions[0].title = "UK tariffs"
scraper
# -

distribution = scraper.distributions[0]
display(distribution)

link = distribution.downloadURL
tariffs_data = pd.read_csv(link)

from IPython.core.display import HTML
for col in tariffs_data:
    if col not in ['Value']:
        tariffs_data[col] = tariffs_data[col].astype('category')
        display(HTML(f"<h2>{col}</h2>"))
        display(tariffs_data[col].cat.categories) 

tariffs_data.dtypes

# +
#outputting for DM
out = Path('out')
out.mkdir(exist_ok=True)

tariffs_data.drop_duplicates().to_csv(out / 'observations.csv', index = False)
# -




