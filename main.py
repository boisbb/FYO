import sys
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from lens import Lens, line_intersection
import math
from skspatial.objects import Circle, Line
import random

from utils import CollapsibleBox

ONE_CM = 5
ARROW_SPACING = ONE_CM - 2
FIRST_LENS_POS = 60 * ONE_CM
        

class DrawingWindow(QWidget):
    def __init__(self, init_lens):
        super().__init__()
        self.width = 800
        self.height = 600
        self.resize(self.width, self.height)
        self.lenses = [init_lens]
        
        self.setNewObjHeight(-15)
        self.object_pos_act = 40
        self.object_pos = self.object_pos_act * ONE_CM
        self.object_coords = [QPoint(0, 0), QPoint(0, 0)]
        self.last_obj_distance = 0
        self.current_mag = 1
    
    def paintEvent(self, event):
        super().paintEvent(event)
                
        first_lens_act_pos = FIRST_LENS_POS + self.lenses[0].distance 
        firstFP = first_lens_act_pos - self.lenses[0].getFocalLength() * ONE_CM
        self.object_coords[0] = QPoint(first_lens_act_pos - self.object_pos, self.object_height)
        self.object_coords[1] = QPoint(first_lens_act_pos - self.object_pos, self.height // 2)
        
        self.setWindowTitle("PyQt")
        painter = QPainter()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        pen = QPen(Qt.black)
        painter.setPen(pen)
        
        painter.drawLine(0, self.height // 2, self.width, self.height // 2)    
        
        painter.drawLine(int(firstFP), self.height // 2 + 10, int(firstFP), self.height // 2 - 10)
        
        painter.drawLine(self.object_coords[0], self.object_coords[1])
        painter.drawLine(self.object_coords[0].x(), self.object_coords[0].y(), self.object_coords[0].x() - ARROW_SPACING, self.object_coords[0].y() + ONE_CM)
        painter.drawLine(self.object_coords[0].x(), self.object_coords[0].y(), self.object_coords[0].x()  + ARROW_SPACING, self.object_coords[0].y() + ONE_CM)
        
        painter.setPen(Qt.blue)
        # for lens in self.lenses:
        distance = 0
        outRays = None
        lensOffset = FIRST_LENS_POS
        obj_h = 0
        # prev_distance = 0
        self.current_mag = 1.0
        for i, lens in enumerate(self.lenses):
            if i == 0:
                fst_line1 = [self.object_coords[0], QPoint(self.width, self.object_coords[0].y())]
                fst_line2 = [QPoint(self.object_coords[0].x(), self.object_height)]
                fst_line2.append(line_intersection([fst_line2[0], QPoint(int(firstFP), self.height // 2)],
                                                   [QPoint(first_lens_act_pos, self.height), QPoint(first_lens_act_pos, 0)]))
                distance = lens.computeDistance(self.object_pos_act)
                lens.paint(lensOffset, painter, self.width, self.height, fst_line1, fst_line2, self.object_height_act, distance, self.object_pos_act)
                outRays = lens.getOutRays()
                self.current_mag *= lens.getMagRatio()
            else:
                prev_distance = (-1) * (distance - lens.getDistance())
                distance = lens.computeDistance(prev_distance)
                lens.paint(lensOffset, painter, self.width, self.height, outRays[0], outRays[1], self.object_height_act * self.current_mag, distance, prev_distance)
                outRays = lens.getOutRays()
                self.current_mag *= lens.getMagRatio()
            
            lensOffset += lens.getDistanceCm()
            print ("distances")
            print(distance)
            # print(prev_distance)
            
            if i == len(self.lenses) - 1:
                self.last_obj_distance = distance
                print(lens.getDistanceCm())
                print(lens.getDistance())
                print(distance * ONE_CM + lensOffset)
                lens.paintLastRay(painter, self.height, distance * ONE_CM + lensOffset)
        
    
    def appendNewLens(self, lens):
        self.lenses.append(lens)                
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.width = self.frameGeometry().width()
        self.height = self.frameGeometry().height()
        self.object_height = self.height // 2 + self.object_height_act * ONE_CM
    
    def setNewObjHeight(self, newH):
        self.object_height_act = newH
        self.object_height = self.height // 2 + self.object_height_act * ONE_CM
        
        
        
class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle('Primitive Lens Designed')
        self.width = 800
        self.height = 600
        self.resize(self.width, self.height)
        
        self.objInfoL = QLabel("Image is: Real")
        self.magRatioL = QLabel("")
        
        self.objPosSL = QSlider(Qt.Horizontal)
        self.objPosSL.setMinimum(1)
        self.objPosSL.setMaximum(100)
        self.objPosSL.setValue(40)
        self.objPosSL.setTickPosition(QSlider.TicksBelow)
        self.objPosSL.setTickInterval(2)
        self.objPosSL.valueChanged.connect(self.objDistanceChanged)
        self.objPosL = QLabel(f"Object distance: {self.objPosSL.value()}")
        
        self.objHeightSL = QSlider(Qt.Horizontal)
        self.objHeightSL.setMinimum(1)
        self.objHeightSL.setMaximum(100)
        self.objHeightSL.setValue(15)
        self.objHeightSL.setTickPosition(QSlider.TicksBelow)
        self.objHeightSL.setTickInterval(2)
        self.objHeightSL.valueChanged.connect(self.objHeightChanged)
        self.objHeightL= QLabel(f"Object height: {self.objHeightSL.value()}")
        
        self.addLensB = QPushButton('+', self)
        self.addLensB.clicked.connect(self.addLens)
        
        self.vlay = None
        self.boxes = []
        
        self.initUI()
        
    def initUI(self):        
        
        dock = QDockWidget("")
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)
        scroll = QScrollArea()
        dock.setWidget(scroll)
        content = QWidget()
        scroll.setWidget(content)
        scroll.setWidgetResizable(True)
        self.vlay = QVBoxLayout(content)
        self.vlay.addWidget(self.objInfoL)
        self.vlay.addWidget(self.magRatioL)
        self.vlay.addWidget(self.objPosL)
        self.vlay.addWidget(self.objPosSL)
        self.vlay.addWidget(self.objHeightL)
        self.vlay.addWidget(self.objHeightSL)
        for i in range(1):
            self.boxes.append(CollapsibleBox("Lens {}".format(i + 1)))
            self.boxes[0].c.valueChanged.connect(self.collapsingBoxChanged)
            self.boxes[0].c.remove.connect(self.removeLens)
            self.vlay.addWidget(self.boxes[0])
            self.boxes[0].setContentLayout()
        
        self.vlay.addWidget(self.addLensB)
        self.vlay.addStretch()
        self.resize(800,600)
        
        self.right_widget = DrawingWindow(self.boxes[-1].getLens())
        self.setCentralWidget(self.right_widget)
        
        self.magRatioL.setText(f"Magnification: {self.right_widget.current_mag}")
        
    def collapsingBoxChanged(self, lens):
        for i, lensDW in enumerate(self.right_widget.lenses):
            if lensDW == lens:
                self.right_widget.lenses[i] = lens
        
        self.right_widget.repaint()
        self.objInfoL.setText("Image is: {}".format("Real" if self.right_widget.last_obj_distance > 0 else "Virtual"))
        self.magRatioL.setText(f"Magnification: {round(self.right_widget.current_mag, 3)}")
    
    def removeLens(self, box):
        print (box.title)
        self.right_widget.lenses.remove(box.lens)
        self.vlay.removeWidget(box)
        box.deleteLater()
        self.boxes.remove(box)
        box = None
        self.repaint()
                        
    
    def objDistanceChanged(self):
        newDist = self.objPosSL.value()
        self.objPosL.setText(f"Object distance: {newDist}")
        self.right_widget.object_pos_act = newDist
        self.right_widget.object_pos = newDist * ONE_CM
        self.right_widget.repaint()
        self.magRatioL.setText(f"Magnification: {round(self.right_widget.current_mag, 3)}")
        
    def objHeightChanged(self):
        newH = self.objHeightSL.value()
        self.objHeightL.setText(f"Object height: {newH}")
        self.right_widget.setNewObjHeight(-newH)
        self.right_widget.repaint()
    
    def addLens(self):
        self.boxes.append(CollapsibleBox(f"Lens {len(self.boxes) + 1}"))
        self.boxes[-1].c.valueChanged.connect(self.collapsingBoxChanged)
        self.boxes[-1].c.remove.connect(self.removeLens)
        self.vlay.insertWidget(self.vlay.count() - 2, self.boxes[-1])
        self.boxes[-1].setContentLayout()
        self.right_widget.appendNewLens(self.boxes[-1].lens)
        self.right_widget.repaint()
        
        


def main():
    App = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(App.exec_())


if __name__ == "__main__":
    main()
    # window()