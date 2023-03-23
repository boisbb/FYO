import sys
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from lens import Lens
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
        # self.lenses.append(Lens(0, r1=20, r2=-20))
        # self.lenses.append(Lens(10, -30))
        # self.lenses.append(Lens(10, 5))
        self.object_height_act = -15
        self.object_height = self.height // 2 + self.object_height_act * ONE_CM
        self.object_pos_act = 40
        self.object_pos = self.object_pos_act * ONE_CM
        self.object_coords = [QPoint(0, 0), QPoint(0, 0)]
    
    def paintEvent(self, event):
        super().paintEvent(event)
        
        print("paint")
        
        first_lens_act_pos = FIRST_LENS_POS + self.lenses[0].distance 
        firstFP = first_lens_act_pos - self.lenses[0].getFocalLength() * ONE_CM
        self.object_coords[0] = QPoint(first_lens_act_pos - self.object_pos, self.object_height)
        self.object_coords[1] = QPoint(first_lens_act_pos - self.object_pos, self.height // 2)
        
        self.setWindowTitle("PyQt")
        painter = QPainter()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        pen = QPen(Qt.black)
        # pen.setWidth(5)
        painter.setPen(pen)
        
        painter.drawLine(0, self.height // 2, self.width, self.height // 2)
        
        
        # def angle(A, B, aspectRatio):
        #     x = B[0] - A[0]
        #     y = B[1] - A[1]
        #     angle = math.atan2(-y, x / aspectRatio)
        #     return angle
        # 
        # a1 = angle((self.width / 2 + 20 * ONE_CM, self.height / 2), (self.width / 2, self.height / 2 + 50), 1)
        # a2 = angle((self.width / 2 + 20 * ONE_CM, self.height / 2), (self.width / 2, self.height / 2 - 50), 1)
        # 
        # print(math.degrees(a1), math.degrees(a2))
        # 
        # painter.drawPoint(self.width // 2, self.height // 2 + 10 * ONE_CM)
        # painter.drawPoint(self.width // 2, self.height // 2 - 10 * ONE_CM)
        # 
        # # painter.drawArc(400, 400, 20 * ONE_CM, 20 * ONE_CM, int(math.degrees(abs(a1))), int(90))
        # painter.drawArc(self.width // 2, self.height // 2 - 20 * ONE_CM, 40 * ONE_CM, 40 * ONE_CM, 153 * 16, 54 * 16)
        
        
        painter.drawLine(int(firstFP), self.height // 2 + 10, int(firstFP), self.height // 2 - 10)
        
        painter.drawLine(self.object_coords[0], self.object_coords[1])
        painter.drawLine(self.object_coords[0].x(), self.object_coords[0].y(), self.object_coords[0].x() - ARROW_SPACING, self.object_coords[0].y() + ONE_CM)
        painter.drawLine(self.object_coords[0].x(), self.object_coords[0].y(), self.object_coords[0].x()  + ARROW_SPACING, self.object_coords[0].y() + ONE_CM)
        
        painter.setPen(Qt.blue)
        # for lens in self.lenses:
        distance = 0
        outRay = []
        lensOffset = FIRST_LENS_POS
        obj_h = 0
        current_mag = 1
        for i, lens in enumerate(self.lenses):
            if i == 0:
                fst_line = [self.object_coords[0], QPoint(self.width, self.object_coords[0].y())]
                distance = lens.computeDistance(self.object_pos_act)
                lens.paint(lensOffset, painter, self.width, self.height, fst_line, self.object_height_act, distance, self.object_pos_act)
                outRay = lens.getOutRay()
                current_mag *= lens.getMagRatio()
            else:
                prev_distance = (-1) * (distance - lens.getDistance())
                distance = lens.computeDistance(prev_distance)
                lens.paint(lensOffset, painter, self.width, self.height, outRay, self.object_height_act * current_mag, distance, prev_distance)
                outRay = lens.getOutRay()
                current_mag *= lens.getMagRatio()
            
            lensOffset += lens.getDistanceCm()
            
            if i == len(self.lenses) - 1:
               lens.paintLastRay(painter, self.height, distance * ONE_CM + lensOffset)
                       
        
                
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.width = self.frameGeometry().width()
        self.height = self.frameGeometry().height()
        self.object_height = self.height // 2 + self.object_height_act * ONE_CM
        
        
        
class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle('Primitive Lens Designed')
        self.width = 800
        self.height = 600
        self.resize(self.width, self.height)
        
        # self.btn_pl = QPushButton('+', self)
        self.objPosSlider = QSlider(Qt.Horizontal)
        self.objPosSlider.setMinimum(1)
        self.objPosSlider.setMaximum(100)
        self.objPosSlider.setValue(40)
        self.objPosSlider.setTickPosition(QSlider.TicksBelow)
        self.objPosSlider.setTickInterval(2)
        self.objPosSlider.valueChanged.connect(self.objDistanceChanged)
        self.objPosLabel = QLabel(f"Object distance: {self.objPosSlider.value()}")
        
        
        self.boxes = []
        
        self.initUI()
        
    def initUI(self):        
        
        dock = QDockWidget("Collapsible Demo")
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)
        scroll = QScrollArea()
        dock.setWidget(scroll)
        content = QWidget()
        scroll.setWidget(content)
        scroll.setWidgetResizable(True)
        vlay = QVBoxLayout(content)
        vlay.addWidget(self.objPosLabel)
        vlay.addWidget(self.objPosSlider)
        for i in range(1):
            self.boxes.append(CollapsibleBox("Lens {}".format(i)))
            self.boxes[0].c.valueChanged.connect(self.collapsingBoxChanged)
            vlay.addWidget(self.boxes[0])
            self.boxes[0].setContentLayout()
        
        vlay.addStretch()
        self.resize(800,600)
        
        self.right_widget = DrawingWindow(self.boxes[-1].getLens())
        self.setCentralWidget(self.right_widget)
        
    def collapsingBoxChanged(self, lens):
        for i, lensDW in enumerate(self.right_widget.lenses):
            if lensDW == lens:
                self.right_widget.lenses[i] = lens
        self.right_widget.repaint()
    
    def objDistanceChanged(self):
        newDist = self.objPosSlider.value()
        self.objPosLabel.setText(f"Object distance: {newDist}")
        self.right_widget.object_pos_act = newDist
        self.right_widget.object_pos = newDist * ONE_CM
        self.right_widget.repaint()


def main():
    App = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(App.exec_())


if __name__ == "__main__":
    main()
    # window()