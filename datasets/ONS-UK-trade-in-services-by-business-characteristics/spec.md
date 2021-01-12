bplist00�_WebMainResource�	
_WebResourceFrameName_WebResourceData_WebResourceMIMEType_WebResourceTextEncodingName^WebResourceURLPO(�<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <meta http-equiv="Content-Style-Type" content="text/css">
  <title></title>
  <meta name="Generator" content="Cocoa HTML Writer">
  <meta name="CocoaVersion" content="1671.6">
  <style type="text/css">
    p.p1 {margin: 0.0px 0.0px 0.0px 0.0px; line-height: 14.0px; font: 12.0px Courier; color: #000000; -webkit-text-stroke: #000000}
    p.p2 {margin: 0.0px 0.0px 0.0px 0.0px; line-height: 15.0px; font: 13.0px Courier; color: #000000; -webkit-text-stroke: #000000}
    span.s1 {font-kerning: none}
    span.Apple-tab-span {white-space:pre}
  </style>
</head>
<body>
<p class="p1"><span class="s1">&lt;!— #region —&gt;</span></p>
<p class="p1"><span class="s1"># COGS Dataset Specification</span></p>
<p class="p1"><span class="s1"><br>
</span></p>
<p class="p1"><span class="s1"># ONS UK trade in services by business characteristics</span></p>
<p class="p1"><span class="s1">[Landing Page](https://www.ons.gov.uk/businessindustryandtrade/internationaltrade/datasets/uktradeingoodsbybusinesscharacteristics)</span></p>
<p class="p1"><span class="s1"><br>
</span></p>
<p class="p1"><span class="s1">### Stage 1. Transform</span></p>
<p class="p1"><span class="s1"><br>
</span></p>
<p class="p1"><span class="s1">#### Sheet: Sheet1</span></p>
<p class="p1"><span class="s1"><br>
</span></p>
<p class="p1"><span class="s1">Transform notes</span></p>
<p class="p1"><span class="s1"><br>
</span></p>
<p class="p1"><span class="s1">#### Table Structure (proposed by DM)</span></p>
<p class="p1"><span class="s1"><br>
</span></p>
<p class="p1"><span class="s1"><span class="Apple-tab-span">	</span><span class="Apple-tab-span">	</span>Period // Business size // Country // Ownership // Industry // Flow // Measure type // Unit of Measure // Value // Marker</span></p>
<p class="p1"><span class="s1"><br>
</span></p>
<p class="p1"><span class="s1">#### DE Stage one notes</span></p>
<p class="p1"><span class="s1">Notes go here.</span></p>
<p class="p1"><span class="s1"><br>
</span></p>
<p class="p1"><span class="s1">### Stage 2 - Harmonisation</span></p>
<p class="p1"><span class="s1"><br>
</span></p>
<p class="p1"><span class="s1">I think these six data tabs can be combined into a single cube: 2016, 2016 Industry Totals, 2017, 2017 Industry Totals, 2018, 2018 Industry Totals.</span></p>
<p class="p1"><span class="s1">Exports (£) and Imports (£) should be combined into a 'Flow' dimension and the values should go in the 'Value' column.</span></p>
<p class="p1"><span class="s1"><br>
</span></p>
<p class="p1"><span class="s1">The year tabs (2016, 2017 and 2018 at present) have one structure and the Industry Totals tabs another.</span></p>
<p class="p1"><span class="s1"><br>
</span></p>
<p class="p1"><span class="s1">The year tabs have three summary tables on top of each other. Each is missing a dimension.</span></p>
<p class="p1"><span class="s1">The first down needs a 'Country' dimension with 'world'.</span></p>
<p class="p1"><span class="s1">The second down needs a 'Business size' dimension with 'any'.</span></p>
<p class="p1"><span class="s1">The third needs an 'Ownership' dimension with 'any'.</span></p>
<p class="p1"><span class="s1"><br>
</span></p>
<p class="p1"><span class="s1">The Industry totals tabs have two tables alongside each other.</span></p>
<p class="p1"><span class="s1">The left one needs a 'Business size' dimension with 'All' and a 'Country' dimension with 'world'.</span></p>
<p class="p1"><span class="s1">The right one needs an 'Ownership' dimension with 'any' and a 'Country' dimension with 'world'.</span></p>
<p class="p1"><span class="s1"><br>
</span></p>
<p class="p1"><span class="s1">This way all the data have the same dimensions and can be combined<span class="Apple-converted-space"> </span></span></p>
<p class="p1"><span class="s1"><br>
</span></p>
<p class="p1"><span class="s1">The Industry Totals tabs have Ownership and Industry breakdowns and should have All for Business size.</span></p>
<p class="p1"><span class="s1">The year totals have Ownership and Business size breakdowns and should have All for Industry.</span></p>
<p class="p1"><span class="s1"><br>
</span></p>
<p class="p1"><span class="s1">The Measure type dimension is 'Current Prices' and Unit of measure is 'gbp-million'.</span></p>
<p class="p1"><span class="s1"><br>
</span></p>
<p class="p1"><span class="s1">### Codelists:</span></p>
<p class="p1"><span class="s1"><br>
</span></p>
<p class="p1"><span class="s1">#### Period:</span></p>
<p class="p1"><span class="s1"><br>
</span></p>
<p class="p1"><span class="s1">#### Business size:</span></p>
<p class="p1"><span class="s1">Change notation to '1-to-49', '11-to-249', '250-and-over', unknown-employees (also 'any' to represent total). Use codelist family-trade/reference/codelists/employment-size-bands</span></p>
<p class="p1"><span class="s1"><br>
</span></p>
<p class="p1"><span class="s1">#### Country:</span></p>
<p class="p1"><span class="s1">Change 'World' to 'WW', 'Total EU28' to 'EU' and 'Non-EU' to 'RW'. Use family-trade/reference/codelists/eu-rw-ww</span></p>
<p class="p1"><span class="s1"><br>
</span></p>
<p class="p1"><span class="s1">#### Ownership:</span></p>
<p class="p1"><span class="s1">Change 'Domestic' to 'uk' and 'All' to 'any'. Use family-trade/reference/codelists/countries-of-ownership</span></p>
<p class="p1"><span class="s1"><br>
</span></p>
<p class="p1"><span class="s1">#### Industry:<span class="Apple-converted-space"> </span></span></p>
<p class="p1"><span class="s1"><br>
</span></p>
<p class="p1"><span class="s1">#### Flow:<span class="Apple-converted-space"> </span></span></p>
<p class="p1"><span class="s1">add 'exports' and 'imports' as per instructions above and use codelist family-trade/reference/codelists/flow-directions</span></p>
<p class="p1"><span class="s1"><br>
</span></p>
<p class="p1"><span class="s1">#### Measure type:</span></p>
<p class="p1"><span class="s1">change 'Current prices' to 'CP'. Use code list: family-trade/reference/codelists/price-classifications</span></p>
<p class="p1"><span class="s1"><br>
</span></p>
<p class="p1"><span class="s1">#### Unit of Measure:</span></p>
<p class="p1"><span class="s1"><br>
</span></p>
<p class="p1"><span class="s1">#### Value:</span></p>
<p class="p1"><span class="s1"><br>
</span></p>
<p class="p1"><span class="s1">#### Marker:<span class="Apple-converted-space"> </span></span></p>
<p class="p1"><span class="s1">Change '..' to 'suppressed' and use codelist ref_common/markers</span></p>
<p class="p1"><span class="s1"><br>
</span></p>
<p class="p1"><span class="s1">### Scraper:</span></p>
<p class="p1"><span class="s1"><br>
</span></p>
<p class="p1"><span class="s1">Dataset-title: uktradeingoodsbybusinesscharacteristics</span></p>
<p class="p1"><span class="s1">Title: UK trade in goods by business characteristics</span></p>
<p class="p1"><span class="s1">Comment: Trade in goods data, including breakdown of imports and exports by Standard Industrial Classification, region (EU and non-EU), business size and by domestic and foreign ownership.</span></p>
<p class="p1"><span class="s1">Description: Trade in goods data, including breakdown of imports and exports by Standard Industrial Classification, region (EU and non-EU), business size and by domestic and foreign ownership.</span></p>
<p class="p1"><span class="s1"><br>
</span></p>
<p class="p1"><span class="s1">Users should note the following:</span></p>
<p class="p1"><span class="s1">Industry data has been produced using Standard Industrial Classification 2007 (SIC07).</span></p>
<p class="p1"><span class="s1"><br>
</span></p>
<p class="p1"><span class="s1">Business size is defined using the following employment size bands:</span></p>
<p class="p1"><span class="s1"><span class="Apple-converted-space">   </span>Small - 0-49 employees</span></p>
<p class="p1"><span class="s1"><span class="Apple-converted-space">   </span>Medium - 50-249 employees</span></p>
<p class="p1"><span class="s1"><span class="Apple-converted-space">   </span>Large - 250+ employees</span></p>
<p class="p1"><span class="s1"><span class="Apple-converted-space">   </span>Unknown - number of employees cannot be determined via IDBR</span></p>
<p class="p1"><span class="s1"><br>
</span></p>
<p class="p1"><span class="s1">Ownership status is defined as:</span></p>
<p class="p1"><span class="s1"><span class="Apple-converted-space">   </span>Domestic - ultimate controlling parent company located in the UK</span></p>
<p class="p1"><span class="s1"><span class="Apple-converted-space">   </span>Foreign - ultimate controlling parent company located outside the UK</span></p>
<p class="p1"><span class="s1"><span class="Apple-converted-space">   </span>Unknown - location of ultimate controlling parent company cannot be determined via IDBR</span></p>
<p class="p1"><span class="s1"><br>
</span></p>
<p class="p1"><span class="s1">Some data cells have been suppressed to protect confidentiality so that individual traders cannot be identified.</span></p>
<p class="p1"><span class="s1"><br>
</span></p>
<p class="p1"><span class="s1">Data</span></p>
<p class="p1"><span class="s1">All data is in £ million, current prices</span></p>
<p class="p1"><span class="s1"><br>
</span></p>
<p class="p1"><span class="s1">Rounding</span></p>
<p class="p1"><span class="s1">Some of the totals within this release (e.g. EU, Non EU and world total) may not exactly match data published via other trade releases due to small rounding differences.</span></p>
<p class="p1"><span class="s1"><br>
</span></p>
<p class="p1"><span class="s1">Trade Asymmetries<span class="Apple-converted-space"> </span></span></p>
<p class="p1"><span class="s1">These data are our best estimate of these bilateral UK trade flows. Users should note that alternative estimates are available, in some cases, via the statistical agencies for bilateral countries or through central databases such as UN Comtrade</span></p>
<p class="p1"><span class="s1"><br>
</span></p>
<p class="p1"><span class="s1">#### DM Notes</span></p>
<p class="p1"><span class="s1"><br>
</span></p>
<p class="p1"><span class="s1">Nothing here yet.</span></p>
<p class="p2"><span class="s1">&lt;!-- #endregion --&gt;}</span></p>
</body>
</html>
Ytext/htmlUutf-8_file:///index.html    ( ? Q g � � �)V)`)f                           ){