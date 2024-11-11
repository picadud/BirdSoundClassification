import pandas as pd
import os
import requests

# Read the CSV file
csv_file_path = "filered_results.csv"
df = pd.read_csv(csv_file_path)[['en', 'file', 'file-name', 'type', 'length', 'date', 'smp']].copy()

# Specify the column containing download links
url_column = "file"
filename_column = 'file-name'

# Specify the directory to save downloaded files
download_directory = "AudioFile"
os.makedirs(download_directory, exist_ok=True)

# Function to download a file
def download_file(url, download_dir, fileName):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            file_name = fileName
            file_path = os.path.join(download_dir, file_name)
            print('downloading')
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            return file_path
        else:
            print(f"Failed to download: {url} (Status code: {response.status_code})")
            return None
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return None

# Download files and add file paths to the DataFrame
df['file_path'] = df.apply(lambda row: download_file(row[url_column], download_directory, row[filename_column]), axis=1)


# Save the updated DataFrame back to CSV
output_csv_file_path = "finalRawData.csv"  # Replace with your desired output CSV file path
df.to_csv(output_csv_file_path, index=False)

print(f"Downloaded files and updated CSV saved at: {output_csv_file_path}")
