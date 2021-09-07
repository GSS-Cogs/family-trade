# -*- coding: utf-8 -*-
# +
from gssutils import * 
import json 
from urllib.parse import urljoin

trace = TransformTrace()
df = pd.DataFrame()
cubes = Cubes("info.json")
# -

info = json.load(open('info.json'))
scraper = Scraper(info['landingPage'][0])
scraper 

#Distribution 
tabs = { tab.name: tab for tab in scraper.distributions[0].as_databaker() }
list(tabs)

# +
tab = tabs["tis_ind_ex"]
datasetTitle = 'uktradeinservicesbyindustrycountryandservicetypeexport'
columns=["Period", "Country", "Industry", "Direction", "Service Account", "Marker", "Measure Type", "Unit"]
trace.start(datasetTitle, tab, columns, scraper.distributions[0].downloadURL)

period =  tab.excel_ref("E1").expand(RIGHT).is_not_blank()
trace.Period("Values taken from cell E1 across")

country = tab.excel_ref("A2").expand(DOWN).is_not_blank()
trace.Country("Values taken from cell A2 across")

industry = tab.excel_ref("B2").expand(DOWN).is_not_blank()
trace.Industry("Values taken from cell B2 across")

direction = tab.excel_ref("C2").expand(DOWN).is_not_blank()
trace.Direction("Values taken from cell B2 across")

service_account = tab.excel_ref("D2").expand(DOWN).is_not_blank()
trace.Service_Account("Values taken from cell B2 across")

observations = period.fill(DOWN).is_not_blank()
dimensions = [
    HDim(period, 'Period', DIRECTLY, ABOVE),
    HDim(country, 'Country', DIRECTLY, LEFT),
    HDim(industry, 'Industry', DIRECTLY, LEFT),
    HDim(direction, 'Direction', DIRECTLY, LEFT),
    HDim(service_account, 'Service Account', DIRECTLY, LEFT),
    ]
tidy_sheet = ConversionSegment(tab, dimensions, observations)
trace.with_preview(tidy_sheet)
savepreviewhtml(tidy_sheet, fname= "tidy_sheet.html") 
trace.store("combined_dataframe", tidy_sheet.topandas())

# -

df = trace.combine_and_trace(datasetTitle, "combined_dataframe")
df.rename(columns={'OBS' : 'Value', 'DATAMARKER' : 'Marker', 'Direction' : 'Flow'}, inplace=True)
df = df.replace({'Flow' : {'EX' : 'exports'}})
df = df.replace({'Marker' : {'..' : 'suppressed-data',}})
df['Period'] = df['Period'].astype(str).replace('\.0', '', regex=True)
df["Country"] = df["Country"].str.split(' ').str[0]
df['Period'] = "year/" + df['Period']
df["Service Account"] = df["Service Account"].str.split(' ').str[0]
df["Industry"] = df["Industry"].str.split(' ').str[0]
tidy_exports = df[["Period", "Country", "Industry", "Flow", "Service Account", "Value", "Marker"]]
tidy_exports

# Transformation of Imports file to be joined to exports transformation done above 

scraper = Scraper(info['landingPage'][1])
scraper 

#Distribution 
tabs = { tab.name: tab for tab in scraper.distributions[0].as_databaker() }
list(tabs)

# +
tab = tabs["tis_ind_im"]
datasetTitle = 'uktradeinservicesbyindustrycountryandservicetypeimport'
columns=["Period", "Country", "Industry", "Direction", "Service Account", "Marker", "Measure Type", "Unit"]
trace.start(datasetTitle, tab, columns, scraper.distributions[0].downloadURL)

period =  tab.excel_ref("E1").expand(RIGHT).is_not_blank()
trace.Period("Values taken from cell E1 across")

country = tab.excel_ref("A2").expand(DOWN).is_not_blank()
trace.Country("Values taken from cell A2 across")

industry = tab.excel_ref("B2").expand(DOWN).is_not_blank()
trace.Industry("Values taken from cell B2 across")

direction = tab.excel_ref("C2").expand(DOWN).is_not_blank()
trace.Direction("Values taken from cell B2 across")

service_account = tab.excel_ref("D2").expand(DOWN).is_not_blank()
trace.Service_Account("Values taken from cell B2 across")

observations = period.fill(DOWN).is_not_blank()
dimensions = [
    HDim(period, 'Period', DIRECTLY, ABOVE),
    HDim(country, 'Country', DIRECTLY, LEFT),
    HDim(industry, 'Industry', DIRECTLY, LEFT),
    HDim(direction, 'Direction', DIRECTLY, LEFT),
    HDim(service_account, 'Service Account', DIRECTLY, LEFT),
    ]
tidy_sheet = ConversionSegment(tab, dimensions, observations)
trace.with_preview(tidy_sheet)
savepreviewhtml(tidy_sheet, fname= "tidy_sheet.html") 
trace.store("combined_dataframe_imports", tidy_sheet.topandas())

# -

df = trace.combine_and_trace(datasetTitle, "combined_dataframe_imports")
df.rename(columns={'OBS' : 'Value', 'DATAMARKER' : 'Marker', 'Direction' : 'Flow'}, inplace=True)
df = df.replace({'Flow' : {'IM' : 'imports'}})
df = df.replace({'Marker' : {'..' : 'suppressed-data',}})
df["Country"] = df["Country"].str.split(' ').str[0]
df['Period'] = df['Period'].astype(str).replace('\.0', '', regex=True)
df["Service Account"] = df["Service Account"].str.split(' ').str[0]
df["Industry"] = df["Industry"].str.split(' ').str[0]
df['Period'] = "year/" + df['Period']
tidy_imports = df[["Period", "Country", "Industry", "Flow", "Service Account", "Value", "Marker"]]
tidy_imports

tidy = pd.concat([tidy_exports, tidy_imports])
tidy.rename(columns={'Industry' : 'Trade Industry'}, inplace=True)


# +
description = f"""
Experimental dataset providing a breakdown of UK trade in services by industry, country and service type on a balance of payments basis. Data are subject to disclosure control, which means some data have been suppressed to protect confidentiality of individual traders.

Users should note the following:    
Industry data has been produced using Standard Industrial Classification 2007 (SIC07).

Service type data has been produced using Extended Balance of Payments (EBOPs).    
Due to risks around disclosing data releated to individual firms we are only able to provide data for certain combinations of the dimensions included, i.e. country, service type and industry. This dataset therefore provides the following two combinations:    
Industry (SIC07 2 digit), by service type (EBOPs 1 digit), by geographic region (world total, EU and non-EU)
Industry (SIC07 2 digit), by total service type, by individual country
Some data cells have been suppressed to protect confidentiality so that individual traders cannot be identified.

Data
All data is in £ million, current prices    

Rounding
Some of the totals within this release (e.g. EU, Non EU and world total) may not exactly match data published via other trade releases due to small rounding differences.

Trade Asymmetries 
These data are our best estimate of these bilateral UK trade flows. Users should note that alternative estimates are available, in some cases, via the statistical agencies for bilateral countries or through central databases such as UN Comtrade (https://comtrade.un.org/)

"""

comment = "Experimental dataset providing a breakdown of UK trade in services by industry, country and service type on a balance of payments basis. Data are subject to disclosure control, which means some data have been suppressed to protect confidentiality of individual traders."
scraper.dataset.title = 'UK trade in services by industry, country and service type, Imports & Exports'
scraper.dataset.description = description
scraper.dataset.family = 'trade'
# -

tidy['Marker'][tidy['Marker'] == 'suppressed-data'] = 'suppressed'
tidy.head(20)

# As trade industry is mostly SIC but with some additional codes, we'll need to turn the codes into URIs for the time being.

trade_industry_codelist = Path('codelists') / 'trade-industry.csv'
trade_industry = pd.read_csv(trade_industry_codelist)
notation_uri = dict(zip(trade_industry['Local Notation'], trade_industry['URI']))
tidy['Trade Industry'] = tidy['Trade Industry'].apply(lambda x: notation_uri[x])
tidy

# The `codelists/trade-industry.csv` file is a mixed codelist and should only contain the codes/concepts used by this dataset, along with any parent concepts.

# +
from rdflib import Graph, URIRef
from rdflib.namespace import SKOS, RDFS
g = Graph()
g.load('http://business.data.gov.uk/companies/sources/vocab/sic-2007.ttl', format="turtle")

trade_industry.drop_duplicates(inplace=True, subset=["URI"])
all_uris = set(trade_industry['URI'].values)
visited = set()
to_visit = set()
to_visit.update(tidy['Trade Industry'].unique())

while len(to_visit) > 0:
    uri = to_visit.pop()
    if uri is not None and uri not in set(trade_industry['URI'].values):
        print(f"Adding {uri}")
        subj = URIRef(uri)
        trade_industry = trade_industry.append({
            'Label': g.value(subj, SKOS.prefLabel),
            'URI': uri,
            'Parent URI': g.value(subj, SKOS.broader),
            'Sort Priority': None,
            'Description': None,
            'Local Notation': g.value(subj, SKOS.notation)
        }, ignore_index=True)
    parent_uris = set(uri for uri in trade_industry['Parent URI'][trade_industry['URI'] == uri].values if isinstance(uri, str))
    visited.add(uri)
    to_visit.update(parent_uris - visited)
codes_used = trade_industry[trade_industry['URI'].isin(visited)]
codes_used.to_csv(trade_industry_codelist, index=False)
# -

cubes.add_cube(scraper, tidy.drop_duplicates(), scraper.dataset.title)
cubes.output_all()

trace.render()
