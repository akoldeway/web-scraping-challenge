from splinter import Browser
from bs4 import BeautifulSoup
from time import sleep
import pandas as pd


# dictionary to hold all the things we need to scrape for
mars_data ={}

def init_browser():
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)


# main scraping method that will scrape all the invidual bits we need
def scrape_info():
    browser = init_browser()

    # # scrape article
    scrape_article(browser)

    # scrape image
    scrape_image(browser)

    # scrape_weather
    scrape_weather(browser)

    #scrape_facts
    scrape_facts(browser)

    #scrape hemisphere data
    scrape_hemispheres(browser)

    # close browser
    browser.quit()

    return mars_data


# Scrape NASA for latest Mars article
def scrape_article(browser):
    url = 'https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'
    browser.visit(url)  

    # sleep a second to let the dang page load
    sleep(2)

    # parse with beautiful soup
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    # get the latest article (first on the page)
    article = soup.find('li', class_='slide')

    # pull news title and news teaster paragraph from article
    news_title = article.find('div', class_='content_title').a.text
    news_p = article.find('div', class_='article_teaser_body').text

    # add news title and paragraph to dictionary
    mars_data['news_title'] = news_title
    mars_data['news_paragraph'] = news_p

# Scrape JPL to get latest Mars image
def scrape_image(browser):
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    url_root = 'https://www.jpl.nasa.gov'

    # sleep a second to let the dang page load
    sleep(2)

    # parse with beautiful soup
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    # have splinter cick the Full Image button
    full_image_button = browser.find_by_id("full_image")
    full_image_button.click()

    # sleep a second to let the dang page load
    sleep(2)

    # have splinter find the More Info button and click it
    more_info_element = browser.find_link_by_partial_text("more info")
    more_info_element.click()

    # sleep a second to let the dang page load
    sleep(2)

    # parse with beautiful soup
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    url_img = soup.find('figure', class_='lede').a['href']
    feature_img_url = f'{url_root}{url_img}'

    # add feature image url to dictionary
    mars_data['feature_img_url'] = feature_img_url


# Get Mars Weather from tweet
def scrape_weather(browser):
    url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(url)

    # sleep a second to let the dang page load
    sleep(2)

    # parse with beautiful soup
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    # get first tweet as it's most recent
    tweet = soup.find('p', class_='tweet-text')

    # tweet has p tage with weather info and anchor tag inside text of p tag.
    # let's use the the strings method to grab just the first string
    mars_weather = list(tweet.strings)[0]

    # add to dictionary
    mars_data['mars_weather'] = mars_weather


# Get Mars Facts
def scrape_facts(browser):
    url = 'https://space-facts.com/mars/'
    browser.visit(url)

    # sleep a second to let the dang page load
    sleep(2)

    # use the pandas read html method to scrape page for all tables
    tables = pd.read_html(url)

    # the second table has the info we want. let's stick it into a dataframe and format all pretty
    columns = ['Description', 'Value']
    tables[1].columns = columns
    mars_facts_html = tables[1].to_html(index=False)
    
    # add to dictionary
    mars_data['mars_facts_html'] = mars_facts_html

# Get Mars Hemisphere Images
def scrape_hemispheres(browser):
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    # sleep a second to let the dang page load
    sleep(2)

    # create list to hold on to stuff
    hemisphere_image_urls = []

    # get list of thumbnails to loop through
    img_thumbnails = browser.find_by_css('img[class="thumb"]')

    index = 0
    # loop through thumbnails using index so the links don't get stale when flipping back
    while index < len(img_thumbnails):
        # get thumbnail
        img_thumbnail = browser.find_by_css('img[class="thumb"]')[index]
    
        # click link
        img_thumbnail.click()
    
        # let the dang page load
        sleep(1)
    
        # parse with beautiful soup
        html = browser.html
        soup = BeautifulSoup(html, 'html.parser')
    
        # get the image url & title
        img_url = soup.find('a', text='Sample')['href']
        title = soup.find('h2').text
    
        # create dictionary and add to list
        hemi_dict = {}
        hemi_dict['title'] = title.replace('Enhanced', '')
        hemi_dict['img_url'] = img_url
        hemisphere_image_urls.append(hemi_dict)
    
        # increment index
        index +=1
    
        # have browser go back a page to get back to list
        browser.back()
        
        # wait a second to load the page
        sleep(1)
    
    # add to dictionary
    mars_data['hemisphere_image_urls'] = hemisphere_image_urls

if __name__ == "__main__":
    scrape_info()
    print(mars_data)

