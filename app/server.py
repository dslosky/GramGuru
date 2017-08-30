import time
import os
import sys
from multiprocessing import Process
from worker import Worker

class Server(object):
    '''
    Runs a loop that generates workers as new processes. These workers get 
    tasks from the database, and will just die if no tasks are available.

    run from the command line in the background:
    python server.py &
    '''
    def __init__(self):
        self.stop_loop = False
        self.stop_server = False
        self.sleep = 5
        
    def loop(self):
        """
        Starts the server loop, and contains the code that is looped by
        the server
        """
        while self.stop_loop is not True:
            self.main()
            time.sleep(self.sleep)

    def main(self):
        '''
        Spins up a new worker to look for jobs
        '''

        w = Worker()
        p = Process(target=w.run)
        p.start()
        return

    def stop(self):
        """
        Stop the server
        """
        
        self.stop_loop = True
        return

            
if __name__ == '__main__':
    server = Server()
    server.loop()
    
    