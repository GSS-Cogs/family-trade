# -*- coding: utf-8 -*-
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

# ## HMRC Regional Trade Statistics
#
# Transform to Tidy Data.
#
# The source data is available from https://www.uktradeinfo.com/Statistics/RTS/Documents/Forms/AllItems.aspx in a series of zip files.
#
# Each zip file contains fixed-width formatted text files following a layout described in https://www.uktradeinfo.com/Statistics/RTS/Documents/RTS%20Detailed%20data%20information%20pack.pdf. Each row is has two measures: net mass in tonnes and statistical value in £1000's. We're assuming each observation has one measure, so split these  out into separate files.

# +
from gssutils import *
import json

scraper = Scraper(json.load(open('info.json'))['landingPage'])
display(scraper.dataset.landingPage)
scraper
# -

# zipped data files were linked from https://www.uktradeinfo.com/Statistics/RTS/Pages/RTS-Downloads.aspx, but sometimes this appears to close. If so, look for them directly from https://www.uktradeinfo.com/Statistics/RTS/Documents/Forms/AllItems.aspx

if len(scraper.distributions) == 0:
    from lxml import html
    from gssutils.metadata import Distribution
    from urllib.parse import urljoin
    from mimetypes import guess_type
    from urllib import quote

    page_uri = 'https://www.uktradeinfo.com/Statistics/RTS/Documents/Forms/AllItems.aspx'
    page = scraper.session.get(page_uri)
    tree = html.fromstring(page.text)
    for anchor in tree.xpath("//a[contains(@href, 'zip')]"):
        dist = Distribution(scraper)
        dist.title = anchor.text.strip()
        dist.downloadURL = urljoin(page_uri, quote('/%', anchor.get('href')))
        dist.mediaType, encoding = guess_type(dist.downloadURL)
        scraper.distributions.append(dist)

for dist in scraper.distributions:
    print(dist.downloadURL)

# +
from zipfile import ZipFile
from io import BytesIO, TextIOWrapper

out = Path('out')
out.mkdir(exist_ok=True, parents=True)
extracted_files = []

observations_file = out / 'observations.csv'
if observations_file.exists():
    observations_file.unlink()
header = True

# For each distribution, open the zipfile and put each source in turn into a dataframe
# for each source we're looking to create one "value" output, and one "mass" output
for distribution in scraper.distributions[-1:]:
    with ZipFile(BytesIO(scraper.session.get(distribution.downloadURL).content)) as zip:
        for name in zip.namelist():
            with zip.open(name, 'r') as quarterFile:
                quarterText = TextIOWrapper(quarterFile, encoding='utf-8')
                table = pd.read_fwf(quarterText, widths=[6, 1, 2, 1, 3, 2, 1, 2, 9, 9], names=[
                    'Period',
                    'Flow',
                    'HMRC Reporter Region',
                    'HMRC Partner Geography',
                    'Codalpha',
                    'Codseq',
                    'SITC Section',
                    'SITC 4',
                    'Value',
                    'Netmass'
                ], dtype=str)
                
                # Generic changes that apply to both "mass" and "value" outputs
                table['Period'] = table['Period'].map(lambda x: f'quarter/{x[2:]}-Q{x[0]}')
                table['Flow'] = table['Flow'].map(lambda x: 'exports' if x == 'E' else 'imports')
                table['HMRC Partner Geography'] = table.apply(
                    lambda x: x['Codseq'] if x['Codseq'][0] != '#' else x['Codalpha'],
                    axis=1)
                assert table['SITC Section'].equals(table['SITC 4'].apply(lambda x: x[0]))
                table.drop(columns=['Codalpha', 'Codseq', 'SITC Section'], inplace=True)
                
                # Output the mass observations for this input file
                mass = table.drop(columns=['Value'])
                mass['Measure Type'] = 'net-mass'
                mass['Unit'] = 'kg-thousands'
                mass.rename(columns={'Netmass': 'Value'}, inplace=True, index=str)
                mass.iloc[:1000].to_csv(observations_file, header=header, mode='a', index=False)
                # only output header row the first time
                header = False
                
                # Output the value observations for this input file
                value = table.drop(columns=['Netmass'])
                value['Measure Type'] = 'gbp-total'
                value['Unit'] = 'gbp-thousands'
                value.iloc[:1000].to_csv(observations_file, header=header, mode='a', index=False)

# +
from gssutils.metadata import THEME
scraper.dataset.family = 'Trade'
scraper.dataset.theme = THEME['business-industry-trade-energy']
import os

dataset_path = pathify(os.environ.get('JOB_NAME', 'gss_data/trade/' + Path(os.getcwd()).name))

with open(out / 'observations.csv-metadata.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())

csvw = CSVWMetadata('https://gss-cogs.github.io/family-trade/reference/')
csvw.create(
    out / 'observations.csv', out / 'observations.csv-metadata.json', with_transform=True,
    base_url='http://gss-data.org.uk/data/', base_path=dataset_path,
    dataset_metadata=scraper.dataset.as_quads(), with_external=False
)
# -


