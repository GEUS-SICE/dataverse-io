import json
import requests  # http://docs.python-requests.org/en/master/
import os
from pyDataverse.api import NativeApi, DataAccessApi
from pyDataverse.models import Dataverse
import time

dataverse_server = 'https://dataverse01.geus.dk'
api_key = '***' # need to get one from dataverse website if planning to edit/create datasets

persistentId = 'doi:10.22008/FK2/B674AR' # toa dataset
# persistentId = 'doi:10.22008/FK2/OIAJVO' # snow characteristics

api = NativeApi(dataverse_server,api_key)

#%% Exemple 1: getting list of files in dataset
dataset = api.get_dataset(persistentId)
files_DV_list = []

for file in dataset.json()['data']['latestVersion']['files']:
    if file["dataFile"]["filename"] !='height.tif':
        files_DV_list.append(file["directoryLabel"]+'/'+file["dataFile"]["filename"] )

#%% Example 2: Uploading files in subfolders
# The master folder containing daily subfolders
InputFolder = 'C:/Data_save/SICE/mosaics_masked/'
# the subfolders will be used as directory on the dataverse as well
# example: C:/Data_save/SICE/mosaics_masked/2017-09-15/r_TOA_03.tif will be uploaded as 2017-09-15/r_TOA_03.tif

# list of files located in each subfolder that needs to be uploaded:
file_list = ['r_TOA_01.tif', 'r_TOA_02.tif', 'r_TOA_03.tif',  'r_TOA_04.tif', 'r_TOA_05.tif', 'r_TOA_06.tif',   'r_TOA_07.tif',   'r_TOA_08.tif',  'r_TOA_09.tif', 'r_TOA_10.tif', 'r_TOA_11.tif', 'r_TOA_12.tif', 'r_TOA_13.tif', 'r_TOA_14.tif',  'r_TOA_15.tif', 'r_TOA_16.tif',  'r_TOA_17.tif', 'r_TOA_18.tif', 'r_TOA_19.tif',   'r_TOA_20.tif',  'r_TOA_21.tif', 'O3.tif',   'OAA.tif',  'OZA.tif', 'SAA.tif', 'SZA.tif',    'WV.tif']

# Add file description
file_description = 'SICE version: Cloud removed, PPGC, SNAP7'
# Here all files have the same description. The script could be modified to give file-specific description directly in the for loop below

overwrite = False
# if false, the script fetches the list of files already on the dataverse and compares, for each upload, whether a file with same name and same directory already exists

# main upload function, see below how it is being called
def upload_files_in_folder(InputFolder, file_list, file_description, overwrite = False):
    # listing subfolders in master folder
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
            filename = os.path.basename(os.path.normpath(folder))+'/'+file
            if not overwrite:
                if filename in files_DV_list:
                    print('skipping ',os.path.basename(os.path.normpath(folder))+'/'+file)
                    continue
            try: 
                files = {'file': open(folder+'/' +file, "rb")}
            except Exception as e:
                print(e)
                continue
                
            params = dict(description=file_description,
                        directoryLabel=os.path.basename(os.path.normpath(folder)))
            
            params_as_json_string = json.dumps(params)
            
            payload = dict(jsonData=params_as_json_string)
    
            url_persistent_id = '%s/api/datasets/:persistentId/add?persistentId=%s&key=%s' % (dataverse_server, persistentId, api_key)
            print('uploading ',os.path.basename(os.path.normpath(folder))+'/'+file)
            r = requests.post(url_persistent_id, data=payload, files=files)
            
            print(r.json()['status'])
            if r.json()['status'] == 'ERROR':
                print(r.json())
    if folder == folder_list[-1] and r.json()['status'] == 'OK':
        return 'done'
    else:
        return filename
    
# Calling the upload function:
# creating a while loop that will re-start the upload until it is done
# needed on my computer because some url requests were denied
# if failing, it waits 5 sec and starts again
flag = 'not done'
while flag != 'done':
   try:
       flag = upload_files_in_folder(InputFolder, file_list, file_description, overwrite = False)
   except Exception as e:
       print(e)
       print('... starting again')
       time.sleep(5)

 #%% Example 3: Updatinge metadata files
 # the code adds appends ", pySICEv1.4" to the existing file description for all files in a dataset. Slow, although the request is simple.
 
# dataverse_server = 'https://dataverse01.geus.dk'
# api_key = '***' 
# persistentId = 'doi:10.22008/FK2/OIAJVO' # snow characteristics

api = NativeApi(dataverse_server,api_key)
dataset = api.get_dataset(persistentId)
   
for i,file in enumerate(dataset.json()['data']['latestVersion']['files']):        
    params = dict(description= file["dataFile"]['description'] + ', pySICEv1.4',
                directoryLabel=file["directoryLabel"])
    
    params_as_json_string = json.dumps(params)
    
    payload = dict(jsonData=params_as_json_string)

    url = '%s/api/files/%s/metadata' % (dataverse_server, str(file["dataFile"]['id']))
    header = {"X-Dataverse-key": api_key}
    print(i,'/',len(dataset.json()['data']['latestVersion']['files']),
          'updating ',file["directoryLabel"]+'/'+file["dataFile"]["filename"] )
    r = requests.post(url, files=payload, headers=header)
    
    print(r)

#%% Finding where the code has crashed
# file_id_crash = file["dataFile"]['id']
# print(file_id_crash)
# for i, file in enumerate(dataset.json()['data']['latestVersion']['files']):        
#     if file["dataFile"]['id'] == file_id_crash:
#         break
# print(i, file["dataFile"]['id'])
        
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