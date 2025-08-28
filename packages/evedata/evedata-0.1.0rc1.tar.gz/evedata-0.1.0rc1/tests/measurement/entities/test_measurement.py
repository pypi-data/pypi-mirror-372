import unittest

import numpy as np

from evedata.measurement.entities import measurement


class TestMeasurement(unittest.TestCase):
    def setUp(self):
        self.measurement = measurement.Measurement()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "scan_modules",
            "machine",
            "beamline",
            "device_snapshots",
            "metadata",
            "scan",
            "station",
            "log_messages",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.measurement, attribute))


class TestData(unittest.TestCase):
    def setUp(self):
        self.data = measurement.Data()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "data",
            "axes",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_data_is_ndarray(self):
        self.assertTrue(isinstance(self.data.data, np.ndarray))

    def test_axes_is_list(self):
        self.assertTrue(isinstance(self.data.axes, list))

    def test_axes_have_right_count_for_1d_data(self):
        self.data.data = np.zeros(0)
        self.assertEqual(len(self.data.axes), 2)

    def test_axes_have_right_count_for_2d_data(self):
        self.data.data = np.zeros([0, 0])
        self.assertEqual(len(self.data.axes), 3)

    def test_modify_data_with_same_dimension_does_not_change_axes(self):
        data = np.zeros(5)
        axis_values = np.arange(len(data))
        self.data.data = data
        self.data.axes[0].values = axis_values
        self.data.data = data
        self.assertTrue(np.allclose(self.data.axes[0].values, axis_values))

    def test_modify_data_with_different_dimensions_keeps_axes_metadata(self):
        old_data = np.zeros([5, 1])
        new_data = np.zeros([5, 2])
        axis_quantity = "foobar"
        self.data.data = old_data
        self.data.axes[0].values = np.arange(len(old_data))
        self.data.axes[0].quantity = axis_quantity
        self.data.data = new_data
        self.assertTrue(self.data.axes[0].quantity, axis_quantity)

    def test_modify_data_with_different_dimensions_adjusts_axes_values(self):
        old_data = np.zeros([5, 1])
        new_data = np.zeros([7, 1])
        self.data.data = old_data
        self.data.axes[0].values = np.arange(len(old_data))
        self.data.data = new_data
        self.assertEqual(new_data.size, self.data.axes[0].values.size)

    def test_modify_data_with_higher_dimension_adds_axis(self):
        old_data = np.random.random([5, 1])
        new_data = np.random.random([4, 3, 2])
        self.data.data = old_data
        self.data.data = new_data
        self.assertEqual(4, len(self.data.axes))

    def test_setting_data_adjusts_axes_values(self):
        new_data = np.zeros([6, 1])
        self.data.data = new_data
        self.assertEqual(new_data.size, self.data.axes[0].values.size)

    def test_setting_data_adjusts_axes_values_for_2D_data(self):
        self.data.data = np.zeros([6, 3])
        shape = self.data.data.shape
        self.assertEqual(shape[0], len(self.data.axes[0].values))
        self.assertEqual(shape[1], len(self.data.axes[1].values))


class TestAxisSetupInConstructor(unittest.TestCase):
    def setUp(self):
        self.data = np.zeros(0)
        self.axes = [measurement.Axis(), measurement.Axis()]
        self.calculated = True

    def test_set_data_in_constructor(self):
        data_obj = measurement.Data(data=self.data)
        self.assertEqual(data_obj.data.tolist(), self.data.tolist())

    def test_set_axes_in_constructor(self):
        data_obj = measurement.Data(axes=self.axes)
        self.assertEqual(data_obj.axes, self.axes)

    def test_setting_too_many_axes_raises(self):
        axes = self.axes
        axes.append(measurement.Axis())
        with self.assertRaises(IndexError):
            measurement.Data(self.data, axes)

    def test_axes_values_dimensions_are_consistent_with_empty_1D_data(self):
        data_obj = measurement.Data(self.data, self.axes)
        self.assertEqual(len(data_obj.axes[0].values), 0)

    def test_axes_values_dimensions_are_consistent_with_empty_2D_data(self):
        tmp_data = np.zeros([0, 0])
        data_obj = measurement.Data(tmp_data)
        self.assertEqual(len(data_obj.axes[0].values), 0)
        self.assertEqual(len(data_obj.axes[1].values), 0)

    def test_axes_values_dimensions_are_consistent_with_nonempty_1D_data(
        self,
    ):
        len_data = 5
        tmp_data = np.zeros(len_data)
        tmp_axes = [measurement.Axis(), measurement.Axis()]
        tmp_axes[0].values = np.zeros(len_data)
        data_obj = measurement.Data(tmp_data, tmp_axes)
        self.assertEqual(len(data_obj.axes[0].values), len_data)

    def test_axes_values_dimensions_are_consistent_with_nonempty_2D_data(
        self,
    ):
        len_data = [5, 3]
        tmp_data = np.zeros(len_data)
        tmp_axes = [
            measurement.Axis(),
            measurement.Axis(),
            measurement.Axis(),
        ]
        tmp_axes[0].values = np.zeros(len_data[0])
        tmp_axes[1].values = np.zeros(len_data[1])
        data_obj = measurement.Data(tmp_data, tmp_axes)
        self.assertEqual(len(data_obj.axes[0].values), len_data[0])
        self.assertEqual(len(data_obj.axes[1].values), len_data[1])

    def test_wrong_axes_values_dimensions_with_nonempty_1D_data_raises(self):
        len_data = 5
        tmp_data = np.zeros(len_data)
        with self.assertRaises(IndexError):
            measurement.Data(tmp_data, self.axes)

    def test_wrong_axes_values_dimensions_with_nonempty_2D_data_raises(self):
        len_data = [5, 3]
        tmp_data = np.zeros(len_data)
        with self.assertRaises(IndexError):
            measurement.Data(tmp_data, self.axes)

    def test_set_wrong_axes_dimensions_with_nonempty_1D_data_raises(self):
        len_data = 5
        tmp_data = np.zeros(len_data)
        tmp_axis = measurement.Axis()
        tmp_axis.values = np.zeros(2 * len_data)
        tmp_axes = [tmp_axis, measurement.Axis()]
        with self.assertRaises(IndexError):
            measurement.Data(tmp_data, tmp_axes)

    def test_set_wrong_axes_dimensions_with_nonempty_2D_data_raises(self):
        len_data = [5, 3]
        tmp_data = np.zeros(len_data)
        tmp_axis1 = measurement.Axis()
        tmp_axis1.values = np.zeros(2 * len_data[0])
        tmp_axis2 = measurement.Axis()
        tmp_axis2.values = np.zeros(2 * len_data[1])
        tmp_axes = [tmp_axis1, tmp_axis2, measurement.Axis()]
        with self.assertRaises(IndexError):
            measurement.Data(tmp_data, tmp_axes)


class TestAxis(unittest.TestCase):
    def setUp(self):
        self.axis = measurement.Axis()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "values",
            "label",
            "quantity",
            "symbol",
            "unit",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.axis, attribute))

    def test_values_is_ndarray(self):
        self.assertTrue(isinstance(self.axis.values, np.ndarray))

    def test_values_is_1d(self):
        self.assertTrue(self.axis.values.ndim, 1)

    def test_has_equidistant_property(self):
        self.assertTrue(hasattr(self.axis, "equidistant"))

    def test_equidistant_is_none_by_default(self):
        self.assertEqual(self.axis.equidistant, None)

    def test_equidistant_is_true_for_equidistant_axes(self):
        self.axis.values = np.linspace(330, 340, num=1024, endpoint=True)
        self.assertTrue(self.axis.equidistant)

    def test_equidistant_is_false_for_nonequidistant_axes(self):
        self.axis.values = np.asarray([0, 1, 2, 4, 8])
        self.assertFalse(self.axis.equidistant)

    def test_set_values(self):
        self.axis.values = np.zeros(0)

    def test_set_wrong_type_for_values_fails(self):
        with self.assertRaisesRegex(ValueError, "Wrong type: expected"):
            self.axis.values = "foo"

    def test_set_multidimensional_values_fails(self):
        with self.assertRaisesRegex(
            IndexError, "Values need to be " "one-dimensional"
        ):
            self.axis.values = np.zeros([0, 0])
