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
        self.last_run_time = 0
        
    def loop(self):
        """
        Starts the server loop, and contains the code that is looped by
        the server
        """
        while self.stop_loop is not True:
            self.main()
            time.sleep(self.sleep)

    def main(self):
        # check database for users that need processing

        # spin a new process that will go and find their info and run the names
        # I'll just use a time trigger for now...
        if time.time() > self.last_run_time + 3600:
            self.last_run_time = time.time()
            w = Worker()
            p = Process(target=w.run_likes)
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
    
    