import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import os
import time
from requests.exceptions import RequestException

def get_page_content(session, url, retries=3):
    attempt = 0
    while attempt < retries:
        try:
            response = session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup
        except RequestException as e:
            attempt += 1
            print(f"Terjadi kesalahan saat mengambil halaman {url}: {e}. Coba lagi ({attempt}/{retries})...")
            time.sleep(2)
    print(f"Gagal mengambil halaman {url} setelah {retries} percobaan.")
    return None

def extract_domain(url):
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception as e:
        print(f"Error saat mengekstrak domain dari {url}: {e}")
        return None

def extract_domains_from_page(soup):
    links = soup.find_all('a', href=True)
    domains = set()
    for link in links:
        href = link['href']
        domain = extract_domain(href)
        if domain and domain != "defacer.net":
            domains.add(domain)
    return domains

def save_domains_to_file(domains, filename):
    with open(filename, "a") as f:
        for domain in domains:
            f.write(domain + "\n")

def count_domains_in_file(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            lines = f.readlines()
            return len(set(line.strip() for line in lines))
    return 0

def scrape_defacer_page(page_url, file_name):
    page = 1
    empty_pages_count = 0
    with requests.Session() as session:
        while True:
            url = f'{page_url}/{page}'
            soup = get_page_content(session, url)
            
            if not soup:
                print("Tidak ada halaman lebih lanjut. Proses selesai.")
                break
            
            domains = extract_domains_from_page(soup)

            if not domains:
                print(f"Tidak ada domain ditemukan pada halaman {page}. Proses selesai.")
                break

            if len(domains) == 1 and "defacer.net" in domains:
                empty_pages_count += 1
                print(f"Halaman {page} hanya mengandung 'defacer.net'.")
            else:
                empty_pages_count = 0
                save_domains_to_file(domains, file_name)
                print(f"Menemukan {len(domains)} domain pada halaman {page}")
            
            if empty_pages_count >= 3:
                print("Tiga halaman berturut-turut hanya mengandung 'defacer.net'. Proses dihentikan.")
                break

            time.sleep(0.5)
            page += 1
    
    total_domains = count_domains_in_file(file_name)
    print(f"\nTotal domain yang telah disimpan dalam {file_name}: {total_domains}")

def main():
    print("Pilih halaman yang ingin Anda scrape:")
    print("https://github.com/pengodehandal/defacernetgrabber (KoderGabut)")
    print("1. Archive (https://defacer.net/archive/)")
    print("2. Onhold (https://defacer.net/onhold/)")
    print("3. Special (https://defacer.net/special/)")
    
    choice = input("Masukkan pilihan (1, 2, atau 3): ")

    if choice == '1':
        print("Memulai Grabber Pada Archive...")
        scrape_defacer_page("https://defacer.net/archive", "defacernetarchive.txt")
    elif choice == '2':
        print("Memulai Grabber Pada Onhold...")
        scrape_defacer_page("https://defacer.net/onhold", "defacernetonhold.txt")
    elif choice == '3':
        print("Memulai Grabber Pada Special...")
        scrape_defacer_page("https://defacer.net/special", "defacernetspecial.txt")
    else:
        print("Pilihan tidak valid. Program dihentikan.")

if __name__ == '__main__':
    main()
