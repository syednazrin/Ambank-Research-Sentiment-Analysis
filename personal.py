import os
import time
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests

BASE_URL = "https://www.bursamalaysia.com"
COMPANY_PAGE = BASE_URL + "/bm/market_information/announcements/company_announcement?company=8869"
MAX_RESULTS = 50
PDF_FOLDER = "pdfs"

# Setup Selenium
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115 Safari/537.36")
driver = webdriver.Chrome(service=Service(), options=chrome_options)

def get_page_html(url):
    driver.get(url)
    time.sleep(3)  # wait for JS to load
    return driver.page_source

def scrape_takeover_announcements(limit=50):
    announcements = []
    page_url = COMPANY_PAGE

    while len(announcements) < limit and page_url:
        html = get_page_html(page_url)
        soup = BeautifulSoup(html, "html.parser")
        rows = soup.select("table.table-announcements tbody tr")

        for row in rows:
            if len(announcements) >= limit:
                break

            cols = row.find_all("td")
            if len(cols) < 2:
                continue

            category = cols[1].get_text(strip=True)
            if category.lower() == "take-over offer":
                link_tag = cols[0].find("a", href=True)
                if link_tag:
                    title = link_tag.get_text(strip=True)
                    href = link_tag['href']
                    full_url = urljoin(BASE_URL, href)
                    announcements.append({
                        'title': title,
                        'url': full_url,
                        'category': category
                    })

        # Pagination
        next_btn = soup.find("a", class_="paginate_button next", href=True)
        if next_btn and len(announcements) < limit:
            page_url = urljoin(BASE_URL, next_btn['href'])
        else:
            page_url = None

    return announcements

def scrape_pdfs(announcement_url):
    html = get_page_html(announcement_url)
    soup = BeautifulSoup(html, "html.parser")
    pdfs = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.lower().endswith('.pdf'):
            pdf_title = a.get_text(strip=True) or os.path.basename(href)
            pdf_url = urljoin(BASE_URL, href)
            pdfs.append({'title': pdf_title, 'url': pdf_url})
    return pdfs

def download_pdf(pdf_info):
    os.makedirs(PDF_FOLDER, exist_ok=True)
    safe_name = pdf_info['title'].replace("/", "-") + '.pdf'
    filename = os.path.join(PDF_FOLDER, safe_name)
    r = requests.get(pdf_info['url'], stream=True)
    r.raise_for_status()
    with open(filename, 'wb') as f:
        for chunk in r.iter_content(1024):
            f.write(chunk)
    print(f"Downloaded: {filename}")

def main():
    announcements = scrape_takeover_announcements(limit=MAX_RESULTS)
    print(f"Found {len(announcements)} Take-over offer announcements")

    for ann in announcements:
        print(f"Fetching: {ann['title']} ({ann['url']})")
        pdfs = scrape_pdfs(ann['url'])
        for pdf in pdfs:
            print(f" - PDF: {pdf['title']} -> {pdf['url']}")
            download_pdf(pdf)

    driver.quit()

if __name__ == "__main__":
    main()
