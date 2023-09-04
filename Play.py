from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

# Create a ChromeOptions object and add the '--headless' argument if needed
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')

# Initialize the webdriver with the ChromeDriverManager
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# the ones with reviews are ->
all_page_ids = ["com.ubs.mobilepass", "com.ubs.swidK2Y.android",
                "com.ubs.swidKXJ.android", "com.ubs.Paymit.android"]

all_pages = ["https://play.google.com/store/apps/details?id=" +
             page_id for page_id in all_page_ids]


# Function to scrape reviews
def scrape_reviews(n_scroll):
    reviews = []

    for i in range(n_scroll):
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'RHo1pe')))
        all_reviews = driver.find_elements(By.CLASS_NAME, 'RHo1pe')

        for review in all_reviews:
            rev = review.text.split('\n')
            reviews.append({
                'Verbatim': rev[3],
                'Dates': rev[2],
                'Stars': int(rev[1][6])
            })

        # Scroll to load more reviews
        driver.execute_script('window.scrollBy(0, 500);')

    return reviews


# Function to scrape a page
def scrape(link):
    driver.get(link)

    # Wait for ratings button to be clickable
    ratings_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'VfPpkd-Bz112c-LgbsSe yHy1rc eT1oJ QDwDD mN1ivc VxpoF')]"))
    )

    # Scroll to button (if needed)
    driver.execute_script("arguments[0].scrollIntoView();", ratings_button)

    # Click ratings button
    ratings_button.click()

    # Scrape reviews
    reviews = scrape_reviews(10)  # Adjust the number of scrolls as needed

    if reviews:
        df = pd.DataFrame(reviews)
        df.to_csv('data/' + link[54:] + '_reviews.csv', index=False)

    # Close the modal
    close_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Close about app dialog']"))
    )
    close_button.click()

    # Switch to tablet view (if available)
    tablet = driver.find_elements(By.XPATH, "//div[@aria-label='Tablet']")
    if tablet:
        tablet[0].click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'RHo1pe')))

        # Click ratings button again (tablet view)
        ratings_button.click()

        # Scrape reviews for tablet
        reviews = scrape_reviews(10)  # Adjust the number of scrolls as needed

        if reviews:
            df = pd.DataFrame(reviews)
            df.to_csv('data/' + link[54:] + '_tablet_reviews.csv', index=False)

    # Close the driver
    driver.quit()


# Main function
def run():
    for link in all_pages:
        scrape(link)


if __name__ == "__main__":
    run()
