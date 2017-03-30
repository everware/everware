from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from settings import *

import time
import re

def login(user, password=""):
    driver = user.get_driver()
    driver.get(user.base_url + "/hub/login")
    user.log("login")
    driver.find_element_by_id("username_input").clear()
    driver.find_element_by_id("username_input").send_keys(user.login)
    driver.find_element_by_id("password_input").clear()
    driver.find_element_by_id("password_input").send_keys(password)
    driver.find_element_by_id("login_submit").click()
    return driver


def fill_repo_info(driver, user, repo):
    user.wait_for_element_present(By.ID, "repository_input")
    driver.find_element_by_id("repository_input").clear()
    driver.find_element_by_id("repository_input").send_keys(repo)
    driver.find_element_by_xpath("//input[@value='Launch notebook']").click()


class User:
    def __init__(self, login=None, repo=DEFAULT_REPO, driver_type=DRIVER):
        self.login = login
        self.repo = repo
        self.log("init")

        self.driver_type = driver_type
        self.driver = None
        self.base_url = "http://localhost:8000/"
        self.verificationErrors = []
        self.accept_next_alert = True


    def get_driver(self):
        if self.driver is None:
            if self.driver_type == "phantomjs":
                os.makedirs(UPLOADDIR, exist_ok=True)
                self.driver = webdriver.PhantomJS(
                    service_log_path=os.path.join(UPLOADDIR, "phantom_%s.log" % self.login))
                self.driver.set_window_size(1024, 768)
            if self.driver_type == "firefox":
                self.driver = webdriver.Firefox()
        return self.driver


    def tearDown(self):
        if hasattr(self, 'driver'):
            self.driver.quit()
            self.driver = None

    def log(self, message):
        print("{}:     {}".format(self.login, message))


    def wait_for_element_present(self, how, what, displayed=True, timeout=TIMEOUT):
        for i in range(timeout):
            if self.is_element_present(how, what, displayed):
                time.sleep(1)  # let handlers attach to the button
                break
            time.sleep(1)
        else:
            assert False, "time out waiting for (%s, %s)" % (how, what)

    def wait_for_pattern_in_page(self, pattern, timeout=TIMEOUT):
        for i in range(timeout):
            page_source = self.driver.page_source
            if re.search(pattern, page_source):
                break
            time.sleep(1)
        else:
            assert False, "time out waiting for pattern %s" % pattern


    def is_element_present(self, how, what, displayed):
        try:
            element = self.driver.find_element(by=how, value=what)
            return element and element.is_displayed() == displayed
        except NoSuchElementException as e: return False


