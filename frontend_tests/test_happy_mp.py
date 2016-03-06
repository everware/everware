# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import time
import traceback
import nose2


# Test matrix
SCENARIOS = ["scenario_short"]

USERS = ["an1", "an2"]

class User:
    def __init__(self, login=None,
                 repo="https://github.com/everware/everware-dimuon-example",
                 driver_type="phantomjs"):
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
            self.driver = webdriver.PhantomJS('/usr/local/bin/phantomjs')
        if self.driver_type == "firefox":
            self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(60)
        return self.driver

    def tearDown(self):
        self.driver.quit()
        # return self.verificationErrors

    def log(self, message):
        print("{}:     {}".format(self.login, message))

    def wait_for_element_present(self, how, what, displayed=True, timeout=30):
        for i in range(timeout):
            element = self.driver.find_element(by=how, value=what)
            if element is not None and element.is_displayed() == displayed: break
            time.sleep(1)
        else: assert False, "time out waiting for (%s, %s)" % (how, what)

    def wait_for_element_id_is_gone(self, value, timeout=30):
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
            yield scenario_runner, scenario, username


def scenario_runner(scenario, username):
    user = User(username)
    try:
        globals()[scenario](user)
    except Exception as e:
        print("oops: %s" % repr(e))
        assert False, traceback.format_stack()
    finally:
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

