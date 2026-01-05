import zipfile
import os

zip_path = "yoga_dataset.zip"           # Change path if your zip is elsewhere
extract_to = "yoga_dataset"             # Folder to extract to

# Create output directory if it doesn't exist
os.makedirs(extract_to, exist_ok=True)

# Extract contents
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_to)

print("Extraction completed.")
