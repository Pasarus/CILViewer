# Changelog

## v21.1.2
* Fix the setting of the view up vector in the y direction, to avoid getting vtk warning messages.
* The event triggered by the "w" key, (i.e. update the window level) is now based on a smaller area of the image under the cursor. The area is 10% in each direction of the whole image extent.
* The auto window level now uses the average value between 1 and 99 percentile as level and the difference for window. Before it was the median.
* Update examples to use PySide2 instead of PyQt5 

## v21.1.1
* fix bug with importing version number

## v21.1.0
* infer the version string from the repository tag
* fix bug with orientation axes when the input image is updated
* Allow colormap to be changed in the 3D viewer to any colormap available in matplotlib

## v21.0.1
* change default orientation of axes
* reduce print-outs from code


## v21.0.0

 * change backend for Qt as PySide2

 * Fix definition of image and world coords

 * Update corner annotation to use new definition
 
 * Fix origin of resampled image to use new coordinate definition

 * Make use of original image origin and spacing when downsampling and cropping images

 * Change default raw datatype to be unit8
