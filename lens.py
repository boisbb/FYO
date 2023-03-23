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
       raise Exception('lines do not intersect')

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
        self.outRay = [QPoint(0, 0), QPoint(0, 0)]
        self.distance = distance * ONE_CM
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
    
    def setR1(self, r1):
        self.focal_length = None
        self.r1 = r1
        
    def setR2(self, r2):
        self.focal_length = None
        self.r2 = r2
    
    def paint(self, offset, painter, windowW, windowH, prevRay, obj_height, obj_distance, prev_obj_distance):
        self.lensLine[0] = QPoint(self.distance + offset, windowH // 2 + 150)
        self.lensLine[1] = QPoint(self.distance + offset, windowH // 2 - 150)
        painter.drawLine(self.lensLine[0], self.lensLine[1])

        prevRay[1] = line_intersection(self.lensLine,  prevRay)
        painter.drawLine(prevRay[0], prevRay[1])
        
        self.mag_ratio = -obj_distance / prev_obj_distance
        new_h = self.mag_ratio * obj_height
        
        self.outRay[0] = prevRay[1]
        # self.outRay[1] = QPoint(offset + self.distance + self.focal_length * ONE_CM, windowH // 2)
        self.outRay[1] = QPoint(offset + self.distance + int(obj_distance) * ONE_CM, windowH // 2 + int(new_h * ONE_CM))
                
    def paintLastRay(self, painter, windowH, distance):
        isect = line_intersection(self.outRay, [QPoint(int(distance), 0), QPoint(int(distance), windowH)])
        painter.drawLine(self.outRay[0], isect)
        pen = QPen(Qt.black)
        painter.setPen(pen)
        painter.drawLine(QPoint(int(distance), windowH // 2), isect)
        
        signed_arrow_pos = ONE_CM if (isect.y() - windowH // 2) <= 0 else -ONE_CM
        painter.drawLine(isect.x(), isect.y(), isect.x() - ARROW_SPACING, isect.y() + signed_arrow_pos)
        painter.drawLine(isect.x(), isect.y(), isect.x() + ARROW_SPACING, isect.y() + signed_arrow_pos)
        # painter.drawLine(QPoint(int(distance), 0), QPoint(int(distance), windowH))

        
    def getFocalLength(self):
        return self.focal_length
    
    def computeDistance(self, object_distance):
        return (object_distance * self.focal_length) / (object_distance - self.focal_length)
    
    def getOutRay(self):
        return self.outRay

    def getDistance(self):
        return self.distance // ONE_CM
    
    def getDistanceCm(self):
        return self.distance
    
    def getMagRatio(self):
        return self.mag_ratio