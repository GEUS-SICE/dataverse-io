# -*- coding: utf-8 -*-
"""

@author: Adrien Wehrlé and Jason Box, GEUS (Geological Survey of Denmark 
and Greenland)

Pull data from a dataset in the SICE 'dataverse' at GEUS

Install pyDataverse: https://pydataverse.readthedocs.io/en/latest/
Dataverse user guide: https://guides.dataverse.org/en/4.19/user/

"""

import json
import requests 
import os
from pyDataverse.api import NativeApi, DataAccessApi 
from pyDataverse.models import Dataverse

# dataverse server and dataset DOI
dataverse_server = 'https://dataverse01.geus.dk'
persistentId = 'doi:targeted/doi' 

# dataverse token (personnal and private, has to be generated in 
# the dataverse account of the user)
api_key = 'you_api_key' 

# path to storage folder
folder_store = '/path/to/storage/'

# access the dataverse
api = NativeApi(dataverse_server, api_key)
data_api = DataAccessApi(dataverse_server, api_key)
dataset = api.get_dataset(persistentId)

# list of files located in each subfolder that need to be downloaded
# (SICE example)
file_list = ['r_TOA_01.tif', 'r_TOA_06.tif', 'r_TOA_17.tif', 'r_TOA_21.tif',
             'albedo_bb_planar_sw.tif', 'snow_specific_surface_area.tif',
             'SCDA_final.tif', 'BBA_combination.tif']

# %% download latest version of targeted files 

files_list = dataset.json()['data']['latestVersion']['files']

for file in files_list:
    
    if file['label'] in file_list:
        
        try:
            os.makedirs(folder_store + file['directoryLabel'])
        except:
            pass
            
        filename = file["dataFile"]["filename"]
        file_id = file["dataFile"]["id"]

        fn=folder_store + file['directoryLabel'] + os.sep + filename

        if bool(os.path.isfile(fn))==False:

            print("downloading "+fn)
            response = data_api.get_datafile(file_id)

            with open(fn, "wb") as f:
                f.write(response.content)

        else:
          print("---------------------- already exists "+fn)
