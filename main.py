from linkedin_scraper import actions
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium_stealth import stealth
from selenium.webdriver.chrome.options import Options
from linkedin_scraper.person import Person
import time
from linkedin_scraper.linkedin_bot import LinkedinBot
chrome_options = Options()
# chrome_options.add_argument("start-maximized")
chrome_options.add_argument("--no-sandbox")
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
actions.login(driver, None,None,"AQEDAT2-LtgAT2FkAAABlrNCitEAAAGW108O0VYAyBrx8IoD5Gtp4CGLxuX_8sfSh5H19WpqprQsfQHb5bCjs3C3FwApPk1ZR24CaB3_c5BY-cYc8TpIb04rS1lcHZ3bMVcXuvjUPWnqBVI_aem2kCMD")

# driver.get("https://www.linkedin.com/mynetwork/invite-connect/connections/")
# original_window = driver.current_window_handle
# driver.execute_script("window.open('about:blank', '_blank');")
# time.sleep(5)
# driver.switch_to.window(driver.window_handles[-1])
# person  = Person("https://www.linkedin.com/in/khusnandyah",driver=driver)
scrapped = 0
def callback_result(person: Person, index):
    global scrapped
    print(f"Scraped {index} people")
    scrapped = index
    print(person.name)
    print(person.experiences)
    print(person.skills)
    print(person.contact_info)

def callback_log(log):
    print(log)
    
def callback_stop_reason():
    global scrapped
    if scrapped == 1:
        return True
    return False

linkedin_bot = LinkedinBot(driver)
linkedin_bot.set_url_pagination("https://www.linkedin.com/search/results/people/?network=%5B%22F%22%5D&origin=MEMBER_PROFILE_CANNED_SEARCH&sid=hpl")
linkedin_bot.set_limit(100)
linkedin_bot.set_current_page(1)
linkedin_bot.set_callback_result(callback_result)
linkedin_bot.set_callback_log(callback_log)
linkedin_bot.set_callback_stop_reason(callback_stop_reason)
linkedin_bot.run_scrape_person()

# print(person.name)
# print(person.skills)
# print(person.experiences)
