import re
import requests
import sys

def main():
    file_path = "./seed_retail_data.py"
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        sys.exit(1)

    # Find all urls matching https://images.unsplash.com/...
    urls = re.findall(r'https://images\.unsplash\.com/[a-zA-Z0-9_\-\.\?\&/\=]+', content)
    unique_urls = sorted(list(set(urls)))
    
    print(f"Found {len(unique_urls)} unique Unsplash image URLs in the seed script.")
    print("Checking HTTP status for each URL...")
    print("-" * 60)

    broken_urls = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    for i, url in enumerate(unique_urls, 1):
        try:
            # We use GET with stream=True or HEAD to quickly check status without downloading the whole image
            response = requests.get(url, headers=headers, stream=True, timeout=5)
            status_code = response.status_code
            if status_code == 200:
                print(f"[{i}/{len(unique_urls)}] OK: {url[:60]}...")
            else:
                print(f"[{i}/{len(unique_urls)}] BROKEN ({status_code}): {url}")
                broken_urls.append((url, status_code))
        except Exception as e:
            print(f"[{i}/{len(unique_urls)}] ERROR ({type(e).__name__}): {url}")
            broken_urls.append((url, str(e)))

    print("-" * 60)
    if broken_urls:
        print(f"Found {len(broken_urls)} broken URLs:")
        for url, err in broken_urls:
            print(f" - {url} (Error: {err})")
    else:
        print("All image URLs returned 200 OK!")

if __name__ == "__main__":
    main()
