import datetime
import math
import os

import spp2086_measurement_data #if an error is thrown here you likely did not install the package correctly


def simple_example():
    
    record = spp2086_measurement_data.MeasurementRecord()

    #start building the header by hand
    header_dict = create_header()

    #add the header to the record and check if it's valid
    record.header = header_dict
    record.validate_header() #this line will throw an error if the header does not conform to the schema

    #add some parameters and validate the header again
    record.add_parameter('param 1', 1, 'm')
    record.add_parameter('param 2', [1.0, 2.3], 's', symbol='Ts')
    record.validate_header() #this line will throw an error if the header does not conform to the schema


    #create some test data
    grid_1_data = [math.pi*0.23*n for n in range(100)]
    grid_2_data = [0, 0.1]

    data_1 = [math.sin(x) for x in grid_1_data]
    data_2 = [math.cos(x) for x in grid_1_data]
    data_3 = [10, 12.2]

    #before a data channel is added the corresponding sampling grid must exist in the record object
    record.add_sampling_grid('grid 1', 's', grid_1_data)
    record.add_sampling_grid('grid 2', 'mm', grid_2_data)

    #add two data channels to sampling grid 1 and write them to an external file
    record.add_data_channel('sin', 'N', 0, data_1, storageType='externalFile')
    record.add_data_channel('cos', 'N', 0, data_2, storageType='externalFile', notes='Something interesting')

    #add an ex situ data channel to grid 2
    record.add_data_channel('Usability', '', 1, data_3, inProcess=False)


    #if desired change the sub directory for external files
    #record.rel_ext_filepath = 'data_test'

    #choose the location where the data is written to
    dir_path = os.path.dirname(os.path.realpath(__file__))
    write_filepath = os.path.join(dir_path, 'example_result.json')

    #write the data to the file
    record.write(write_filepath) #before the data is written it is validated against the schema so this might throw a validation error
   
    #read the data written to the file back into memory
    record_read = spp2086_measurement_data.MeasurementRecord.from_filename(write_filepath)

    return



def create_header():
    """
    Helper function to create a minimal header with meta data.
    Real processes will require more data.
     """

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


if __name__ == '__main__':
    simple_example()
