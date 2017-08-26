import time
import os
import sys
from multiprocessing import Process
from worker import Worker

class Server(object):

    
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
        # spin up a new worker and let it look for jobs
        w = Worker()
        p = Process(target=w.run)
        p.start()

    def stop(self):
        """
        Stop server loop; It will be restarted immediately. This
        functionality could be used to reload functions in the event
        of an update
        """
        
        self.stop_loop = True
        return {'status': 'finished',
                'message': 'Stopping loop...'}

            
if __name__ == '__main__':
    server = Server()
    server.loop()
    
    