import os
import unittest

import numpy as np
import vtk
from ccpi.viewer.utils.conversion import (Converter, cilBaseResampleReader,
                                          cilMetaImageResampleReader,
                                          cilNumpyResampleReader)


def calculate_target_downsample_shape(max_size, total_size, shape, acq=False):
    if not acq:
        xy_axes_magnification = np.power(max_size/total_size, 1/3)
        slice_per_chunk = np.int(1/xy_axes_magnification)
    else:
        slice_per_chunk = 1
        xy_axes_magnification = np.power(max_size/total_size, 1/2)
    num_chunks = 1 + len([i for i in
                          range(slice_per_chunk, shape[2], slice_per_chunk)])

    target_image_shape = (int(xy_axes_magnification * shape[0]),
                          int(xy_axes_magnification * shape[1]), num_chunks)
    return target_image_shape


class TestResampleReaders(unittest.TestCase):

    def setUp(self):
        # Generate random 3D array and write to HDF5:
        self.input_3D_array = np.random.randint(10, size=(5, 10, 6), dtype=np.uint8)
        bytes_3D_array = bytes(self.input_3D_array)
        self.raw_filename_3D = 'test_3D_data.raw'
        with open(self.raw_filename_3D, 'wb') as f:
            f.write(bytes_3D_array)

        self.numpy_filename_3D = 'test_3D_data.npy'
        np.save(self.numpy_filename_3D, self.input_3D_array)

        self.meta_filename_3D = 'test_3D_data.mha'
        vtk_image = Converter.numpy2vtkImage(self.input_3D_array)
        writer = vtk.vtkMetaImageWriter()
        writer.SetFileName(self.meta_filename_3D)
        writer.SetInputData(vtk_image)
        writer.SetCompression(False)
        writer.Write()

    def test_base_resample_reader(self):
        # Tests image with correct target size is generated by resample reader:
        # Not a great test, but at least checks the resample reader runs
        # without crashing
        # TODO: improve this test
        reader = cilBaseResampleReader()
        og_shape = np.shape(self.input_3D_array)
        reader.SetFileName(self.raw_filename_3D)
        target_size = 100
        reader.SetTargetSize(target_size)
        reader.SetBigEndian(False)
        reader.SetIsFortran(False)
        reader.SetRawTypeCode(str(self.input_3D_array.dtype))
        reader.SetStoredArrayShape(og_shape)
        reader.Update()
        image = reader.GetOutput()
        extent = image.GetExtent()
        resulting_shape = (extent[1]+1, (extent[3]+1), (extent[5]+1))
        og_shape = (og_shape[2], og_shape[1], og_shape[0])
        og_size = og_shape[0]*og_shape[1]*og_shape[2]
        expected_shape = calculate_target_downsample_shape(
            target_size, og_size, og_shape)
        self.assertEqual(resulting_shape, expected_shape)

        # # Now test if we get the full image extent if our
        # # target size is larger than the size of the image:
        target_size = og_size*2
        reader.SetTargetSize(target_size)
        reader.Update()
        image = reader.GetOutput()
        extent = image.GetExtent()
        expected_shape = og_shape
        resulting_shape = (extent[1]+1, (extent[3]+1), (extent[5]+1))
        self.assertEqual(resulting_shape, expected_shape)
        resulting_array = Converter.vtk2numpy(image)
        np.testing.assert_array_equal(self.input_3D_array, resulting_array)

        # # Now test if we get the correct z extent if we set that we
        # # have acquisition data
        # reader = cilBaseResampleReader()
        # reader.SetDatasetName("ImageData")
        target_size = 100
        reader.SetTargetSize(target_size)
        reader.SetIsAcquisitionData(True)
        reader.Update()
        image = reader.GetOutput()
        extent = image.GetExtent()
        shape_not_acquisition = calculate_target_downsample_shape(
            target_size, og_size, og_shape, acq=True)
        expected_size = shape_not_acquisition[0] * \
            shape_not_acquisition[1]*shape_not_acquisition[2]
        resulting_shape = (extent[1]+1, (extent[3]+1), (extent[5]+1))
        resulting_size = resulting_shape[0] * \
            resulting_shape[1]*resulting_shape[2]
        # angle (z direction) is first index in numpy array, and in cil
        # but it is the last in vtk.
        resulting_z_shape = extent[5]+1
        og_z_shape = np.shape(self.input_3D_array)[0]
        self.assertEqual(resulting_size, expected_size)
        self.assertEqual(resulting_z_shape, og_z_shape)

    def test_meta_and_numpy_resample_readers(self):
        # Tests image with correct target size is generated by resample reader:
        # Not a great test, but at least checks the resample reader runs
        # without crashing
        # TODO: improve this test
        readers = [cilNumpyResampleReader(), cilMetaImageResampleReader()]
        filenames = [self.numpy_filename_3D, self.meta_filename_3D]
        subtest_labels = ['cilNumpyResampleReader',
                          'cilMetaImageResampleReader']
        for i, reader in enumerate(readers):
            with self.subTest(reader=subtest_labels[i]):
                filename = filenames[i]
                og_shape = np.shape(self.input_3D_array)
                reader.SetFileName(filename)
                target_size = 100
                reader.SetTargetSize(target_size)
                reader.Update()
                image = reader.GetOutput()
                extent = image.GetExtent()
                resulting_shape = (extent[1]+1, (extent[3]+1), (extent[5]+1))
                og_shape = (og_shape[2], og_shape[1], og_shape[0])
                og_size = og_shape[0]*og_shape[1]*og_shape[2]
                expected_shape = calculate_target_downsample_shape(
                    target_size, og_size, og_shape)
                self.assertEqual(resulting_shape, expected_shape)

                # # Now test if we get the full image extent if our
                # # target size is larger than the size of the image:
                target_size = og_size*2
                reader.SetTargetSize(target_size)
                reader.Update()
                image = reader.GetOutput()
                extent = image.GetExtent()
                expected_shape = og_shape
                resulting_shape = (extent[1]+1, (extent[3]+1), (extent[5]+1))
                self.assertEqual(resulting_shape, expected_shape)
                resulting_array = Converter.vtk2numpy(image)
                np.testing.assert_array_equal(
                    self.input_3D_array, resulting_array)

                # # Now test if we get the correct z extent if we set that we
                # # have acquisition data
                target_size = 100
                reader.SetTargetSize(target_size)
                reader.SetIsAcquisitionData(True)
                reader.Update()
                image = reader.GetOutput()
                extent = image.GetExtent()
                shape_not_acquisition = calculate_target_downsample_shape(
                    target_size, og_size, og_shape, acq=True)
                expected_size = shape_not_acquisition[0] * \
                    shape_not_acquisition[1]*shape_not_acquisition[2]
                resulting_shape = (extent[1]+1, (extent[3]+1), (extent[5]+1))
                resulting_size = resulting_shape[0] * \
                    resulting_shape[1]*resulting_shape[2]
                # angle (z direction) is first index in numpy array, and in cil
                # but it is the last in vtk.
                resulting_z_shape = extent[5]+1
                og_z_shape = np.shape(self.input_3D_array)[0]
                self.assertEqual(resulting_size, expected_size)
                self.assertEqual(resulting_z_shape, og_z_shape)

    def tearDown(self):
        files = [self.raw_filename_3D]
        for f in files:
            os.remove(f)


if __name__ == '__main__':
    unittest.main()
