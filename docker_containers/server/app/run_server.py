logger_name = "PLATFORM"

import logging
import os
import sys

import yaml
from database.manager import (
    DeleteDataBaseManager,
    RegisterDataBaseManager,
    SearchDataBaseManager,
    UpdateDataBaseManager,
)
from interface.server import BasicHandler, EncryptedHandler, ShutdownHandler
from msg_logging.MsgLog import LogInit
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import define, options, parse_command_line
from tornado.web import Application
from utils import log_level


def make_app(config):
    app = Application(
        [
            (
                r"/registry/delete",
                BasicHandler,
                dict(database=DeleteDataBaseManager(config=config)),
            ),
            (
                r"/registry/register",
                BasicHandler,
                dict(database=RegisterDataBaseManager(config=config)),
            ),
            (
                r"/registry/search",
                BasicHandler,
                dict(database=SearchDataBaseManager(config=config)),
            ),
            (
                r"/registry/update",
                BasicHandler,
                dict(database=UpdateDataBaseManager(config=config)),
            ),
            (r"/shutdown", ShutdownHandler),
        ],
        debug=False,  # server.start requires False
    )
    return app


def main():
    config = yaml.full_load(open(os.getenv("CONFIG_FILE"), "r"))["databases"]["redis"]
    app = make_app(config)
    server1 = HTTPServer(app, xheaders=True)  # True if with nginx
    server1.listen(port=os.getenv("PORT1"), address=os.getenv("HOST"))
    server1.start(
        num_processes=0, max_restarts=1
    )  # num_processes=0 - forks one process per cpu
    IOLoop.current().start()


if __name__ == "__main__":
    log = LogInit(
        logger_name,
        os.path.join("../app", "logs", "logs.log"),
        debuglevel=log_level("INFO"),
        log=True,
    )
    main()
