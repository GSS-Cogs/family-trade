#!/usr/bin/env python
# coding: utf-8
# %%


from gssutils import *

cubes = Cubes("info.json")
# ONS "UK trade in services by partner country experimental data" is available via https://www.ons.gov.uk/businessindustryandtrade/internationaltrade/bulletins/exportsandimportsstatisticsbycountryforuktradeinservices/apriltojune2018/relateddata.
# 
# Todo: figure out whether/how to scrape this page directly and how to model it so that the latest data is always fetched. N.B. This is an "experimental" dataset.

# %%
tables = []

get_ipython().run_line_magic('run', '"Trade in Services by Country.py"')
tables.append(new_table)

get_ipython().run_line_magic('run', '"UK trade in services by partner country.py"')
tables.append(new_table)


# We just combine these two into the same table for now.

# %%
observations = pd.concat(tables).drop_duplicates()

# %%
cubes.add_cube(scraper, observations, "UK Trade in Services by Country and Partner Country")

# %%
cubes.output_all()
