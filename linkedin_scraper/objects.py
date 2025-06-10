from dataclasses import dataclass
from time import sleep

from selenium.webdriver import Chrome

from . import constants as c

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import asyncio
import inspect

@dataclass
class Contact:
    name: str = None
    occupation: str = None
    url: str = None
    
@dataclass
class CallbackLog:
    currentUrl: str = None
    targetUrl: str = None
    current_pagination: int = None
    total_pagination: int = None
    message: str = None
    
@dataclass
class ContactInfo:
    account_address: str = None
    account_email: str = None
    account_birthday: str = None
    connected_at: str = None
    account_dist_value: str = None
    account_phone: str = None

@dataclass
class PaginationBotOptions:
    driver: webdriver.Chrome = None
    url_pagination: str = None
    callback: any = None
    callbackLog: CallbackLog = None
    currentPage: int = 1
    callbackStopReason: any = None
    limit: int = 10000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
    


@dataclass
class Institution:
    institution_name: str = None
    linkedin_url: str = None
    website: str = None
    industry: str = None
    type: str = None
    headquarters: str = None
    company_size: int = None
    founded: int = None


@dataclass
class Experience(Institution):
    from_date: str = None
    to_date: str = None
    description: str = None
    position_title: str = None
    duration: str = None
    location: str = None


@dataclass
class Education(Institution):
    from_date: str = None
    to_date: str = None
    description: str = None
    degree: str = None


@dataclass
class Interest(Institution):
    title = None


@dataclass
class Accomplishment(Institution):
    category = None
    title = None
    
class SafeElement:
    def __init__(self, element, default=None):
        self._element = element
        self.default = default

    @property
    def text(self):
        if self._element:
            return self._element.text
        return self.default  # atau "" kalau mau string kosong

    def __getattr__(self, item):
        # Forward other attribute accesses to the real element (if exists)
        if self._element:
            return getattr(self._element, item)
        raise AttributeError(f"'NoneType' has no attribute '{item}'")


@dataclass
class Scraper:
    driver: Chrome = None
    WAIT_FOR_ELEMENT_TIMEOUT = 5
    TOP_CARD = "pv-top-card"

    @staticmethod
    def wait(duration):
        sleep(int(duration))

    def focus(self):
        self.driver.execute_script('alert("Focus window")')
        self.driver.switch_to.alert.accept()

    def mouse_click(self, elem):
        action = webdriver.ActionChains(self.driver)
        action.move_to_element(elem).perform()

    def wait_for_element_to_load(self, by=By.CLASS_NAME, name="pv-top-card", base=None):
        base = base or self.driver
        return WebDriverWait(base, self.WAIT_FOR_ELEMENT_TIMEOUT).until(
            EC.presence_of_element_located(
                (
                    by,
                    name
                )
            )
        )
        
    def safe_callback(self, cb, *args, **kwargs):
        if not callable(cb):
            raise TypeError(f"Callback harus fungsi atau coroutine, bukan {type(cb)}")
        if inspect.iscoroutinefunction(cb):
            try:
                loop = asyncio.get_running_loop()
                asyncio.create_task(cb(*args, **kwargs))
            except RuntimeError:
                asyncio.run(cb(*args, **kwargs))
        else:
            cb(*args, **kwargs)
            
    def safe_callback_with_return(self, cb, *args, **kwargs):
        if not callable(cb):
            raise TypeError(f"Callback harus fungsi atau coroutine, bukan {type(cb)}")

        if inspect.iscoroutinefunction(cb):
            try:
                loop = asyncio.get_running_loop()
                # Jika loop sedang berjalan, gunakan create_task()
                return asyncio.create_task(cb(*args, **kwargs))  # Menjalankan coroutine
            except RuntimeError:
                # Jika tidak ada loop yang sedang berjalan, gunakan asyncio.run()
                return asyncio.run(cb(*args, **kwargs))
        else:
            return cb(*args, **kwargs)  # Kalau bukan coroutine, panggil langsung

        
    def wait_for_element_to_be_clickable(self, xpath, by=By.XPATH):
        return WebDriverWait(self.driver, self.WAIT_FOR_ELEMENT_TIMEOUT).until(
            EC.element_to_be_clickable(
                (
                    by,
                    xpath
                )
            )
        )

    def wait_for_all_elements_to_load(self, by=By.CLASS_NAME, name="pv-top-card", base=None):
        base = base or self.driver
        return WebDriverWait(base, self.WAIT_FOR_ELEMENT_TIMEOUT).until(
            EC.presence_of_all_elements_located(
                (
                    by,
                    name
                )
            )
        )


    def is_signed_in(self):
        try:
            WebDriverWait(self.driver, self.WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located(
                    (
                        By.CLASS_NAME,
                        c.VERIFY_LOGIN_ID,
                    )
                )
            )

            self.driver.find_element(By.CLASS_NAME, c.VERIFY_LOGIN_ID)
            return True
        except Exception as e:
            pass
        return False

    def scroll_to_half(self):
        self.driver.execute_script(
            "window.scrollTo(0, Math.ceil(document.body.scrollHeight/2));"
        )

    def scroll_to_bottom(self):
        self.driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);"
        )

    def scroll_class_name_element_to_page_percent(self, class_name:str, page_percent:float):
        self.driver.execute_script(
            f'elem = document.getElementsByClassName("{class_name}")[0]; elem.scrollTo(0, elem.scrollHeight*{str(page_percent)});'
        )

    def __find_element_by_class_name__(self, class_name):
        try:
            self.driver.find_element(By.CLASS_NAME, class_name)
            return True
        except:
            pass
        return False

    def __find_element_by_xpath__(self, tag_name, returnElm = False):
        try:
            element = self.driver.find_element(By.XPATH,tag_name)
            if returnElm:
                return SafeElement(element, default="Not Available")
            return True
        except:
            pass
        return SafeElement(None, default="Not Available") if returnElm else False

    def __find_enabled_element_by_xpath__(self, tag_name):
        try:
            elem = self.driver.find_element(By.XPATH,tag_name)
            return elem.is_enabled()
        except:
            pass
        return False
    
    def __scroll_into__(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView();", element)
        
    def clean_url_from_query(self,url):
        from urllib.parse import urlparse, urlunparse

        # Parse URL
        parsed_url = urlparse(url)

        # Hapus query string
        clean_url = urlunparse(parsed_url._replace(query=""))

        return clean_url
    
    @classmethod
    def __find_first_available_element__(cls, *args):
        for elem in args:
            if elem:
                return elem[0]
