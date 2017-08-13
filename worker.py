from crawler import Insta, shuffle
import time
import json

class Worker(object):
    def __init__(self):
        pass

    def run_likes(self):
        insta = Insta()
        insta.login()
        time.sleep(1)

        # get tags, these will come from the db
        with open('user.json', 'r') as user_json:
            user = json.loads(user_json.read())

        tags = shuffle(user['tags'])
        like_count = 0
        for tag in tags:
            insta.search(tag)
            like_count += insta.like_tag(tag)
            time.sleep(5)

        insta.driver.quit()
        return like_count
