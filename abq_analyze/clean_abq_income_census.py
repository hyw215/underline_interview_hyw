import pandas as pd
import os

module_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

def get_census():
	path = 'ACSST5Y2019.S1901_data_with_overlays_2021-05-10T204117.csv'
	path_full = os.path.join(module_path,'abq_analyze', 'income_census_tract_data', path)
	census_income = pd.read_csv(path_full, skiprows=0)
	census_income = census_income.drop(index=0)
	return census_income

def get_mapping():
	path = 'ACSST5Y2019.S1901_metadata_2021-05-10T204117.csv'
	path_full = os.path.join(module_path,'abq_analyze', 'income_census_tract_data', path)
	mapping = pd.read_csv(path_full, dtype='str', header=None)
	mapping = mapping.set_index(0).to_dict()[1]
	return mapping

def consolidate_low_income_ranges(row):
	percent = (row['Estimate!!Households!!Total!!Less than $10,000'] 
				+ row['Estimate!!Households!!Total!!$10,000 to $14,999']
				+(row['Estimate!!Households!!Total!!$15,000 to $24,999']/2)
				)
	percent = percent/100
	total_households = percent * row['Estimate!!Households!!Total']
	return total_households

def consolidate_mid_income_ranges(row):
	percent = ((row['Estimate!!Households!!Total!!$15,000 to $24,999']/2)
				+row['Estimate!!Households!!Total!!$25,000 to $34,999']
				+row['Estimate!!Households!!Total!!$35,000 to $49,999']
				+row['Estimate!!Households!!Total!!$50,000 to $74,999']
				)
	percent = percent/100
	total_households = percent * row['Estimate!!Households!!Total']
	return total_households

def consolidate_high_income_ranges(row):
	percent = (row['Estimate!!Households!!Total!!$75,000 to $99,999']
				+row['Estimate!!Households!!Total!!$100,000 to $149,999']
				+row['Estimate!!Households!!Total!!$150,000 to $199,999']
				+row['Estimate!!Households!!Total!!$200,000 or more']
				)
	percent = percent/100
	total_households = percent * row['Estimate!!Households!!Total']
	return total_households

def clean_income(census_income, mapping):
	# only keep columns related to household estimates of income
	col = ['GEO_ID', 'NAME', 'S1901_C01_001E', 'S1901_C01_002E', 
			'S1901_C01_003E', 'S1901_C01_004E','S1901_C01_005E', 
			'S1901_C01_006E', 'S1901_C01_007E', 'S1901_C01_008E', 
			'S1901_C01_009E', 'S1901_C01_010E', 'S1901_C01_011E']
	census_income[col[2:]] = census_income[col[2:]].apply(pd.to_numeric, errors='coerce')
	census_income = census_income[col].rename(columns=mapping)

	census_income['Income Less than 20,000'] = census_income.apply(lambda x: consolidate_low_income_ranges(x), axis=1)
	census_income['Income 20,000 to 74,999'] = census_income.apply(lambda x: consolidate_mid_income_ranges(x), axis=1)
	census_income['Income 75,000 or more'] = census_income.apply(lambda x: consolidate_mid_income_ranges(x), axis=1)
	census_income['County'] = census_income['Geographic Area Name'].str.split(',').str[1:].str.join(',').str.strip(' ')
	census_income = census_income[['id', 'Geographic Area Name','County', 'Income Less than 20,000', 'Income 20,000 to 74,999', 'Income 75,000 or more']]
	return census_income

def income_tract_breakdown():
	mapping = get_mapping()
	income_by_tract = get_census()
	income_by_tract = clean_income(income_by_tract, mapping)
	return income_by_tract
