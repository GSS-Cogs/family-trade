{\rtf1\ansi\ansicpg1252\cocoartf1671\cocoasubrtf600
{\fonttbl\f0\fmodern\fcharset0 Courier;}
{\colortbl;\red255\green255\blue255;\red0\green0\blue0;\red27\green31\blue34;\red255\green255\blue255;
}
{\*\expandedcolortbl;;\cssrgb\c0\c0\c0;\cssrgb\c14118\c16078\c18039;\cssrgb\c100000\c100000\c100000;
}
\paperw11900\paperh16840\margl1440\margr1440\vieww21020\viewh12980\viewkind0
\deftab720
\pard\pardeftab720\partightenfactor0

\f0\fs26 \cf0 \expnd0\expndtw0\kerning0
<!-- #region -->\
# COGS Dataset Specification\
----------\
\
## \cf3 \cb4 ONS UK trade in services by business characteristics\cf0 \cb1 \
[Landing Page](https://www.ons.gov.uk/businessindustryandtrade/internationaltrade/datasets/uktradeingoodsbybusinesscharacteristics)\
\
----------\
\
### Stage 1. Transform\
\
#### Sheet: Sheet1 \
    \
Transform notes   \
\
#### Table Structure\
\
		Columns go here\
\
#### DE Stage one notes \
Notes go here.\
\
### Stage 2 - Harmonisation\
\
Exports (\'a3m) and Imports (\'a3m) should be combined into a dimension and the values should go in the \'91Value\'92 column.\
\
I think the six data tabs can be combined into a single cube: 2016, 2016 Industry Totals, 2017, 2017 Industry Totals, 2018, 2018 Industry Totals.\
\
A possible dataset structure would be:\
Business size // Ownership // Industry // Direction // Data Marking // Value\
\
The Industry Totals tabs have Ownership and Industry breakdowns and should have \'91Total\'92 for Business size.\
The year totals have Ownership and Business size breakdowns and should have \'91Total\'92 for Industry.\
\
\
#### DM Notes\
\
Nothing here yet.\
<!-- #endregion -->}