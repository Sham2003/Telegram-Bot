from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_all_elements_located
from selenium.webdriver.common.by import By
import os

class Quote:
    def __init__(self, query):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        self.driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)
        self.qurl = f"https://www.brainyquote.com/search_results?q={query}"
        self.wait = WebDriverWait(self.driver, 1)
        self.quotes = []
        self.driver.get(self.qurl)
        self.getquote()
        self.driver.close()

    def getquote(self):
        self.wait.until(presence_of_all_elements_located((By.ID, 'quotesList')))
        element = self.driver.find_element_by_css_selector('div#quotesList.new-msnry-grid.bqcpx')
        for i in element.find_elements_by_class_name('m-brick'):
            try:
                qauthor = i.find_elements_by_tag_name('a')
                self.quotes.append({'Quote': qauthor[0].text,
                                    'Author': qauthor[1].text})
            except:
                continue

    def printquotes(self):
        self.quotes = list(filter(lambda element: len(element['Quote']) > len(element['Author']), self.quotes))
        for i in self.quotes:
            print(i, end="\n")

    def __len__(self):
        return len(self.quotes)

    def __getitem__(self, item):
        return self.quotes.__getitem__(item)
