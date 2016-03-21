# -*- coding: utf-8 -*-
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def scenario_x(user):
    driver = user.get_driver()
    print(user.driver_type)

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
    user.wait_for_element_present(By.ID, "repository_input")
    driver.find_element_by_id("repository_input").clear()
    driver.find_element_by_id("repository_input").send_keys(user.repo)
    driver.find_element_by_xpath("//input[@value='Spawn']").click()
    user.log("spawn clicked")
    user.wait_for_element_present(By.LINK_TEXT, "Control Panel")
    driver.find_element_by_link_text("Control Panel").click()
    user.wait_for_element_present(By.ID, "stop")
    driver.find_element_by_id("stop").click()
    user.log("stop clicked")
    user.wait_for_element_present(By.ID, "start")
    driver.find_element_by_id("logout").click()
    user.log("logout clicked")


def scenario_no_jupyter(user):
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
    user.wait_for_element_present(By.ID, "repository_input")
    driver.find_element_by_id("repository_input").clear()
    driver.find_element_by_id("repository_input").send_keys('docker:busybox')
    driver.find_element_by_xpath("//input[@value='Spawn']").click()
    user.log("spawn clicked")
    user.wait_for_element_present(By.ID, "resist")
    text = ("Something went wrong during building."
            " Error: Container doesn't have jupyter-singleuser inside")
    assert text in driver.page_source
    user.log("correct, no jupyter in container")
    driver.find_element_by_id("resist").click()
    user.wait_for_element_present(By.ID, "repository_input")
    driver.find_element_by_id("repository_input").clear()
    driver.find_element_by_id("repository_input").send_keys(user.repo)
    driver.find_element_by_xpath("//input[@value='Spawn']").click()
    user.log("spawn clicked (second try)")
    user.wait_for_element_present(By.LINK_TEXT, "Control Panel")
    driver.find_element_by_link_text("Control Panel").click()
    user.wait_for_element_present(By.ID, "stop")
    driver.find_element_by_id("stop").click()
    user.log("stop clicked")
    user.wait_for_element_present(By.ID, "start")
    driver.find_element_by_id("logout").click()
    user.log("logout clicked")


def scenario_timeout(user):
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
    user.wait_for_element_present(By.ID, "repository_input")
    driver.find_element_by_id("repository_input").clear()
    driver.find_element_by_id("repository_input").send_keys(
        'https://github.com/everware/test_long_creation'
    )
    driver.find_element_by_xpath("//input[@value='Spawn']").click()
    user.log("spawn clicked")
    user.wait_for_element_present(By.ID, "resist")
    assert "Building took too long" in driver.page_source or \
            "This image is too heavy to build" in driver.page_source
    user.log('correct, timeout happened')
    driver.find_element_by_id("resist").click()
    user.log("resist clicked")
    user.wait_for_element_present(By.ID, "repository_input")
    driver.find_element_by_id("repository_input").clear()
    driver.find_element_by_id("repository_input").send_keys(
        'https://github.com/everware/test_long_creation'
    )
    driver.find_element_by_xpath("//input[@value='Spawn']").click()
    user.log("spawn clicked (second try)")
    user.wait_for_element_present(By.ID, "resist")
    assert "This image is too heavy to build" in driver.page_source


def scenario_no_dockerfile(user):
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
    user.wait_for_element_present(By.ID, "repository_input")
    driver.find_element_by_id("repository_input").clear()
    driver.find_element_by_id("repository_input").send_keys(
        'https://github.com/everware/runnable_examples'
    )
    driver.find_element_by_xpath("//input[@value='Spawn']").click()
    user.log("spawn clicked")
    user.wait_for_element_present(By.ID, "resist")
    text = ("Something went wrong during building."
            " Error: Your repo doesn't include Dockerfile")
    assert text in driver.page_source
    user.log("correct, no dockerfile")

