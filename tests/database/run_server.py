
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'platform')))
os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'platform')))


from tornado.ioloop import IOLoop
from tornado.web import Application
from tornado.httpserver import HTTPServer
from tornado.options import define, options, parse_command_line
from interface.server import BasicHandler, ShutdownHandler, EncryptedHandler
from database.manager import (DeleteDataBaseManager,
                              RegisterDataBaseManager,
                              SearchDataBaseManager,
                              UpdateDataBaseManager)
import yaml

# define("port", default=8084, help="run on the given port", type=int)
define("address", default='127.0.0.1', help="address to run", type=str)
define("debug", default=True, help="run in debug mode")

def make_app(config):
    app = Application([
                        (r"/registry/delete", BasicHandler, dict(database=DeleteDataBaseManager(config=config))),
                        (r"/registry/register", BasicHandler, dict(database=RegisterDataBaseManager(config=config))),
                        (r"/registry/search", BasicHandler, dict(database=SearchDataBaseManager(config=config))),
                        (r"/registry/update", BasicHandler, dict(database=UpdateDataBaseManager(config=config))),
                        (r"/shutdown", ShutdownHandler)],
                        debug=options.debug
                     )
    return app

def main():
    config = yaml.full_load(open(os.getenv("CONFIG_FILE"), 'r'))['databases']['redis']
    app = make_app(config)
    server1 = HTTPServer(app, xheaders=False) # True if with nginx
    server2 = HTTPServer(app, xheaders=False) # True if with nginx
    ports = [8084,8085]
    server1.listen(port=ports[0], address=options.address)
    server2.listen(port=ports[1], address=options.address)
    #server1.start(0)  # forks one process per cpu
    #server2.start(0)  # forks one process per cpu
    IOLoop.current().start()

if __name__ == "__main__":
    main()
