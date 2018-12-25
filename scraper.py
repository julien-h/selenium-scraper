from selenium import webdriver
from urllib.request import urlretrieve
from os.path import join

LOGIN_URL = 'http://localhost:8889/login'


class Scraper:
    def __init__(self, driver=None):
        if driver:
            self.driver = driver
        else:
            options = webdriver.ChromeOptions()
            options.add_argument("user-data-dir=selenium-data")
            self.driver = webdriver.Chrome(options=options)

    def login(self):
        self.driver.get(LOGIN_URL)
        self.driver.find_element_by_id('login').send_keys('username')
        self.driver.find_element_by_id('pass').send_keys('password')
        remember = self.driver.find_element_by_name('remember_login')
        if not remember.get_attribute('checked'):
            remember.click()
        self.driver.find_element_by_xpath("//input[@type='submit' and @value='Login']").click()

    def get(self, url):
        self.driver.get(url)
        if self.must_login(url, self.driver.current_url):
            self.login()
            self.get(url)

    def must_login(self, requested_url, response_url):
        return 'login' in response_url

    # Delegate every other methods to the driver
    def __getattr__(self, attr):
        return getattr(self.driver, attr)


if __name__ == '__main__':
    scraper = Scraper()
    scraper.get('http://localhost:8889/list')
    links = scraper.find_elements_by_css_selector('li a')
    urls = [item.get_attribute('href') for item in links]
    for url in urls:
        scraper.get(url)
        img = scraper.find_element_by_tag_name('img').get_attribute('src')
        filename = join('downloaded', scraper.current_url.split('/')[-1] + '.jpg')
        urlretrieve(img, filename)
