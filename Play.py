#import libraries
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from time import sleep

# not needed
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC


#page list
# the ones with reviews are ->
all_page_ids = ["com.ubs.mobilepass", "com.ubs.swidK2Y.android",
                "com.ubs.swidKXJ.android", "com.ubs.Paymit.android",]

all_pages = ["https://play.google.com/store/apps/details?id=" +
             page_id for page_id in all_page_ids]


# set up webdriver - global variable
options = webdriver.ChromeOptions()
options.add_argument('--headless')

# Initialize the webdriver with the options
driver = webdriver.Chrome(options=options)


#helper functions 


# scrapes reviews of the modal
def scrape_reviews(n_scroll):
    fBody = driver.find_element("xpath", "//div[@jsname='bN97Pc']")

    # scroll through page
    for i in range(n_scroll):
        driver.execute_script(
            'arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;', fBody)
    #     temp = WebDriverWait(driver, 3).until(EC.invisibility_of_element_located(("xpath", "//*[name()='svg' and @aria-label='Loading...']")))

    # extract all reviews
    all_reviews = driver.find_elements(
        "xpath", "//div[contains(@class,'RHo1pe')]")
    all_star_ratings = fBody.find_elements(
        "xpath", "//div[@class='iXRFPc']")[3:]

    # output formatting
    all_descriptions = []
    all_dates = []
    all_stars = []

    for review in all_reviews:
        rev = review.text.split('\n')
        all_dates.append(rev[2])
        all_descriptions.append(rev[3])

    for rating in all_star_ratings:
        all_stars.append(int(rating.get_attribute('ariaLabel')[6]))

    return {'Verbatim': all_descriptions, 'Dates': all_dates, 'Stars': all_stars}


# scrapes all reviews of a page
def scrape(link):

    driver.get(link) #driver is global variable
    sleep(3) #forced for smoother page loading
    # ratings modal

    headers = driver.find_elements("xpath", "//header[@class=' cswwxf']")
    ratings_modal = []
    for header in headers:
        if "Ratings and reviews" in header.text:
            ratings_modal = header.find_elements(
                "xpath", "//button[contains(@class,'VfPpkd-Bz112c-LgbsSe yHy1rc eT1oJ QDwDD mN1ivc VxpoF')]")
    
    if ratings_modal == []:
        return '' #no reviews - checked only once cause if no phone reviews then there won't be any tablet reviews

    # number of reviews
    n_reviews = driver.find_element(
        "xpath", "//div[contains(@class,'EHUI5b')]").text[:-8]
    if 'K' in n_reviews:
        n_reviews = float(n_reviews[:-1]) * 1000
    n_scroll = int(n_reviews)//3  # if int(n_reviews) <=500 else 250

    # enter modal
    ratings_modal[1].click()

    # scrape reviews
    all_reviews_dict = scrape_reviews(n_scroll)
    # serial number added separately for easier merge with tablet reviews
    all_reviews_dict['S/N'] = [i for i in range(
        1, len(all_reviews_dict['Verbatim'])+1)]

    df = pd.DataFrame(data=all_reviews_dict)[['S/N', 'Verbatim', 'Dates', 'Stars']]
    df.to_csv('data/'+link[54:]+'_phone.csv', index=False)


    #close modal
    driver.find_element("xpath", "//button[@aria-label='Close about app dialog']").click()
    sleep(2)

    # multiple devices - tablet
    # note - mutiple devices means phone + tablet. Banking apps don't keep pc version. Hence the hardcoding to check element once instead of going through entire dropdown list
    tablet = driver.find_elements("xpath", "//div[@aria-label='Tablet']")
    if len(tablet)>0:
        tablet[0].click()
        tablet[0].click()
        sleep(2) #wait for page to load

        # number of reviews
        n_reviews = driver.find_element(
            "xpath", "//div[contains(@class,'EHUI5b')]").text[:-8]
        if 'K' in n_reviews:
            n_reviews = float(n_reviews[:-1]) * 1000
        n_scroll = int(n_reviews)//3  # if int(n_reviews) <=500 else 250

        # enter modal
        ratings_modal[1].click()


        # scrape reviews - add tag tablet or append to current reviews
        all_reviews_dict = scrape_reviews(n_scroll)
        all_reviews_dict['S/N'] = [i for i in range(
            1, len(all_reviews_dict['Verbatim'])+1)]

        df = pd.DataFrame(data=all_reviews_dict)[['S/N', 'Verbatim', 'Dates', 'Stars']]
        df.to_csv('data/'+link[54:]+'_tablet.csv', index=False)


#main function 
def run():
    for link in all_pages: #all_pages is global
        scrape(link)


if __name__ == "__main__":
    run()
    driver.quit()