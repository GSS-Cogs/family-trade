# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.4.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# # ONS Trade in goods: country-by-commodity, imports and exports
#
#  This data is split into two distributions, one for imports and the other for exports:

# In[1]:


from gssutils import *


for script in ['exports.py', 'imports.py']:
    get_ipython().run_line_magic('run', script)
    print(landingPage)
    
    cubes.add_cube(scraper, table, title)
    cubes.output_all()


# +
