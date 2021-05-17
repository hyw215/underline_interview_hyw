import pandas as pd
import os


module_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

def get_census():
	file = 'ACSST5Y2019.S2801_data_with_overlays_2021-05-09T161516.csv'
	path = os.path.join(module_path,'abq_analyze', 'abq_counties_internet_sub', file)
	census_internet = pd.read_csv(path, skiprows=0)
	census_internet = census_internet.drop(index=0)
	return census_internet

def get_mapping():
	file = 'ACSST5Y2019.S2801_metadata_2021-05-09T161516.csv'
	path = os.path.join(module_path,'abq_analyze', 'abq_counties_internet_sub', file)
	mapping = pd.read_csv(path, dtype='str', header=None)
	mapping = mapping.set_index(0).to_dict()[1]
	return mapping


def abq_internet_data_county_level():
	census_internet = get_census()
	mapping = get_mapping()
	# only keep columns related to household estimates of income
	col = ['GEO_ID', 'NAME', 
			'S2801_C02_019E', 'S2801_C02_014E', 'S2801_C02_013E',
			'S2801_C02_021E', 'S2801_C02_022E', 'S2801_C02_023E', 
			'S2801_C02_025E', 'S2801_C02_026E', 'S2801_C02_027E',
			'S2801_C02_029E', 'S2801_C02_030E', 'S2801_C02_031E'
	]
	census_internet[col[2:]] = census_internet[col[2:]].apply(pd.to_numeric, errors='coerce')
	census_internet = census_internet[col].rename(columns=mapping)
	census_internet_dict = census_internet.set_index('Geographic Area Name').to_dict()
	
	return census_internet_dict