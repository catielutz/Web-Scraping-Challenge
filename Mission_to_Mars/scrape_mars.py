# Dependencies
from splinter import Browser
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup as bs
import pandas as pd
import time
import pymongo

def init_browser():
    executable_path = {'executable_path': ChromeDriverManager().install()}
    return Browser("chrome", **executable_path, headless=False)

def scrape():
    #setup connection to mongoDB
    conn = "mongodb://localhost:27017"
    client = pymongo.MongoClient(conn)
    # Select database and collection to use
    db = client.mars_db
    collection = db.mars

    # set destination
    url = 'https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'
    browser = init_browser()
    browser.visit(url)
    time.sleep(1)
    soup = bs(browser.html, 'html.parser')

    # scrape destination
    result = soup.find_all('div', class_='content_title')
    news_title = (result[1].text)

    result_p = soup.find_all('div', class_='article_teaser_body')
    news_p = (result_p[1].text)

    # JPL Mars Space Images - Featured Image

    # visit jpl 
    jpl_url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(jpl_url)

    # create image soup
    jpl_html = browser.html
    image_soup = bs(jpl_html, 'html.parser')

    # find image url
    top_img = image_soup.find('img', class_='headerimage fade-in')['src']

    # append html link to daily image
    featured_image_url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/'+top_img

    browser.quit()

    # Mars Facts
    
    # read the table into a df
    mars_facts = pd.read_html('https://space-facts.com/mars/')[0]
    mars_facts

    # convert the table to an html object
    mars_html = mars_facts.to_html(index=False, header=False)

    # Mars Hemispheres

    # set destination
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    # setup splinter
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=False)
    browser.visit(url)
    time.sleep(1)
    soup = bs(browser.html, 'html.parser')

    # find all hemisphere items, loop through divs to create each hemisphere url and append to a list
    items = soup.find_all('div', class_='item')
    url_list = []
    for i in items:
        img = i.find('a')['href']
        hemi_url = 'https://astrogeology.usgs.gov' + img
        url_list.append(hemi_url)

    # loop through url list and append title & img_url keys to a dictionary
    hemisphere_image_urls = []
    for url in url_list:
        browser.visit(url)
        soup = bs(browser.html, 'html.parser')
        find_pic = soup.find('div', class_='downloads')
        pic_url = find_pic.find('a')["href"]
        find_title = soup.find('div', class_='content')
        title = find_title.find('h2').text
        hemisphere_image_urls.append({"Title": title, "img_url":pic_url})
    
    browser.quit()

    # insert data into dictionary
    data = {
        "article_title": news_title,
        "article_text": news_p,
        "featured_image": featured_image_url,
        "table": mars_html,
        "hemisphere_images": hemisphere_image_urls
    }
    
    return data

