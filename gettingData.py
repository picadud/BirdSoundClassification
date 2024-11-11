
import pandas as pd
import requests
pd.set_option('display.max_columns', None)   # Display all columns
pd.set_option('display.max_colwidth', None)  # Display the full width of each column
occurrenceFile = 'occurrence.txt'
rowDf = pd.read_csv(occurrenceFile, delimiter='\t')
df = rowDf[['catalogNumber', 'vernacularName']].copy()
df.loc[:, 'recording_id'] = df['catalogNumber'].str.extract(r'(\d+)$')
print(df.head(5))
target_species = df['vernacularName'].unique()  # Replace with actual species names
print(target_species)
target_duration = 300  # 300 seconds per species
species_duration = {species: 0 for species in target_species}  # Initialize accumulated duration for each species
# Create an empty DataFrame to store the results
filtered_results = pd.DataFrame()
def get_recording_data(recording_id):
    url = f'https://www.xeno-canto.org/api/2/recordings?query=nr:{recording_id}'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data['recordings']:
            return data['recordings'][0]  # Return the first recording found
    return None

for index, row in df.iterrows():
    species = row['vernacularName']
    recording_id = row['recording_id']

    # Skip if we've reached the 300-second target
    if species_duration[species] >= target_duration:
        continue

    # Fetch recording data
    recording_data = get_recording_data(recording_id)

    if recording_data and recording_data['q'] == 'A' and int(recording_data['smp']) >= 44100:  # Check for quality 'A' and sample rate
        length_seconds = float(recording_data['length'].split(":")[0]) * 60 + float(recording_data['length'].split(":")[1])
        species_duration[species] += length_seconds
        row_data = pd.json_normalize(recording_data)
        filtered_results = pd.concat([filtered_results, row_data], ignore_index=True)
        print(str(species) + ', ' + str(species_duration[species]))
    if all(duration >= target_duration for duration in species_duration.values()):
        print("Target durations reached for all species.")
        break

print(filtered_results.head())
filtered_results.to_csv('filered_results.csv')