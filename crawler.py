from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

import time
import json
import random
import sys
import copy

class Insta(object):
    def __init__(self):
        # load settings
        with open('configs.json', 'r') as configs:
            conf = json.loads(configs.read())
        
        # load the driver
        if conf['browser'] == 'chrome':
            self.driver = webdriver.Chrome()
        elif conf['browser'] == 'phantomjs':
            self.driver = webdriver.PhantomJS()
        else:
            raise Exception('No browser configured; add one to configs.json')
        
        # open instagram
        self.driver.get('https://instagram.com')
        self.main_handle = self.driver.window_handles[0]
        self.configs = conf

    def search(self, tag):
        self.driver.get('https://www.instagram.com/explore/tags/' + tag + '/')

    def scroll(self, count=0):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        try:
            self.driver.find_element_by_xpath("//*[contains(text(), 'Load more')]").click()
            time.sleep(1)
        except:
            pass

        for i in xrange(count):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

    def open_tabs(self, tag='', scroll_count=0):
        self.scroll(count=scroll_count)

        links = self.driver.find_elements_by_xpath("//a")
        links = shuffle(links)

        # set a page limit to avoid overclocking
        page_limit = min(self.configs['pageLimit'], len(links))
        for a in links[:page_limit]:
            if a.get_attribute('href') not in self.configs['avoidUrls']:
                self.driver.execute_script('window.open("' + a.get_attribute('href') + '","_blank");')

        # wait for all the tabs to open
        time.sleep(2)

    def follow(self, tag):
        open_tabs(tag=tag, scroll_count=0)
        new_follows = []
        for window in self.driver.window_handles:
            if window != self.main_handle:
                self.driver.switch_to_window(window)

                try:
                    button = self.driver.find_element_by_xpath("//*[contains(text(), 'Following')]")
                except Exception as e:
                    try:
                        button = self.driver.find_element_by_xpath("//*[contains(text(), 'Follow')]")
                        button.click()
                        time.sleep(5)
                        new_follows += [(self.driver
                                                .find_element_by_class_name('notranslate')
                                                .get_attribute('text'))]
                    except Exception as e:
                        pass

            # close the window
            self.driver.execute_script('window.close()')

        self.driver.switch_to_window(self.main_handle)

        if len(new_follows) > 0:
            with open('following.json', 'r') as file_:
                following = json.loads(file_.read())
                following['following'] += new_follows
                following['following'] = list(set(following['following']))

            with open('following.json', 'w') as file_:
                file_.write(json.dumps(following, indent=4))

        return new_follows

    def unfollow_all(self):
        with open('following.json', 'r') as file_:
            current_lst = json.loads(file_.read())

        failed = []
        deleted = []
        for user in current_lst['following']:
            try:
                self.driver.get('https://www.instagram.com/' + user + '/')
                button = self.driver.find_element_by_xpath("//*[contains(text(), 'Following')]")
                button.click()
                deleted += [user]
            except Exception as e:
                failed += [user]

        failed_json = json.dumps({"following": [], "failedToDelete": failed}, indent=4)
        with open('following.json', 'w') as file_:
            file_.write(failed_json)

        return deleted

    def like_feed(self, scroll_count=15):
        self.driver.get('https://www.instagram.com/')
        self.scroll(count=scroll_count)
        pics = self.driver.find_elements_by_class_name("_si7dy")

        for pic in pics:
            actionChains = ActionChains(self.driver)
            actionChains.double_click(pic).perform()
            time.sleep(2)

    def like_tag(self, tag, scroll_count=5):
        self.open_tabs(tag=tag, scroll_count=scroll_count)

        count = 0
        for window in self.driver.window_handles:
            if window != self.main_handle:
                self.driver.switch_to_window(window)
                try:
                    pic = self.driver.find_element_by_class_name("_si7dy")
                except:
                    self.driver.execute_script('window.close()')
                    continue

                actionChains = ActionChains(self.driver)
                actionChains.double_click(pic).perform()
                count += 1
                time.sleep(2)

                self.driver.execute_script('window.close()')

        self.driver.switch_to_window(self.main_handle)
        return count

    def login(self, username='', password=''):
        with open('user.json', 'r') as user_json:
            user = json.loads(user_json.read())
        
        self.driver.find_element_by_link_text('Log in').click()
        self.driver.find_element_by_name('username').send_keys(user['username'])
        self.driver.find_element_by_name('password').send_keys(user['password'])
        self.driver.find_element_by_xpath("//*[contains(text(), 'Log in')]").click()

def shuffle(lst):
    new_lst = []
    lst = copy.copy(lst)
    while len(lst) > 1:
        pos = int(round(random.random() * (len(lst)-1)))    
        item = lst.pop(pos)
        new_lst.append(item)

    new_lst += lst
    return new_lst

if __name__ == '__main__':
    insta = Insta()
    insta.login()
    time.sleep(1)

    with open('user.json', 'r') as user_json:
        user = json.loads(user_json.read())

    tags = shuffle(user['tags'])

    if sys.argv[1] == 'like':
        for tag in tags:
            insta.search(tag)
            insta.like_tag(tag)
            time.sleep(5)

    if sys.argv[1] == 'feed':
        insta.like_feed()

    elif sys.argv[1] == 'follow':
        for tag in tags:
            insta.search(tag)
            insta.follow(tag)
            time.sleep(5)

    insta.driver.quit()