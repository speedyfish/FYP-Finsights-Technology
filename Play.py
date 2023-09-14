import pandas as pd
from google_play_scraper import reviews_all
from time import sleep

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

def scrape(page_id):
    
    all_descriptions = []
    all_dates = []
    all_stars = []
    all_versions = []
    
    #scrape reveiws
    reviews = reviews_all(page_id, country='sg')
    
    for review in reviews:
        all_descriptions.append(review["content"])
        all_dates.append(review["at"].date())
        all_stars.append(review["score"])
        all_versions.append(review["appVersion"])
        
        
    all_reviews_dict = {'Verbatim': all_descriptions, 'Dates': all_dates, 'Stars': all_stars, 'Version': all_versions}

    #add serial number
    all_reviews_dict['S/N'] = [i for i in range(1, len(all_reviews_dict['Verbatim'])+1)]
    
    #create dataframe
    df = pd.DataFrame(data=all_reviews_dict)[['S/N', 'Verbatim', 'Dates', 'Stars', 'Version']]
    df.to_csv('data/'+page_id+'.csv', index=False)


if __name__ == "__main__":
    for page_id in all_page_ids: #all_page_ids is global
        scrape(page_id)
        sleep(3)
    