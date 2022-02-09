import datetime
import unittest
import measurement_data
import jsonschema
import tempfile
import os

class TestMeasurementRecord(unittest.TestCase):

    def test_create_json_validator(self):
        json_validator = measurement_data.create_json_validator()
        self.assertIsInstance(json_validator, jsonschema.validators.Draft7Validator)


    def test_empty_header_not_valid(self):
        record = measurement_data.MeasurementRecord()
        self.assertRaises(jsonschema.ValidationError, record.validate_header)


    def test_minimal_header_is_valid(self):
        record = measurement_data.MeasurementRecord()
        record.header = self.create_minimal_header()
        try:
            record.validate_header()
        except Exception as err:
            self.fail(err)


    def test_minimal_header_not_valid_for_special_processes(self):
        record = measurement_data.MeasurementRecord()
        header = self.create_minimal_header()
        header["process"]["processType"] = "test_process" #this is a process type with special restrictions
        record.header = header
        self.assertRaises(jsonschema.ValidationError, record.validate_header)


    def test_write_header_only(self):
        record = measurement_data.MeasurementRecord()
        record.header = self.create_minimal_header()
        record.add_parameter("test", 1, "")
        filename = os.path.join(self._tempdir.name, "test_header_only.json")
        record.write(filename)

    
    def test_write_file_inplace_data_only(self):
        record = measurement_data.MeasurementRecord()
        record.header = self.create_minimal_header()
        record.add_sampling_grid("grid", "", [1,2,3], storageType="inplace", notes="mockup")
        record.add_data_channel("mockup data", "1", 0, [0.1, 0.2, 0.1], inProcess=False) #default behaviour is inplace
        filename = os.path.join(self._tempdir.name, "test_inplace_data.json")
        record.write(filename)


    def test_write_file_inplace_external(self):
        record = measurement_data.MeasurementRecord()
        record.header = self.create_minimal_header()
        record.add_sampling_grid("grid", "", [1,2,3], storageType="inplace", notes="mockup")
        record.add_data_channel("mockup data", "1", 0, [0.1, 0.2, 0.1], inProcess=True, storageType="externalFile")
        filename = os.path.join(self._tempdir.name, "test_inplace_data.json")
        record.write(filename)




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