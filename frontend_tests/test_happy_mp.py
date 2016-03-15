# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import traceback
import nose2
import time
import os

# REPO = "https://github.com/everware/everware-dimuon-example"
REPO = "https://github.com/everware/everware-cpp-example.git"
# repo = "docker:yandex/rep-tutorial:0.1.3"
# repo = "docker:everware/https_github_com_everware_everware_dimuon_example-5e87f9567d33842e12636038d56544d54c3d0702"
# repo = "docker:everware/https_github_com_everware_everware_dimuon_example-9bec6770485eb6b245648bc251d045a204973cc9"
# REPO = "docker:yandex/rep-tutorial"

DRIVER = "phantomjs"
DRIVER = "firefox"

# Test matrix
SCENARIOS = ["scenario_full", "scenario_short"]
# SCENARIOS = ["scenario_short", "scenario_short_bad"]
# USERS = ["user_1", "an2"]
USERS = ["user1"]
TIMEOUT = 120
UPLOADDIR = os.environ['UPLOADDIR']

def make_screenshot(driver, name):
    if not os.path.exists(UPLOADDIR):
        os.makedirs(UPLOADDIR)
    driver.save_screenshot(os.path.join(UPLOADDIR, name))


class User:
    def __init__(self, login=None, repo=REPO, driver_type=DRIVER):
        self.login = login
        self.repo = repo
        self.password = ""
        self.log("init")

        self.driver_type = driver_type
        self.base_url = "http://localhost:8000/"
        self.verificationErrors = []
        self.accept_next_alert = True


    def get_driver(self):
        if self.driver_type == "phantomjs":
            self.driver = webdriver.PhantomJS()
            self.driver.set_window_size(1024, 768)
        if self.driver_type == "firefox":
            self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(TIMEOUT)
        return self.driver


    def tearDown(self):
        self.driver.quit()
        # return self.verificationErrors

    def log(self, message):
        print("{}:     {}".format(self.login, message))


    def wait_for_element_present(self, how, what, displayed=True, timeout=TIMEOUT):
        for i in range(timeout):
            element = self.driver.find_element(by=how, value=what)
            if element is not None and element.is_displayed() == displayed: break
            time.sleep(1)
        else: assert False, "time out waiting for (%s, %s)" % (how, what)


    def wait_for_element_id_is_gone(self, value, timeout=TIMEOUT):
        for i in range(timeout):
            try:
                element = self.driver.find_element_by_id(value)
            except NoSuchElementException as e:
                break
            time.sleep(1)
            # self.log("waiting for %s to go %d" % (value, i))
        else: self.fail("time out wairing for (%s) to disappear" % (what))
        self.log("gone finally (%d)" % i)


    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e: return False
        return True


def test_generator():
    for scenario in SCENARIOS:
        for username in USERS:
            yield run_scenario, scenario, username


def run_scenario(scenario, username):
    user = User(username)
    try:
        globals()[scenario](user)
    except NoSuchElementException as e:
        assert False, "Cannot find element {}\n{}".format(e.msg, ''.join(traceback.format_stack()))
    except Exception as e:
        print("oops: %s" % repr(e))
        assert False, traceback.format_stack()
    finally:
        make_screenshot(user.driver, "{}-{}.png".format(scenario, username))
        user.tearDown()


def scenario_short(user):
    driver = user.get_driver()
    driver.get(user.base_url + "/hub/login")
    user.log("login")
    driver.find_element_by_id("username_input").clear()
    driver.find_element_by_id("username_input").send_keys(user.login)
    driver.find_element_by_id("password_input").clear()
    driver.find_element_by_id("password_input").send_keys(user.password)
    driver.find_element_by_id("login_submit").click()
    user.wait_for_element_present(By.ID, "start")
    driver.find_element_by_id("logout").click()
    user.log("logout clicked")


def scenario_short_bad(user):
    driver = user.get_driver()
    driver.get(user.base_url + "/hub/login")
    user.log("login")
    driver.find_element_by_id("username_input").clear()
    driver.find_element_by_id("username_input").send_keys(user.login)
    driver.find_element_by_id("password_input").clear()
    driver.find_element_by_id("password_input").send_keys(user.password)
    driver.find_element_by_id("login_submit").click()
    user.wait_for_element_present(By.ID, "start1")
    driver.find_element_by_id("logout").click()
    user.log("logout clicked")


def scenario_full(user):
    driver = user.get_driver()
    driver.get(user.base_url + "/hub/login")
    user.log("login")
    driver.find_element_by_id("username_input").clear()
    driver.find_element_by_id("username_input").send_keys(user.login)
    driver.find_element_by_id("password_input").clear()
    driver.find_element_by_id("password_input").send_keys(user.password)
    driver.find_element_by_id("login_submit").click()
    user.wait_for_element_present(By.ID, "start")
    driver.find_element_by_id("start").click()
    driver.find_element_by_id("repository_input").clear()
    driver.find_element_by_id("repository_input").send_keys(user.repo)
    driver.find_element_by_xpath("//input[@value='Spawn']").click()
    user.log("spawn clicked")
    user.wait_for_element_present(By.LINK_TEXT, "Control Panel")
    driver.find_element_by_link_text("Control Panel").click()
    user.wait_for_element_present(By.ID, "stop")
    driver.find_element_by_id("stop").click()
    user.log("stop clicked")
    user.wait_for_element_id_is_gone("stop")
    driver.find_element_by_id("logout").click()
    user.log("logout clicked")

if __name__ == "__main__":
    nose2.main()
