from typing import List
import hashlib
import os
import json
import itertools

import jsonschema
import importlib_resources

def create_json_validator():
    """ create a JSON validator from the stored SPP schema"""

    #load the schema from package resources
    package_resources = importlib_resources.files( __package__+".schemas")
    ref =  package_resources / "schema_spp2086.json"
    with importlib_resources.as_file(ref) as schema_filepath:
        with open(schema_filepath) as json_file:
            spp_schema = json.load(json_file)


    #check our schema against the draft-07 JSON schema specifications
    jsonschema.Draft7Validator.check_schema(spp_schema)

    return jsonschema.Draft7Validator(spp_schema)


class MeasurementRecord:
    """represents content of a JSON file and associated external files"""

    json_validator = create_json_validator()

    def __init__(self):
        self.sampling_grids = []
        self.data_channels = []
        self.header = {}
        self.base_filepath = ""
        self.rel_ext_filepath = "data"


    @classmethod
    def from_filename(cls, filename):
        """ Initialize instance from a file"""

        with open(filename, mode='rt', encoding='utf-8') as file:
            file_dict = json.load(file)
            cls.json_validator.validate(file_dict)

        header = file_dict["header"]
        sampling_grids = file_dict["data"]["samplingGrids"]
        data_channels = file_dict["data"]["dataChannels"]

        #read sampling grids and data channels into memory
        for data_iter in itertools.chain(sampling_grids, data_channels):
            if data_iter["storageType"] == "inplace":
                data_iter["data"] = cls.__read_inplace(data_iter["data"])
            elif data_iter["storageType"] == "externalFile":
                data_iter["data"] = cls.__read_from_external_file(data_iter["data"], filename)
            else:
                raise ValueError()

        self = cls()
        self.header = header
        self.sampling_grids = sampling_grids
        self.data_channels = data_channels
        return self


    def add_sampling_grid(self, name, unit, data, **kwargs):
        """ add a sampling grid"""

        storage_type = kwargs.pop("storageType", "inplace")
        notes = kwargs.pop("notes", None)

        if storage_type not in ("inplace", "externalFile"):
            raise ValueError("Unsupported storage type")

        sampling_grid = {
            "name": name,
            "unit": unit,
            "storageType": storage_type,
            "data": data,
        }

        if notes is not None:
            sampling_grid["notes"] = notes

        self.sampling_grids.append(sampling_grid)
        return len(self.sampling_grids)-1


    def add_data_channel(self, name, unit, sampling_grid_idx, data, **kwargs):
        """ add a data channel sampled over an existing sampling grid"""

        if sampling_grid_idx >= len(self.sampling_grids):
            raise ValueError("The specified sampling-grid index does not exist")

        in_process = kwargs.pop("inProcess", True)
        storage_type = kwargs.pop("storageType", "inplace")
        notes = kwargs.pop("notes", None)

        if storage_type not in ("inplace", "externalFile"):
            raise ValueError("Unsupported storage type")

        data_channel = {
            "name": name,
            "unit": unit,
            "samplingGridIndex": sampling_grid_idx,
            "storageType": storage_type,
            "inProcess": in_process,
            "data": data
        }

        if notes is not None:
            data_channel["notes"] = notes

        self.data_channels.append(data_channel)


    def write(self, filepath):
        """write the record to a compliant JSON file"""
        
        self.base_filepath = os.path.dirname(filepath)
        filename = os.path.splitext(os.path.basename(filepath))[0]
        self.rel_ext_filepath = os.path.join(self.rel_ext_filepath, filename)
        if not os.path.exists(self.base_filepath):
            os.makedirs(self.base_filepath)

        #write sampling grids and data channels
        for data_iter in itertools.chain(self.sampling_grids, self.data_channels):
            if data_iter["storageType"] == "inplace":
                data_iter["data"] = self.__write_inplace(data_iter["data"])
            elif data_iter["storageType"] == "externalFile":
                data_iter["data"] = self.__write_to_external_file(data_iter["data"], data_iter["name"])
            else:
                raise ValueError()

        file_dict = {
            "$schema": self.json_validator.schema["$id"],
            "header": self.header,
            "data": {"samplingGrids": self.sampling_grids, "dataChannels": self.data_channels}
            }

        with open(filepath, mode='wt', encoding='utf-8') as file:
            self.json_validator.validate(file_dict)
            json.dump(file_dict, file, ensure_ascii=False, indent=2)
        return


    def __write_inplace(self, data:List):
        return {"length": len(data), "items": data}


    def __write_to_external_file(self, data:List, filename:str):
        """write channel or grid data to an external file"""

        ext_filepath = os.path.join(self.base_filepath, self.rel_ext_filepath, filename + '.json')
        ext_file_dir =  os.path.join(self.base_filepath, self.rel_ext_filepath)

        if not os.path.exists(ext_file_dir):
            os.makedirs(ext_file_dir)

        #write as json to file
        with open(ext_filepath, mode='wt', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, separators=(',', ':'))
        
        #read back in binary mode for md5 hash
        with open(ext_filepath, mode='rb') as file:
            file_hash = hashlib.md5()
            while chunk := file.read(8192):
                file_hash.update(chunk)

        md5_checksum = file_hash.hexdigest()
       
        external_file = {
            "relativeFilePath": os.path.join(self.rel_ext_filepath, filename + '.json'),
            "md5": md5_checksum,
            "fileEncoding": "json"
        }
        return external_file

    @staticmethod
    def __read_inplace(data):
        return data["items"]

    @staticmethod
    def __read_from_external_file(external_file, base_filename):
        """read data from external file with absolute path given by filename"""

        md5_checksum_valid = external_file["md5"]
        file_encoding = external_file["fileEncoding"]
        relative_filepath = external_file["relativeFilePath"]
        
        filename = os.path.join(os.path.dirname(base_filename), relative_filepath)

        #read back in binary mode for md5 hash
        with open(filename, mode='rb') as file:
            file_hash = hashlib.md5()
            while chunk := file.read(8192):
                file_hash.update(chunk)

        md5_checksum_actual = file_hash.hexdigest()

        if md5_checksum_actual != md5_checksum_valid:
            raise RuntimeError(f"calculated md5 checksum of {filename} is different from the specified one")


        with open(filename, mode='rt', encoding='utf-8') as file:
            if file_encoding == "json":
                data = json.load(file)
            else:
                raise RuntimeError(f"Unkown encoding {file_encoding}")
        
        return data
