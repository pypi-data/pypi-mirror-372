#!/usr/bin/env python3
import clipboard,os, logging, traceback, threading, io, sys, faulthandler, traceback, signal
from typing import *
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler
from ...content_utils.file_utils import get_directory_map, findGlobFiles

from ...file_filtering.file_filters import collect_filepaths
from ...python_utils.utils.utils import get_py_script_paths
from ...content_utils.diff_engine import plan_previews,apply_diff_text,ApplyReport,write_text_atomic 
from ...content_utils.find_content import findContent,getLineNums,findContentAndEdit,findContent,get_line_content

# your code: the functions you pasted
# ✅ Qt6 imports
from PyQt6 import QtGui, QtCore, QtWidgets
from PyQt6.QtGui import (
    QTextCursor, QDesktopServices, QKeySequence, QGuiApplication,
    QClipboard, QTextOption
    )
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, Qt, QSignalBlocker, QRect, QSize, QTimer, QUrl,
    QObject, QPropertyAnimation, QSettings
    )
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QTabWidget,
    QLabel, QLineEdit, QPushButton, QTextEdit, QListWidget, QListWidgetItem,
    QCheckBox, QFileDialog, QSpinBox, QMessageBox,QToolButton, QHBoxLayout,
    QLayout,QButtonGroup,QScrollArea,QLayout,  QSizePolicy, QLayout,
    QMainWindow ,QComboBox, QRadioButton,QListView
)



