import pandas as pd
import sys
import os
module_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.join(module_path,'abq_analyze'))

import clean_abq_internet_census as abq_internet
import clean_abq_income_census as abq_income

import importlib
importlib.reload(abq_internet)
importlib.reload(abq_income)

def estimate_internet_stats(row, mapping, data_type='dial_up'):
	
	if data_type=='dial_up':
		low_est = 'Estimate!!Percent!!Total households!!HOUSEHOLD INCOME IN THE PAST 12 MONTHS (IN 2019 INFLATION-ADJUSTED DOLLARS)!!Less than $20,000:!!With dial-up Internet subscription alone' 
		mid_est = 'Estimate!!Percent!!Total households!!HOUSEHOLD INCOME IN THE PAST 12 MONTHS (IN 2019 INFLATION-ADJUSTED DOLLARS)!!$20,000 to $74,999:!!With dial-up Internet subscription alone'
		high_est ='Estimate!!Percent!!Total households!!HOUSEHOLD INCOME IN THE PAST 12 MONTHS (IN 2019 INFLATION-ADJUSTED DOLLARS)!!$75,000 or more:!!With dial-up Internet subscription alone'

	if data_type=='broadband':
		low_est = 'Estimate!!Percent!!Total households!!HOUSEHOLD INCOME IN THE PAST 12 MONTHS (IN 2019 INFLATION-ADJUSTED DOLLARS)!!Less than $20,000:!!With a broadband Internet subscription'
		mid_est = 'Estimate!!Percent!!Total households!!HOUSEHOLD INCOME IN THE PAST 12 MONTHS (IN 2019 INFLATION-ADJUSTED DOLLARS)!!$20,000 to $74,999:!!With a broadband Internet subscription'
		high_est= 'Estimate!!Percent!!Total households!!HOUSEHOLD INCOME IN THE PAST 12 MONTHS (IN 2019 INFLATION-ADJUSTED DOLLARS)!!$75,000 or more:!!With a broadband Internet subscription'
	
	if data_type=='without_internet':
		low_est = 'Estimate!!Percent!!Total households!!HOUSEHOLD INCOME IN THE PAST 12 MONTHS (IN 2019 INFLATION-ADJUSTED DOLLARS)!!Less than $20,000:!!Without an Internet subscription'
		mid_est = 'Estimate!!Percent!!Total households!!HOUSEHOLD INCOME IN THE PAST 12 MONTHS (IN 2019 INFLATION-ADJUSTED DOLLARS)!!$20,000 to $74,999:!!Without an Internet subscription'
		high_est = 'Estimate!!Percent!!Total households!!HOUSEHOLD INCOME IN THE PAST 12 MONTHS (IN 2019 INFLATION-ADJUSTED DOLLARS)!!$75,000 or more:!!Without an Internet subscription'

	mapping
	county = row['County']
	low_pop = row['Income Less than 20,000'] * (mapping.get(low_est).get(county) /100)
	mid_pop = row['Income 20,000 to 74,999'] * (mapping.get(mid_est).get(county) /100)
	high_pop = row['Income 75,000 or more'] * (mapping.get(high_est).get(county) /100)

	return low_pop+mid_pop+high_pop

def abq_tract_internet_analysis():
	income_by_tract = abq_income.income_tract_breakdown()
	abq_internet_data = abq_internet.abq_internet_data_county_level()
	income_by_tract['Total Households'] = income_by_tract['Income Less than 20,000'] + income_by_tract['Income 20,000 to 74,999'] + income_by_tract['Income 75,000 or more']

	# apply county level data for internet sub stats to tract income data to estimate internet data on tract level 
	income_by_tract['With dial-up Internet subscription alone'] = income_by_tract.apply(lambda x: estimate_internet_stats(x, abq_internet_data, data_type='dial_up'), axis=1)
	income_by_tract['With a broadband Internet subscription'] = income_by_tract.apply(lambda x: estimate_internet_stats(x, abq_internet_data, data_type='broadband'), axis=1)
	income_by_tract['Without an Internet subscription'] = income_by_tract.apply(lambda x: estimate_internet_stats(x, abq_internet_data, data_type='without_internet'), axis=1)
	
	# get percent of households
	income_by_tract['With dial-up Internet subscription alone PERCENT'] = income_by_tract['With dial-up Internet subscription alone']/income_by_tract['Total Households']
	income_by_tract['With a broadband Internet subscription PERCENT'] = income_by_tract['With a broadband Internet subscription']/income_by_tract['Total Households']
	income_by_tract['Without an Internet subscription PERCENT'] = income_by_tract['Without an Internet subscription']/income_by_tract['Total Households']

	#get us averages
	US_without_internet = abq_internet_data['Estimate!!Percent!!Total households!!TYPE OF INTERNET SUBSCRIPTIONS!!Without an Internet subscription']['United States'] /100
	US_broadbnad = abq_internet_data['Estimate!!Percent!!Total households!!TYPE OF INTERNET SUBSCRIPTIONS!!With an Internet subscription:!!Broadband of any type']['United States'] /100
	US_dialup = abq_internet_data['Estimate!!Percent!!Total households!!TYPE OF INTERNET SUBSCRIPTIONS!!With an Internet subscription:!!Dial-up with no other type of Internet subscription']['United States'] /100

	income_by_tract['Better than US average - With dial-up Internet subscription alone'] = (income_by_tract['With dial-up Internet subscription alone PERCENT'] - US_dialup)/US_dialup
	income_by_tract['Better than US average - With a broadband Internet subscription'] = (income_by_tract['With a broadband Internet subscription PERCENT'] - US_broadbnad)/US_broadbnad
	income_by_tract['Better than US average - Without an Internet subscription'] = (US_without_internet - income_by_tract['Without an Internet subscription PERCENT'])/US_without_internet

	# Seperate id to get geo id
	income_by_tract['GEOID'] = income_by_tract['id'].str.split('US').str[1]

	#remove income data
	remove_list = ['Income Less than 20,000','Income 20,000 to 74,999', 'Income 75,000 or more']
	income_by_tract = income_by_tract.drop(columns=remove_list)

	return income_by_tract