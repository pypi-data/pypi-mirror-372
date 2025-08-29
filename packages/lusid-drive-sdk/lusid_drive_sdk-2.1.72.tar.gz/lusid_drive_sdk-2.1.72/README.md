<a id="documentation-for-api-endpoints"></a>
## Documentation for API Endpoints

All URIs are relative to *https://fbn-prd.lusid.com/drive*

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*ApplicationMetadataApi* | [**list_access_controlled_resources**](docs/ApplicationMetadataApi.md#list_access_controlled_resources) | **GET** /api/metadata/access/resources | [EARLY ACCESS] ListAccessControlledResources: Get resources available for access control
*FilesApi* | [**create_file**](docs/FilesApi.md#create_file) | **POST** /api/files | CreateFile: Uploads a file to Lusid Drive. If using an SDK, consider using the UploadAsStreamAsync function for larger files instead.
*FilesApi* | [**delete_file**](docs/FilesApi.md#delete_file) | **DELETE** /api/files/{id} | [EARLY ACCESS] DeleteFile: Deletes a file from Drive.
*FilesApi* | [**download_file**](docs/FilesApi.md#download_file) | **GET** /api/files/{id}/contents | DownloadFile: Download the file from Drive.
*FilesApi* | [**get_file**](docs/FilesApi.md#get_file) | **GET** /api/files/{id} | [EARLY ACCESS] GetFile: Get a file stored in Drive.
*FilesApi* | [**update_file_contents**](docs/FilesApi.md#update_file_contents) | **PUT** /api/files/{id}/contents | [EARLY ACCESS] UpdateFileContents: Updates contents of a file in Drive.
*FilesApi* | [**update_file_metadata**](docs/FilesApi.md#update_file_metadata) | **PUT** /api/files/{id} | [EARLY ACCESS] UpdateFileMetadata: Updates metadata for a file in Drive.
*FoldersApi* | [**create_folder**](docs/FoldersApi.md#create_folder) | **POST** /api/folders | [EARLY ACCESS] CreateFolder: Create a new folder in LUSID Drive
*FoldersApi* | [**delete_folder**](docs/FoldersApi.md#delete_folder) | **DELETE** /api/folders/{id} | [EARLY ACCESS] DeleteFolder: Delete a specified folder and all subfolders
*FoldersApi* | [**get_folder**](docs/FoldersApi.md#get_folder) | **GET** /api/folders/{id} | [EARLY ACCESS] GetFolder: Get metadata of folder
*FoldersApi* | [**get_folder_contents**](docs/FoldersApi.md#get_folder_contents) | **GET** /api/folders/{id}/contents | GetFolderContents: List contents of a folder
*FoldersApi* | [**get_root_folder**](docs/FoldersApi.md#get_root_folder) | **GET** /api/folders | GetRootFolder: List contents of root folder
*FoldersApi* | [**move_folder**](docs/FoldersApi.md#move_folder) | **POST** /api/folders/{id} | [EARLY ACCESS] MoveFolder: Move files to specified folder
*FoldersApi* | [**update_folder**](docs/FoldersApi.md#update_folder) | **PUT** /api/folders/{id} | [EARLY ACCESS] UpdateFolder: Update an existing folder's name, path
*SearchApi* | [**search**](docs/SearchApi.md#search) | **POST** /api/search | [EARLY ACCESS] Search: Search for a file or folder with a given name and path


<a id="documentation-for-models"></a>
## Documentation for Models

 - [AccessControlledAction](docs/AccessControlledAction.md)
 - [AccessControlledResource](docs/AccessControlledResource.md)
 - [ActionId](docs/ActionId.md)
 - [CreateFolder](docs/CreateFolder.md)
 - [IdSelectorDefinition](docs/IdSelectorDefinition.md)
 - [IdentifierPartSchema](docs/IdentifierPartSchema.md)
 - [Link](docs/Link.md)
 - [LusidProblemDetails](docs/LusidProblemDetails.md)
 - [LusidValidationProblemDetails](docs/LusidValidationProblemDetails.md)
 - [PagedResourceListOfStorageObject](docs/PagedResourceListOfStorageObject.md)
 - [ResourceListOfAccessControlledResource](docs/ResourceListOfAccessControlledResource.md)
 - [SearchBody](docs/SearchBody.md)
 - [StorageObject](docs/StorageObject.md)
 - [UpdateFile](docs/UpdateFile.md)
 - [UpdateFolder](docs/UpdateFolder.md)

