from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re

class TestSeLoginFailed(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "http://localhost:5000/"
        self.verificationErrors = []
        self.accept_next_alert = True
    
    def test_se_login_failed(self):
        driver = self.driver
        driver.get("http://localhost:5000/login")
        driver.find_element_by_id("name").clear()
        driver.find_element_by_id("name").send_keys("fail")
        driver.find_element_by_id("password").clear()
        driver.find_element_by_id("password").send_keys("fail")
        driver.find_element_by_css_selector("button.btn").click()
        self.assertEqual("http://localhost:5000/login", driver.current_url)
        # Warning: assertTextPresent may require manual changes
        self.assertRegexpMatches(driver.find_element_by_css_selector("BODY").text, r"^[\s\S]*$")
    
    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e: return False
        return True
    
    def is_alert_present(self):
        try: self.driver.switch_to_alert()
        except NoAlertPresentException, e: return False
        return True
    
    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
