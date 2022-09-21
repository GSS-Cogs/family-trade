#!/usr/bin/env python
# coding: utf-8
# %%

# %%


from gssutils import *
import json
import numpy as np


df = pd.DataFrame()

scraper = Scraper(seed = 'info.json')
scraper



tidied_sheets = []

distribution = scraper.distribution(latest = True)
distribution


# %%
tabs = { tab.name: tab for tab in distribution.as_databaker() }

for name, tab in tabs.items():

    period = tab.name[0:4]

    if 'Contents' in name:
        continue
    elif tab.name in ['SIC by Ownership', 'SIC by Size']:

        print(tab.name)

        pivot = tab.excel_ref('A3')

        country = 'World'

        industry = pivot.fill(DOWN).is_not_blank()

        if 'ownership' in tab.name.lower():
            ownership = pivot.shift(2, 0).fill(DOWN).is_not_blank()
        else:
            ownership = 'unknown'

        flow = pivot.shift(3, 0).fill(DOWN).is_not_blank()

        period = pivot.shift(4, 0).expand(RIGHT).is_not_blank()

        if 'ownership' in tab.name.lower():
            business_size = 'all'
        else:
            business_size = pivot.shift(2, 0).fill(DOWN).is_not_blank()

        measure_type = 'value-of-trade'

        unit = 'gbp-million'

        observations = period.fill(DOWN).is_not_blank()

        if 'ownership' in tab.name.lower():
            dimensions = [
                HDim(period, "Period", DIRECTLY, ABOVE),
                HDimConst("Business Size", business_size),
                HDimConst("Country", country),
                HDim(industry, 'Industry', DIRECTLY, LEFT),
                HDim(flow, 'Flow', DIRECTLY, LEFT),
                HDim(ownership, 'Ownership', DIRECTLY, LEFT),
                HDimConst('Measure Type', measure_type),
                HDimConst('Unit', unit)
            ]
        else:
            dimensions = [
                HDim(period, "Period", DIRECTLY, ABOVE),
                HDim(business_size, 'Business Size', DIRECTLY, LEFT),
                HDimConst("Country", country),
                HDim(industry, 'Industry', DIRECTLY, LEFT),
                HDim(flow, 'Flow', DIRECTLY, LEFT),
                HDimConst("Ownership", ownership),
                HDimConst('Measure Type', measure_type),
                HDimConst('Unit', unit)
            ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        df = tidy_sheet.topandas()
        tidied_sheets.append(df)
        savepreviewhtml(tidy_sheet,fname=tab.name + " Preview.html")

    elif tab.name in ['SIC Count']:

        print(tab.name)

        pivot = tab.excel_ref('A3')

        country = 'World'

        industry = pivot.fill(DOWN).is_not_blank()

        ownership = 'unknown'

        flow = pivot.shift(2, 0).fill(DOWN).is_not_blank()

        period = pivot.shift(3, 0).expand(RIGHT).is_not_blank()

        business_size = 'all'

        measure_type = 'count'

        unit = 'firms-trading'

        observations = period.fill(DOWN).is_not_blank()

        dimensions = [
            HDim(period, "Period", DIRECTLY, ABOVE),
            HDimConst("Business Size", business_size),
            HDimConst("Country", country),
            HDim(industry, 'Industry', DIRECTLY, LEFT),
            HDim(flow, 'Flow', DIRECTLY, LEFT),
            HDimConst("Ownership", ownership),
            HDimConst('Measure Type', measure_type),
            HDimConst('Unit', unit)
        ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        df = tidy_sheet.topandas()
        tidied_sheets.append(df)
        savepreviewhtml(tidy_sheet,fname=tab.name + " Preview.html")

    elif tab.name in ['Size by Ownership', 'Size Ownership Count']:

        print(tab.name)

        pivot = tab.excel_ref('A3')

        country = 'World'

        industry = 'all'

        ownership = pivot.shift(RIGHT).fill(DOWN).is_not_blank()

        flow = pivot.shift(2, 0).fill(DOWN).is_not_blank()

        period = pivot.shift(3, 0).expand(RIGHT).is_not_blank()

        business_size = pivot.fill(DOWN).is_not_blank()

        if 'count' in tab.name.lower():
            measure_type = 'count'

            unit = 'firms-trading'

        else:
            measure_type = 'value-of-trade'

            unit = 'gbp-million'

        observations = period.fill(DOWN).is_not_blank()

        dimensions = [
            HDim(period, "Period", DIRECTLY, ABOVE),
            HDim(business_size, "Business Size", DIRECTLY, LEFT),
            HDimConst("Country", country),
            HDimConst( 'Industry', industry),
            HDim(flow, 'Flow', DIRECTLY, LEFT),
            HDim(ownership, "Ownership", DIRECTLY, LEFT),
            HDimConst('Measure Type', measure_type),
            HDimConst('Unit', unit)
        ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        df = tidy_sheet.topandas()
        tidied_sheets.append(df)
        savepreviewhtml(tidy_sheet,fname=tab.name + " Preview.html")

    elif tab.name in ['Region by Ownership', 'Region Ownership Count', 'Region by Size', 'Region Size Count']:

        print(tab.name)

        pivot = tab.excel_ref('A3')

        country = pivot.fill(DOWN).is_not_blank()

        industry = 'all'

        if 'size' in tab.name.lower():
            ownership = 'all'
        else:
            ownership = pivot.shift(RIGHT).fill(DOWN).is_not_blank()

        flow = pivot.shift(2, 0).fill(DOWN).is_not_blank()

        period = pivot.shift(3, 0).expand(RIGHT).is_not_blank()

        if 'size' in tab.name.lower():
            business_size = pivot.shift(RIGHT).fill(DOWN).is_not_blank()
        else:
            business_size = 'all'

        if 'count' in tab.name.lower():
            measure_type = 'count'

            unit = 'firms-trading'

        else:
            measure_type = 'value-of-trade'

            unit = 'gbp-million'

        observations = period.fill(DOWN).is_not_blank()

        if 'size' in tab.name.lower():
            dimensions = [
                HDim(period, "Period", DIRECTLY, ABOVE),
                HDim(business_size, "Business Size", DIRECTLY, LEFT),
                HDim(country, "Country", DIRECTLY, LEFT),
                HDimConst('Industry', industry),
                HDim(flow, 'Flow', DIRECTLY, LEFT),
                HDimConst("Ownership", ownership),
                HDimConst('Measure Type', measure_type),
                HDimConst('Unit', unit)
            ]

        else:

            dimensions = [
                HDim(period, "Period", DIRECTLY, ABOVE),
                HDimConst("Business Size", business_size),
                HDim(country, "Country", DIRECTLY, LEFT),
                HDimConst('Industry', industry),
                HDim(flow, 'Flow', DIRECTLY, LEFT),
                HDim(ownership, "Ownership", DIRECTLY, LEFT),
                HDimConst('Measure Type', measure_type),
                HDimConst('Unit', unit)
            ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        df = tidy_sheet.topandas()
        tidied_sheets.append(df)
        savepreviewhtml(tidy_sheet,fname=tab.name + " Preview.html")

    else:
        continue


# %%


#Post Processing
df = pd.concat(tidied_sheets)
df.rename(columns={'OBS' : 'Value','DATAMARKER' : 'Marker'}, inplace=True)
df['Period'] =  'year/' + df['Period']
df['Value'] = df.apply(lambda x: '0.0' if 'Suppressed' in str(x['Marker']) else x['Value'], axis = 1)

df['Marker'] = df['Marker'].str.replace('Suppressed', 'suppressed')

df["Business Size"] = df["Business Size"].map(lambda x: "0-to-49" if x == "Small (0-49)"
                                             else ("50-to-249" if x == "Medium (50-249)"
                                             else ("250" if x == "Large (250+)"
                                             else ("unknown-employees" if x == "Unknown" else "any"))))

df['Country'] = df['Country'].apply(lambda x: 'WW' if 'World' in x
                                    else ('RW' if 'Non-EU' in x
                                    else ('EU' if 'Total EU' in x else x)))

df["Ownership"] = df["Ownership"].map(lambda x: "uk" if x == "Domestic"
                                    else ("foreign" if x == "Foreign"
                                    else ("unknown" if x == "Unknown" else "any")))

df["Flow"] = df["Flow"].map(lambda x : "exports" if x == 'Export'
                            else ("imports" if x == "Import"
                            else x))

df['Value'] = pd.to_numeric(df['Value'], errors='coerce').astype('Int64')


df['Flow'] = df['Flow'].apply(pathify)

df = df[['Period', 'Business Size', 'Country', 'Ownership', 'Industry', 'Flow', 'Value', 'Marker', 'Measure Type', 'Unit']]

df


# %%


#additional scraper info needed
comment = "Trade in goods data, including breakdown of imports and exports by Standard Industrial Classification, region (EU and non-EU), business size and by domestic and foreign ownership."
des = """
Trade in goods data, including breakdown of imports and exports by Standard Industrial Classification, region (EU and non-EU), business size and by domestic and foreign ownership.

Users should note the following:
Industry data has been produced using Standard Industrial Classification 2007 (SIC07).

Business size is defined using the following employment size bands:
   Small - 0-49 employees
   Medium - 50-249 employees
   Large - 250+ employees
   Unknown - number of employees cannot be determined via IDBR

Ownership status is defined as:
   Domestic - ultimate controlling parent company located in the UK
   Foreign - ultimate controlling parent company located outside the UK
   Unknown - location of ultimate controlling parent company cannot be determined via IDBR

Some data cells have been suppressed to protect confidentiality so that individual traders cannot be identified.

Data
All data is in £ million, current prices

Rounding
Some of the totals within this release (e.g. EU, Non EU and world total) may not exactly match data published via other trade releases due to small rounding differences.

Trade Asymmetries
These data are our best estimate of these bilateral UK trade flows. Users should note that alternative estimates are available, in some cases, via the statistical agencies for bilateral countries or through central databases such as UN Comtrade

"""
scraper.dataset.description = des
scraper.dataset.comment = comment
scraper.dataset.title = distribution.title

df.head(10)
for c in df.columns:
    if c != "Value":
        print(c)
        print(df[c].unique())
        print("########################################################")

df.to_csv('observations.csv', index=False)

catalog_metadata = scraper.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')


# %%




