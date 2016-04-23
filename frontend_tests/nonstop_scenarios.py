# -*- coding: utf-8 -*-
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def get_files(driver):
    elems = driver.find_elements_by_xpath('//span[@class="item_name"]')
    files = [
        elem.get_attribute('innerHTML')
        for elem in elems
    ]
    return sorted(files)

def scenario_simple(user):
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
    old_files = get_files(driver)
    driver.find_element_by_link_text("Control Panel").click()
    user.wait_for_element_present(By.ID, "stop")
    driver.find_element_by_id("stop").click()
    user.log("stop clicked")
    user.wait_for_pattern_in_page(r"Start\s+My\s+Server")

    driver.find_element_by_id("start").click()
    user.wait_for_element_present(By.ID, "repository_input")
    driver.find_element_by_id("repository_input").clear()
    driver.find_element_by_id("repository_input").send_keys(
        'https://github.com/betatim/everware-demo'
    )
    driver.find_element_by_xpath("//input[@value='Spawn']").click()
    user.log("spawn clicked (second time)")
    user.wait_for_element_present(By.LINK_TEXT, "Control Panel")
    new_files = get_files(driver)

    assert old_files != new_files, """It's an old container:
    Old elems: %s, New elems: %s
    """ % (' '.join(old_files), ' '.join(new_files))
