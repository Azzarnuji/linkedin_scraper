import random
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time
from .objects import (Accomplishment, CallbackLog, Contact, ContactInfo, Education, Experience,
    Interest, Scraper)
import os
from linkedin_scraper import selectors


class Person(Scraper):

    __TOP_CARD = "main"
    __WAIT_FOR_ELEMENT_TIMEOUT = 5

    def __init__(
        self,
        linkedin_url=None,
        name=None,
        about=None,
        experiences=None,
        educations=None,
        interests=None,
        accomplishments=None,
        company=None,
        job_title=None,
        contacts=None,
        driver=None,
        get=True,
        scrape=True,
        close_on_complete=True,
        time_to_wait_after_login=0,
        callback_log: CallbackLog = None,
        html_element: str | None = None
    ):
        self.linkedin_url = linkedin_url
        self.name = name
        self.headline = None
        self.about = about or []
        self.experiences = experiences or []
        self.educations = educations or []
        self.interests = interests or []
        self.accomplishments = accomplishments or []
        self.also_viewed_urls = []
        self.contacts = contacts or []
        self.contact_info = None
        self.skills = []
        self.callback_log = callback_log
        self.html_element = html_element

        if driver is None:
            try:
                if os.getenv("CHROMEDRIVER") == None:
                    driver_path = os.path.join(
                        os.path.dirname(__file__), "drivers/chromedriver"
                    )
                else:
                    driver_path = os.getenv("CHROMEDRIVER")

                driver = webdriver.Chrome(driver_path)
            except:
                driver = webdriver.Chrome()

        if get:
            driver.get(linkedin_url)

        self.driver = driver

        if scrape:
            self.scrape(close_on_complete)

    def add_about(self, about):
        self.about.append(about)

    def add_experience(self, experience):
        self.experiences.append(experience)

    def add_education(self, education):
        self.educations.append(education)

    def add_interest(self, interest):
        self.interests.append(interest)

    def add_accomplishment(self, accomplishment):
        self.accomplishments.append(accomplishment)

    def add_location(self, location):
        self.location = location

    def add_contact(self, contact):
        self.contacts.append(contact)
    

    def scrape(self, close_on_complete=True):
        if self.is_signed_in():
            self.scrape_logged_in(close_on_complete=close_on_complete)
        else:
            print("you are not logged in!")

    def _click_see_more_by_class_name(self, class_name):
        try:
            _ = WebDriverWait(self.driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_name))
            )
            div = self.driver.find_element(By.CLASS_NAME, class_name)
            div.find_element(By.TAG_NAME, "button").click()
        except Exception as e:
            pass

    def is_open_to_work(self):
        try:
            return "#OPEN_TO_WORK" in self.driver.find_element(By.CLASS_NAME,"pv-top-card-profile-picture").find_element(By.TAG_NAME,"img").get_attribute("title")
        except:
            return False

    def get_experiences(self):
        if self.html_element:
            url = self.html_element
        else:    
            url = os.path.join(self.linkedin_url, "details/experience")
        self.driver.get(url)
        self.focus()
        main = self.wait_for_element_to_load(by=By.TAG_NAME, name="main")
        self.wait(3)
        self.scroll_to_half()
        self.scroll_to_bottom()
        main_list = self.wait_for_element_to_load(name="pvs-list__container", base=main)
        for position in main_list.find_elements(By.CLASS_NAME, "pvs-list__paged-list-item"):
                
            position = position.find_element(By.CSS_SELECTOR, "div[data-view-name='profile-component-entity']")
            
            # Fix: Handle case where more than 2 elements are returned
            elements = position.find_elements(By.XPATH, "*")
            if len(elements) < 2:
                continue  # Skip if we don't have enough elements
                
            company_logo_elem = elements[0]
            position_details = elements[1]

            # company elem
            try:
                company_linkedin_url = company_logo_elem.find_element(By.XPATH,"*").get_attribute("href")
                if not company_linkedin_url:
                    continue
            except NoSuchElementException:
                continue

            # position details
            position_details_list = position_details.find_elements(By.XPATH,"*")
            position_summary_details = position_details_list[0] if len(position_details_list) > 0 else None
            position_summary_text = position_details_list[1] if len(position_details_list) > 1 else None
            
            if not position_summary_details:
                continue
                
            outer_positions = position_summary_details.find_element(By.XPATH,"*").find_elements(By.XPATH,"*")

            if len(outer_positions) == 4:
                position_title = outer_positions[0].find_element(By.TAG_NAME,"span").text
                company = outer_positions[1].find_element(By.TAG_NAME,"span").text
                work_times = outer_positions[2].find_element(By.TAG_NAME,"span").text
                location = outer_positions[3].find_element(By.TAG_NAME,"span").text
            elif len(outer_positions) == 3:
                if "·" in outer_positions[2].text:
                    position_title = outer_positions[0].find_element(By.TAG_NAME,"span").text
                    company = outer_positions[1].find_element(By.TAG_NAME,"span").text
                    work_times = outer_positions[2].find_element(By.TAG_NAME,"span").text
                    location = ""
                else:
                    position_title = ""
                    company = outer_positions[0].find_element(By.TAG_NAME,"span").text
                    work_times = outer_positions[1].find_element(By.TAG_NAME,"span").text
                    location = outer_positions[2].find_element(By.TAG_NAME,"span").text
            else:
                position_title = ""
                company = outer_positions[0].find_element(By.TAG_NAME,"span").text if outer_positions else ""
                work_times = outer_positions[1].find_element(By.TAG_NAME,"span").text if len(outer_positions) > 1 else ""
                location = ""

            # Safely extract times and duration
            if work_times:
                parts = work_times.split("·")
                times = parts[0].strip() if parts else ""
                duration = parts[1].strip() if len(parts) > 1 else None
            else:
                times = ""
                duration = None

            from_date = " ".join(times.split(" ")[:2]) if times else ""
            to_date = " ".join(times.split(" ")[3:]) if times and len(times.split(" ")) > 3 else ""
            
            if position_summary_text and any(element.get_attribute("class") == "pvs-list__container" for element in position_summary_text.find_elements(By.XPATH, "*")):
                try:
                    inner_positions = (position_summary_text.find_element(By.CLASS_NAME,"pvs-list__container")
                                    .find_element(By.XPATH,"*").find_element(By.XPATH,"*").find_element(By.XPATH,"*")
                                    .find_elements(By.CLASS_NAME,"pvs-list__paged-list-item"))
                except NoSuchElementException:
                    inner_positions = []
            else:
                inner_positions = []
            
            if len(inner_positions) > 1:
                descriptions = inner_positions
                for description in descriptions:
                    try:
                        res = description.find_element(By.TAG_NAME,"a").find_elements(By.XPATH,"*")
                        position_title_elem = res[0] if len(res) > 0 else None
                        work_times_elem = res[1] if len(res) > 1 else None
                        location_elem = res[2] if len(res) > 2 else None

                        location = location_elem.find_element(By.XPATH,"*").text if location_elem else None
                        position_title = position_title_elem.find_element(By.XPATH,"*").find_element(By.TAG_NAME,"*").text if position_title_elem else ""
                        work_times = work_times_elem.find_element(By.XPATH,"*").text if work_times_elem else ""
                        
                        # Safely extract times and duration
                        if work_times:
                            parts = work_times.split("·")
                            times = parts[0].strip() if parts else ""
                            duration = parts[1].strip() if len(parts) > 1 else None
                        else:
                            times = ""
                            duration = None
                            
                        from_date = " ".join(times.split(" ")[:2]) if times else ""
                        to_date = " ".join(times.split(" ")[3:]) if times and len(times.split(" ")) > 3 else ""

                        experience = Experience(
                            position_title=position_title,
                            from_date=from_date,
                            to_date=to_date,
                            duration=duration,
                            location=location,
                            description=description,
                            institution_name=company,
                            linkedin_url=company_linkedin_url
                        )
                        self.add_experience(experience)
                    except (NoSuchElementException, IndexError) as e:
                        # Skip this description if elements are missing
                        continue
            else:
                description = position_summary_text.text if position_summary_text else ""

                experience = Experience(
                    position_title=position_title,
                    from_date=from_date,
                    to_date=to_date,
                    duration=duration,
                    location=location,
                    description=description,
                    institution_name=company,
                    linkedin_url=company_linkedin_url
                )
                    
                self.add_experience(experience)
            
            

    def get_educations(self):
        if self.html_element:
            url = self.html_element
        else:    
            url = os.path.join(self.linkedin_url, "details/education")
        self.driver.get(url)
        self.focus()
        main = self.wait_for_element_to_load(by=By.TAG_NAME, name="main")
        self.scroll_to_half()
        self.scroll_to_bottom()
        main_list = self.wait_for_element_to_load(name="pvs-list__container", base=main)
        for position in main_list.find_elements(By.CLASS_NAME,"pvs-list__paged-list-item"):
            try:
                position = position.find_element(By.CSS_SELECTOR, "div[data-view-name='profile-component-entity']")
                
                # Fix: Handle case where more than 2 elements are returned
                elements = position.find_elements(By.XPATH,"*")
                if len(elements) < 2:
                    continue  # Skip if we don't have enough elements
                    
                institution_logo_elem = elements[0]
                position_details = elements[1]

                # institution elem
                try:
                    institution_linkedin_url = institution_logo_elem.find_element(By.XPATH,"*").get_attribute("href")
                except NoSuchElementException:
                    institution_linkedin_url = None

                # position details
                position_details_list = position_details.find_elements(By.XPATH,"*")
                position_summary_details = position_details_list[0] if len(position_details_list) > 0 else None
                position_summary_text = position_details_list[1] if len(position_details_list) > 1 else None
                
                if not position_summary_details:
                    continue
                    
                outer_positions = position_summary_details.find_element(By.XPATH,"*").find_elements(By.XPATH,"*")

                institution_name = outer_positions[0].find_element(By.TAG_NAME,"span").text if outer_positions else ""
                degree = outer_positions[1].find_element(By.TAG_NAME,"span").text if len(outer_positions) > 1 else None

                from_date = None
                to_date = None
                
                if len(outer_positions) > 2:
                    try:
                        times = outer_positions[2].find_element(By.TAG_NAME,"span").text

                        if times and "-" in times:
                            split_times = times.split(" ")
                            dash_index = split_times.index("-") if "-" in split_times else -1
                            
                            if dash_index > 0:
                                from_date = split_times[dash_index-1]
                            if dash_index < len(split_times) - 1:
                                to_date = split_times[-1]
                    except (NoSuchElementException, ValueError):
                        from_date = None
                        to_date = None

                description = position_summary_text.text if position_summary_text else ""

                education = Education(
                    from_date=from_date,
                    to_date=to_date,
                    description=description,
                    degree=degree,
                    institution_name=institution_name,
                    linkedin_url=institution_linkedin_url
                )
                self.add_education(education)
            except (NoSuchElementException, IndexError) as e:
                # Skip this education entry if elements are missing
                continue

    def get_name_and_location(self):
        top_panel = self.driver.find_element(By.XPATH, "//*[@class='mt2 relative']")
        self.name = top_panel.find_element(By.TAG_NAME, "h1").text
        self.location = top_panel.find_element(By.XPATH, "//*[@class='text-body-small inline t-black--light break-words']").text
        self.headline = top_panel.find_element(By.XPATH, "//*[@class='text-body-medium break-words']").text
    def get_contact_info(self):
        if self.html_element:
            url = self.html_element
        else:    
            url = os.path.join(self.linkedin_url, "overlay/contact-info/")
        self.driver.get(url)
        self.wait_for_element_to_load(by=By.CLASS_NAME, name="artdeco-modal-overlay")
        account_email = self.__find_element_by_xpath__(
                '//section[contains(@class,"pv-contact-info") and h3[text()[contains(.,"Email") or contains(.,"Email")]]]//div//a[contains(@class,"link-without-visited-state") and contains(@rel,"noopener noreferrer") and contains(@href,"mail")]'
            ,True
        )
        account_details = {
            "account_address": self.__find_element_by_xpath__(
                '//section[contains(@class,"pv-contact-info") and h3[text()[contains(.,"Address") or contains(.,"Alamat")]]]//div//a[contains(@class,"link-without-visited-state") and contains(@rel,"noopener noreferrer") and contains(@href,"maps")]'
            ,True
            ).text,
            "account_email": account_email.get_attribute('href').split(":")[1] if hasattr(account_email, 'get_attribute') else "Not Available",
            "account_birthday": self.__find_element_by_xpath__(
                '//section[contains(@class,"pv-contact-info") and h3[text()[contains(.,"Birthday") or contains(.,"Ulang Tahun")]]]//span[contains(@class,"t-14")]'
            ,True
            ).text,
            "connected_at": self.__find_element_by_xpath__(
                '//section[contains(@class,"pv-contact-info") and h3[text()[contains(.,"Connected") or contains(.,"Terhubung")]]]//span[contains(@class,"t-14")]'
            ,True
            ).text,
            "account_dist_value": self.__find_element_by_xpath__(
                '//span[contains(@class,"dist-value")]'
            ,True
            ).text,
            "account_phone": self.__find_element_by_xpath__(
                '//section[contains(@class,"pv-contact-info") and h3[text()[contains(.,"Phone") or contains(.,"Telepon")]]]//span[contains(@class,"t-14")]'
            ,True
            ).text,
        }
        
        self.contact_info = ContactInfo(**account_details)
        
        

    def get_about(self):
        try:
            about = self.driver.find_element(By.ID,"about").find_element(By.XPATH,"..").find_element(By.CLASS_NAME,"display-flex").text
        except NoSuchElementException :
            about=None
        self.about = about

    def scrape_logged_in(self, close_on_complete=True):
        driver = self.driver
        duration = None

        root = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
            EC.presence_of_element_located(
                (
                    By.TAG_NAME,
                    self.__TOP_CARD,
                )
            )
        )
        self.focus()
        self.wait(5)

        # get name and location
        self.get_name_and_location()
        self.wait(5)
        
        self.open_to_work = self.is_open_to_work()
        self.wait(5)
        
        
        # get about
        self.get_about()
        self.wait(5)
        
        driver.execute_script(
            "window.scrollTo(0, Math.ceil(document.body.scrollHeight/2));"
        )
        driver.execute_script(
            "window.scrollTo(0, Math.ceil(document.body.scrollHeight/1.5));"
        )
        
        #get contact info
        self.get_contact_info()
        self.wait(5)
        
        # get experience
        self.get_experiences()
        self.wait(5)
        
        # get education
        self.get_educations()
        self.wait(5)
        
        #get skills
        self.get_skills()
        self.wait(5)

        driver.get(self.linkedin_url)

        if close_on_complete:
            driver.quit()

    def get_skills(self):
        if self.html_element:
            url = self.html_element
        else:    
            url = os.path.join(self.linkedin_url, "details/skills")
        self.driver.get(url)
        self.focus()
        main = self.wait_for_element_to_load(by=By.TAG_NAME, name="main")
        self.scroll_to_half()
        self.scroll_to_bottom()
        a_href_list = main.find_elements(By.XPATH, "//a[@data-field='skill_page_skill_topic']")
        skills = []
        for a_href in a_href_list:
            self.wait_for_element_to_load(By.XPATH, './/span[@aria-hidden="true"]', base=a_href)
            element = a_href.find_element(By.XPATH, './/span[@aria-hidden="true"]')
            self.__scroll_into__(element)
            time.sleep(2)
                
            skills.append(element.text)
        self.skills = skills
        

    @property
    def company(self):
        if self.experiences:
            return (
                self.experiences[0].institution_name
                if self.experiences[0].institution_name
                else None
            )
        else:
            return None

    @property
    def job_title(self):
        if self.experiences:
            return (
                self.experiences[0].position_title
                if self.experiences[0].position_title
                else None
            )
        else:
            return None

    def __repr__(self):
        return "<Person {name}\n\nAbout\n{about}\n\nExperience\n{exp}\n\nSkills\n{skills}\n\nEducation\n{edu}\n\nInterest\n{int}\n\nAccomplishments\n{acc}\n\nContacts\n{conn}\n\nContact Information\n{contact_info}\n>".format(
            name=self.name,
            about=self.about,
            exp=self.experiences,
            edu=self.educations,
            int=self.interests,
            acc=self.accomplishments,
            conn=self.contacts,
            skills=self.skills,
            contact_info=self.contact_info
        )
