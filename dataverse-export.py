import json
import requests  # http://docs.python-requests.org/en/master/
import os

dataverse_server = 'https://dataverse01.geus.dk' # no trailing slash
api_key = '***'
# persistentId = 'doi:10.22008/FK2/8EYJSN' # deaccessioned dataset
persistentId = 'doi:10.22008/FK2/B674AR' # toa dataset
# persistentId = 'doi:10.22008/FK2/OIAJVO' # snow characteristics

#%% dataset content
from pyDataverse.api import NativeApi, DataAccessApi
from pyDataverse.models import Dataverse

api = NativeApi(dataverse_server,api_key)
data_api = DataAccessApi(dataverse_server)

dataset = api.get_dataset(persistentId)
files_DV_list = []

for file in dataset.json()['data']['latestVersion']['files']:
    if file["dataFile"]["filename"] !='height.tif':
        files_DV_list.append(file["directoryLabel"]+'/'+file["dataFile"]["filename"] )

#%% Finding where the code has crashed
# file_id_crash = file["dataFile"]['id']
# print(file_id_crash)
# for i, file in enumerate(dataset.json()['data']['latestVersion']['files']):        
#     if file["dataFile"]['id'] == file_id_crash:
#         break
# print(i, file["dataFile"]['id'])

 #%% Updatinge metadata files
   
# for i,file in enumerate(dataset.json()['data']['latestVersion']['files'][1975:]):        
#     params = dict(description= file["dataFile"]['description'] + ', pySICEv1.4',
#                 directoryLabel=file["directoryLabel"])
    
#     params_as_json_string = json.dumps(params)
    
#     payload = dict(jsonData=params_as_json_string)

#     url = '%s/api/files/%s/metadata' % (dataverse_server, str(file["dataFile"]['id']))
#     header = {"X-Dataverse-key": api_key}
#     print(i,'/',len(dataset.json()['data']['latestVersion']['files'][1975:]),
#           'updating ',file["directoryLabel"]+'/'+file["dataFile"]["filename"] )
#     r = requests.post(url, files=payload, headers=header)
    
#     print(r)
#%% Uploading files
# InputFolder = 'C:/Data_save/SICE/mosaics_masked/'
InputFolder = 'C:/Data_save/SICE/mosaics_masked/'

# file_list = ['al.tif', 'albedo_bb_planar_sw.tif', 'diagnostic_retrieval.tif',
# 'grain_diameter.tif',   'r0.tif',  'snow_specific_area.tif']

file_list = ['r_TOA_01.tif', 'r_TOA_02.tif', 'r_TOA_03.tif',  'r_TOA_04.tif', 'r_TOA_05.tif',
'r_TOA_06.tif',   'r_TOA_07.tif',   'r_TOA_08.tif',  'r_TOA_09.tif', 'r_TOA_10.tif', 'r_TOA_11.tif', 'r_TOA_12.tif', 'r_TOA_13.tif', 'r_TOA_14.tif',  'r_TOA_15.tif', 'r_TOA_16.tif',  'r_TOA_17.tif', 'r_TOA_18.tif', 'r_TOA_19.tif',   'r_TOA_20.tif',  'r_TOA_21.tif', 'O3.tif',   'OAA.tif',  'OZA.tif', 'SAA.tif', 'SZA.tif',    'WV.tif']
# 'ir_TOA_17.tif',  'ir_TOA_21.tif','OZA_eff.tif','SZA_eff.tif','r_TOA_S1.tif',   'r_TOA_S5.tif', 'r_TOA_S5_rc.tif',

file_description = 'SICE version: Cloud removed, PPGC, SNAP7'
 
overwrite = False

def upload_files_in_folder(InputFolder, file_list, file_description, overwrite = False):
    folder_list = [x[0] for x in os.walk(InputFolder)][1:]
    
    if not overwrite:
       print('Reading files on the dataverse')
       dataset = api.get_dataset(persistentId)
       files_DV_list = []
       
       for file in dataset.json()['data']['latestVersion']['files']:
           if file["dataFile"]["filename"] !='height.tif':
               files_DV_list.append(file["directoryLabel"]+'/'+file["dataFile"]["filename"] )
               
    for folder in folder_list:
        for file in file_list:
            # Checking if the file exist
            filename = folder[-10:]+'/'+file
            if not overwrite:
                if filename in files_DV_list:
                    print('skipping ',folder[-10:]+'/'+file)
                    continue
            try: 
                files = {'file': open(folder+'/' +file, "rb")}
            except Exception as e:
                print(e)
                continue
                
            params = dict(description=file_description,
                        directoryLabel=folder[-10:])
            
            params_as_json_string = json.dumps(params)
            
            payload = dict(jsonData=params_as_json_string)
    
            url_persistent_id = '%s/api/datasets/:persistentId/add?persistentId=%s&key=%s' % (dataverse_server, persistentId, api_key)
            print('loading ',folder[-10:]+'/'+file)
            r = requests.post(url_persistent_id, data=payload, files=files)
            
            print(r.json()['status'])
            if r.json()['status'] == 'ERROR':
                print(r.json())
    if folder == folder_list[-1] and r.json()['status'] == 'OK':
        return 'done'
    else:
        return filename

import time
flag = 'not done'
while flag != 'done':
   try:
       flag = upload_files_in_folder(InputFolder, file_list, file_description, overwrite = False)
   except:
       print('error, starting again')
       time.sleep(5)
            
#%% Removing files
# need to use
# https://guides.dataverse.org/en/5.1.1/api/sword.html#delete-a-file-by-database-id
# Delete a file by database id

# You must have EditDataset permission (Contributor role or above such as Curator or Admin) on the dataset to delete files.

# curl -u $API_TOKEN: -X DELETE https://$HOSTNAME/dvn/api/data-deposit/v1.1/swordv2/edit-media/file/123


# # InputFolder = 'C:/Data_save/SICE/mosaics_masked/'
# InputFolder = 'C:/Data_save/SICE/mosaics_masked/'
# folder_list = [x[0] for x in os.walk(InputFolder)][1:]

# for folder in folder_list:
  
#     file_list = [ ]
#     # 'ir_TOA_17.tif',  'ir_TOA_21.tif','OZA_eff.tif','SZA_eff.tif','r_TOA_S1.tif',   'r_TOA_S5.tif', 'r_TOA_S5_rc.tif',

#     for file in file_list:
        
#         # Checking if the file exist
#         filename = folder[-10:]+'/'+file
#         if filename in files_DV_list:
#             print('skipping ',folder[-10:]+'/'+file)
#             continue
#         try: 
#             files = {'file': open(folder+'/' +file, "rb")}
#         except Exception as e:
#             print(e)
#             continue
            
#         params = dict(description='SICE version: Cloud removed, PPGC, SNAP7',
#                     directoryLabel=folder[-10:])
        
#         params_as_json_string = json.dumps(params)
        
#         payload = dict(jsonData=params_as_json_string)

#         url_persistent_id = '%s/api/datasets/:persistentId/add?persistentId=%s&key=%s' % (dataverse_server, persistentId, api_key)
#         print('loading ',folder[-10:]+'/'+file)
#         r = requests.post(url_persistent_id, data=payload, files=files)
        
#         print(r.json()['status'])
#         if r.json()['status'] == 'ERROR':
#             print(r.json())
