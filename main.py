import argparse
from src.clips_downloader import download_clips
from src.converter import convert_clips
from src.yt_uploader import upload_clips


# Set up command-line arguments
parser = argparse.ArgumentParser(description='Process clips')
parser.add_argument('--download', action='store_true', help='Download clips')
parser.add_argument('--convert', action='store_true', help='Convert clips')
parser.add_argument('--upload', action='store_true', help='Upload clips')

args = parser.parse_args()

if args.download:
  downloaded_count = download_clips()
  print(f"~downloaded: {downloaded_count}\n")

if args.convert:
  converted_count = convert_clips()
  print(f"~converted: {converted_count}\n")

if args.upload:
  uploaded_count = upload_clips()
  print(f"~uploaded: {uploaded_count}\n")
