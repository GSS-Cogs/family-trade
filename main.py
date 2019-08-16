# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.1.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
from gssutils import *

scraper = Scraper('https://www.ons.gov.uk/economy/nationalaccounts/balanceofpayments/datasets/'
                  'tradeingoodsmretsallbopeu2013timeseriesspreadsheet')
scraper
# -

dist = scraper.distribution(mediaType='text/prs.ons+csdb')
dist

# +
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
        print(label)
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
                 'australia', 'thailand', 'united-arab-emirates', 'new-zealand', 'greece', 'egypt', 'rw'])
DIRECTION = set(['imports', 'exports', 'balance', 'ex', 'im', 'bal', 'terms-of-trade'])
BASIS = set(['bop'])
ADJUST = set(['nsa', 'sa'])
CP = set(['cp', 'cvm', 'tons', 'idef', 'av-value-per-ton'])
TIG = 'Trade in Goods'
TT = 'total trade'

TradeInProduct = namedtuple('TradeInProduct', 'country, product, direction, basis, cp, adjustment')
SterlingEffectiveERI = namedtuple('SterlingEffectiveERI', 'measure base')
ExchangeRate = namedtuple('ExchangeRate', 'currency')
import re
ERI_RE = re.compile(r'Sterling effective exchange rate index: ([^(]*) \(([^)]*)\)')

sitc = {}
currency_label = {}
country_label = {}
product_label = {}

def dim_val(t):
    if t.startswith(TIG) and t[len(TIG)+1] != ':':
        t = t[0:len(TIG)] + ':' + t[len(TIG)+1:]
    elif t.lower().startswith(TT):
        t = TIG + ':' + t
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
        if dims[1] in COUNTRIES and dims[3] in DIRECTION and dims[4] in BASIS and dims[5] in CP and dims[6] in ADJUST:
            country_label[dims[1]] = labels[1]
            product = 'total-goods' if dims[2] == 'total' else dims[2]
            product_label[product] = labels[2]
            return TradeInProduct(
                country=dims[1], product='total-goods' if dims[2] == 'total' else dims[2],
                direction=dims[3], basis=dims[4], cp=dims[5], adjustment=dims[6])
        elif dims[2] in COUNTRIES and dims[3] in DIRECTION and dims[4] in BASIS and dims[5] in CP and dims[6] in ADJUST:
            country_label[dims[2]] = labels[2]
            product = 'total-goods' if dims[1] == 'total' else dims[1]
            product_label[product] = labels[1]
            return TradeInProduct(
                country=dims[2], product='total-goods' if dims[1] == 'total' else dims[1],
                direction=dims[3], basis=dims[4], cp=dims[5], adjustment=dims[6])
        # ['trade-in-goods', 'emu-19', 'balance', 'bop', 'cp', 'sa']
        elif dims[1] in COUNTRIES and dims[2] in DIRECTION and dims[3] in BASIS and dims[4] in CP and dims[5] in ADJUST:
            country_label[dims[1]] = label[1]
            return TradeInProduct(
                country=dims[1], product='total-goods', direction=dims[2],
                basis=dims[3], cp=dims[4], adjustment=dims[5])
        else:
            raise(Exception(dims))
    elif dims[0] == 'trade-in-goods-t' and dims[1] in COUNTRIES and dims[2] in DIRECTION and dims[3] in BASIS and dims[4] in CP and dims[5] in ADJUST:
        country_label[dims[1]] = label[1]
        return TradeInProduct(
            country=dims[1], product='total-goods', direction=dims[2],
            basis=dims[3], cp=dims[4], adjustment=dims[5])
    elif dims[0] == 'trade-in-services-ts' and dims[1] == 'ww' and dims[2] in DIRECTION and dims[3] in BASIS and dims[4] in CP and dims[5] in ADJUST:
        country_label[dims[1]] = label[1]
        return TradeInProduct(
            country=dims[1], product='total-services', direction=dims[2], basis=dims[3],
            cp=dims[4], adjustment=dims[5])
    elif dims[0] in set(['eu-2004', 'non-eu-2004']) and dims[1] in BASIS and dims[2] in DIRECTION and dims[5].startswith('sitc'):
        country_label[dims[0]] = label[0]
        product_label[dims[4]] = label[4]
        sitc[dims[4]] = dims[5]
        return TradeInProduct(
            country=dims[0], product=dims[4], direction=dims[2], basis=dims[1], adjustment=dims[3], cp='cp')
    # ['bop', 'ex', 'sa', 'ships-and-aircraft-sna', 'sitc-792-793']
    elif dims[0] in BASIS and dims[1] in DIRECTION and dims[2] in ADJUST and dims[4].startswith('sitc'):
        sitc[dims[3]] = dims[4]
        product_label[dims[3]] = label[3]
        return TradeInProduct(
            country='ww', product=dims[3], direction=dims[1], basis=dims[0], cp='cp',
            adjustment=dims[2])
    else:
        raise(Exception(dims))



# +
TradeObservation = namedtuple('TradeObservation', ('period',) + TradeInProduct._fields + ('value',))
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
        for i, v in enumerate(s['observations']):
            dim_vals = dim_val(s['label'])
            p = period(s['header'].periodicity, s['struct'].year_start, i)
            if isinstance(dim_vals, TradeInProduct):
                product_data.append(TradeObservation._make(
                    (p,) + dim_vals + (v, )))
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

# +
out = Path('out')
out.mkdir(exist_ok=True)

product_observations.to_csv(out / 'product-observations.csv', index=False)
effective_eri_observations.to_csv(out / 'effective-eri-observations.csv', index=False)
exchange_currency_observations.to_csv(out / 'exchange-currency-observations.csv', index=False)
# -

currency_label


