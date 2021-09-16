import time
import unidecode
import csv
import threading
from selenium import webdriver
from datetime import datetime
import sys

path = 'chromedriver.exe'


def scroll_ifortuna(driver):
    """iFortuna Scroller.

    this function helps us scroll down the webpage of iFortuna in order to scrape all of the available data on matches.

    :param driver: selenium driver
    """
    # First, we set the pause time
    SCROLL_PAUSE_TIME = 0.5

    # Second, we get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # then, we scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page using predefined pause time
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height, if equal - stop, if not - keep going
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def scroll_synottip(driver):
    """SynotTip Scroller.

    this function helps us scroll down the webpage of SynotTip to scrape all of the available data on matches.
    Here we need to scroll down an inner element of the page, thus we need a different function from scroll_ifortuna.

    :param driver: selenium driver
    """
    SCROLL_PAUSE_TIME = 1
    content = driver.find_element_by_class_name('content-container')
    content = content.find_element_by_class_name('simplebar-scroll-content')

    # Get scroll height - scrolling element found from inspected page
    rows = driver.find_elements_by_xpath(
        '//div[@data-test-role="event-list__item"]')

    while True:
        # Scroll down to bottom
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", content)

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_rows = driver.find_elements_by_xpath(
            '//div[@data-test-role="event-list__item"]')

        if new_rows == rows:
            break
        rows = new_rows


def scrape(t1, t2, t3, t4):
    """Starts Threads and waits for them to finish

    :param t1: thread 1
    :param t2: thread 2
    :param t3: thread 3
    :param t4: thread 4
    """
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t1.join()
    t2.join()
    t3.join()
    t4.join()


def scrape_tenis():
    """Scrape data on tennis.

    Here we define threads that open individual betting office's webpage with data on tennis.
    Arguments scrape_sport_* used later on to find relevant .csv file and url for scraping correct site
    """
    t1 = threading.Thread(target=scrape_sport_chanceOrTipsport,
                          args=("tenis", "https://www.tipsport.cz/kurzy/tenis-43?limit=500", 'tipsport',))
    t2 = threading.Thread(target=scrape_sport_ifortuna,
                          args=("tenis", "https://www.ifortuna.cz/sazeni/tenis",))
    t3 = threading.Thread(target=scrape_sport_synottip,
                          args=("tenis", "https://sport.synottip.cz/#/zapasy/19?categoryId=19",))
    t4 = threading.Thread(target=scrape_sport_chanceOrTipsport,
                          args=("tenis", "https://www.chance.cz/kurzy/tenis-43?limit=500", 'chance',))

    scrape(t1, t2, t3, t4)


def scrape_voleyball():
    """Scrape data on volleyball

    Here we define threads that open individual betting office's webpage with data on volleyball.
    Arguments scrape_sport_* used later on to find relevant .csv file and url for scraping correct site
    """
    t1 = threading.Thread(target=scrape_sport_chanceOrTipsport,
                          args=("voleyball", "https://www.tipsport.cz/kurzy/volejbal-47?limit=500", 'tipsport',))
    t2 = threading.Thread(target=scrape_sport_ifortuna,
                          args=("voleyball", "https://www.ifortuna.cz/sazeni/volejbal",))
    t3 = threading.Thread(target=scrape_sport_synottip,
                          args=("voleyball", "https://sport.synottip.cz/#/zapasy/23?categoryId=23",))
    t4 = threading.Thread(target=scrape_sport_chanceOrTipsport,
                          args=("voleyball", "https://www.chance.cz/kurzy/volejbal-47?limit=500", 'chance',))
    scrape(t1, t2, t3, t4)


def findDateAndName(element):
    """Finds Date and Name.

    Finds information on Date and Name from a specific element of a webpage. In case date and playtime are stored in
    different elements we need to combine these together and store the information in a specific format.
    In case playtime is not available only date is extracted - does not matter for future matching

    :param element: specific element of a webpage containing data on Date or Name of a specific match
    :return: Date and Name of a specific match
    """
    # unidecode used everytime when name is stored in order to remove diacritics
    name = unidecode.unidecode(element.find_element_by_class_name('o-matchRow__matchName').text)
    dateSpans = element.find_element_by_class_name('o-matchRow__dateClosed').find_elements_by_xpath('span')

    if len(dateSpans) > 1:
        date = element.find_element_by_class_name('o-matchRow__dateClosed').find_elements_by_xpath('span')[0].text
        date = date + ' ' + \
               element.find_element_by_class_name('o-matchRow__dateClosed').find_elements_by_xpath('span')[1].text
        date = datetime.strptime(date, '%d.%m.%Y %H:%M')
    else:
        date = element.find_element_by_class_name('o-matchRow__dateClosed').find_elements_by_xpath('span')[0]
        date = datetime.strptime(date, '%d.%m.%Y')
    return date, name


def findRates(element):
    """Finds offered Rates on matches by iFortuna or Chance webpage.

    Finds information on Rates from a specific element of a webpage. We predefine win-draw-loss (home-draw-away) as
    zeros (including draw for possible future use with different sports including this option)
    in order to detect possible unsuitable observations missing either home or away values. If we find 2 values,
    we assign them to home and away rates, if we find three, we assign them to home, draw and away rates.

    :param element: specific element of a webpage containing data on betting Rates offered for a specific match
    :return: Rates for home, draw and away
    """
    rates = element.find_element_by_class_name('o-matchRow__rightSideInner').find_element_by_class_name(
        'm-matchRowOdds').find_elements_by_class_name('btnRate')

    home = 0
    away = 0
    draw = 0
    if len(rates) == 2:
        home = rates[0].text
        away = rates[1].text
    if len(rates) == 3:
        home = rates[0].text
        draw = rates[1].text
        away = rates[2].text
    return home, draw, away


def saveToCSV(office, sport, matches, driver):
    """Saves scraped data to csv file.

    :param office: betting office
    :param sport: specific sport we scrape data for
    :param matches: array of all scraped matches
    :param driver: selenium driver
    """
    # fill .csv file with the scraped matches (rewrites the existing values in provided datafile with fresh ones)
    with open(office + '/' + sport + '.csv', 'w', newline='', encoding='utf-8') as f:
        write = csv.writer(f)
        write.writerow(['name', 'date', 'home', 'draw', 'away'])
        write.writerows(matches)
    # close chrome driver
    driver.quit()


def scrape_sport_chanceOrTipsport(sport, url, office):
    """Scraper for Chance or Tipsport.

    Scrapes data on Name, Date and Rates for all available matches for a specific sport from aforementioned webpages.
    As these two betting offices have identical webpages, we can use one function to scrape both of them.

    :param sport: specific sport we scrape data for
    :param url: Betting office's webpage
    :param office: Betting office
    """
    # Selenium driver
    driver = webdriver.Chrome(path)
    # empty field with matches that I will save to csv when filled with data
    matches = []
    # driver gets url where to scrape from
    driver.get(url)
    # 3s break to ensure Chrome had enough time to start
    time.sleep(3)
    # fid rows with matches
    rows = driver.find_elements_by_class_name('o-matchRow__main')

    # And for each of these rows:
    for row in rows:
        # looking for match Name and date (playtime)
        date, name = findDateAndName(row.find_element_by_class_name('o-matchRow__leftSide'))
        home, draw, away = findRates(row.find_element_by_class_name('o-matchRow__rightSide'))
        # if home or away was not found, dont append the observation
        if home != 0 and away != 0:
            matches.append([name, date, home, draw, away])

    saveToCSV(office, sport, matches, driver)


def findRates_synottip(odds):
    """Finds offered Rates on matches by SynotTip.

    Finds information on Rates from a specific element of a webpage. We predefine win-draw-loss (home-draw-away) as
    zeros (including draw for possible future use with different sports including this option)
    in order to detect possible unsuitable observations missing either home or away values. If we find 2 values,
    we assign them to home and away rates, if we find three, we assign them to home, draw and away rates.

    :param odds: scraped data on Rates from SynotTip webpage
    :return: Rates for home, draw and away
    """
    home = 0
    away = 0
    draw = 0
    odds1 = odds[0].text
    odds1 = float(odds1.replace(",", "."))
    odds2 = odds[1].text
    odds2 = float(odds2.replace(",", "."))
    if len(odds) == 2:
        home = odds1
        away = odds2
    if len(odds) == 3:
        home = odds1
        draw = odds2
        odds3 = odds[2].text
        odds3 = float(odds3.replace(",", "."))
        away = odds3
    return home, draw, away


def scrape_sport_synottip(sport, url):
    """Scraper for SynotTip webpage.

    Scrapes data on Name, Date and Rates for all available matches for a specific sport from SynotTip's webpages.

    :param sport: specific sport we scrape data for
    :param url: Betting office's webpage
    """
    driver = webdriver.Chrome(path)
    matches = []
    driver.get(url)
    time.sleep(3)
    scroll_synottip(driver)
    rows = driver.find_elements_by_xpath(
        '//div[@data-test-role="event-list__item"]')

    for row in rows:
        odds = row.find_elements_by_class_name('rate')
        name = unidecode.unidecode(row.find_element_by_class_name('match-label').text)
        if len(odds) > 1:
            try:
                # here we need to edit existing strings in order to reformat as float due to different float formatting
                date = row.find_element_by_class_name('v-center').text.replace('\n', ' ')
                date = datetime.strptime(date, '%d.%m.%y %H:%M')
            except:
                continue
            home, draw, away = findRates_synottip(odds)
            if home != 0 and away != 0:
                matches.append([name, date, home, draw, away])

    saveToCSV('synottip', sport, matches, driver)


def findRates_ifortuna(rates):
    """Finds offered Rates on matches by iFortuna.

    Finds information on Rates from a specific element of a webpage. We predefine win-draw-loss (home-draw-away) as
    zeros (including draw for possible future use with different sports including this option)
    in order to detect possible unsuitable observations missing either home or away values. If we find 2 values, we assign
    them to home and away rates, if we find three, we assign them to home, draw and away rates.

    :param rates:
    :return: Rates for home, draw and away
    """
    home = 0
    draw = 0
    away = 0
    if len(rates) == 2:
        home = rates[0].text
        away = rates[1].text
    if len(rates) >= 3:
        home = rates[0].text
        draw = rates[1].text
        away = rates[2].text
    return home, draw, away


# same as above, except for using different scroller
def scrape_sport_ifortuna(sport, url):
    """Scraper for iFortuna's webpage.

    Scrapes data on Name, Date and Rates for all available matches for a specific sport from iFortuna's webpages.

    :param sport: specific sport we scrape data for
    :param url: Betting office's webpage
    """
    driver = webdriver.Chrome(path)
    matches = []
    driver.get(url)
    time.sleep(3)
    scroll_ifortuna(driver)
    rows = driver.find_elements_by_xpath("//table/tbody/tr")
    for row in rows:
        try:
            name = row.find_element_by_class_name('col-title').text
            date = datetime.fromtimestamp(
                float(row.find_element_by_class_name('col-date').get_attribute("data-value")) / 1000)
            home, draw, away = findRates_ifortuna(row.find_elements_by_class_name('col-odds'))
            matches.append([name, date, home, draw, away])
        except:
            continue

    if len(matches) > 0:
        saveToCSV('ifortuna', sport, matches, driver)


try:
    if sys.argv[1] == 'tenis':
        scrape_tenis()
    elif sys.argv[1] == 'voleyball':
        scrape_voleyball()
    elif sys.argv[1] == 'all':
        scrape_tenis()
        scrape_voleyball()
    else:
        print('Argument is invalid. Choose from "tenis","voleyball" and "all"')
except:
    print('Argument is missing or invalid. Choose from "tenis","voleyball" and "all"')
