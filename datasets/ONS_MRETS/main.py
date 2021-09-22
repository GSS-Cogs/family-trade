# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.5
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# +
import json
from os import environ
import copy 
import pandas as pandas
from gssutils import *
from gssutils.metadata import THEME
from dateutil import parser

infoFileName = 'info.json'
cubes = Cubes('info.json')
info = json.load(open('info.json'))
landingPage = info['landingPage']
metadata = Scraper(seed="info.json")

# Convert all issued time to datetime format
metadata.dataset.issued = parser.parse(str(metadata.dataset.issued))
for dist in metadata.distributions:
    dist.issued = parser.parse(str(dist.issued))

dist = metadata.distribution(mediaType='text/prs.ons+csdb', latest=True)
dist

# +
# # + tags=["outputPrepend"]
from io import TextIOWrapper
from itertools import accumulate, zip_longest
from collections import namedtuple, defaultdict
from decimal import *

def make_parser(fieldwidths):
    cuts = tuple(cut for cut in accumulate(abs(fw) for fw in fieldwidths))
    pads = tuple(fw < 0 for fw in fieldwidths) # bool values for padding fields
    flds = tuple(zip_longest(pads, (0,)+cuts, cuts))[:-1]  # ignore final one
    parse = lambda line: tuple(line[i:j] for pad, i, j in flds if not pad)
    # optional informational function attributes
    parse.size = sum(abs(fw) for fw in fieldwidths)
    parse.fmtstring = ' '.join('{}{}'.format(abs(fw), 'x' if fw < 0 else 's')
                                                for fw in fieldwidths)
    return parse

first_line_parser = make_parser((2, 4, 2, 2, 12, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2))

data = TextIOWrapper(dist.open())

(line_type, year, month, day, title, nine,
 identifier_len, periodicity_len, seasonal_len, prices_base_year_len,
 index_base_year_len, index_base_month_len, sic_len, pub_len, table_len) = first_line_parser(data.readline())
assert(line_type == ' 0')

parse_1 = lambda line: (line[0:2], line[2:4], line[4:])
parse_92 = make_parser((-2, int(identifier_len), int(periodicity_len), int(seasonal_len),
                        int(prices_base_year_len), int(index_base_year_len),
                        int(index_base_month_len), int(sic_len), int(pub_len), int(table_len)))
parse_93 = lambda line: line[2:]
parse_96 = make_parser((-2, 1, 1, 4, 3, 4, 2, 2, 5, 14, 2, 2))


table_index = []
line = data.readline()[:-1]
while line[0:2] == ' 1':
    (lt, index, title) = parse_1(line)
    assert(lt == ' 1')
    table_index.append((index, title))
    line = data.readline()

TableHeader = namedtuple('TableHeader', [pathify(ti[1]).replace('-', '_') for ti in table_index])
TableStruct = namedtuple('TableStruct', 'period, ims, year_start, start_period, year_end, month, day, count, cols, width, decimals')
TableStruct_types = (str, str, int, int, int, int, int, int, int, int, int)

header = None
struct = None
label = None
all_labels = set()
observations = []

slices = defaultdict(list)

while line:
    line_type = line[0:2]
    if line_type == '92':
        if len(observations) > 0:
            slice = {
                'label': label,
                'header': header,
                'struct': struct,
                'observations': observations
            }
            slices[header.identifier].append(slice)
        observations = []
        header = TableHeader._make(parse_92(line))
    elif line_type == '93':
        label = parse_93(line)
        all_labels.add(label)
    elif line_type == '96':
        struct = TableStruct._make(t(v) for (v, t) in zip(parse_96(line), TableStruct_types))
    elif line_type == '97':
        w = int(struct.width)
        observations.extend([
            Decimal(line[s:(s+w)]) for s in range(2, len(line), int(struct.width))
        ])                                                
    else:
        break
    
    line = data.readline()[:-1]

slices[header.identifier].append({
    'label': label,
    'header': header,
    'struct': struct,
    'observations': observations
})
#with open("./wtf.json", "w") as f:
#    json.dump(slices, f, default=lambda x: str(x))



# +
AV_STERLING_EXCHANGE = 'Average Sterling exchange rate: '
COUNTRIES = set(['estonia', 'ww', 'cyprus', 'latvia', 'lithuania', 'malta', 'slovakia',
                'slovenia', 'austria', 'finland', 'sweden', 'netherlands', 'denmark',
                'norway', 'south-korea', 'portugal', 'spain', 'malaysia',
                'hungary', 'czech-republic', 'kuwait', 'eu', 'non-eu',
                'poland', 'singapore', 'russia', 'indonesia', 'extra-eu-27',
                'total-eu-27', 'saudi-arabia', 'croatia', 'italy', 'israel',
                'south-africa', 'taiwan', 'india', 'united-states-inc-puerto-rico', 'turkey',
                'mexico', 'switzerland', 'hong-kong', 'ww',
                'philippines', 'pakistan', 'brazil', 'emu-19', 'bulgaria', 'romania', 'iceland',
                'australia', 'thailand', 'united-arab-emirates', 'new-zealand', 'greece', 'egypt', 'rw',
                'ww-ttlesspm'])
DIRECTION = set(['imports', 'exports', 'balance', 'ex', 'im', 'bal', 'terms-of-trade'])
BASIS = set(['bop'])
ADJUST = set(['nsa', 'sa'])
UNIT = set(['cp', 'cvm', 'tons', 'idef', 'av-value-per-ton'])
TIG = 'Trade in Goods'
TT = 'total trade'

TradeInProduct = namedtuple('TradeInProduct', 'country, product, product_label, direction, basis, unit, adjustment')
SterlingEffectiveERI = namedtuple('SterlingEffectiveERI', 'measure base')
ExchangeRate = namedtuple('ExchangeRate', 'currency')

import re
ERI_RE = re.compile(r'Sterling effective exchange rate index: ([^(]*) \(([^)]*)\)')
PROD_RE = re.compile(r'.*\(([^)]+)\)')

sitc = {}
currency_label = {}
country_label = {}
product_label = {}

def prod_code(l):
    match = PROD_RE.match(l)
    if match is not None:
        return match.group(1)
    return None

def dim_val(t):
    if t.startswith(TIG) and t[len(TIG)+1] != ':':
        t = t[0:len(TIG)] + ':' + t[len(TIG)+1:]
    elif t.lower().startswith(TT):
        t = TIG + ': ' + t
    labels = [d.strip() for d in t.split(':')]
    dims = [pathify(l) for l in labels]
    if dims[0] == 'average-sterling-exchange-rate':
        currency_label[dims[1]] = labels[1]
        return ExchangeRate(dims[1])
    elif dims[0] == 'sterling-effective-exchange-rate-index':
        match = ERI_RE.match(t)
        if match:
            return SterlingEffectiveERI(match.group(1), match.group(2))
        raise(Exception(t))
    elif dims[0] == 'trade-in-goods':
        if dims[1] in COUNTRIES and dims[3] in DIRECTION and dims[4] in BASIS and dims[5] in UNIT and dims[6] in ADJUST:
            country_label[dims[1]] = labels[1]
            product = prod_code(labels[2])
            if product is None:
                assert labels[2] == 'Total', f"Trade in Goods: some-country should be something in brackets or 'Total' but it's {labels[2]}"
                product = 'T'
            product_label[product] = labels[2]
            return TradeInProduct(
                country=dims[1], product=product, product_label=labels[2],
                direction=dims[3], basis=dims[4], unit=dims[5], adjustment=dims[6])
        elif dims[2] in COUNTRIES and dims[3] in DIRECTION and dims[4] in BASIS and dims[5] in UNIT and dims[6] in ADJUST:
            country_label[dims[2]] = labels[2]
            product = prod_code(labels[1])
            if product is None:
                raise(Exception(labels[1]))
            product_label[product] = labels[1]
            return TradeInProduct(
                country=dims[2], product=product, product_label=labels[1],
                direction=dims[3], basis=dims[4], unit=dims[5], adjustment=dims[6])
        # ['trade-in-goods', 'emu-19', 'balance', 'bop', 'cp', 'sa']
        elif dims[1] in COUNTRIES and dims[2] in DIRECTION and dims[3] in BASIS and dims[4] in UNIT and dims[5] in ADJUST:
            country_label[dims[1]] = label[1]
            return TradeInProduct(
                country=dims[1], product='T', product_label=label[1], direction=dims[2],
                basis=dims[3], unit=dims[4], adjustment=dims[5])
        else:
            raise(Exception(dims))
    elif dims[0] == 'trade-in-goods-t' and dims[1] in COUNTRIES and dims[2] in DIRECTION and dims[3] in BASIS and dims[4] in UNIT and dims[5] in ADJUST:
        product = prod_code(labels[0])
        if product is None:
            raise Exception(labels[0])
        product_label[product] = labels[0]
        country_label[dims[1]] = labels[1]
        return TradeInProduct(
            country=dims[1], product=product, product_label=labels[1], direction=dims[2],
            basis=dims[3], unit=dims[4], adjustment=dims[5])
    elif dims[0] == 'trade-in-services-ts' and dims[1] == 'ww' and dims[2] in DIRECTION and dims[3] in BASIS and dims[4] in UNIT and dims[5] in ADJUST:
        product = prod_code(labels[0])
        if product is None:
            raise(Exception(t))
        product_label[product] = labels[0]
        country_label[dims[1]] = labels[1]
        return TradeInProduct(
            country=dims[1], product=product, product_label=labels[1] ,direction=dims[2], basis=dims[3],
            unit=dims[4], adjustment=dims[5])
    elif dims[0] in set(['eu-2004', 'non-eu-2004']) and dims[1] in BASIS and dims[2] in DIRECTION and dims[5].startswith('sitc'):
        country_label[dims[0]] = labels[0]
        product = labels[5].replace(' ', '_')
        product_label[product] = labels[4]
        sitc[product] = dims[5]
        return TradeInProduct(
            country=dims[0], product=product, product_label=labels[4], direction=dims[2], basis=dims[1], adjustment=dims[3], unit='cp')
    # ['bop', 'ex', 'sa', 'ships-and-aircraft-sna', 'sitc-792-793']
    elif dims[0] in BASIS and dims[1] in DIRECTION and dims[2] in ADJUST and dims[4].startswith('sitc'):
        product = labels[4].replace(' ', '_')
        sitc[product] = dims[4]
        product_label[product] = labels[3]
        return TradeInProduct(
            country='ww', product=product, product_label=labels[3], direction=dims[1], basis=dims[0], unit='cp',
            adjustment=dims[2])
    else:
        raise(Exception(dims))



# +
TradeObservation = namedtuple('TradeObservation', ('period',) + TradeInProduct._fields + ('value','decimals',))
SterlingEffectiveERIObservation = namedtuple('SterlingEffectiveERIObservation', 'period rate measure base')
ExchangeRateObservation = namedtuple('ExchangeRateCountryObservation', 'period currency rate')

product_data = []
exchange_currency_data = []
effective_exchange_data = []

def period(periodicity, year_start, i):
    if periodicity == 'A':
        return f"year/{int(year_start) + i}"
    elif periodicity == 'Q':
        return f"quarter/{int(year_start) + (i // 4)}-Q{(i % 4) + 1}"
    elif periodicity == 'M':
        return f"month/{int(year_start) + (i // 12)}-{((i % 12) + 1):02}"

for csid, slice_list in slices.items():
    for s in slice_list:
        try:
            dim_vals = dim_val(s['label'])
        except Exception as e:
            print(f'Error:\n{e}')
            continue                
        for i, v in enumerate(s['observations']):
            p = period(s['header'].periodicity, s['struct'].year_start, i)
            if isinstance(dim_vals, TradeInProduct):
                product_data.append(TradeObservation._make(
                    (p,) + dim_vals + (v, s['struct'].decimals)))
            elif isinstance(dim_vals, SterlingEffectiveERI):
                effective_exchange_data.append(SterlingEffectiveERIObservation(
                    p, v, dim_vals.measure, dim_vals.base))
            elif isinstance(dim_vals, ExchangeRate):
                exchange_currency_data.append(ExchangeRateObservation(
                    p, dim_vals.currency, v))

product_observations = pd.DataFrame(data=product_data)
effective_eri_observations = pd.DataFrame(data=effective_exchange_data)
exchange_currency_observations = pd.DataFrame(data=exchange_currency_data)
# -

product_observations.replace(
    {'product': {'-t': 'total-goods'}}, inplace=True)


# ## Note - spoke with Alex, to start with we're going to concentrate on the product data
#
# so once we're up and running, we need to add the effective_eri_observations and exchange_currency_observations
# dataframes to the outputs dict below
#

def fix_short_hand_flow(val):
    if val in ["imports", "exports", "balance", "terms-of-trade"]:
        return val
    elif val == "im":
        return "imports"
    elif val == "ex":
        return "exports"
    elif val == "bal":
        return "balance"
    else:
        raise Exception("Aborting. Unexpected 'Flow direction' of {} encountered.".format(val))


def measure_type_lookup(val):
    """
    We'll use the unit of measure to lookup the measure type
    """
    if val == "cvm":
        return "Chained volume measure"
    if val == "cp":
        return "Current Price"
    if val == "av-value-per-ton":
        return "Average value per ton"
    if val == "idef":
        return "Implied Deflator"
    if val == "tons":
        return "Net Mass"
    else:
        raise Exception("Aborting. Cannot find the measure type for {}.".format(val))


# +

# Tidy up the product labels to just be the labels
product_observations["product_label"] = product_observations["product_label"].map(lambda x: x.split("(")[0].strip())
product_observations.head()
# -


from os import environ
from gssutils.metadata import THEME

# Rename columns
rename_columns = {"period": "Period",
                  "country": "Trade Area",
                  "product": "Product",
                  "direction": "Flow Directions",
                  "basis": "Basis",
                  "unit": "Unit",
                  "adjustment": "Seasonal Adjustment",
                  "value": "Value",
                  "decimals": "Decimals"}
product_observations.rename(rename_columns, axis=1, inplace=True)

# +
# Correct casing to match codelists
if "Seasonal Adjustment" in product_observations.columns.values:
    product_observations["Seasonal Adjustment"] = product_observations["Seasonal Adjustment"].str.upper()
    
if "Product" in product_observations.columns.values:
    product_observations["Product"] = product_observations["Product"].apply(pathify)
    
if "Flow Directions" in product_observations.columns.values:
    product_observations["Flow Directions"] = product_observations["Flow Directions"].apply(fix_short_hand_flow)
     
if "Basis" in product_observations.columns.values:
    product_observations = product_observations.drop("Basis", axis=1)
    
product_observations["Measure Type"] = product_observations["Unit"].apply(measure_type_lookup)

try:
    del product_observations['product_label']
except:
    print("No product label column")
    
try:
    del product_observations['Decimals']
except:
    print("No Decimals column")
    

product_observations_cvm = product_observations[product_observations["Measure Type"] == "Chained volume measure"]
product_observations_cp = product_observations[product_observations["Measure Type"] == "Current Price"]
product_observations_avg = product_observations[product_observations["Measure Type"] == "Average value per ton"]
product_observations_def = product_observations[product_observations["Measure Type"] == "implied-deflator"]
product_observations_cvm["Measure Type"] = 'chained-volume-measure'
product_observations_cp["Measure Type"] = 'current-price'
product_observations_avg["Measure Type"] = 'avg-per-ton'
product_observations_def["Measure Type"] = 'implied-deflator'

# +
del product_observations_cvm['Measure Type']
del product_observations_cvm['Unit']
product_observations_cvm['Trade Area'] = product_observations_cvm['Trade Area'].str.upper()

del product_observations_cp['Measure Type']
del product_observations_cp['Unit']
product_observations_cp['Trade Area'] = product_observations_cp['Trade Area'].str.upper()
# -

"""
Measure Type
'Current Price', 'Chained volume measure', 'Net Mass','Implied Deflator', 'Average value per ton'
"""
product_observations_cvm['Trade Area'] = product_observations_cvm['Trade Area'].apply(pathify)
product_observations_cvm.head(10)

# +

#product_observations_cp['Trade Area'].unique()
product_observations_cvm['Trade Area'].unique()

# +
#### CHAINED VOLUME MEASURES
cubes = Cubes(infoFileName)

metadata.dataset.title = 'UK trade time series - Chained Value Measures'
metadata.dataset.comment = 'Monthly value of UK exports and imports of goods and services by chained volume measures.'
metadata.dataset.description = metadata.dataset.comment + ' Figures are to 0 decimal places.'

with open("info.json", "r") as jsonFile:
    data = json.load(jsonFile)
    data["transform"]["columns"]["Value"]["measure"] = "http://gss-data.org.uk/def/measure/cvm"
    data["transform"]["columns"]["Value"]["unit"] = "http://gss-data.org.uk/def/concept/measurement-units/gbp-million"
    with open("info.json", "w") as jsonFile:
        json.dump(data, jsonFile)
product_observations_cvm = product_observations_cvm.drop_duplicates()   
cubes.add_cube(copy.deepcopy(metadata), product_observations_cvm, 'uk-trade-time-series-chained-value-measures', 'uk-trade-time-series-chained-value-measures', data)
# -

product_observations_cp['Trade Area'] = product_observations_cp['Trade Area'].apply(pathify)

# +
#### CURRENT PRICES
metadata.dataset.title = 'UK trade time series - Current Prices'
metadata.dataset.comment = 'Monthly value of UK exports and imports of goods and services by current prices.'
metadata.dataset.description = metadata.dataset.comment + ' Figures are to 0 decimal places.'

with open("info.json", "r") as jsonFile:
    data = json.load(jsonFile)
    data["transform"]["columns"]["Value"]["measure"] = "http://gss-data.org.uk/def/measure/current-prices"
    data["transform"]["columns"]["Value"]["unit"] = "http://gss-data.org.uk/def/concept/measurement-units/gbp-million"
    with open("info.json", "w") as jsonFile:
        json.dump(data, jsonFile)
product_observations_cp = product_observations_cp.drop_duplicates()   
cubes.add_cube(copy.deepcopy(metadata), product_observations_cp, 'uk-trade-time-series-current-prices', 'uk-trade-time-series-current-prices', data)
# -
for cube in cubes.cubes:
    print(cube.scraper.title)

cubes.output_all()
