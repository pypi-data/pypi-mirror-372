#!/usr/bin/env python3
from ...imports import *
import clipboard,os, logging, traceback, threading, io, sys, faulthandler, traceback, signal
from typing import *
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler
from abstract_gui import attach_functions, startConsole
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



