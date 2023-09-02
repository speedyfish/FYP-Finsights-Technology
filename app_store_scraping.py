import pandas as pd
from app_store_scraper import AppStore

# Define a list of apps
apps = [
    {'country': 'us', 'app_name': 'ubs-access-secure-login', 'app_id': '1121666286'},
    {'country': 'us', 'app_name': 'ubs-ubs-key4', 'app_id': '441068021'},
    # Add more apps as needed
]

# Fetch and store reviews for all apps
all_reviews = []

for app_info in apps:
    app = AppStore(country=app_info['country'], app_name=app_info['app_name'], app_id=app_info['app_id'])
    app.review(how_many=2000)
    
    # Add keys 'app_name' and 'app_id' to each review dictionary
    for review in app.reviews:
        review['app_name'] = app_info['app_name']
        review['app_id'] = app_info['app_id']
    
    all_reviews.extend(app.reviews)

# Create a DataFrame from all reviews
reviews_df = pd.DataFrame(all_reviews)

# Export DataFrame to CSV
csv_filename = 'app_reviews.csv'
reviews_df.to_csv(csv_filename, index=False)

print(f"DataFrame exported to '{csv_filename}'")