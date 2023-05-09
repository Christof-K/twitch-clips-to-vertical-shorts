import argparse
from src.clips_downloader import download_clips
from src.converter import convert_clips
from src.yt_uploader import upload_clips


# Set up command-line arguments
parser = argparse.ArgumentParser(description='Process clips')
parser.add_argument('--skip-download', action='store_true', help='Skip downloading clips')
parser.add_argument('--skip-convert', action='store_true', help='Skip converting clips')
parser.add_argument('--skip-upload', action='store_true', help='Skip uploading clips')

args = parser.parse_args()

if not args.skip_download:
  downloaded_count = download_clips()
  print(f"~downloaded: {downloaded_count}\n")

if not args.skip_convert:
  converted_count = convert_clips()
  print(f"~converted: {converted_count}\n")

if not args.skip_upload:
  uploaded_count = upload_clips()
  print(f"~uploaded: {uploaded_count}\n")