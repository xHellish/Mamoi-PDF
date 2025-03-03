
# -------------------------------------------------------- #
# Librerías necesarias para el funcionamiento de la App
from googlesearch import search

import sys
import requests
import fitz  # PyMuPDF

from PIL.ImageQt import ImageQt  
from PIL import Image

from PyQt5.QtCore import Qt, QPropertyAnimation, QTimer, QVariantAnimation
from PyQt5.QtGui import QFont, QColor, QPixmap, QImage
from PyQt5.QtWidgets import (
    QApplication, QWidget, QErrorMessage, QFrame, QVBoxLayout, 
    QHBoxLayout, QLineEdit, QPushButton, QLabel, QScrollArea
)