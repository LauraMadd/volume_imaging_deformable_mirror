from PySide import QtGui, QtCore

class hands_on_image(QtGui.QLabel):

    def __init__(self, picture):
        super(hands_on_image, self).__init__()
        self.pix = QtGui.QPixmap(picture)
        #self.pix.scaled(size_x/2, size_y/2, QtCore.Qt.KeepAspectRatio)
        self.setPixmap(self.pix)
        # xStart and yStart are in row-cols notation, numpy-friendly
        self.xStart, self.yStart = 0., 0.
        self.xEnd, self.yEnd = 0., 0.
        self.rubberBand = QtGui.QRubberBand(QtGui.QRubberBand.Rectangle, self)
        self.origin = QtCore.QPoint()
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.xStart, self.yStart = event.pos().y(), event.pos().x()
            self.origin = QtCore.QPoint(event.pos())
            self.rubberBand.setGeometry(QtCore.QRect(self.origin,\
                                                        QtCore.QSize()))
            self.rubberBand.show()
    
    def mouseMoveEvent(self, event):
        if not self.origin.isNull():
            self.rubberBand.setGeometry(QtCore.QRect(self.origin,\
                                                    event.pos()).normalized())
    
    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.xEnd, self.yEnd = event.pos().y(), event.pos().x()
        temp_x, temp_y = 0., 0.
        if (self.xStart > self.xEnd) :
            temp_x = self.xStart
            self.xStart = self.xEnd
            self.xEnd = temp_x
        if (self.yStart > self.yEnd) :
            temp_y = self.yStart
            self.yStart = self.yEnd
            self.yEnd = temp_y
            #self.rubberBand.hide()
            
    def update_image(self):
        self.setPixmap(self.pix)
        return None