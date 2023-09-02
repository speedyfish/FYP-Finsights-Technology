#import libraries
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
# not needed
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import pandas as pd



#page list
all_page_ids = ["com.ubs.swidK2Y.android",
                "com.ubs.clientmobile",
                "com.ubs.swidKXJ.android",
                "com.ubs.mobilepass",
                "com.ubs.Paymit.android",
                "com.ubs.wm.circleone",
                "com.ubs.neo",
                "com.ubs.myday",
                "com.ubs.prod.intune.myhubmobile",
                "com.ubs.wm.je2.ebanking",
                "com.ubs.neo.fx"]

# the ones with reviews are ->
# all_page_ids = ["com.ubs.swidK2Y.android", "com.ubs.swidKXJ.android", "com.ubs.mobilepass", "com.ubs.Paymit.android"]

all_pages = ["https://play.google.com/store/apps/details?id=" +
             page_id for page_id in all_page_ids]


#set up webdriver - global variable
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                          options=webdriver.ChromeOptions())



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

    # output formatting
    all_descriptions = []
    all_dates = []

    for review in all_reviews:
        rev = review.text.split('\n')
        all_dates.append(rev[2])
        all_descriptions.append(rev[3])

    return {'Verbatim': all_descriptions, 'Dates': all_dates}


# scrapes all reviews of a page
def scrape(link):

    driver.get(link) #driver is global variable
    # ratings modal

    ratings_modal = driver.find_elements(
        "xpath", "//button[contains(@class,'VfPpkd-Bz112c-LgbsSe yHy1rc eT1oJ QDwDD mN1ivc VxpoF')]")
    if len(ratings_modal) <= 1:
        return "no reviews"

    # number of reviews
    n_reviews = driver.find_element(
        "xpath", "//div[contains(@class,'EHUI5b')]").text[:-8]
    if 'K' in n_reviews:
        n_reviews = float(n_reviews[:-1]) * 1000
    n_scroll = int(n_reviews)//4  # if int(n_reviews) <=500 else 250

    # enter modal
    ratings_modal[1].click()

    # scrape reviews
    all_reviews_dict = scrape_reviews(n_scroll)
    # serial number added separately for easier merge with tablet reviews
    all_reviews_dict['S/N'] = [i for i in range(
        1, len(all_reviews_dict['Verbatim'])+1)]

    df = pd.DataFrame(data=all_reviews_dict)[['S/N', 'Verbatim', 'Dates']]
    df.to_csv('data/'+link[54:]+'_phone.csv', index=False)

    # multiple devices - tablet
    # note - mutiple devices means phone + tablet. Banking apps don't keep pc version. Hence the hardcoding to check element once instead of going through entire dropdown list
    device = driver.find_elements("xpath", "//div[@id='formFactor_2']")

    if "arrow_drop_down" in device[1].text:
        device[1].click()
        driver.find_elements(
            "xpath", "//span[@jsname='j7LFlb']")[-1].click()  # select tablet

        # scrape reviews - add tag tablet or append to current reviews
        all_reviews_dict = scrape_reviews(n_scroll)
        all_reviews_dict['S/N'] = [i for i in range(
            1, len(all_reviews_dict['Verbatim'])+1)]

        df = pd.DataFrame(data=all_reviews_dict)[['S/N', 'Verbatim', 'Dates']]
        df.to_csv('data/'+link[54:]+'_tablet.csv', index=False)


#main function 
def run():
    for link in all_pages: #all_pages is global
        scrape(link)


if __name__ == "__main__":
    scrape(all_pages[3])
    # run()
    driver.quit()