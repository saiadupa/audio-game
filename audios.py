import os
import pandas as pd
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError

# Define the paths
csv_file_path = 'audios.csv'
source_folder = '/data/Data/AsvSpoofData_2019/train/LA/ASVspoof2019_LA_eval/flac'
destination_folder = './extracted_audios_mp3'

# Create the destination directory if it doesn't exist
if not os.path.exists(destination_folder):
    os.makedirs(destination_folder)

# Read the CSV file
audio_metadata = pd.read_csv(csv_file_path)

# Iterate over each row in the metadata
for index, row in audio_metadata.iterrows():
    file_name = row['filename'] + '.flac'  # Add the file extension
    
    # Construct full file path
    src_file_path = os.path.join(source_folder, file_name)
    
    # Construct destination file path
    dst_file_path = os.path.join(destination_folder, row['filename'] + '.mp3')
    
    # Check if the file exists in the source directory
    if os.path.exists(src_file_path):
        try:
            # Load the .flac file
            audio = AudioSegment.from_file(src_file_path, format='flac')
            
            # Export the file as .mp3
            audio.export(dst_file_path, format='mp3')
            print(f"Converted and saved: {file_name} to {row['filename']}.mp3")
        except CouldntDecodeError:
            print(f"Error decoding file: {file_name}")
    else:
        print(f"File not found: {file_name}")

print("File conversion complete.")