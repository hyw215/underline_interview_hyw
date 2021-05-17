from bs4 import BeautifulSoup as bs
import requests
import json
import re



def scrape_site():
    url = 'https://abqlibrary.org/hours-locations'
    r = requests.get(url)
    soup = bs(r.content, features='html.parser')
    return soup

def extract_library_locations(soup):
    lib_data = []
    lib_html_info = soup.find_all('td', {'class','location'})
    pattern_regex = re.compile("\\n\\t\\t\\t.*?\\n\\t\\t\\t")
    for i in lib_html_info:
        lib_name = (i.find_all('a')[1]['title'])
        location = pattern_regex.search(i.text).group()
        location = location.replace('\t', '').replace('\n', '')
        lib = (lib_name, location)
        lib_data.append(lib)
        
    return lib_data

def get_library():
    soup = scrape_site()
    lib_data = extract_library_locations(soup)
    return lib_data
    
if __name__ == '__main__':
    lib_data = get_library()
    print(lib_data)