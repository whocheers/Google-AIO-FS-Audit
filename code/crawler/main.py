import time
from websurfer import WebSurfer

import pandas as pd

df_qry_new = pd.read_csv('/Users/deshenghu/Desktop/Google_knowledge_component/code/2025_03_16/sample_qry_after_adjust_ques_type/full_qry_to_be_crawled.csv')
print("len of df_qry_new:", len(df_qry_new))

#df_qry_new = df_qry_new[:3]



queries, indexes = df_qry_new['query_standardized'].tolist(), df_qry_new['new_index'].tolist() # read_queries_from_csv('/Users/deshenghu/Desktop/Google_knowledge_component/code/2024_12_01/merge_qry/query_all_types_merged_new.csv')
#queries, indexes = read_queries_from_csv('binary_query_with_various_semantic.csv')
print("number of query:", len(queries))
print("number of indexes:", len(indexes))

# Example usage with location spoofing
LOCATIONS = {
    "New York City": {'latitude': 40.7128, 'longitude': -74.0060, 'accuracy': 1},
    #"Kansas City": {'latitude': 39.1000, 'longitude': -94.5784, 'accuracy': 1},
    "Kansas City": {'latitude': 39.0998, 'longitude': -94.5786, 'accuracy': 1},
    "San Francisco": {'latitude': 37.7749, 'longitude': -122.4194, 'accuracy': 1},

    "Houston": {'latitude': 29.7608, 'longitude': -95.3695, 'accuracy': 1},

    "Madison": {'latitude': 43.0739, 'longitude': -89.3852, 'accuracy': 1},
}

websurfer = WebSurfer(
    profile="selenium_profiles/default",
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    #location=LOCATIONS["San Francisco"],
    location=LOCATIONS["New York City"],
    #location=LOCATIONS["Charleston"],
    #location=LOCATIONS["Houston"],
    #location=LOCATIONS["San Francisco"],

)

# Example of localization
websurfer.navigate_to('https://www.dennys.com/order', save_html=True)
time.sleep(5)


# Initial Google load - will use actual location
websurfer.navigate_to('https://www.google.com/maps', save_html=True)
time.sleep(5)

# Next Google load(s) - will use desired location
websurfer.navigate_to('https://www.google.com/maps', save_html=True)
time.sleep(5)

# # Search for pizza with desired location


websurfer.navigate_to('https://www.google.com/search?q=pizza', save_html=True)
time.sleep(5)

# # Search query likely to generate a AI Overview with desired location


websurfer.navigate_to('https://www.google.com/search?q=why+is+the+sky+blue%3F',save_html=True)
time.sleep(5)

websurfer.navigate_to('https://www.google.com/search?q=can+you+feed+babis+honey%3F',save_html=True)
#websurfer.navigate_to('https://www.google.com/search?q=pizza', save_html=True)
# time.sleep(5)




#Perform searches and save results
print("\n\n\n  gonnal crawl final baby related queries!!")
time.sleep(5)
for query, index in zip(queries, indexes):
    search_url = f"https://www.google.com/search?q={query}"
    websurfer.navigate_to(search_url, query_index=index, save_html=True)
    time.sleep(50)  # Adjust sleep time as needed




# Exit
input("Press Enter to close the browser...")
websurfer.shutdown()