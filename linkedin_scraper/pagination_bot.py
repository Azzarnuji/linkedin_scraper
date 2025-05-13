import asyncio
from linkedin_scraper.person import Person
from selenium import webdriver
from linkedin_scraper.objects import CallbackLog, PaginationBotOptions, Scraper
from selenium.webdriver.common.by import By
import time
import random
import traceback


class PaginationBot(Scraper):
    def __init__(self, driver, url_pagination, callback, callbackLog, currentPage, limit, callbackStopReason):
        self.driver: webdriver.Chrome = driver
        self.callback  = callback
        self.url_pagination = url_pagination
        self.callback_log = callbackLog
        self.current_page = currentPage
        self.converted_to_page = currentPage // 10
        self.pagination_count = 1
        self.limit = limit
        self.scrapped = 0
        self.original_window = None
        self.callback_stop_reason = callbackStopReason
    
    async def run(self):
        self.driver.get(self.url_pagination)
        self.wait_for_all_elements_to_load(by=By.TAG_NAME, name="main")
        self.wait_for_element_to_load(by=By.XPATH, name="//div[contains(@class,'artdeco-pagination')]//ul/li[last()]/button/span")
        total_pagination_elm = self.__find_element_by_xpath__("//div[contains(@class,'artdeco-pagination')]//ul/li[last()]/button/span", returnElm=True)
        total_pagination_pages = int(total_pagination_elm.text)
        self.original_window = self.driver.current_window_handle
        if self.converted_to_page > 0 and self.converted_to_page != None:
            for i in range(1, self.converted_to_page + 1):
                self.scroll_to_bottom()
                pagination_button = self.wait_for_element_to_be_clickable('//button[contains(@aria-label,"Berikutnya") or contains(@aria-label,"Next")]')
                pagination_button.click()
                time.sleep(random.randint(2, 5))
                self.pagination_count += 1
                await self.callback_log(CallbackLog(
                    currentUrl = self.driver.current_url,
                    targetUrl = self.url_pagination,
                    current_pagination = self.pagination_count,
                    total_pagination = total_pagination_pages
                ))
        while self.pagination_count < total_pagination_pages and self.scrapped < self.limit:
            if self.callback_stop_reason != None:
                stopped = await self.callback_stop_reason()
                print(stopped)
                if stopped:
                    break
            await self._run_scrape()
                
                
    async def _run_scrape(self):
        try:
            for i in range(1, 11):
                if self.callback_stop_reason != None:
                    stopped = await self.callback_stop_reason()
                    if stopped:
                        self.driver.quit()
                        return
                profiles_link_xpath = '//li[{index}]//a[contains(@href, "/in/") and contains(@class,"scale-down")]'
                profile_link_elm = self.__find_element_by_xpath__(profiles_link_xpath.format(index=i), returnElm=True)
                self.__scroll_into__(profile_link_elm)
                target_url = self.clean_url_from_query(profile_link_elm.get_attribute("href"))
                time.sleep(random.randint(2,5))
                self.driver.execute_script("window.open('about:blank', '_blank');")
                self.driver.switch_to.window(self.driver.window_handles[-1])
                time.sleep(random.randint(2,5))
                await self.callback_log(CallbackLog(
                    currentUrl = self.driver.current_url,
                    targetUrl = target_url,
                    current_pagination = self.pagination_count,
                    total_pagination = None
                ))
                
                get_scrape_data = Person(linkedin_url=target_url, driver=self.driver, close_on_complete=False, callback_log=self.callback_log, scrape=False)
                await get_scrape_data.scrape(close_on_complete=False)
                self.driver.close()
                self.driver.switch_to.window(self.original_window)
                
                self.scrapped += 1
                await self.callback(get_scrape_data, self.scrapped)

                if self.scrapped == self.limit:
                    break
        except Exception as e:
            print(e)
            traceback.print_exc()
            raise e
            
        
    