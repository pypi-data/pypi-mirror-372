import os
import re
import time
from bs4 import BeautifulSoup
from pypers.steps.base.fetch_step_http import FetchStepHttpAuth
from pypers.utils.utils import ls_dir
from datetime import datetime

#from selenium import webdriver
#from selenium.webdriver.chrome.options import Options
#from selenium.webdriver.common.by import By
#from selenium.webdriver.support.wait import WebDriverWait

class Trademarks(FetchStepHttpAuth):

    pattern = re.compile("^apc(\d+)\.zip$")

    spec = {
        "version": "2.0",
        "descr": [
            "Fetch using HTTP GET"
        ],
        "args":
        {
            "params": [
                {
                    "name": "file_xml_regex",
                    "type": "str",
                    "descr": "regular expression to filter files",
                    "value": ".*"
                },
                {
                    "name": "file_img_regex",
                    "type": "str",
                    "descr": "regular expression to filter files",
                    "value": ".*"
                }
            ],
        }
    }

    def _process_from_local_folder(self):
        # getting files from local dir
        if self.fetch_from.get('from_dir'):
            self.logger.info(
                'getting %s files that match the regex [%s] from %s' % (
                    'all' if self.limit == 0 else self.limit,
                    '%s or %s' % (self.file_xml_regex, self.file_img_regex),
                    self.fetch_from['from_dir']))
            xml_archives = ls_dir(
                os.path.join(self.fetch_from['from_dir'], '*'),
                regex=self.file_xml_regex, limit=self.limit,
                skip=self.done_archives)

            img_archives = ls_dir(
                os.path.join(self.fetch_from['from_dir'], '*'),
                regex=self.file_img_regex % ('.*'), limit=self.limit,
                skip=self.done_archives)
            self.output_files = xml_archives + img_archives
            return True
        return False

    def specific_http_auth_process_exp(self, session):
        print("self.page_url:", self.page_url)
        page_img_url = "https://bulkdata.uspto.gov/data/trademark/application/images/" + str(datetime.today().year) + '/'
        print("page_img_url:", page_img_url)

        cmd = 'wget -q --retry-connrefused --waitretry=15 ' \
              '--read-timeout=60 --timeout=15 -t 5 %s ' \
              '--directory-prefix=%s'

        # download archives for xml applications with Selenium
        '''
        options = Options()
        #options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36")
        options.add_argument("--window-size=1920,1080")

        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(2)
        driver.get(self.page_url + "?fileDataFromDate=2025-01-01&fileDataToDate=2025-07-01")
        #driver.get(self.page_url)
        print("loading:", self.page_url+ "?fileDataFromDate=2025-01-01&fileDataToDate=2025-07-01")
        #print("loading:", self.page_url)
        time.sleep(10)
        #driver.get(self.page_url + "?fileDataFromDate=2025-01-01&fileDataToDate=2025-07-01")
        #time.sleep(20)
        print("current url:", driver.current_url)

        # downloaded xml archvie uid (180101) to get their matching images
        archive_uids = []

        #print(driver.page_source)

        elems = driver.find_elements(by=By.XPATH, value='.//a')

        print("found " + str(len(elems)) + " links in the page")

        for elem in elems: 
            print(elem.text)
            # pattern follows apc250630.zip
            if self.pattern.match(elem.text):
                # link to an archive, check if not already done
                if elem.text not in self.done_archives:
                    print("element:", elem.text)
                    archive_uid = re.sub(r'\D', '', elem.text)
                    archive_uids.append(archive_uid)

                    # this will trigger the download url of the XML archive, a link to a zip with a temporary token
                    elem.click()
                    print(driver.current_url)
        '''

        archive_uids = []

        # download archives for individual trademark images
        file_img_regex = self.file_img_regex % '|'.join(archive_uids)
        img_rgx = re.compile('.*%s' % file_img_regex,
                             re.IGNORECASE)
        marks_page = session.get(page_img_url, stream=True,
                                 proxies=self.proxy_params)
        download_lines = []
        # enough to look in the first 1000 lines
        for line in marks_page.text.splitlines():
            if line:
                if img_rgx.match(line):
                    download_lines.append(line)
        marks_dom = BeautifulSoup(''.join(download_lines), 'html.parser')
        # find marks links
        a_elts = marks_dom.findAll('a', href=img_rgx)
        a_links = [a.attrs['href'] for a in a_elts]

        count = 0
        for archive_path in a_links:
            archive_name = os.path.basename(archive_path)
            archive_url = os.path.join(page_img_url, archive_path)
            print(cmd % (archive_url, self.output_dir))
            count, should_break = self.parse_links(archive_name, count, cmd,
                                                   archive_url=archive_url)
            if should_break:
                break

        #driver.quit()

    def specific_http_auth_process(self, session):

        page_xml_url = os.path.join(self.page_url, 'dailyxml', 'applications/')
        page_img_url = os.path.join(self.page_url, 'application', 'images',
                                    str(datetime.today().year) + '/' )

        # regex to find xml archives download links
        xml_rgx = re.compile('^[^-]+\.zip', re.IGNORECASE)
        # downloaded xml archvie uid (180101) to get their matching images
        archive_uids = []

        cmd = 'wget -q --retry-connrefused --waitretry=15 ' \
              '--read-timeout=60 --timeout=15 -t 5 %s ' \
              '--directory-prefix=%s'
        # 1- download archives for xml applications
        # --------------------------------------
        count = 0
        marks_page = session.get(page_xml_url, proxies=self.proxy_params)
        marks_dom = BeautifulSoup(marks_page.text, 'html.parser')
        # find marks links
        a_elts = marks_dom.findAll('a', href=xml_rgx)
        a_links = [a.attrs['href'] for a in a_elts]
        #a_links.reverse()
        for archive_path in a_links:
            archive_name = os.path.basename(archive_path)
            archive_uid = re.sub(r'\D', '', archive_name)
            archive_uids.append(archive_uid)
            archive_url = os.path.join(page_xml_url, archive_name)
            # it had become increasingly hard to download xml archives
            print(cmd)
            count, should_break = self.parse_links(archive_name, count, cmd,
                                                   archive_url=archive_url)
            if should_break:
                break

        # 2- download archives for tm images
        # -------------------------------
        file_img_regex = self.file_img_regex % '|'.join(archive_uids)
        img_rgx = re.compile('.*%s' % file_img_regex,
                             re.IGNORECASE)
        marks_page = session.get(page_img_url, stream=True,
                                 proxies=self.proxy_params)
        download_lines = []
        # enough to look in the first 1000 lines
        for line in marks_page.text.splitlines():
            if line:
                if img_rgx.match(line):
                    download_lines.append(line)
        marks_dom = BeautifulSoup(''.join(download_lines), 'html.parser')
        # find marks links
        a_elts = marks_dom.findAll('a', href=img_rgx)
        a_links = [a.attrs['href'] for a in a_elts]

        count = 0
        for archive_path in a_links:
            archive_name = os.path.basename(archive_path)
            archive_url = os.path.join(page_img_url, archive_path)
            count, should_break = self.parse_links(archive_name, count, cmd,
                                                   archive_url=archive_url)
            if should_break:
                break
