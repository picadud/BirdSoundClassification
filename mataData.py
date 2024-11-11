import pandas as pd
import numpy as np
import ast

# Function to convert the string representation of segments to the total length of them
def segments_to_length(data_str):
    def tuple_to_length(seg):
        return seg[1] - seg[0]


    cleaned_string = data_str.replace("np.float64", "")
    arr = ast.literal_eval(cleaned_string)
    print(arr)
    length_list = list(map(tuple_to_length, arr))
    length_sum = sum(length_list)
    return length_sum


df = pd.read_csv('segmentedData.csv')
def convert_to_seconds(time_str):
    minutes, seconds = map(int, time_str.split(':'))
    return minutes * 60 + seconds

# Step 2: Apply the function to the 'length' column to create a new column for total seconds
df['length_in_seconds'] = df['length'].apply(convert_to_seconds)
df['segments_length'] = df['segments'].apply(segments_to_length)

result1 = df.groupby('en')['length_in_seconds'].sum().reset_index()
print(result1.head())
result2 = df.groupby('en')['segments_count'].sum().reset_index()
print(result2.head())
result3 = df.groupby('en')['segments_length'].sum().reset_index()
print(result3.head())
meta_data_df = pd.concat([result1['en'], result1['length_in_seconds'], result2['segments_count'], result3['segments_length']], axis = 1)
print(meta_data_df.head())
meta_data_df.to_csv('meta_data.csv')