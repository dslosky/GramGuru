import time
import os
import sys
from multiprocessing import Process
import socket
import select as select_

from worker import Worker
from util import log

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
        self.port = 4555
        self.socket = socket.socket()

    def setup_socket(self):
        """
        Connects the server to a specific socket
        """
        connected = False
        attempts = 0
        while connected is False and attempts < 60:
            try:
                self.socket.bind(('', self.port))
                self.socket.listen(5)
                connected = True
                
            except:
                time.sleep(2)
            attempts += 1

    def check_socket(self):
        """
        Check if any connections have been established
        """
        conns = select_.select([self.socket], [], [], 0)[0]
        if len(conns) > 0:
            conn, addr = self.socket.accept()
            conn.setblocking(0)
            
            mess_check = select_.select([conn], [], [], 60)[0]
            if len(mess_check) > 0:
                # receive the message
                data = ''
                part = None
                while part != "" and mess_check != []:
                    part = conn.recv(4096).decode()
                    data += part
                    mess_check = select_.select([conn], [], [], 0)[0]
                
                if data == 'shutdown':
                    self.stop()
        
    def loop(self):
        """
        Starts the server loop, and contains the code that is looped by
        the server
        """
        log(msg="Server started.")
        while self.stop_loop is not True:
            self.main()
            self.check_socket()
            time.sleep(self.sleep)


        log(msg="Server stopped.")
        

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
        log(msg="Shutting down server...")
        return

    def shutdown(self):
        """
        Shutdown method run from the command line to stop an instance
        of a running server

        Usage:
        python server.py stop
        """
        # connect to the server
        conn = socket.socket()
        conn.settimeout(3)
        conn.connect(('localhost', self.port))
        conn.send('shutdown'.encode())
        conn.shutdown(1)

    @staticmethod
    def usage():
        return """
GramGuru Server Usage:
----------------------

    python server.py [OPTION]

    Options:
    --------
    start   Starts the server
    stop    Connects to an already running server to stop it
    help    Prints this message
    """
    
if __name__ == '__main__':
    server = Server()
    if len(sys.argv) > 1:
        if sys.argv[1] == 'start':
            log(msg="Starting server...")
            server.setup_socket()
            server.loop()
        
        elif sys.argv[1] == 'stop':
            server.shutdown()
        
        elif sys.argv[1] == 'help':
            print(server.usage())
        else:
            print(server.usage())
    else:
        print(server.usage())
    