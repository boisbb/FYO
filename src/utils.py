from PyQt5.QtCore import QPoint
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from src.lens import Lens


class CollapsibleBox(QWidget):
    def __init__(self, title="", parent=None):
        super(CollapsibleBox, self).__init__(parent)
        self.title = title
        self.toggle_button = QToolButton(
            text=title, checkable=True, checked=False
        )
        self.toggle_button.setStyleSheet("QToolButton { border: none; }")
        self.toggle_button.setToolButtonStyle(
            Qt.ToolButtonTextBesideIcon
        )
        self.toggle_button.setArrowType(Qt.RightArrow)
        self.toggle_button.pressed.connect(self.on_pressed)

        self.toggle_animation = QParallelAnimationGroup(self)

        self.content_area = QScrollArea(
            maximumHeight=0, minimumHeight=0
        )
        self.content_area.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Fixed
        )
        self.content_area.setFrameShape(QFrame.NoFrame)

        lay = QVBoxLayout(self)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.toggle_button)
        lay.addWidget(self.content_area)

        self.toggle_animation.addAnimation(
            QPropertyAnimation(self, b"minimumHeight")
        )
        self.toggle_animation.addAnimation(
            QPropertyAnimation(self, b"maximumHeight")
        )
        self.toggle_animation.addAnimation(
            QPropertyAnimation(self.content_area, b"maximumHeight")
        )
        
        self.distanceSL = QSlider(Qt.Horizontal)
        self.distanceSL.setMinimum(0)
        self.distanceSL.setMaximum(100)
        self.distanceSL.setValue(0)
        self.distanceSL.setTickPosition(QSlider.TicksBelow)
        self.distanceSL.setTickInterval(2)
        self.distanceSL.valueChanged.connect(self.distanceChanged)
        self.distanceL = QLabel(f"Distance: {self.distanceSL.value()}")
        
        self.r1SL = QSlider(Qt.Horizontal)
        self.r1SL.setMinimum(-100)
        self.r1SL.setMaximum(100)
        self.r1SL.setValue(20)
        self.r1SL.setTickPosition(QSlider.TicksBelow)
        self.r1SL.setTickInterval(2)
        self.r1SL.valueChanged.connect(self.r1Changed)
        self.r1L = QLabel(f"Radius 1: {self.r1SL.value()}")
        
        self.r2SL = QSlider(Qt.Horizontal)
        self.r2SL.setMinimum(-100)
        self.r2SL.setMaximum(100)
        self.r2SL.setValue(-20)
        self.r2SL.setTickPosition(QSlider.TicksBelow)
        self.r2SL.setTickInterval(2)
        self.r2SL.valueChanged.connect(self.r2Changed)
        self.r2L = QLabel(f"Radius 2: {self.r2SL.value()}")
        
        self.c = Communicate()        
        
        self.lens = Lens(0, r1=20, r2=-20)
        self.focalLengthLabel = QLabel(f"Focal length: {round(self.lens.focal_length, 3)}")
        
        if self.title != "Lens 1":
            self.deleteButton = QPushButton("Delete", self)
            self.deleteButton.clicked.connect(self.deleteLens)

    def getLens(self):
        return self.lens

    @pyqtSlot()
    def on_pressed(self):
        checked = self.toggle_button.isChecked()
        self.toggle_button.setArrowType(
            Qt.DownArrow if not checked else Qt.RightArrow
        )
        self.toggle_animation.setDirection(
            QAbstractAnimation.Forward
            if not checked
            else QAbstractAnimation.Backward
        )
        self.toggle_animation.start()

    def setContentLayout(self):
        layout = QVBoxLayout()
        layout.addWidget(self.focalLengthLabel)
        layout.addWidget(self.distanceL)
        if self.title != "Lens 1":
            layout.addWidget(self.distanceSL)
        layout.addWidget(self.r1L)
        layout.addWidget(self.r1SL)
        layout.addWidget(self.r2L)
        layout.addWidget(self.r2SL)
        if self.title != "Lens 1":
            layout.addWidget(self.deleteButton)
                
        lay = self.content_area.layout()
        del lay
        self.content_area.setLayout(layout)
        collapsed_height = (
            self.sizeHint().height() - self.content_area.maximumHeight()
        )
        content_height = layout.sizeHint().height()
        for i in range(self.toggle_animation.animationCount()):
            animation = self.toggle_animation.animationAt(i)
            animation.setDuration(500)
            animation.setStartValue(collapsed_height)
            animation.setEndValue(collapsed_height + content_height)

        content_animation = self.toggle_animation.animationAt(
            self.toggle_animation.animationCount() - 1
        )
        content_animation.setDuration(500)
        content_animation.setStartValue(0)
        content_animation.setEndValue(content_height)
        
    def distanceChanged(self):
        newDist = self.distanceSL.value()
        self.distanceL.setText(f"Distance: {newDist}")
        self.lens.setDistance(newDist)
        self.lens.update()
        self.c.valueChanged.emit(self.lens)
            
    def r1Changed(self):
        newR = self.r1SL.value()
        if newR == 0 or newR == self.r2SL.value():
            return
        self.r1L.setText(f"Radius 1: {newR}")
        self.lens.setR1(newR)
        self.lens.update()
        self.c.valueChanged.emit(self.lens)
        self.focalLengthLabel.setText(f"Focal length: {round(self.lens.focal_length, 3)}")
        
    def r2Changed(self):
        newR = self.r2SL.value()
        if newR == 0 or newR == self.r1SL.value():
            return
        self.r2L.setText(f"Radius 2: {newR}")
        self.lens.setR2(newR)
        self.lens.update()
        self.c.valueChanged.emit(self.lens)
        self.focalLengthLabel.setText(f"Focal length: {round(self.lens.focal_length, 3)}")
    
    def deleteLens(self):
        self.c.remove.emit(self)
        
class Communicate(QObject):

    valueChanged = pyqtSignal(Lens)
    remove = pyqtSignal(CollapsibleBox)
