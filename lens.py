from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

ONE_CM = 5
GLASS_REFRAC = 1.5
AIR_REFRAC = 1
ARROW_SPACING = ONE_CM - 2

def line_intersection(lineA, lineB):
    line1 = [[lineA[0].x(), lineA[0].y()], [lineA[1].x(), lineA[1].y()]] 
    line2 = [[lineB[0].x(), lineB[0].y()], [lineB[1].x(), lineB[1].y()]] 
    
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
        exit
        # raise Exception('lines do not intersect')

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return QPoint(int(x), int(y))

class Lens():
    
    def __init__(self, distance, focal_length=None, thickness=None, r1=None, r2=None):
        self.focal_length = focal_length
        self.thickness = thickness
        self.distance = distance
        self.r1 = r1
        self.r2 = r2
        
        self.update()
        
        self.x = 0
        self.lensLine = [QPoint(0, 0), QPoint(0, 0)]
        self.outRay1 = [QPoint(0, 0), QPoint(0, 0)]
        self.outRay2 = [QPoint(0, 0), QPoint(0, 0)]
        self.outRay3 = [QPoint(0, 0), QPoint(0, 0)]
        self.distance_act = distance * ONE_CM
        self.mag_ratio = 0
    
    def update(self):
        if self.focal_length is None:
            # if self.thickness is None:
            if self.r1 is not None and self.r2 is not None:
                f_frac = (GLASS_REFRAC - AIR_REFRAC) * ((1 / self.r1) - (1 / self.r2))
                self.focal_length = 1 / f_frac
                    
            # else:
            # if self.r1 is not None and self.r2 is not None:
            #     f_frac1 = (GLASS_REFRAC - AIR_REFRAC)
            #     f_frac2 = (1 / self.r1) - (1 / self.r2) + (((GLASS_REFRAC - AIR_REFRAC) * thickness) / (GLASS_REFRAC * r1 * r2))
            #     self.focal_length = 1 / (f_frac1 * f_frac2)
        else:
            self.focal_length = self.focal_length
    
    def setDistance(self, distance):
        self.focal_length = None
        self.distance = distance
        self.distance_act = self.distance * ONE_CM
    
    def setR1(self, r1):
        self.focal_length = None
        self.r1 = r1
        
    def setR2(self, r2):
        self.focal_length = None
        self.r2 = r2
    
    def paint(self, offset, painter, windowW, windowH, prevRay1, prevRay2, prevRay3, obj_height, obj_distance, prev_obj_distance):
        self.lensLine[0] = QPoint(self.distance_act + offset, int(windowH / 2 + 150))
        self.lensLine[1] = QPoint(self.distance_act + offset, int(windowH / 2 - 150))
        painter.drawLine(self.lensLine[0], self.lensLine[1])

        try:
            prevRay1[1] = line_intersection(self.lensLine,  prevRay1)
        except:
            prevRay1 = prevRay1
        
        try:
            prevRay2[1] = line_intersection(self.lensLine,  prevRay2)
        except:
            prevRay2 = prevRay2
            
        try:
            prevRay3[1] = line_intersection(self.lensLine,  prevRay3)
        except:
            prevRay3 = prevRay3
            
        
        # ray painting
        pen = QPen(Qt.red)
        pen.setWidth(1)
        pen.setStyle(Qt.DashLine)
        painter.setPen(pen)
        painter.drawLine(prevRay1[0], prevRay1[1])
        
        pen = QPen(Qt.darkGreen)
        pen.setStyle(Qt.DashLine)
        painter.setPen(pen)
        painter.drawLine(prevRay2[0], prevRay2[1])
        
        pen = QPen(Qt.blue)
        pen.setStyle(Qt.DashLine)
        painter.setPen(pen)
        painter.drawLine(prevRay3[0], prevRay3[1])
        
        pen.setColor(Qt.darkCyan)
        pen.setWidth(5)
        pen.setStyle(Qt.SolidLine)
        painter.setPen(pen)
        
        try:
            self.mag_ratio = -obj_distance / prev_obj_distance
        except:
            self.mag_ratio = 1.0
        new_h = self.mag_ratio * obj_height
        # print("new_h")
        # print(obj_height)
        # print(self.mag_ratio)
        # print(new_h)
        obj_distance * ONE_CM + offset + self.distance_act
        
        
        if self.mag_ratio != 1.0:
            self.outRay1[0] = prevRay1[1]
            self.outRay2[0] = prevRay2[1]
            self.outRay3[0] = prevRay3[1]
            self.outRay1[1] = QPoint(int(offset + self.distance_act + obj_distance * ONE_CM), int(windowH / 2 + new_h * ONE_CM))  
            self.outRay2[1] = QPoint(int(offset + self.distance_act + obj_distance * ONE_CM), int(windowH / 2 + new_h * ONE_CM))
            self.outRay3[1] = QPoint(int(offset + self.distance_act + obj_distance * ONE_CM), int(windowH / 2 + new_h * ONE_CM))
        else:
            self.outRay1 = prevRay1
            self.outRay2 = prevRay2
            self.outRay3 = prevRay3
                        
    def paintLastRay(self, painter, windowH, distance):
        isect = line_intersection(self.outRay1, [QPoint(int(distance), 0), QPoint(int(distance), windowH)])
        isect2 = line_intersection(self.outRay2, [QPoint(int(distance), 0), QPoint(int(distance), windowH)])
        isect3 = line_intersection(self.outRay3, [QPoint(int(distance), 0), QPoint(int(distance), windowH)])
        
        # print(self.outRay1)
        # print(self.outRay2)
        # print([QPoint(int(distance), 0), QPoint(int(distance), windowH)])
        pen = QPen(Qt.red)
        pen.setWidth(1)
        pen.setStyle(Qt.DashLine)
        painter.setPen(pen)
        painter.drawLine(self.outRay1[0], isect)
        # painter.drawLine(self.outRay1[0], self.outRay1[1])
        
        pen = QPen(Qt.darkGreen)
        pen.setStyle(Qt.DashLine)
        painter.setPen(pen)
        # painter.drawLine(self.outRay2[0], self.outRay2[1])
        painter.drawLine(self.outRay2[0], isect2)
        
        pen = QPen(Qt.blue)
        pen.setStyle(Qt.DashLine)
        painter.setPen(pen)
        painter.drawLine(self.outRay3[0], isect3)
        
        pen.setColor(Qt.black)
        pen.setWidth(2)
        pen.setStyle(Qt.SolidLine)
        painter.setPen(pen)
        # painter.drawLine(QPoint(int(distance), 0), QPoint(int(distance), windowH))
        
        painter.drawLine(QPoint(int(distance), windowH // 2), isect2)
        
        signed_arrow_pos = ONE_CM if int(isect2.y() - windowH / 2) <= 0 else -ONE_CM
        painter.drawLine(isect2.x(), isect2.y(), isect2.x() - ARROW_SPACING, isect2.y() + signed_arrow_pos)
        painter.drawLine(isect2.x(), isect2.y(), isect2.x() + ARROW_SPACING, isect2.y() + signed_arrow_pos)

        
    def getFocalLength(self):
        return self.focal_length
    
    def computeDistance(self, object_distance):
        return (object_distance * self.focal_length) / (object_distance - self.focal_length)
    
    def getOutRays(self):
        return (self.outRay1, self.outRay2, self.outRay3)

    def getDistance(self):
        return self.distance
    
    def getDistanceCm(self):
        return self.distance_act
    
    def getMagRatio(self):
        return self.mag_ratio