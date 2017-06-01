'''
Created on 02/12/2015

@author: david
'''

from SocketServer import TCPServer, StreamRequestHandler
import json
import traceback


class Dispatcher(StreamRequestHandler): 

    def setup(self):
        
        StreamRequestHandler.setup(self)
                
        
    def finish(self):
        
        StreamRequestHandler.finish(self)        
    
    
    def handle(self):
        
        print "New dialog"

        try:
            done = False
            while not done:
                
                rawMessage = self.rfile.readline().strip()
                
                if rawMessage != "":
                    message = json.loads(rawMessage)
                    
                    print "key: {0}; data: {1}".format(message["key"], message["data"])                    
    
                    done = message["key"] == "close"                   
                    
                else:
                    done = True
                    
        except Exception as ex:
            
            print "Dispatching-error {0}".format(ex)   
            print traceback.format_exc()                 

        print "End request"


def main():
    
    server = TCPServer(("127.0.0.1", 2121), Dispatcher)

    print "I'm waiting for commands..."
    try:
        server.serve_forever()
    finally:
        print "Goodbye!"



if __name__ == '__main__':
    
    main()
