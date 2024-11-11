import pandas as pd
import os
from pydub import AudioSegment

# Read the CSV file
csv_file_path = 'finalRawData.csv'
df = pd.read_csv(csv_file_path)

# Specify the directory for converted WAV files
converted_directory = "AudioFilesInWav"
os.makedirs(converted_directory, exist_ok=True)

# Function to convert audio files to WAV format
def convert_to_wav(file_path, output_directory):
    try:
        # Load the audio file
        audio = AudioSegment.from_file(file_path)
        # Create the output file path
        file_name_without_ext = os.path.splitext(os.path.basename(file_path))[0]
        wav_file_path = os.path.join(output_directory, f"{file_name_without_ext}.wav")
        # Export as WAV
        audio.export(wav_file_path, format='wav')
        return wav_file_path
    except Exception as e:
        print(f"Error converting {file_path}: {e}")
        return None

# Convert downloaded files to WAV and store paths
df['converted_file_path'] = df['file_path'].apply(lambda path: convert_to_wav(path, converted_directory))

# Save the updated DataFrame back to CSV
output_csv_file_path = "finalRawData.csv"
df.to_csv(output_csv_file_path, index=False)

print(f"Downloaded files, converted to WAV, and updated CSV saved at: {output_csv_file_path}")
