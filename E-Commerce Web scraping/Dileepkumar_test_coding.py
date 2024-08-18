# # Bambus Technology LLC Python Test - Web scrapping -1
# -- -------------------------------------------------------------------------------------------


# #### Importing Necessary Packages

import pandas as pd
import numpy as np
import re
import json
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from urllib import request

import pickle
import time

import seaborn as sns
import plotly.express as px


df = pd.read_excel('input.xlsx')


## Checking Duplicate values

df[df.duplicated()].values[0]

### This link has a duplicated

df[df['Link']=='https://www.mister-sandman.de/products/kaltschaum-topper-doppeltuchbezug-80x200']


# ### Drop the duplicates

df = df.drop_duplicates()


# ### Here we can see there's no duplicates

df[df.duplicated()]


### Getting the links in the lists

links_lists = list(df['Link'].values)


# ### Functions for scrapping the required data from the web pages

def prod_names(soup):

    prod_name_list = []
    try:
        titles = soup.find('h1', class_='product-title')
        if titles != None:
            prod_name = titles.text
            #prod_name_list.append(prod_name)
    except Exception as e:
        #prod_name = ''
        prod_name = ''
    
    return prod_name

def extract_json_data_ean(soup):
    script_tag = soup.find('script', {'type': 'application/json', 'data-section-type': 'static-product'})
    if script_tag:
        try:
            json_data = json.loads(script_tag.string)
            return json_data
        except json.JSONDecodeError:
            print("Error decoding JSON")
            return None
    return None

def sizes(soup):
    chosen_value = ''  # Initialize chosen_value with an empty string

    try:
        sizes = soup.find('select', id='template--20429025378649__main-data-variant-option-0-template--20429025378649__main')

        if sizes != None:
            # Ensure the select element is found
            select_element = soup.find('select', class_='options-selection__input-select')
            #print(type(select_element), len(select_element), select_element)
            
            if select_element:
                # Extract the value of the 'data-variant-option-chosen-value' attribute
                chosen_value = select_element.get('data-variant-option-chosen-value')
                #print(type(select_element), len(select_element), select_element)
        
        else:
            select_element = prod_names(soup).split()[-1]
            chosen_value = select_element
            #print(type(select_element), len(select_element), select_element)
            
    except Exception as e:
        print(f"An error occurred: {e}. Sizes(soup) function.")

    return chosen_value

def vpb_lists(soup):
    
    result = ['', '', '']  # Initialize result with default values
    
    try:
        # Find the price element
        price = soup.find('div', class_='product-pricing').find('div', class_='price__current').find_all('span')
        #print(type(price), len(price))  #, price)
        if price:
            price_text = price[-1].text.strip()
            price_text = price_text.replace(',', '').replace('€', '').strip()
            #print(price_text)
            if price_text.isdigit():  # Check if the price_text is a digit
                price_to_find = int(price_text)
                data1 = extract_json_data_ean(soup)
                # Iterate over the variants and find matching price
                for variant in data1['product']['variants']:
                    if (variant['price'] == price_to_find):
                        #print(sizes(soup))
                        #print(variant['title'])
                        if sizes(soup) in variant['title']:
                            result = [variant['id'], price_to_find, variant['barcode']]
                            break  # Stop iteration once a match is found
                        elif sizes(soup) in data1['product']['title']:
                            result = [variant['id'], price_to_find/100, variant['barcode']]
            else:
                print(f"Non-numeric price found: {price_text}")
                return result  # Return default result if price is not numeric

    except Exception as e:
        print(f"An error occurred: {e}")

    return result

def images_list(soup):
    # Initialize an empty list to store the image URLs
    image_src_links1 = []
    image_src_links2 = []
    
    try:
        # Find all divs with the specified class
        divs = soup.find_all('div', class_='product-gallery--image-background')

        # Iterate over each div
        for div in range(2):
            if div == 0:
                # Find all img tags within the div
                img_tags = divs[div].find_all('img')
                # Iterate over each img tag
                for img in range(1):
                    if 'src' in img_tags[img].attrs:
                        src_url = img_tags[img]['src']
                        #print(src_url)
                        if src_url in image_src_links1:
                            pass
                        else:
                            image_src_links1.append('https:'+src_url)
            else:
                # Find all img tags within the div
                img_tags = divs[div].find_all('img')
                # Iterate over each img tag
                for img in range(1):
                    if 'src' in img_tags[img].attrs:
                        src_url = img_tags[img]['src']
                        if src_url not in image_src_links2:
                            image_src_links2.append('https:'+src_url)
    except Exception as e:
        image_src_links1.append('')
        image_src_links2.append('')
                    
    return image_src_links1[0], image_src_links2[0]


# ### The below codes run and scrape the webpages from the links_lists

if __name__ == '__main__':
    
    # Initialize a requests session with custom headers
    session = requests.Session()
    session.headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        "Accept-Encoding": "*",
        "Connection": "keep-alive"}

    data = {'url':[], 'Product_title': [], 'Variation_id':[], 'Size':[], 'Price':[], 'Ean':[], 'Img1_url':[], 'Img2_url':[]}

    for url in range(len(links_lists)):

        #req = requests.get(links_lists[url])
        req = session.get(links_lists[url])

        #pickle.dump(req, open(f'C:\\Users\\johan\\OneDrive\\Desktop\\DS Python\\Tasks\\Bambus\\Technical assessment\\Test_Coding_implementation\\Test_Coding\\Dump\\requests{url}.pkl', 'wb'))
        #req1 = pickle.load(open(f'C:\\Users\\johan\\OneDrive\\Desktop\\DS Python\\Tasks\\Bambus\\Technical assessment\\Test_Coding_implementation\\Test_Coding\\Dump\\requests{url}.pkl', 'rb'))

        soup = BeautifulSoup(req.text, 'html.parser')

        vpb = vpb_lists(soup)

        images = images_list(soup)

        img1 = images[0]
        img2 = images[1]

        data['url'].append(links_lists[url])
        data['Product_title'].append(prod_names(soup))
        data['Variation_id'].append(vpb[0])
        data['Price'].append(vpb[1])
        data['Ean'].append(vpb[2])
        data['Size'].append(sizes(soup))
        data['Img1_url'].append(img1)
        data['Img2_url'].append(img2)

        # Sleep for a short random time to avoid overloading the server
        time.sleep(2)
        print(url, 'Executed')

final_df = pd.DataFrame(data)


# Get the current date and time
file_name = datetime.now()
# Format the datetime object
formatted_file_name = file_name.strftime("%d.%m.%Y-%H%M%S")

# Conver the dataframe into an excel file
final_df.to_excel(f'Webshop_ProdData_ {formatted_file_name}.xlsx', index=False)

print(f'Webshop_ProdData_ {formatted_file_name}.xlsx File Created')


pd.read_excel('Webshop_ProdData_ 10.07.2024-103205.xlsx')

