import os
import sys
import requests
from urllib.parse import urlparse
from datetime import datetime

DOWNLOADS_FOLDER = os.path.join(str(os.path.expanduser("~")), "Downloads")
DEFAULT_CHUNK_SIZE = 8192
DEFAULT_TIMEOUT = 30  # Set the default timeout to 30 seconds
VERSION = "1.9"
GITHUB_API_URL = "https://api.github.com/repos/IgorCielniak/ictfd/releases/latest"
LATEST_VERSION = requests.get(GITHUB_API_URL).json()["tag_name"]
GITHUB_RELEASE_URL = f"https://raw.githubusercontent.com/IgorCielniak/ictfd/{LATEST_VERSION}/ictfd.py"

def create_downloads_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def download_http_file(url, download_dir, chunk_size=DEFAULT_CHUNK_SIZE, timeout=DEFAULT_TIMEOUT):
    try:
        response = requests.get(url, stream=True, timeout=timeout)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        file_name = os.path.join(download_dir, url.split("/")[-1])

        print(f"{url}")
        print(f"Resolving {parsed_url.netloc} ({parsed_url.netloc})... connected.")
        print(f"HTTP request sent, awaiting response... {response.status_code} {response.reason}")
        print(f"Length: {total_size} ({format_bytes(total_size)}) [{response.headers['content-type']}]")

        if os.path.exists(file_name):
            if not prompt_user_overwrite(file_name):
                print("Download canceled.")
                return

        print(f"Saving to: '{file_name}'")
        print(f"Using chunk size: {chunk_size} bytes")
        print(f"Timeout: {timeout} seconds")
        print("Press Ctrl+C to cancel the download.")

        start_time = datetime.now()
        downloaded_size = 0

        with open(file_name, "wb") as file:
            for chunk in response.iter_content(chunk_size=chunk_size):
                file.write(chunk)
                downloaded_size += len(chunk)

                elapsed_time = (datetime.now() - start_time).total_seconds()
                download_speed = downloaded_size / elapsed_time
                percentage = (downloaded_size / total_size) * 100
                estimated_time = (total_size - downloaded_size) / download_speed if download_speed > 0 else 0

                print(f"\rDownload Speed: {format_bytes(download_speed)}/s | "
                      f"Progress: {percentage:.2f}% | "
                      f"Estimated Time: {estimated_time:.0f} seconds", end="", flush=True)

        print("\nFile downloaded successfully.")
        print(f"Total Time: {format_time(elapsed_time)}")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")
        if isinstance(e, requests.exceptions.Timeout):
            print("The download timed out. Please check your internet connection or try again later.")
        elif isinstance(e, requests.exceptions.ConnectionError):
            print("Connection error occurred. Please check your network.")
        return
    except KeyboardInterrupt:
        print("\nDownload canceled. Deleting incomplete file...")
        os.remove(file_name)
        print("Incomplete file deleted.")

def prompt_user_overwrite(file_path):
    user_input = input(f"File '{file_path}' already exists. Do you want to overwrite it? (y/n): ").lower()
    return user_input == 'y'

def display_help():
    print("Usage:")
    print("  python ictfd.py [URL] [-c CHUNK_SIZE] [-d DOWNLOAD_DIR] [-t TIMEOUT] [-h] [-v]")
    print("\nOptions:")
    print("  URL                  The URL of the file to download.")
    print("  -c, --chunk-size     Custom chunk size for downloading.")
    print("  -d, --download-dir   Custom directory for downloaded files.")
    print("  -t, --timeout        Custom download timeout in seconds (default is 30).")
    print("  -h, --help           Display this help message.")
    print("  -v, --version        Display the version and check for updates.")

def display_version():
    print(f"ICTFD Version {VERSION}")

    if "--version" or "-v" in sys.argv:
        try:
            latest_version = requests.get(GITHUB_API_URL).json()["tag_name"]
            if latest_version != VERSION:
                print(f"\nA newer version ({latest_version}) is available. You can download it from: {GITHUB_RELEASE_URL}")
                user_input = input("Do you want to download the newer version? (y/n): ").lower()
                if user_input == 'y':
                    # Download the newer version
                    print("Downloading the newer version...")
                    download_file(GITHUB_RELEASE_URL)
        except Exception as e:
            print("Failed to check for updates:", e)

def format_bytes(size):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0

def format_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

def download_file(url, custom_chunk_size=None, custom_download_dir=None, timeout=DEFAULT_TIMEOUT):
    try:
        global parsed_url
        parsed_url = urlparse(url)
        scheme = parsed_url.scheme.lower()

        if custom_download_dir:
            download_dir = custom_download_dir
        else:
            download_dir = DOWNLOADS_FOLDER

        create_downloads_folder(download_dir)

        if scheme in ["http", "https"]:
            chunk_size = custom_chunk_size if custom_chunk_size is not None else DEFAULT_CHUNK_SIZE
            download_http_file(url, download_dir, chunk_size, timeout)
        else:
            print(f"Unsupported scheme: {scheme}. Cannot download the file.")
    except Exception as e:
            print(f"Error downloading file: {e}")

def interactive_mode():
    print("\nICTFD - Interactive Mode\n")
    print("Welcome to ICTFD (Interactive Command-Line File Downloader)!\n")
    print("To download files, please follow these steps:")
    print("1. Enter the number of files you want to download.")
    print("2. For each file, enter the URL of the file.")
    print("3. Optionally, specify a custom chunk size for downloading.")
    print("4. Optionally, specify a custom download directory.")
    print("5. Optionally, specify a custom download timeout.")
    print("6. Press Enter after each URL to proceed to the next file.\n")

    try:
        num_files = int(input("Enter the number of files to download: "))
    except ValueError:
        print("Invalid input. Please enter a valid number.")
        return

    for i in range(1, num_files + 1):
        print(f"\nFile {i}:")
        url = input("Enter the URL of the file: ")

        custom_chunk_size = None
        chunk_size_input = input("Enter custom chunk size (press Enter for default): ")
        if chunk_size_input:
            try:
                custom_chunk_size = int(chunk_size_input)
            except ValueError:
                print("Invalid chunk size. Using default.")

        custom_download_dir = input("Enter custom download directory (press Enter to use default): ")
        
        custom_timeout = None
        timeout_input = input("Enter custom timeout (in seconds, press Enter for default 30): ")
        if timeout_input:
            try:
                custom_timeout = int(timeout_input)
            except ValueError:
                print("Invalid timeout. Using default.")

        download_file(url, custom_chunk_size, custom_download_dir, custom_timeout)

    input("\nPress Enter to exit.")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        interactive_mode()
    else:
        custom_download_dir = None
        custom_chunk_size = None
        custom_timeout = DEFAULT_TIMEOUT
        url_index = 1

        for index, arg in enumerate(sys.argv[1:], start=1):
            if arg in ["-d", "--download-dir"]:
                try:
                    custom_download_dir = sys.argv[index + 1]
                except IndexError:
                    print("Invalid custom download directory. Using default.")
            elif arg in ["-c", "--chunk-size"]:
                try:
                    custom_chunk_size = int(sys.argv[index + 1])
                except IndexError:
                    print("Invalid custom chunk size. Using default.")
            elif arg in ["-t", "--timeout"]:
                try:
                    custom_timeout = int(sys.argv[index + 1])
                except IndexError:
                    print("Invalid timeout. Using default.")

        if sys.argv[1] in ["-h", "--help"]:
            display_help()
        elif sys.argv[1] in ["-v", "--version"]:
            display_version()
        else:
            download_file(sys.argv[url_index], custom_chunk_size, custom_download_dir, custom_timeout)

