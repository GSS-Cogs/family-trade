# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py
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
import glob

py_files = [i for i in glob.glob('*.{}'.format('py'))]

for i in py_files:
    file = "'" + i + "'"
    if file.startswith("'main") == True:
        continue
    %run $file

# -


