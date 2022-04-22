import os
import sys
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from PyQt5 import QtWidgets

class DataInterpreter(QtWidgets.QApplication):
    def __init__(self, char):
        super(DataInterpreter, self).__init__(char)

class DataWindowVisualizer(QtWidgets.QWidget):
    def __init__(self):
        super(DataWindowVisualizer, self).__init__()
        self.setWindowTitle("PoCVTK")
        self.pathData = QtWidgets.QFileDialog.getExistingDirectory(self, "Select files folder")
        VolumetricRendering(self.pathData).generateVolumetricContour()
        VolumetricRendering(self.pathData).mapRender()

class VolumetricRendering():
    core = vtk
    camera = vtk.vtkCamera()
    reader = core.vtkDICOMImageReader()
    writer = core.vtkSTLWriter()
    renderer = core.vtkRenderer()
    interactor = core.vtkRenderWindowInteractor()
    window = core.vtkRenderWindow()
    # Contour filter
    contourFilter = core.vtkContourFilter()
    polyDataNormals = core.vtkPolyDataNormals()
    polyDataMapper = core.vtkPolyDataMapper()
    actor = core.vtkActor()
    # Volume ray cast mapper
    volumeRayCastMapper = core.vtkGPUVolumeRayCastMapper()
    colorTransfer = core.vtkColorTransferFunction()
    scalarOpacity = core.vtkPiecewiseFunction()
    gradientOpacity = core.vtkPiecewiseFunction()
    property = core.vtkVolumeProperty()
    volume = core.vtkVolume()
    # Properties
    isSkinVisible = False
    # Render window
    window.AddRenderer(renderer)
    # Constructor
    def __init__(self, path):
        o = os.path.join(path, "VTKAsset.stl")
        self.writer.SetFileName(o)
        self.interactor.SetRenderWindow(self.window)
        self.window.SetSize(1024,1024)
        self.renderer.SetActiveCamera(self.camera)
        self.renderer.SetBackground(0,0,0)
        self.reader.SetDataByteOrderToLittleEndian()
        self.reader.SetDirectoryName(path)
        self.reader.SetDataSpacing(3.2, 3.2, 1.5)
        self.camera.SetViewUp(0,0,-1)
        self.camera.SetPosition(0,1,0)
        self.camera.SetFocalPoint(0,0,0)
        self.camera.ComputeViewPlaneNormal()
    # Generate volumetric and filter contour
    def generateVolumetricContour(self):
        # Color
        self.colorTransfer.AddRGBPoint(0, 50.0, 50.0, 50.0)
        self.colorTransfer.AddRGBPoint(500, 0.5, 0.5, 0.5)
        self.colorTransfer.AddRGBPoint(1000, 1.0, 1.0, 1.0)
        # Scalar opacity
        self.scalarOpacity.AddPoint(0, 0.00)
        self.scalarOpacity.AddPoint(500, 0.25)
        self.scalarOpacity.AddPoint(1000, 0.75)
        # Gradient opacity
        self.gradientOpacity.AddPoint(0, 0.0)
        self.gradientOpacity.AddPoint(75, 0.5)
        self.gradientOpacity.AddPoint(100, 1.0)
        # Setup input properties
        self.property.SetColor(self.colorTransfer)
        self.property.SetScalarOpacity(self.scalarOpacity)
        self.property.SetGradientOpacity(self.gradientOpacity)
        self.property.SetInterpolationTypeToLinear()
        self.property.ShadeOn()
        self.property.SetAmbient(0.5)
        self.property.SetDiffuse(0.7)
        self.property.SetSpecular(0.3)
        # Setup input connections filter
        self.contourFilter.SetInputConnection(self.reader.GetOutputPort())
        self.contourFilter.SetValue(0, 0.01)
        self.polyDataNormals.SetInputConnection(self.contourFilter.GetOutputPort())
        self.polyDataNormals.SetFeatureAngle(60.0)
        self.polyDataMapper.SetInputConnection(self.polyDataNormals.GetOutputPort())
        self.polyDataMapper.ScalarVisibilityOff()
        self.actor.SetMapper(self.polyDataMapper)
        # Setup input connections mapper
        self.volumeRayCastMapper.SetInputConnection(self.reader.GetOutputPort())
        self.volumeRayCastMapper.SetBlendModeToComposite()
        self.volume.SetMapper(self.volumeRayCastMapper)
        self.volume.SetProperty(self.property)
        self.writer.SetInputConnection(self.polyDataNormals.GetOutputPort())
        self.writer.Write()
    # Show/Hide contour
    def updateContourVisibility(self):
        if self.isSkinVisible == False:
           self.isSkinVisible = True
        else:
           self.isSkinVisible = False
    # Render
    def mapRender(self):
        self.camera.Dolly(1)
        if (self.isSkinVisible):
           self.renderer.AddActor(self.actor)
        self.renderer.AddViewProp(self.volume)
        self.renderer.ResetCamera()
        self.renderer.ResetCameraClippingRange()
        self.interactor.Initialize()
        self.window.Render()
        self.interactor.Start()

class Daemon():
    def __init__(self):
        super(Daemon, self).__init__()
        self.interpreter = DataInterpreter(sys.argv)
        self.visualizer = DataWindowVisualizer()
        self.visualizer.show()
        sys.exit()

if __name__ == '__main__':
    Daemon()

