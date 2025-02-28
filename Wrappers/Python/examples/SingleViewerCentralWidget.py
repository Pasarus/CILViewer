import sys
import vtk
from PySide2 import QtCore, QtWidgets
from ccpi.viewer import viewer2D, viewer3D
from ccpi.viewer.QCILViewerWidget import QCILViewerWidget


class SingleViewerCenterWidget(QtWidgets.QMainWindow):

    def __init__(self, parent = None, viewer=viewer2D):
        QtWidgets.QMainWindow.__init__(self, parent)
        
        self.frame = QCILViewerWidget(viewer=viewer, shape=(600,600))
                
        reader = vtk.vtkMetaImageReader()
        reader.SetFileName('head.mha')
        reader.Update()
        
        self.frame.viewer.setInputData(reader.GetOutput())
        
        self.setCentralWidget(self.frame)
    
        self.show()
        

if __name__ == "__main__":
 
    app = QtWidgets.QApplication(sys.argv)
    # can change the behaviour by setting which viewer you want
    # between viewer2D and viewer3D
    window = SingleViewerCenterWidget(viewer=viewer3D)
 
    sys.exit(app.exec_())
