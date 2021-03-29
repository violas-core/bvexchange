#! /usr/bin/python3

class ReadonlyException(Exception):
    def __init__(self, error = ""):
        self.error = "only read property. {}".format(error)

    def __str__(self):
        return self.error

