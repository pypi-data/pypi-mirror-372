# address_constants.py

# zcta download link from us census bureau:
# https://www2.census.gov/geo/tiger/TIGER2023/ZCTA5/
ZCTA_LINK = "https://www.census.gov/cgi-bin/geo/shapefiles/index.php?year=2020&layergroup=ZIP%20Code%20Tabulation%20Areas"

# STATE_DICT maps two-letter state abbreviations to their full state names.
# This dictionary is used to populate address-related fields in a database
# or to validate and expand abbreviated state codes.
STATE_DICT = {
    'AL': 'Alabama',
    'AK': 'Alaska',
    'AZ': 'Arizona',
    'AR': 'Arkansas',
    'CA': 'California',
    'CO': 'Colorado',
    'CT': 'Connecticut',
    'DE': 'Delaware',
    'FL': 'Florida',
    'GA': 'Georgia',
    'HI': 'Hawaii',
    'ID': 'Idaho',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'IA': 'Iowa',
    'KS': 'Kansas',
    'KY': 'Kentucky',
    'LA': 'Louisiana',
    'ME': 'Maine',
    'MD': 'Maryland',
    'MA': 'Massachusetts',
    'MI': 'Michigan',
    'MN': 'Minnesota',
    'MS': 'Mississippi',
    'MO': 'Missouri',
    'MT': 'Montana',
    'NE': 'Nebraska',
    'NV': 'Nevada',
    'NH': 'New Hampshire',
    'NJ': 'New Jersey',
    'NM': 'New Mexico',
    'NY': 'New York',
    'NC': 'North Carolina',
    'ND': 'North Dakota',
    'OH': 'Ohio',
    'OK': 'Oklahoma',
    'OR': 'Oregon',
    'PA': 'Pennsylvania',
    'RI': 'Rhode Island',
    'SC': 'South Carolina',
    'SD': 'South Dakota',
    'TN': 'Tennessee',
    'TX': 'Texas',
    'UT': 'Utah',
    'VT': 'Vermont',
    'VA': 'Virginia',
    'WA': 'Washington',
    'WV': 'West Virginia',
    'WI': 'Wisconsin',
    'WY': 'Wyoming',
    'DC': 'District of Columbia'
}

# STATE_ZIP_RANGES maps two-letter state abbreviations to a list of ZIP code ranges.
# Each value is a list of tuples, where each tuple represents a ZIP code range
# (start ZIP, end ZIP) associated with that state.
#
# These ranges can be used for:
#   - Validating ZIP codes against known state boundaries
#   - Filtering or grouping addresses by geographic region
#   - Populating address tables with ZIP-based constraints
STATE_ZIP_RANGES = {
    'AK': [('99501', '99950')],
    'AL': [('35004', '36925')],
    'AR': [('71601', '72959'), ('75502', '75502')],
    'AZ': [('85001', '86556')],
    'CA': [('90001', '96162')],
    'CO': [('80001', '81658')],
    'CT': [('06001', '06389'), ('06401', '06928')],
    'DC': [('20001', '20039'), ('20042', '20599'), ('20799', '20799')],
    'DE': [('19701', '19980')],
    'FL': [('32004', '34997')],
    'GA': [('30001', '31999'), ('39901', '39901')],
    'HI': [('96701', '96898')],
    'IA': [('50001', '52809'), ('68119', '68120')],
    'ID': [('83201', '83876')],
    'IL': [('60001', '62999')],
    'IN': [('46001', '47997')],
    'KS': [('66002', '67954')],
    'KY': [('40003', '42788')],
    'LA': [('70001', '71232'), ('71234', '71497')],
    'MA': [('01001', '02791'), ('05501', '05544')],
    'MD': [('20331', '20331'), ('20335', '20797'), ('20812', '21930')],
    'ME': [('03901', '04992')],
    'MI': [('48001', '49971')],
    'MN': [('55001', '56763')],
    'MO': [('63001', '65899')],
    'MS': [('38601', '39776'), ('71233', '71233')],
    'MT': [('59001', '59937')],
    'NC': [('27006', '28909')],
    'ND': [('58001', '58856')],
    'NE': [('68001', '68118'), ('68122', '69367')],
    'NH': [('03031', '03897')],
    'NJ': [('07001', '08989')],
    'NM': [('87001', '88441')],
    'NV': [('88901', '89883')],
    'NY': [('06390', '06390'), ('10001', '14975')],
    'OH': [('43001', '45999')],
    'OK': [('73001', '73199'), ('73401', '74966')],
    'OR': [('97001', '97920')],
    'PA': [('15001', '19640')],
    'RI': [('02801', '02940')],
    'SC': [('29001', '29948')],
    'SD': [('57001', '57799')],
    'TN': [('37010', '38589')],
    'TX': [('73301', '73301'), ('75001', '75501'), ('75503', '79999'), ('88510', '88589')],
    'UT': [('84001', '84784')],
    'VA': [('20040', '20041'), ('20040', '20167'), ('20042', '20042'), ('22001', '24658')],
    'VT': [('05001', '05495'), ('05601', '05907')],
    'WA': [('98001', '99403')],
    'WI': [('53001', '54990')],
    'WV': [('24701', '26886')],
    'WY': [('82001', '83128')]
}