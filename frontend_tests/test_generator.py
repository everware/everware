# -*- coding: utf-8 -*-
from selenium import webdriver
import nose2
import time
import os
import happy_scenarios as hs
from selenium.common.exceptions import NoSuchElementException
import traceback


REPO = "https://github.com/everware/everware-cpp-example.git"

if os.environ.get('TRAVIS') == 'true':
    DRIVER = "phantomjs"
else:
    DRIVER = "firefox"

# Test matrix
SCENARIOS = [
    hs.scenario_timeout, # need to be in beginning
    hs.scenario_full, hs.scenario_short,
    hs.scenario_no_jupyter, hs.scenario_no_dockerfile,
]
USERS = ["user1", "user2"]
TIMEOUT = 250
UPLOADDIR = os.environ['UPLOADDIR']


def make_screenshot(driver, name):
    os.makedirs(UPLOADDIR, exist_ok=True)
    driver.save_screenshot(os.path.join(UPLOADDIR, name))


class User:
    def __init__(self, login=None, repo=REPO, driver_type=DRIVER):
        self.login = login
        self.repo = repo
        self.password = ""
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
            self.driver.implicitly_wait(TIMEOUT)
        return self.driver


    def tearDown(self):
        if hasattr(self, 'driver'):
            self.driver.quit()
            self.driver = None

    def log(self, message):
        print("{}:     {}".format(self.login, message))


    def wait_for_element_present(self, how, what, displayed=True, timeout=TIMEOUT):
        for i in range(timeout):
            element = self.driver.find_element(by=how, value=what)
            if element is not None and element.is_displayed() == displayed:
                time.sleep(1)  # let handlers attach to the button
                break
            time.sleep(1)
        else: assert False, "time out waiting for (%s, %s)" % (how, what)


    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e: return False
        return True


def test_generator():
    for username in USERS:
        yield run_scenario, username, SCENARIOS


def run_scenario(username, scenarios):
    user = User(username)
    for s in scenarios:
        try:
            s(user)
        except Exception as e:
            make_screenshot(user.driver, "{}-{}.png".format(username, s.__name__))
            print("Exception for {} {}: {}\n{}".format(
                username, s.__name__, repr(e), ''.join(traceback.format_stack())))
            raise e
    user.tearDown()

if __name__ == "__main__":
    nose2.main()
