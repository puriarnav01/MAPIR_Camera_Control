import os
from PyQt5 import QtCore, QtGui, QtWidgets
import PyQt5.uic as uic
import cv2
import copy
import numpy as np
RASTER_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'MAPIR_Processing_dockwidget_raster.ui'))


class Calculator(QtWidgets.QDialog, RASTER_CLASS):
    ndvi = None
    def __init__(self, parent=None):
        """Constructor."""
        super(Calculator, self).__init__(parent=parent)
        self.parent = parent
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        img = cv2.imread(os.path.dirname(__file__) + "/ndvi_400px.jpg")
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w = img.shape[:2]
        img2 = QtGui.QImage(img, w, h, w * 3, QtGui.QImage.Format_RGB888)
        self.IndexFormula.setPixmap(QtGui.QPixmap.fromImage(img2))
        self.RasterX.addItem(self.parent.KernelBrowserFile.text().split(r'/')[-1] + " @Band1(Red Channel)")
        self.RasterX.addItem(self.parent.KernelBrowserFile.text().split(r'/')[-1] + " @Band2(Green Channel)")
        self.RasterX.addItem(self.parent.KernelBrowserFile.text().split(r'/')[-1] + " @Band3(Blue Channel)")
        self.RasterY.addItem(self.parent.KernelBrowserFile.text().split(r'/')[-1] + " @Band1(Red Channel)")
        self.RasterY.addItem(self.parent.KernelBrowserFile.text().split(r'/')[-1] + " @Band2(Green Channel)")
        self.RasterY.addItem(self.parent.KernelBrowserFile.text().split(r'/')[-1] + " @Band3(Blue Channel)")
        self.RasterZ.hide()
        self.ZLabel.hide()
        # self.RasterZ.addItem(self.parent.KernelBrowserFile.text().split(os.sep)[-1] + " @Band1")
        # self.RasterZ.addItem(self.parent.KernelBrowserFile.text().split(os.sep)[-1] + " @Band2")
        # self.RasterZ.addItem(self.parent.KernelBrowserFile.text().split(os.sep)[-1] + " @Band3")
        self.parent.ViewerCalcButton.setEnabled(False)
    def on_RasterApplyButton_released(self):
        try:
            self.processIndex()
            self.parent.ViewerIndexBox.setEnabled(True)
            if self.parent.LUTwindow == None or not self.parent.LUTwindow.isVisible():
                self.parent.LUTButton.setEnabled(True)
            if self.parent.ViewerIndexBox.isChecked():
                self.parent.applyRaster()
            else:
                self.parent.ViewerIndexBox.setChecked(True)
        except Exception as e:
            print(e)
    def on_RasterOkButton_released(self):
        try:
            self.processIndex()
            self.parent.ViewerIndexBox.setEnabled(True)
            if self.parent.LUTwindow == None or not self.parent.LUTwindow.isVisible():
                self.parent.LUTButton.setEnabled(True)
            if self.parent.ViewerIndexBox.isChecked():
                self.parent.applyRaster()
            else:
                self.parent.ViewerIndexBox.setChecked(True)
            self.parent.ViewerCalcButton.setEnabled(True)

            self.close()
        except Exception as e:
            print(e)

    def on_RasterCloseButton_released(self):
        self.parent.ViewerCalcButton.setEnabled(True)
        self.close()

    def processIndex(self):
        try:
            h, w = self.parent.display_image_original.shape[:2]
            bands = [self.parent.display_image_original[:, :, 0], self.parent.display_image_original[:, :, 1], self.parent.display_image_original[:, :, 2]]
            self.ndvi = self.parent.calculateIndex(bands[self.RasterX.currentIndex()], bands[self.RasterY.currentIndex()])
            self.parent.LUT_Min = copy.deepcopy(np.percentile(self.ndvi, 2))
            self.parent.LUT_Max = copy.deepcopy(np.percentile(self.ndvi, 98))
            midpoint = (self.parent.LUT_Max - self.parent.LUT_Min) / 2
            steps = midpoint * 1 / 3
            self.parent.legend_max.setText(str(round(self.parent.LUT_Max, 2)))
            self.parent.legend_2thirds.setText(str(round(self.parent.LUT_Max - (steps), 2)))
            self.parent.legend_1third.setText(str(round(self.parent.LUT_Max - (steps * 2), 2)))
            self.parent.legend_zero.setText(str(round(self.parent.LUT_Max - (steps * 3), 2)))
            self.parent.legend_min.setText(str(round(self.parent.LUT_Min, 2)))
            self.parent.legend_neg2thirds.setText(str(round(self.parent.LUT_Max - (steps * 5), 2)))
            self.parent.legend_neg1third.setText(str(round(self.parent.LUT_Max - (steps * 4), 2)))
            QtWidgets.QApplication.processEvents()
            self.ndvi -= self.ndvi.min()
            self.ndvi /= (self.ndvi.max())
            self.ndvi *= 255.0
            # self.ndvi += 128.0
            self.ndvi = np.around(self.ndvi)
            self.ndvi = self.ndvi.astype("uint8")
            self.ndvi = cv2.equalizeHist(self.ndvi)
            # self.ndvi = cv2.cvtColor(self.ndvi, cv2.COLOR_GRAY2RGB)
        except Exception as e:
            print(e)

