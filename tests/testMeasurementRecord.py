import unittest
import measurement_data
import jsonschema

class TestMeasurementRecord(unittest.TestCase):

    def test_create_json_validator(self):
        json_validator = measurement_data.create_json_validator()
        self.assertIsInstance(json_validator, jsonschema.validators.Draft7Validator)