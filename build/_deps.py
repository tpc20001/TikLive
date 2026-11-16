# TikLive 程式（app\*.py）會用到的每個模組都列在這裡，PyInstaller 才會包進 EXE。
# 多列一些標準庫：以後只換程式（不換 EXE）也能用到。
import array, asyncio, atexit, base64, bisect, collections, concurrent.futures, contextlib, contextvars, csv  # noqa
import ctypes, ctypes.wintypes, dataclasses, datetime, email, functools, gc, glob, gzip, hashlib, heapq, hmac, html  # noqa
import html.parser, http.client, http.cookies, importlib, importlib.metadata, io, itertools, json, locale, logging  # noqa
import math, mimetypes, operator, os, pathlib, platform, queue, random, re, secrets, shutil, signal, socket, sqlite3  # noqa
import ssl, statistics, string, struct, subprocess, sys, tempfile, textwrap, threading, time, traceback, typing  # noqa
import unicodedata, urllib.error, urllib.parse, urllib.request, uuid, wave, weakref, zipfile, zlib  # noqa
import py_compile, ast, xml.etree.ElementTree, runpy, copy, fnmatch, numbers, pprint, shlex  # noqa
from PySide6 import QtCore, QtGui, QtWidgets, QtMultimedia, QtNetwork  # noqa
import httpx  # noqa
import TikTokLive  # noqa
from TikTokLive import TikTokLiveClient  # noqa
from TikTokLive.events import ConnectEvent, DisconnectEvent  # noqa
import TikTokLive.client.errors, TikTokLive.client.web.web_client, TikTokLive.client.web.web_settings  # noqa
import TikTokLive.client.web.routes.fetch_is_live, TikTokLive.client.web.routes.fetch_room_id_api  # noqa
import TikTokLive.client.web.routes.fetch_room_id_live_html, TikTokLive.client.web.routes.fetch_signed_websocket  # noqa
