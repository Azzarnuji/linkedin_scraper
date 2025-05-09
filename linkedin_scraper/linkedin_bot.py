
from linkedin_scraper.pagination_bot import PaginationBot
from linkedin_scraper.objects import PaginationBotOptions

class LinkedinBot:
    def __init__(self, driver):
        self.driver = driver
        self.callback  = None
        self.url_pagination = None
        self.callback_log = None
        self.current_page = None
        self.limit = None

    def set_current_page(self, current_page):
        self.current_page = current_page
        
    def set_limit(self, limit):
        self.limit = limit
        
    def set_callback_result(self, callback):
        self.callback = callback
        
    def set_url_pagination(self, url_pagination):
        self.url_pagination = url_pagination
        
    def set_callback_log(self, callback_log):
        self.callback_log = callback_log
        
    def set_callback_stop_reason(self, callback_stop_reason):
        self.callback_stop_reason = callback_stop_reason
        
    def run_scrape_person(self):
        PaginationBot(
            PaginationBotOptions(
                driver=self.driver,
                url_pagination=self.url_pagination,
                callback=self.callback,
                callbackLog=self.callback_log,
                currentPage=self.current_page,
                limit=self.limit,
                callbackStopReason=self.callback_stop_reason
            )
        )
        
    def login_with_cookie(self, cookie):
        from linkedin_scraper import actions
        actions._login_with_cookie(self.driver, cookie)
