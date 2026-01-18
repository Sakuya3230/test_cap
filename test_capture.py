# -*- coding: utf-8 -*-try:

import maya.cmds as cmds
import maya.OpenMayaUI as omui
import maya.api.OpenMaya as om2
import maya.api.OpenMayaUI as omui2

import math
import os

try:
    from PySide6 import QtWidgets, QtGui, QtCore
    from shiboken6 import wrapInstance
except ImportError:
    from PySide2 import QtWidgets, QtGui, QtCore
    from shiboken2 import wrapInstance
    
    
try:
    from PySide6.QtWidgets import *
    from PySide6.QtGui import *
    from PySide6.QtCore import *
    from shiboken6 import wrapInstance
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from shiboken2 import wrapInstance
    
WINDOW_TITLE = "Test Main Window"
OBJECT_NAME = "testMainWindow"

class CaptureUtils(object):
    @staticmethod
    def find_panel_from_view(view):
        panels = cmds.getPanel(type="modelPanel")

        for panel in panels:
            temp_view = omui2.M3dView.getM3dViewFromModelPanel(panel)
            if temp_view.widget() == view.widget():
                return panel
        
        return None
    
    @staticmethod    
    def capture_active_view(path):
        view = omui2.M3dView.active3dView()
        
        panel = CaptureUtils.find_panel_from_view(view)
        orig = cmds.modelEditor(panel, q=True, hud=True)
        cmds.modelEditor(panel, e=True, hud=False)

        img = om2.MImage()
        view.refresh()
        view.readColorBuffer(img, True)
        img.writeToFile(path, "jpg")
        
        cmds.modelEditor(panel, e=True, hud=orig)
        
        return QPixmap(path)

class CaptureThumbnail(QWidget):
    def __init__(self, pixmap=None, parent=None):
        super(CaptureThumbnail, self).__init__(parent)
        self.setFixedSize(256, 256)
        self._pixmap = pixmap
        self._border_color = QColor(210, 100, 210)
        self._border_width = 2
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if self._pixmap:
            scaled_pixmap = self._pixmap.scaled(256, 256, mode=Qt.SmoothTransformation)
            x = (self.width() - scaled_pixmap.width()) / 2
            y = (self.height() - scaled_pixmap.height()) / 2
            painter.drawPixmap(x, y, scaled_pixmap)
            
        else:
            #　ドットの境界線を描画
            pen = QPen(self._border_color)
            pen.setStyle(Qt.DashLine)
            pen.setCapStyle(Qt.FlatCap)
            pen.setJoinStyle(Qt.MiterJoin)
            pen.setWidth(5)
            pen.setWidth(self._border_width)
            painter.setPen(pen)
            painter.drawRect(self._border_width / 2, self._border_width / 2,
                             self.width() - self._border_width, self.height() - self._border_width)
            
            # テキストを中央に描画            
            text = "No Image"
            font = QFont("Arial", 14)
            painter.setFont(font)
            text_rect = painter.fontMetrics().boundingRect(text)
            painter.drawText((self.width() - text_rect.width()) / 2, (self.height() - text_rect.height()) / 2, text)

    def setPixmap(self, pixmap):
        self._pixmap = pixmap
        self.update()
        
    def savePixmap(self, path=None, size=256):
        if self._pixmap:
            if path is None:
                path, _ = QFileDialog.getSaveFileName(self, "Save Capture", "", "JPEG Files (*.jpg);;PNG Files (*.png)")
            
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))
                
            pixmap = self._pixmap.scaled(size, size, mode=Qt.SmoothTransformation)
            pixmap.save(path)

class TestMainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(TestMainWindow, self).__init__(parent)

        self.setWindowTitle(WINDOW_TITLE)
        self.setObjectName(OBJECT_NAME)
        self.resize(256, 288)
        
        self.setup_ui()
        
    def setup_ui(self):
        self.central_widget = QWidget(self)
        self._layout = QVBoxLayout(self.central_widget)
        self._layout.setSpacing(2)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setAlignment(Qt.AlignHCenter)

        self.setCentralWidget(self.central_widget)

        self._capture_label = CaptureThumbnail()
        self._capture_label.setFixedSize(256, 256)
        self._layout.addWidget(self._capture_label)
        
        self._capture_button = QPushButton("Capture Active View")
        self._capture_button.setFixedHeight(30)
        self._capture_button.clicked.connect(self._on_capture_button_clicked)
        self._layout.addWidget(self._capture_button)
        
        self._save_button = QPushButton("Save Capture")
        self._save_button.setFixedHeight(30)
        self._save_button.clicked.connect(self._on_save_button_clicked)
        self._layout.addWidget(self._save_button)

    def _on_capture_button_clicked(self):
        pixmap = CaptureUtils.capture_active_view(r"D:\panel_capture.jpg")
        self._capture_label.setPixmap(pixmap)
        
    def _on_save_button_clicked(self):
        self._capture_label.savePixmap(r"D:\panel_capture_saved.jpg")

def main():
    maya_main_window = wrapInstance(int(omui.MQtUtil.mainWindow()), QWidget)
    this_win = maya_main_window.findChild(QWidget, OBJECT_NAME)
    if this_win:
        this_win.close()
        this_win.deleteLater()
    
    app = QApplication.instance()
    win = TestMainWindow(maya_main_window)
    
    win.show()
    app.exec_()
