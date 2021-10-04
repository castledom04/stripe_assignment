#!/bin/bash

flake8 . --exclude=migrations,apps.py,settings.py,__init__.py --ignore=E501,E722,W503
