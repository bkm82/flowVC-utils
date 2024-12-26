# import paraview
# paraview.compatibility.major = 5
# paraview.compatibility.minor = 13

#### import the simple module from the paraview
from paraview.simple import *

paraview.simple._DisableFirstRenderCameraReset()


def visualize_with_threshold(threshold_value=0.0, lower_bound=0.0, upper_bound=60.0):
    # find the latest source
    source = GetActiveSource()

    if source is None:
        raise RuntimeError("No active source found.")

    renderView = GetActiveViewOrCreate("RenderView")
    renderView.CameraPosition = [
        -0.41008466181434233,
        1.0354369516515214,
        0.3224846022996795,
    ]
    renderView.CameraFocalPoint = [
        -0.005735980346799026,
        0.17267299816012374,
        0.20363696012645943,
    ]
    renderView.CameraViewUp = [
        0.0213563993649863,
        -0.1266030774278735,
        0.9917235325391625,
    ]
    renderView.CameraParallelScale = 0.24851807644746754

    # create a new 'Threshold'
    threshold = Threshold(registrationName="Threshold", Input=source)
    # Properties modified on threshold1
    threshold.UpperThreshold = 0.0
    threshold.ThresholdMethod = "Above Upper Threshold"

    # scalar_fieldTF2D = GetTransferFunction2D('scalar_field')
    # # get color transfer function/color map for 'scalar_field'
    # scalar_fieldLUT = GetColorTransferFunction('scalar_field')
    # scalar_fieldLUT.RescaleTransferFunction(-1.0, 60.0)

    # # get opacity transfer function/opacity map for 'scalar_field'
    # scalar_fieldPWF = GetOpacityTransferFunction('scalar_field')
    # scalar_fieldPWF.RescaleTransferFunction(-1.0, 60.0)

    # # Rescale 2D transfer function
    # scalar_fieldTF2D.RescaleTransferFunction(-1.0, 60.0, -1.0, 2977.302001953125)

    threshold1Display = Show(threshold, renderView, "UnstructuredGridRepresentation")
    threshold1Display.SetRepresentationType("Volume")
    renderView.Update()
    RenderAllViews()


# Call the function with default parameters
visualize_with_threshold()
