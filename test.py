from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium_stealth import stealth
from selenium.webdriver.chrome.options import Options
from linkedin_scraper.person import Person
from bs4 import BeautifulSoup
chrome_options = Options()
# chrome_options.add_argument("start-maximized")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-features=NetworkService")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
chrome_options.add_argument("--disable-software-rasterizer")  # Disable software rasterizer
chrome_options.add_argument("--disable-features=VizDisplayCompositor")
chrome_options.add_argument("--disable-accelerated-2d-canvas")
chrome_options.add_argument("--disable-accelerated-video-decode")
chrome_options.add_argument("--disable-background-networking")
chrome_options.add_argument("--disable-breakpad")
chrome_options.add_argument("--disable-client-side-phishing-detection")
chrome_options.add_argument("--disable-component-update")
chrome_options.add_argument("--disable-default-apps")
chrome_options.add_argument("--disable-hang-monitor")
chrome_options.add_argument("--disable-popup-blocking")
chrome_options.add_argument("--disable-prompt-on-repost")
chrome_options.add_argument("--disable-sync")
chrome_options.add_argument("--disable-translate")
chrome_options.add_argument("--metrics-recording-only")
chrome_options.add_argument("--no-first-run")
chrome_options.add_argument("--safebrowsing-disable-auto-update")
# chrome_options.add_argument("--remote-debugging-port=9222")  # Enable remote debugging
chrome_options.add_argument("--disable-extensions")  # Disable all Chrome extensions
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--enable-logging")
chrome_options.add_argument("--v=99")
chrome_options.add_argument("--js-flags=--max-old-space-size=6144")
chrome_options.binary_location = "/usr/bin/google-chrome"
chrome_options.set_capability("goog:loggingPrefs", {
    "performance": "ALL",
    "browser": "ALL",
    "driver": "ALL"
})
# Create a new Chrome session
driver = webdriver.Chrome(service=Service("./chromedriver/chromedriver"), options=chrome_options)
stealth(
    driver,
    languages=["en-US", "en", "id", "id-ID"],
    vendor="Google Inc.",
    platform="Win32",
    webgl_vendor="Intel Inc.",
    renderer="Intel Iris OpenGL Engine",
    fix_hairline=True,
    user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
)
from linkedin_scraper.person import Person
import time
import urllib.parse
import tempfile

def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    # Hapus semua script yang punya src atau berisi keyword tracking
    for tag in soup.find_all("script"):
        if tag.get("src"):
            tag.decompose()
        elif any(keyword in tag.text.lower() for keyword in ["fetch", "new image", "navigator.sendbeacon", "tracking", "analytics"]):
            tag.decompose() 

    # Domain eksternal yang ingin diblok
    block_domains = [
        "protechts.net", "licdn.com", "doubleclick.net", "googletagmanager.com", "google-analytics.com"
    ]

    # Hapus <img>, <iframe>, <link> yang mengarah ke domain eksternal
    for tag in soup.find_all(["img", "iframe", "link", "image"]):
        for attr in ["src", "href"]:
            url = tag.get(attr, "")
            if any(domain in url for domain in block_domains):
                tag.decompose()
                break
        tag.decompose()
        

    return str(soup)

mapping = [
    {
        "type":"get_name_and_location",
        "file":"profile.html"
    },
    {
        "type":"get_skills",
        "file":"skill.html"
    },
    
    {
        "type":"get_educations",
        "file":"education_profile.html"
    },
    {
        "type":"get_experiences",
        "file":"experience_profile.html"
    },
    {
        "type":"get_contact_info",
        "file":"overlay_profile.html"
    }
]
result = Person(get=False, scrape=False, driver=driver)
with open("profile.html", "r", encoding="utf-8") as f:
    html = f.read()

with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as f:
    html_clean = str(clean_html(html))
    f.write(html_clean)
    temp_html_path = f.name
result.html_element = "file://" + temp_html_path
result.driver.get("file://" + temp_html_path)
result.get_name_and_location()
# for m in mapping:
#     print(m["type"])
#     with open(m["file"], "r", encoding="utf-8") as f:
#         html = f.read()

#     with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as f:
#         f.write(html)
#         temp_html_path = f.name
#     result.html_element = "file://" + temp_html_path
#     result.__getattribute__(m["type"])()

print(result)
time.sleep(3600)
        