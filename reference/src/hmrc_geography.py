#!/usr/bin/env python3

import csv

countryCode = {}
countryLabel = {}
with open('input/hmrc-geographies.csv') as f:
    r = csv.DictReader(f)
    for row in r:
        assert row['Notation'] != countryLabel, row['Notation']
        countryLabel[row['Notation']] = row['Label']
        if row['Label'] == 'Stores & Provisions':
            continue
        assert row['Label'].strip() not in countryCode, row['Label']
        countryCode[row['Label'].strip()] = row['Notation']

regionCode = {
    'Asia and Oceania': 'A',
    'Eastern Europe (excl. EU)': 'B',
    'European Union': 'C',
    'Latin America and Caribbean': 'D',
    'Middle East and North Africa': 'F',
    'North America': 'G',
    'Sub-Saharan Africa': 'H',
    'Western Europe (excl. EU)': 'I'
}

countryCodeParent = {}
shortened = {
    'Christmas Is': 'Christmas Islands',
    'Heard & Mcdonald': 'Heard Island and McDonald Islands',
    'Fr Southern Terr': 'French Southern Territories',
    'Micronesia': 'Micronesia (Federated States of)',
    'N Mariana Is': 'Northern Mariana Islands',
    'Philipines': 'Philippines',
    'Us Minor Islands': 'United States Minor outlying islands',
    'Wallis & Futuna': 'Wallis and Futuna',
    'Fyr Macedonia': 'Former Yugoslav Republic of Macedonia',
    'Bosnia & Herz.': 'Bosnia-Herzegovina',
    'Kyrkyz Republic': 'Kyrgyz Republic',
    'Moldova': 'Moldova, Republic of',
    'Dominican Rep': 'Dominican Republic',
    'Falkland Islands': 'Falklands Islands and dependencies',
    'Trinidad:Tobago': 'Trinidad and Tobago',
    'Venezuela': 'Venezuela, Bolivarian Republic of',
    'Antigua:Barbuda': 'Antigua and Barbuda',
    'Bonaire': 'Bonaire, Sint Eustatius and Saba',
    'Br Virgin Is': 'British Virgin Islands',
    'Saint Maarten': 'Sint Maarten (Dutch part)',
    'St Kitts & Nevis': 'St Kitts and Nevis',
    'St Vincent': 'St Vincent and the Grenadines',
    'Turks & Caicos': 'Turks and Caicos Islands',
    'Us Virgin Is': 'United States Virgin Islands',
    'UAE': 'United Arab Emirates',
    'Iran': 'Iran (Islamic Republic of)',
    'Occ Palestinian Territories': 'Occupied Palestinian Territory',
    'USA incl. Puerto Rico': 'United States',
    'St Pierre-Mique': 'St Pierre and Miquelon',
    'Congo (Republic)': 'Congo',
    'Equat. Guinea': 'Equatorial Guinea',
    'Tanzania': 'Tanzania (United Republic of)',
    'Br Ind Oc Terr': 'British Indian Ocean Territory',
    'Burkina': 'Burkina Faso',
    'Cent Afr Rep': 'Central Africa Republic',
    'Congo (Dem. Rep)': 'Congo (Democratic Republic of the)',
    'Guinea-Bissau': 'Guinea Bissau',
    'Sao Tome-Princ.': 'Sao Tome and Principe',
    'St Helena': 'St Helena, Ascension and Tristan da Cunha',
    'Vatican City': 'Vatican City State'
}
with open('input/suppressed-countries-rts.csv') as f:
    r = csv.DictReader(f)
    for row in r:
        label = row['Country']
        if label in shortened:
            label = shortened[label]
        code = countryCode[label]
        parent = regionCode[row['Geographical Area']]
        countryCodeParent[code] = parent

with open('codelists/hmrc-geographies.csv', 'w') as f:
    w = csv.DictWriter(f, fieldnames=['Label', 'Notation', 'Parent Notation'])
    w.writeheader()
    for code in countryLabel:
        w.writerow({
            'Label': countryLabel[code],
            'Notation': code,
            'Parent Notation': countryCodeParent.get(code, '')
        })
    for label in regionCode:
        w.writerow({
            'Label': label,
            'Notation': regionCode[label],
            'Parent Notation': ''
        })

