
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
        self.callback_stop_reason = None

    def set_current_page(self, current_page):
        self.current_page = current_page
        
    def set_limit(self, limit):
        self.limit = limit
        
    def set_callback_result(self, callback):
        print("🚨 Callback type set_callback_result:", type(callback))  # Debugging
        self.callback = callback
        
    def set_url_pagination(self, url_pagination):
        self.url_pagination = url_pagination
        
    def set_callback_log(self, callback_log):
        print("🚨 Callback type set_callback_log:", type(callback_log))  # Debugging
        self.callback_log = callback_log
        
    def set_callback_stop_reason(self, callback_stop_reason):
        print("🚨 Callback type set_callback_stop_reason:", type(callback_stop_reason))  # Debugging
        self.callback_stop_reason = callback_stop_reason
        
    def run_scrape_person(self):
        PaginationBot(
            self.driver,
            self.url_pagination,
            self.callback,
            self.callback_log,
            self.current_page,
            self.limit,
            self.callback_stop_reason
        ).run()
        
    def login_with_cookie(self, cookie):
        from linkedin_scraper import actions
        actions._login_with_cookie(self.driver, cookie)
