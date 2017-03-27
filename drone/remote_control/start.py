# -*- coding: utf-8 -*-

'''
Created on 15/06/2015

@author: david
'''

import sys

if sys.version_info.major < 3:
    from SocketServer import TCPServer
else:
    from socketserver import TCPServer
import datetime
import logging

from remote_control.dispatching import Dispatcher


def main():
    
    logging.basicConfig(filename="remote_control_{0}.log".format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S")), \
                    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s', datefmt='%d/%m/%y %H:%M:%S', \
                    level=logging.ERROR)
    logging.info("**** [Starting server...] ****")
    
    server = TCPServer(("0.0.0.0", 2121), Dispatcher)

    message = "Waiting for remote control..." 
    logging.info(message)
    print(message)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("[CTRL+C] -> Stop")
    finally:
        print("Goodbye!")
        logging.info("**** [Server finish] ****")


if __name__ == '__main__':
    
    main()
    
    
