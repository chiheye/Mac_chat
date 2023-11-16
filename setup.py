"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['chat.py']
DATA_FILES = []
OPTIONS = {
    'iconfile': 'chat.icns'  # Specify the path to your .icns file
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
