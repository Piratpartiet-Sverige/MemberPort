#!/usr/bin/env python

from unittest import defaultTestLoader
from os import path
from tornado import testing


def all():
    suite = defaultTestLoader.discover('./app/test', 'test_*.py', path.dirname(path.abspath(__file__)))
    print(suite)
    return suite


if __name__ == '__main__':
    testing.main()
