#import libraries
import pandas as pd
import os
from app_store_scraper import AppStore

def create_csv(df, directory_name, filename):
    #create directory if doesn't exist
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)

    # Export DataFrame to CSV
    csv_filename = directory_name + filename
    df.to_csv(csv_filename, index=False)


def merge_data_files():
    directory_path = './data'  # Update this with the path to your directory

    dataframes = []

    for filename in os.listdir(directory_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(directory_path, filename)
            df = pd.read_csv(file_path)
            
            if 'Stars' in df.columns:
                df.rename(columns={"Stars": "Ratings"}, inplace=True)
                
            if 'Dates' in df.columns:
                df.rename(columns={"Dates": "Date"}, inplace=True)
                
            dataframes.append(df)

    #merge all dataframes
    merged_df = pd.concat(dataframes, ignore_index=True)

    #re-index the S/N
    merged_df['S/N'] = range(1, len(merged_df) + 1)

    create_csv(merged_df, './merged_data/', 'reviews.csv')


def scrap_data_app_store():
    apps = [
        {'country': 'us', 'app_name': 'ubs-access-secure-login', 'app_id': '1121666286'},
        {'country': 'us', 'app_name': 'ubs-ubs-key4', 'app_id': '441068021'}
    ]

    # Fetch and store reviews for all apps
    all_reviews = []

    for app_info in apps:
        app = AppStore(country=app_info['country'], app_name=app_info['app_name'], app_id=app_info['app_id'])
        app.review(how_many=20000)
        
        # Add keys 'app_name' and 'app_id' to each review dictionary
        for review in app.reviews:
            review['app_name'] = app_info['app_name']
            review['app_id'] = app_info['app_id']
        
        all_reviews.extend(app.reviews)

    # Create a DataFrame from all reviews
    reviews_df = pd.DataFrame(all_reviews)

    #add new column
    # reviews_df['S/N'] = range(1, len(reviews_df) + 1)
    reviews_df.insert(0, "S/N", range(1, len(reviews_df) + 1), True)

    #rename columns
    reviews_df.rename(columns={"review": "Verbatim", "rating": "Ratings", "date": "Date", "title": "Title"}, inplace=True)

    #drop columns
    reviews_df.drop(columns=['developerResponse', 'isEdited', 'userName', 'app_name', 'app_id', 'Title'], inplace=True)

    create_csv(reviews_df, './data/', 'App_Store_Reviews.csv')

    merge_data_files()

#add function to scrap playstore data

scrap_data_app_store()