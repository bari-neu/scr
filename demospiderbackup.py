import re
import numpy as np
import sqlite3
import datetime
import time
import schedule
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

def init_driver():
    driver = webdriver.Firefox()
    driver.wait = WebDriverWait(driver, 5)
    return driver
def istag(tag, foo):
    if (re.search(tag, foo) != None):
        result = True
    else:
        result = False
    return result
def find_brs(size):
    #this method finds the number of bathrooms
    split = size.strip('/- ').split(' - ')
    if len(split) == 2:
        n_brs = split[0].replace('br', '')
        this_size = split[1].replace('ft2', '')
    elif 'br' in split[0]:
        # It's the n_bedrooms
        n_brs = split[0].replace('br', '')
        this_size = np.nan
    elif 'ft2' in split[0]:
        # It's the size
        this_size = split[0].replace('ft2', '')
        n_brs = np.nan
    else:
        n_brs = 0
    return float(n_brs)
def scrapeit():
    driver = init_driver()
    start = time.time()
    page = 0;
    string = "?s="
    url4 = 'http://boston.craigslist.org/search/jjj'
    url_base = 'http://boston.craigslist.org/search/hhh'
    url2 = 'http://boston.craigslist.org'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    #The headers were from before I used selenium, I should probably remove them
    conn = sqlite3.connect('housingthing.db')
    c = conn.cursor()
    x = 0
    count = 0
    page = 0
    repeat = 0
    while (page <= 2300 & repeat < 10):
        if (page == 0):
            done = 0
            while (done == 0):
                try:
                    driver.get(url_base)
                    done = 1
                except:
                    #if the page hasn't loaded yet, it waits 20 seonds and tries again
                    time.sleep(20)
        else:
            newurl = url_base+ string+ str(page)
            done = 0
            while (done == 0):
                try:
                    driver.get(newurl)
                    done = 1
                except:
                    #see previous comment
                    time.sleep(20)
        pageno=0

        apts = driver.find_elements_by_class_name('result-info')
        i = 0
        while i < len(apts):
            skip = 0
            print ("apt number " + str(i))
            try:
                #finding the neighborhood
                hood = driver.find_elements_by_class_name('result-hood')[i].text
            except IndexError:
                hood = "None"
            print(i)
            time.sleep(10)
            address2 = driver.find_elements_by_class_name('result-title')[i].get_attribute('href')
            #print(address)
            #address2 = driver.find_element_by_partial_link_text(address).get_attribute('href')
            print(address2)
            done = 0
            while (done == 0):
                try:
                    driver.get(address2)
                    done = 1
                except:
                    time.sleep(20)
            try:
                #finding the latitude and longitude
                lata = driver.find_elements_by_class_name('viewposting')[0]
                lat = lata.get_attribute('data-latitude')
                long = lata.get_attribute('data-longitude')
                print(lat)
                print(long)
            except IndexError:
                lat = 0
                long = 0
            timea = driver.find_elements_by_class_name('timeago')
            try:
                timeb = timea[0].get_attribute('datetime')
                #finding when the entry was posted
            except:
               timeb = "Unknown"
            try:
                #finding the page title
                title = driver.find_element_by_tag_name('title').text
            except AttributeError:
                title = "error, can't find title"
            try:
                housing=driver.find_element_by_class_name('housing').text
            except:
                housing='Error, no info'
            bedrooms = find_brs (housing)
            try:
               price = driver.find_element_by_class_name('price').text.strip('$')
            except:
               skip = 1
            #print(html2.prettify())
            try:
                #finding the various tags
                foo = driver.find_elements_by_class_name('attrgroup')[1].text
                #print(foo)
                cats = istag("cats", foo)
                dogs = istag("dogs", foo)
                privroom = istag("private room", foo)
                privbath = istag("private bath", foo)
                nosmoke = istag("smoking", foo)
                furnished = istag("furnished", foo)
                wheelchair = istag("wheelchair", foo)
                if (istag("apartment", foo)):
                    house = "apartment"
                elif(istag("condo", foo)):
                    house = "condo"
                elif (istag("cottage", foo)):
                    house = "cottage"
                elif (istag("duplex", foo)):
                    house = "duplex"
                elif (istag("flat", foo)):
                    house = "flat"
                elif (istag("in-law", foo)):
                    house = "in-law"
                elif (istag("loft", foo)):
                    house = "loft"
                elif (istag("townhouse", foo)):
                    house = "townhouse"
                elif (istag("manufactured", foo)):
                    house = "manufactured"
                elif (istag("assisted living", foo)):
                    house = "assisted living"
                elif (istag("land", foo)):
                    house = "land"
                elif (istag("house", foo)):
                    house = "house"
                else:
                    house = "unknown"
                if (istag("w/d in unit", foo)):
                    washer = "w/d in unit"
                elif(istag("w/d hookups", foo)):
                    washer = "w/d hookups"
                elif (istag("laundry in bldg", foo)):
                    washer = "laundry in bldg"
                elif (istag("laundry on site", foo)):
                    washer = "laundry on site"
                elif (istag("no laundry on site", foo)):
                    washer = "no laundry on site"
                else:
                    washer = "unknown"
                if (istag("carport", foo)):
                    park = "carport"
                elif(istag("attached garage", foo)):
                    park = "attached garage"
                elif (istag("detached garage", foo)):
                    park = "detached garage"
                elif (istag("off-street parking", foo)):
                    park = "off-street parking"
                elif (istag("street parking", foo)):
                    park = "street parking"
                elif (istag("valet parking", foo)):
                    park = "valet parking"
                elif (istag("no parking", foo)):
                    park = "no parking"
                else:
                    park = "unknown"
            except IndexError:
                print("Error, no info")
                cats = False
                dogs = False
                privroom = False
                privbath = False
                nosmoke = False
                furnished = False
                wheelchair = False
                park = "unknown"
                washer = "unknown"
                house = "unknown"
            #print(html2)
            #print(title)
            #print(price)
            #print(bedrooms)
            #print(lat)
            #print(long)
            #print(time)
            #print(hood)
            if (skip == 0):
                print(str(datetime.datetime.now().time()))
                values = (title, price, bedrooms, lat, long, timeb, hood, cats, dogs, wheelchair, nosmoke, privroom, privbath, furnished,  park, house, washer)
                try:
                    #submitting it to SQL
                    c.execute("INSERT INTO housing (Source, Title, Price, Bedrooms, Lat, Long, Time, Hood, cats, dogs, wheelchair, nosmoke, privateroom, privatebath, furnished, parking, house, washer) VALUES ('Craigslist',?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", values)
                    x=0

                    count = count+1
                except sqlite3.IntegrityError:
                    print ("Duplicate found")
                    reapeat = repeat+1
                conn.commit()
            #i=101
            i=i+1
            driver.execute_script("window.history.go(-1)")


        if (x == 5):
            page = 2600
        page = page+100
    page = 0
    print("done")
    end = time.time()
    print(end - start)
    repeat = 0
    while (page <= 2400 & repeat < 20):
        if (page == 0):
            done = 0
            while (done == 0):
                try:
                    driver.get(url4)
                    done = 1
                except:
                    time.sleep(20)
        else:
            newurl = url4 + string + str(page)
            done = 0
            while (done == 0):
                try:
                    driver.get(newurl)
                    done = 1
                except:
                    time.sleep(20)
        jobs = driver.find_elements_by_class_name('result-info')
        x = 0
        #print (len(jobs))
        while (x < len(jobs)):
            skip = 0
            #print("job number "+ str(x))
            this_job = jobs[x]
            try:
                hood = driver.find_elements_by_class_name('result-hood')[x].text
            except IndexError:
                hood = "None"
            address = driver.find_elements_by_class_name('result-info')
            time.sleep(10)
            url3 = driver.find_elements_by_class_name('result-title')[x].get_attribute('href')
            print(url3)
            done = 0
            while(done == 0):
                try:
                    driver.get(url3)
                    done = 1
                except:
                    time.sleep(20)
            #print(html2.prettify())
            time.sleep(10)
            try:
                lata = driver.find_elements_by_class_name('viewposting')[0]
                lat = lata.get_attribute('data-latitude')
                long = lata.get_attribute('data-longitude')
            except IndexError:
                lat = 0
                long = 0

            try:
                title = driver.find_element_by_tag_name('title').text
                print(title)
            except AttributeError:
                title = "error, can't find title"
            try:
                foo = driver.find_element_by_class_name('attrgroup').text
                print(foo)
                if (re.search("part-time", foo) != None):
                    jobtype = "part-time"
                elif (re.search("contract", foo) != None):
                    jobtype = "contract"
                elif (re.search("full-time", foo) != None):
                    jobtype = "full-time"
                else:
                    jobtype = "employee's choice"
                foo2 = driver.find_element_by_class_name('attrgroup').text
                compensation = foo2.split(': ')[1]
                comp2 = compensation.split('\n')[0]
                print("compensation is")
                print (comp2)
            except IndexError:
                print("Error, no info")
                jobtype="Unknown"
                compensation = "Unknown"
            timea = driver.find_elements_by_class_name('timeago')
            try:
                timeb = timea[0].get_attribute('datetime')
            except:
                timeb = "Unknown"
            if (skip == 0):
                print(str(datetime.datetime.now().time()))
                values = (title, lat, long, jobtype, hood, timeb, compensation)
                try:
                    c.execute("INSERT INTO jobs (Source, Title, lat, long, type, Hood, Time, pay) VALUES ('Craigslist',?,?,?,?,?,?,?)", values)

                except sqlite3.IntegrityError:
                    print ("Duplicate found")
                    repeat = repeat+1
                conn.commit()
            x=x+1
            #x=101
            driver.execute_script("window.history.go(-1)")
        page = page+100

#this code is for scheduling the program to run at specific intervals, in case the server doesn't do that.
#schedule.every().day.at("22:01").do(scrapeit)

#while True:
#    schedule.run_pending()
#    time.sleep(60)
scrapeit()