# general utility functions shared by all other modules
import json
from cryptography.fernet import Fernet
import base64
import time
import random
import copy

class Configs(dict):
    def __init__(self,*arg,**kw):
        super(Configs, self).__init__(*arg, **kw)
    
        with open('configs.json', 'r') as f_:
            configs = json.loads(f_.read())

        for key, value in configs.items():
            self[key] = value

            if key == 'encryptionKey':
                self[key] = value.encode()

        if not self['encryptionKey']:
            key = Fernet.generate_key()
            self['encryptionKey'] = key
            self.save()

    def save(self):
        self['encryptionKey'] = self['encryptionKey'].decode()
        with open('configs.json', 'w') as file_:
            file_.write(json.dumps(self, indent=4))

        self['encryptionKey'] = self['encryptionKey'].encode()

def shuffle(lst):
    new_lst = []
    lst = copy.copy(lst)
    while len(lst) > 1:
        pos = int(round(random.random() * (len(lst)-1)))    
        item = lst.pop(pos)
        new_lst.append(item)

    new_lst += lst
    return new_lst

def rando_hour():
    '''
    Generate a random time between 45 and 75 mins
    '''
    return 2700 + (1800 * random.random())

def log(msg, err=None):
    timestamp = (datetime.datetime.fromtimestamp(time.time())
                                    .strftime('%Y-%m-%d %H:%M:%S'))
    if err is not None:
        error_msg = 'ERROR: {}: {}\n'.format(type(err), err)
    else:
        error_msg = ''

    with open('crawler.log', 'a') as log:
        log.write('{}: {}\n{}'.format(timestamp, msg, error_msg))