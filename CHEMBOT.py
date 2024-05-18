import random
from xml.dom import minidom
import requests
from selenium import webdriver
from selenium.common.exceptions import *
import os

NOTFOUND = "Nothing"


class Compound:
    def __init__(self, cid=None, name=None):
        self.url = "https://pubchem.ncbi.nlm.nih.gov/"
        self.cid = cid  # finished
        self.name = None if name is None else name  # finshed
        self.molecularmass = float()
        self.iupacname = str()  # finished
        self.formula = str()  # finished
        self.density = str()  # finished
        self.meltingpoint = str()  # finished
        self.boilingpoint = str()  # finished
        self.othernames = list()  # finished
        self.vapourdensity = str()  # finsihed
        self.threestruct = f"https://molview.org/?cid={str(cid)}"
        self.about = ''''''
        self.hazards = list()  # finished
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        self.driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)
        self.url = self.url + 'compound/' + str(cid)
        self.driver.get(self.url)

    def getproperties(self):
        if self.name is None:
            title = self.driver.title
            title = title.split("|")
            self.name = title[0]
        self.getiupac()  # 1
        self.getmolecularmassandformula()  # 2
        self.getdensity()
        self.getmeltingpoint()
        self.getboilingpoint()
        self.getvapordensity()
        self.find_hazards()
        self.getothernames()

    def getiupac(self):
        try:
            element = self.driver.find_element_by_id('IUPAC-Name').find_element_by_css_selector(
                'div.section-content-item')
            self.iupacname = element.find_element_by_tag_name('p').text
        except NoSuchElementException:
            self.iupacname = NOTFOUND

    def getmolecularmassandformula(self):
        try:
            element = self.driver.find_element_by_css_selector(
                "table.summary.f-1.f-lh-15.with-padding-small.fixed-layout.no-border-last-row.rowed")
            element2 = element.find_elements_by_tag_name('tr')
            for i in element2:
                subelement = i.find_element_by_tag_name('th')
                if subelement.text == "Molecular Formula":
                    a = i.find_element_by_tag_name('span')
                    self.formula = a.text
                if subelement.text == "Molecular Weight":
                    a = i.find_element_by_tag_name('p')
                    self.molecularmass = float(a.text[:len(a.text) - 6])
                    break
        except NoSuchElementException:
            print("Could Not Be FOund, mass or formula")

    def getboilingpoint(self):
        try:
            elements = self.driver.find_element_by_css_selector("section#Boiling-Point").find_elements_by_css_selector(
                "div.section-content-item")
            i = random.choice(elements)
            self.boilingpoint = i.find_element_by_tag_name('p').text
        except NoSuchElementException as s:
            self.boilingpoint = NOTFOUND

    def getmeltingpoint(self):
        try:
            elements = self.driver.find_element_by_id("Melting-Point").find_elements_by_css_selector(
                "div.section-content-item")
            i = random.choice(elements)
            self.meltingpoint = i.find_element_by_tag_name('p').text
        except:
            print("Could not be found melting point")
            self.meltingpoint = NOTFOUND

    def getdensity(self):
        try:
            elements = self.driver.find_element_by_css_selector("section#Density").find_elements_by_css_selector(
                "div.section-content-item")
            i = random.choice(elements)
            self.density = i.find_element_by_tag_name('p').text
        except NoSuchElementException:
            print("Could not be found")

    def getvapordensity(self):
        try:
            element = self.driver.find_element_by_css_selector("section#Vapor-Density")
            elements = element.find_elements_by_class_name("section-content-item")
            i = elements[0]
            vap = i.find_element_by_tag_name('p').text
            print(vap[:5])
            self.vapourdensity = vap[:5]
        except NoSuchElementException:
            self.vapourdensity = NOTFOUND

    def find_hazards(self):
        try:
            table = 'table.summary.f-1.f-lh-15.with-padding-small.fixed-layout.no-border-last-row.rowed'
            element1 = self.driver.find_element_by_css_selector(table)
            tabcont = element1.find_elements_by_tag_name('tr')
            for cont in tabcont:
                try:
                    hazards = cont.find_elements_by_css_selector("div.captioned.caption-lg.f-gray.inline-block::after")
                except:
                    continue
            for i in hazards:
                print(i.text)
                self.hazards.append(i.text)
        except NoSuchElementException:
            print("Could not be Found hazards")

    def getothernames(self):
        try:
            table = 'table.summary.f-1.f-lh-15.with-padding-small.fixed-layout.no-border-last-row.rowed'
            element1 = self.driver.find_element_by_css_selector(table)
            element1 = element1.find_elements_by_tag_name('tr')
            for i in element1:
                # print(i.text.startswith("Synonyms"))
                try:
                    subelement = i.find_element_by_class_name('truncated-columns')
                except:
                    continue
                othername = subelement.find_elements_by_tag_name('p')
                for j in othername:
                    self.othernames.append(j.text)
        except NoSuchElementException:
            self.othernames = NOTFOUND


def findbyquery(query: str = None):
    query = query.lower()
    if query.__contains__(" "):
        query = query.replace(" ", "%20")
    searchurl = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{query}/cids/txt?name_type=complete"
    response = requests.get(searchurl)
    cids = response.text.split()
    result = []
    if len(cids) > 5:
        cids = cids[:6]
    for i in cids:
        print(i)
        nameurl = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{int(i)}/description/XML"
        response = requests.get(nameurl)
        xmlresponse = response.text
        mydoc = minidom.parseString(xmlresponse)
        title_element = mydoc.getElementsByTagName("Title")
        title = title_element[0].firstChild.data
        imageurl = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{int(i)}/record/PNG"
        try:
            desc_element = mydoc.getElementsByTagName("Description")
            description = desc_element[0].firstChild.data
        except:
            description = "Nothing Found"
        result.append({'Name': title,
                       'Description': description,
                       'Url': imageurl,
                       'CID': int(i)
                       })
    return result
