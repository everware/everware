from selenium.webdriver.common.by import By
import commons

def get_files(driver):
    elems = driver.find_elements_by_xpath('//span[@class="item_name"]')
    files = [
        elem.get_attribute('innerHTML')
        for elem in elems
    ]
    return sorted(files)

def scenario_simple(user):
    driver = commons.login(user)
    user.wait_for_element_present(By.ID, "start")
    driver.find_element_by_id("start").click()
    commons.fill_repo_info(driver, user, user.repo)
    user.log("spawn clicked")
    user.wait_for_element_present(By.LINK_TEXT, "Control Panel")
    old_files = get_files(driver)
    driver.find_element_by_link_text("Control Panel").click()
    user.wait_for_element_present(By.ID, "stop")
    driver.find_element_by_id("stop").click()
    user.log("stop clicked")
    user.wait_for_pattern_in_page(r"Launch\s+a\s+notebook")

    driver.find_element_by_id("start").click()
    commons.fill_repo_info(driver, user, 'https://github.com/everware/travis-test-repo')
    user.log("spawn clicked (second time)")
    user.wait_for_element_present(By.LINK_TEXT, "Control Panel")
    new_files = get_files(driver)

    assert old_files != new_files, """It's an old container:
    Old elems: %s, New elems: %s
    """ % (' '.join(old_files), ' '.join(new_files))
