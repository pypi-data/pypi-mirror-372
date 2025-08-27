#!/usr/bin/env python3
from typing import *
from functools import partial, lru_cache
from abstract_utilities import eatAll
from abstract_utilities.type_utils import MIME_TYPES
from PyQt6 import QtGui, QtCore, QtWidgets
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
import time,  pydot, inspect, threading, enum, sys, requests, subprocess, os, logging, traceback, re, json,clipboard, logging, traceback, threading, io, sys, faulthandler, traceback, signal
from abstract_utilities import is_number,make_list,safe_read_from_json,read_from_file,make_dirs,eatAll
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler
