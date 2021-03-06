from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

import time
import datetime
import json
import random
import sys

from orm import *
from util import shuffle, Configs, log
CONFIG = Configs()

class Insta(object):
    def __init__(self):
        # load settings

        # load the driver
        if CONFIG['browser'] == 'chrome':
            self.driver = webdriver.Chrome()
        elif CONFIG['browser'] == 'phantomjs':
            self.driver = webdriver.PhantomJS()
        else:
            raise Exception('No browser configured; add one to configs.json')
        
        # open instagram
        self.user = None
        self.driver.get('https://instagram.com')
        self.main_handle = self.driver.window_handles[0]

    def search(self, tag):
        self.driver.get('https://www.instagram.com/explore/tags/' + tag + '/')

    def scroll(self, count=0):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        try:
            self.driver.find_element_by_xpath("//*[contains(text(), 'Load more')]").click()
            time.sleep(1)
        except:
            pass

        for i in range(count):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

    def open_tabs(self, tag='', scroll_count=0):
        '''
        Open up a bunch of tabs of individual photo urls
        '''

        self.scroll(count=scroll_count)

        links = self.driver.find_elements_by_xpath("//a")
        links = shuffle(links)

        # set a page limit to avoid overclocking
        page_limit = min(CONFIGS['pageLimit'], len(links))
        for a in links[:page_limit]:
            if a.get_attribute('href') not in CONFIGS['avoidUrls']:
                try:
                    self.driver.execute_script('window.open("' + a.get_attribute('href') + '","_blank");')
                except Exception as e:
                    pass
        # wait for all the tabs to open
        time.sleep(2)

    def close_open_tabs(self):
        for window in self.driver.window_handles:
            if window != self.main_handle:
                try:
                    self.driver.execute_script('window.close()')
                except:
                    # window already deleted
                    pass


    def follow(self, tag):
        '''
        Follow users found by searching for a specific tag
        '''
        self.open_tabs(tag=tag, scroll_count=0)
    
        # scroll to the tabs and follow everyone
        new_follows = []
        finished = False
        for window in self.driver.window_handles:
            if window != self.main_handle:
                self.driver.switch_to_window(window)
                time.sleep(1)

                if self.is_following() or not self.can_follow():
                    # skip this one, we're already following
                    self.driver.execute_script('window.close()')
                    continue
                else:
                    button = self.driver.find_element_by_xpath("//*[contains(text(), 'Follow')]")
                    actionChains = ActionChains(self.driver)
                    actionChains.click(button).perform()
                    time.sleep(2)

                if self.is_following():
                    # Save the followers we're adding so we can track them
                    new_follows += [(self.driver
                                        .find_element_by_class_name('notranslate')
                                        .get_attribute('text'))]
                else:
                    # maxed out follows, time to quit
                    finished = True
                    # close the tabs
                    self.close_open_tabs()
                    break
                
                # close the window
                self.driver.execute_script('window.close()')

        self.driver.switch_to_window(self.main_handle)

        #log('Followed {} in #{} for {}'.format(len(new_follows), tag, self.user))
        return new_follows, finished

    def is_following(self):
        '''
        Check if this user is already being followed
        '''
        try:
            self.driver.find_element_by_xpath("//*[contains(text(), 'Following')]")
        except:
            return False
        return True

    def can_follow(self):
        '''
        Check if there is an option to follow available
        '''
        try:
            self.driver.find_element_by_xpath("//*[contains(text(), 'Follow')]")
        except:
            return False
        return True
    
    def unfollow(self, following=None):
        deleted = []
        delete_count = 0
        for follow in following:
            self.driver.get('https://www.instagram.com/' + follow + '/')
            time.sleep(2)
            if self.is_following():
                button = self.driver.find_element_by_xpath("//*[contains(text(), 'Following')]")
                actionChains = ActionChains(self.driver)
                actionChains.click(button).perform()
                time.sleep(1)
                self.driver.get('https://www.instagram.com/' + follow + '/')
                time.sleep(2)
                if self.is_following():
                    # the unfollow didn't work
                    try:
                        self.driver.find_element_by_xpath("//*[contains(text(), 'Following')]").click()
                        # can't unfollow, time to stop
                        break
                    except:
                        # Looks like it might be okay
                        deleted += [follow]
                        delete_count += 1
                else:
                    deleted += [follow]
                    delete_count += 1
            else:
                deleted += [follow]
        
        
        #log('Unfollowed {} people for {}'.format(delete_count, self.user))
        return deleted

    def like_feed(self, scroll_count=2):
        self.driver.get('https://www.instagram.com/')
        self.scroll(count=scroll_count)
        pics = self.driver.find_elements_by_class_name("_si7dy")

        for pic in pics:
            actionChains = ActionChains(self.driver)
            actionChains.double_click(pic).perform()
            time.sleep(2)

        #log('Liked {} in feed for {}'.format(len(pics), self.user))
        return len(pics)

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

        #log('Liked {} in #{} for {}'.format(count, tag, self.user))
        return count

    def count_followers(self, username):
        self.driver.get('https://www.instagram.com/' + username + '/')
        el = self.driver.find_element_by_xpath("//*[contains(text(), 'followers')]")
        el_str = el.text
        
        # just full the follower count out of there
        nums = '0123456789'
        f_count_str = ''
        for l in el_str:
            if l in nums:
                f_count_str += l

        return int(f_count_str)

    def login(self, username='', password=''):
        if not username:
            with open('user.json', 'r') as user_json:
                user = json.loads(user_json.read())
            username = user['username']
            password = user['password']
        
        self.user = username
        self.driver.find_element_by_link_text('Log in').click()
        self.driver.find_element_by_name('username').send_keys(username)
        self.driver.find_element_by_name('password').send_keys(password)
        self.driver.find_element_by_xpath("//*[contains(text(), 'Log in')]").click()
        time.sleep(3)
        # check if the login worked
        try:
            login_el = self.driver.find_element_by_xpath("//*[contains(text(), 'Log in')]")
            # If that element is found, we're still on the login page... bad credentials
            return False
        except Exception as e:
            # no more login element, login successful!
            return True

if __name__ == '__main__':
    session = Session()
    username = sys.argv[1]
    user = session.query(IUser).filter(IUser.username == username)
    insta = Insta()
    insta.login(username=username)
    time.sleep(1)

    tag_names = [t.tag for t in user.tags]
    tags = shuffle(tag_names)

    if sys.argv[2] == 'like':
        for tag in tags:
            try:
                insta.search(tag)
                insta.like_tag(tag)
            except Exception as e:
                msg = 'Like failed on #{}'.format(tag)
                log(msg=msg, err=e)
            time.sleep(5)

    elif sys.argv[2] == 'feed':
        try:
            insta.like_feed()
        except Exception as e:
            msg = 'Feed failed'
            log(msg=msg, err=e)

    elif sys.argv[2] == 'follow':
        for tag in tags:
            try:
                insta.search(tag)
                users, finished = insta.follow(tag)
                if finished is True:
                    break

                time.sleep(5)
            except Exception as e:
                msg = 'Follow failed on #{}'.format(tag)
                log(msg=msg, err=e)

    elif sys.argv[2] == 'unfollow':
        try:
            insta.unfollow()
        except Exception as e:
            msg = 'Unfollow failed'
            log(msg=msg, err=e)

    insta.driver.quit()
    Session.remove()