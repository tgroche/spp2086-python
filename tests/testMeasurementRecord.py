import datetime
import unittest
import spp2086.measurement_data
import jsonschema
import tempfile
import os

class TestMeasurementRecord(unittest.TestCase):

    def test_create_json_validator(self):
        json_validator = spp2086.measurement_data.create_json_validator()
        self.assertIsInstance(json_validator, jsonschema.validators.Draft7Validator)


    def test_empty_header_not_valid(self):
        record = spp2086.measurement_data.MeasurementRecord()
        self.assertRaises(jsonschema.ValidationError, record.validate_header)


    def test_minimal_header_is_valid(self):
        record = spp2086.measurement_data.MeasurementRecord()
        record.header = self.create_minimal_header()
        try:
            record.validate_header()
        except Exception as err:
            self.fail(err)


    def test_minimal_header_not_valid_for_special_processes(self):
        record = spp2086.measurement_data.MeasurementRecord()
        header = self.create_minimal_header()
        header["process"]["processType"] = "test_process" #this is a process type with special restrictions
        record.header = header
        self.assertRaises(jsonschema.ValidationError, record.validate_header)


    def test_write_header_only(self):
        record = spp2086.measurement_data.MeasurementRecord()
        record.header = self.create_minimal_header()
        record.add_parameter("test", 1, "")
        filename = os.path.join(self._tempdir.name, "test_header_only.json")
        record.write(filename)

    
    def test_write_file_inplace_data_only(self):
        record = spp2086.measurement_data.MeasurementRecord()
        record.header = self.create_minimal_header()
        record.add_sampling_grid("grid", "", [1,2,3], storageType="inplace", notes="mockup")
        record.add_data_channel("mockup data", "1", 0, [0.1, 0.2, 0.1], inProcess=False) #default behaviour is inplace
        filename = os.path.join(self._tempdir.name, "test_inplace_data.json")
        record.write(filename)


    def test_write_file_inplace_external(self):
        record = spp2086.measurement_data.MeasurementRecord()
        record.header = self.create_minimal_header()
        record.add_sampling_grid("grid", "", [1,2,3], storageType="inplace", notes="mockup")
        record.add_data_channel("mockup data", "1", 0, [0.1, 0.2, 0.1], inProcess=True, storageType="externalFile")
        filename = os.path.join(self._tempdir.name, "test_external_file_data.json")
        record.write(filename)


    def test_read_write_file(self):
        record = spp2086.measurement_data.MeasurementRecord()
        record.header = self.create_minimal_header()
        record.add_sampling_grid("grid", "", [1,2,3], storageType="inplace", notes="mockup")
        write_data = [0.1, 0.2, 0.112]
        record.add_data_channel("mockup data", "1", 0, write_data, inProcess=True, storageType="externalFile")
        filename = os.path.join(self._tempdir.name, "test_read_write_data.json")
        record.write(filename)

        record_read = spp2086.measurement_data.MeasurementRecord.from_filename(filename)
        read_data = record_read.data_channels[0]["data"]
        self.assertEqual(write_data, read_data)


    def test_data_channel_util(self):
        record = spp2086.measurement_data.MeasurementRecord()
        grid_idx = record.add_sampling_grid("grid", "m", [1,2,3])
        record.add_data_channel("channel 1", "", grid_idx, [2,3,4])
        record.add_data_channel("channel 2", "", grid_idx, [2,1,4])

        channel_names = record.get_data_channel_names()
        self.assertListEqual(channel_names, ["channel 1", "channel 2"])
        channel, grid = record.get_data_channel("channel 1")
        self.assertDictEqual(channel, record.data_channels[0])
        self.assertDictEqual(grid, record.sampling_grids[0])
        self.assertRaises(ValueError, record.get_data_channel, "channel 3")


    def test_lazy_loading(self):
        record = spp2086.measurement_data.MeasurementRecord()
        record.header = self.create_minimal_header()
        record.add_sampling_grid("grid", "", [1,2,3], storageType="inplace", notes="mockup")
        write_data = [0.1, 0.2, 0.112]
        record.add_data_channel("mockup data", "1", 0, write_data, inProcess=True, storageType="externalFile")
        filename = os.path.join(self._tempdir.name, "test_read_write_data.json")
        record.write(filename)

        record_read = spp2086.measurement_data.MeasurementRecord.from_filename(filename, lazy_loading=True)
        
        #data should not be loaded yet
        self.assertIn("relativeFilePath", record_read.data_channels[0]["data"])
        
        #get data channel should load the file
        read_channel, read_grid = record_read.get_data_channel("mockup data")
        self.assertListEqual(write_data, read_channel["data"])


    @classmethod
    def create_minimal_header(cls) -> dict:       
        tool_dict = {"id": "ID1"}
        workpiece_dict = {"name": "test piece"}
        parameters_list = []
        process_dict = {
            "processType": "test process",
            "tool": tool_dict,
            "workpiece": workpiece_dict,
            "parameters": parameters_list
        }

        header_dict = {
            "projectName": "test project",
            "location": "nowhere",
            "creationDate": str(datetime.date.today()),
            "machine": {"name": "mockup machine"},
            "process": process_dict
        }

        return header_dict
    
    @classmethod
    def setUpClass(cls) -> None:
        cls._tempdir = tempfile.TemporaryDirectory()

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tempdir.cleanup()