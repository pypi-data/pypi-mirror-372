# spice_client.DefaultApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_one_asset**](DefaultApi.md#create_one_asset) | **POST** /api/assets | Create one asset
[**create_one_experiment**](DefaultApi.md#create_one_experiment) | **POST** /api/experiments | Create one experiment
[**create_one_location**](DefaultApi.md#create_one_location) | **POST** /api/locations | Create one location
[**create_one_project**](DefaultApi.md#create_one_project) | **POST** /api/projects | Create one project
[**create_one_sample**](DefaultApi.md#create_one_sample) | **POST** /api/samples | Create one sample
[**create_one_tray_configuration**](DefaultApi.md#create_one_tray_configuration) | **POST** /api/tray_configurations | Create one tray_configuration
[**create_one_treatment**](DefaultApi.md#create_one_treatment) | **POST** /api/treatments | Create one treatment
[**delete_many_assets**](DefaultApi.md#delete_many_assets) | **DELETE** /api/assets/batch | Delete many assets
[**delete_many_experiments**](DefaultApi.md#delete_many_experiments) | **DELETE** /api/experiments/batch | Delete many experiments
[**delete_many_locations**](DefaultApi.md#delete_many_locations) | **DELETE** /api/locations/batch | Delete many locations
[**delete_many_projects**](DefaultApi.md#delete_many_projects) | **DELETE** /api/projects/batch | Delete many projects
[**delete_many_samples**](DefaultApi.md#delete_many_samples) | **DELETE** /api/samples/batch | Delete many samples
[**delete_many_tray_configurations**](DefaultApi.md#delete_many_tray_configurations) | **DELETE** /api/tray_configurations/batch | Delete many tray_configurations
[**delete_many_treatments**](DefaultApi.md#delete_many_treatments) | **DELETE** /api/treatments/batch | Delete many treatments
[**delete_one_asset**](DefaultApi.md#delete_one_asset) | **DELETE** /api/assets/{id} | Delete one asset
[**delete_one_experiment**](DefaultApi.md#delete_one_experiment) | **DELETE** /api/experiments/{id} | Delete one experiment
[**delete_one_location**](DefaultApi.md#delete_one_location) | **DELETE** /api/locations/{id} | Delete one location
[**delete_one_project**](DefaultApi.md#delete_one_project) | **DELETE** /api/projects/{id} | Delete one project
[**delete_one_sample**](DefaultApi.md#delete_one_sample) | **DELETE** /api/samples/{id} | Delete one sample
[**delete_one_tray_configuration**](DefaultApi.md#delete_one_tray_configuration) | **DELETE** /api/tray_configurations/{id} | Delete one tray_configuration
[**delete_one_treatment**](DefaultApi.md#delete_one_treatment) | **DELETE** /api/treatments/{id} | Delete one treatment
[**get_all_assets**](DefaultApi.md#get_all_assets) | **GET** /api/assets | Get all assets
[**get_all_experiments**](DefaultApi.md#get_all_experiments) | **GET** /api/experiments | Get all experiments
[**get_all_locations**](DefaultApi.md#get_all_locations) | **GET** /api/locations | Get all locations
[**get_all_projects**](DefaultApi.md#get_all_projects) | **GET** /api/projects | Get all projects
[**get_all_samples**](DefaultApi.md#get_all_samples) | **GET** /api/samples | Get all samples
[**get_all_tray_configurations**](DefaultApi.md#get_all_tray_configurations) | **GET** /api/tray_configurations | Get all tray_configurations
[**get_all_treatments**](DefaultApi.md#get_all_treatments) | **GET** /api/treatments | Get all treatments
[**get_one_asset**](DefaultApi.md#get_one_asset) | **GET** /api/assets/{id} | Get one asset
[**get_one_experiment**](DefaultApi.md#get_one_experiment) | **GET** /api/experiments/{id} | Get one experiment
[**get_one_location**](DefaultApi.md#get_one_location) | **GET** /api/locations/{id} | Get one location
[**get_one_project**](DefaultApi.md#get_one_project) | **GET** /api/projects/{id} | Get one project
[**get_one_sample**](DefaultApi.md#get_one_sample) | **GET** /api/samples/{id} | Get one sample
[**get_one_tray_configuration**](DefaultApi.md#get_one_tray_configuration) | **GET** /api/tray_configurations/{id} | Get one tray_configuration
[**get_one_treatment**](DefaultApi.md#get_one_treatment) | **GET** /api/treatments/{id} | Get one treatment
[**get_ui_config**](DefaultApi.md#get_ui_config) | **GET** /api/config | 
[**healthz**](DefaultApi.md#healthz) | **GET** /healthz | 
[**update_one_asset**](DefaultApi.md#update_one_asset) | **PUT** /api/assets/{id} | Update one asset
[**update_one_experiment**](DefaultApi.md#update_one_experiment) | **PUT** /api/experiments/{id} | Update one experiment
[**update_one_location**](DefaultApi.md#update_one_location) | **PUT** /api/locations/{id} | Update one location
[**update_one_project**](DefaultApi.md#update_one_project) | **PUT** /api/projects/{id} | Update one project
[**update_one_sample**](DefaultApi.md#update_one_sample) | **PUT** /api/samples/{id} | Update one sample
[**update_one_tray_configuration**](DefaultApi.md#update_one_tray_configuration) | **PUT** /api/tray_configurations/{id} | Update one tray_configuration
[**update_one_treatment**](DefaultApi.md#update_one_treatment) | **PUT** /api/treatments/{id} | Update one treatment


# **create_one_asset**
> Asset create_one_asset(asset_create)

Create one asset

Creates a new asset.

This resource represents assets stored in S3, including metadata such as file size, type, and upload details.

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import spice_client
from spice_client.models.asset import Asset
from spice_client.models.asset_create import AssetCreate
from spice_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = spice_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = spice_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with spice_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = spice_client.DefaultApi(api_client)
    asset_create = spice_client.AssetCreate() # AssetCreate | 

    try:
        # Create one asset
        api_response = api_instance.create_one_asset(asset_create)
        print("The response of DefaultApi->create_one_asset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->create_one_asset: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **asset_create** | [**AssetCreate**](AssetCreate.md)|  | 

### Return type

[**Asset**](Asset.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json, text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Resource created successfully |  -  |
**409** | Duplicate record |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_one_experiment**
> Experiment create_one_experiment(experiment_create)

Create one experiment

Creates a new experiment.

Experiments track ice nucleation testing sessions with associated data and results.

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import spice_client
from spice_client.models.experiment import Experiment
from spice_client.models.experiment_create import ExperimentCreate
from spice_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = spice_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = spice_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with spice_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = spice_client.DefaultApi(api_client)
    experiment_create = spice_client.ExperimentCreate() # ExperimentCreate | 

    try:
        # Create one experiment
        api_response = api_instance.create_one_experiment(experiment_create)
        print("The response of DefaultApi->create_one_experiment:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->create_one_experiment: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **experiment_create** | [**ExperimentCreate**](ExperimentCreate.md)|  | 

### Return type

[**Experiment**](Experiment.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json, text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Resource created successfully |  -  |
**409** | Duplicate record |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_one_location**
> Location create_one_location(location_create)

Create one location

Creates a new location.

Locations represent physical places where experiments are conducted. Each location belongs to a project and can contain multiple samples and experiments.

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import spice_client
from spice_client.models.location import Location
from spice_client.models.location_create import LocationCreate
from spice_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = spice_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = spice_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with spice_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = spice_client.DefaultApi(api_client)
    location_create = spice_client.LocationCreate() # LocationCreate | 

    try:
        # Create one location
        api_response = api_instance.create_one_location(location_create)
        print("The response of DefaultApi->create_one_location:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->create_one_location: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **location_create** | [**LocationCreate**](LocationCreate.md)|  | 

### Return type

[**Location**](Location.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json, text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Resource created successfully |  -  |
**409** | Duplicate record |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_one_project**
> Project create_one_project(project_create)

Create one project

Creates a new project.

Projects provide a way to organise locations hierarchically. Each project can contain multiple locations and provides visual organization through color coding.

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import spice_client
from spice_client.models.project import Project
from spice_client.models.project_create import ProjectCreate
from spice_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = spice_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = spice_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with spice_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = spice_client.DefaultApi(api_client)
    project_create = spice_client.ProjectCreate() # ProjectCreate | 

    try:
        # Create one project
        api_response = api_instance.create_one_project(project_create)
        print("The response of DefaultApi->create_one_project:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->create_one_project: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_create** | [**ProjectCreate**](ProjectCreate.md)|  | 

### Return type

[**Project**](Project.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json, text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Resource created successfully |  -  |
**409** | Duplicate record |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_one_sample**
> Sample create_one_sample(sample_create)

Create one sample

Creates a new sample.

This resource manages samples associated with experiments.

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import spice_client
from spice_client.models.sample import Sample
from spice_client.models.sample_create import SampleCreate
from spice_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = spice_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = spice_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with spice_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = spice_client.DefaultApi(api_client)
    sample_create = spice_client.SampleCreate() # SampleCreate | 

    try:
        # Create one sample
        api_response = api_instance.create_one_sample(sample_create)
        print("The response of DefaultApi->create_one_sample:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->create_one_sample: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sample_create** | [**SampleCreate**](SampleCreate.md)|  | 

### Return type

[**Sample**](Sample.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json, text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Resource created successfully |  -  |
**409** | Duplicate record |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_one_tray_configuration**
> TrayConfiguration create_one_tray_configuration(tray_configuration_create)

Create one tray_configuration

Creates a new tray_configuration.

This endpoint manages tray configurations, which define the setup of trays used in experiments.

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import spice_client
from spice_client.models.tray_configuration import TrayConfiguration
from spice_client.models.tray_configuration_create import TrayConfigurationCreate
from spice_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = spice_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = spice_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with spice_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = spice_client.DefaultApi(api_client)
    tray_configuration_create = spice_client.TrayConfigurationCreate() # TrayConfigurationCreate | 

    try:
        # Create one tray_configuration
        api_response = api_instance.create_one_tray_configuration(tray_configuration_create)
        print("The response of DefaultApi->create_one_tray_configuration:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->create_one_tray_configuration: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **tray_configuration_create** | [**TrayConfigurationCreate**](TrayConfigurationCreate.md)|  | 

### Return type

[**TrayConfiguration**](TrayConfiguration.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json, text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Resource created successfully |  -  |
**409** | Duplicate record |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_one_treatment**
> Treatment create_one_treatment(treatment_create)

Create one treatment

Creates a new treatment.

Treatments are applied to samples during experiments to study their effects on ice nucleation.

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import spice_client
from spice_client.models.treatment import Treatment
from spice_client.models.treatment_create import TreatmentCreate
from spice_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = spice_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = spice_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with spice_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = spice_client.DefaultApi(api_client)
    treatment_create = spice_client.TreatmentCreate() # TreatmentCreate | 

    try:
        # Create one treatment
        api_response = api_instance.create_one_treatment(treatment_create)
        print("The response of DefaultApi->create_one_treatment:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->create_one_treatment: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **treatment_create** | [**TreatmentCreate**](TreatmentCreate.md)|  | 

### Return type

[**Treatment**](Treatment.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json, text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Resource created successfully |  -  |
**409** | Duplicate record |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_many_assets**
> List[str] delete_many_assets(request_body)

Delete many assets

Deletes many assets by their IDs and returns array of deleted UUIDs.

This resource represents assets stored in S3, including metadata such as file size, type, and upload details.

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import spice_client
from spice_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = spice_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = spice_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with spice_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = spice_client.DefaultApi(api_client)
    request_body = ['request_body_example'] # List[str] | 

    try:
        # Delete many assets
        api_response = api_instance.delete_many_assets(request_body)
        print("The response of DefaultApi->delete_many_assets:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->delete_many_assets: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_body** | [**List[str]**](str.md)|  | 

### Return type

**List[str]**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json, text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Resources deleted successfully |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_many_experiments**
> List[str] delete_many_experiments(request_body)

Delete many experiments

Deletes many experiments by their IDs and returns array of deleted UUIDs.

Experiments track ice nucleation testing sessions with associated data and results.

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import spice_client
from spice_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = spice_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = spice_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with spice_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = spice_client.DefaultApi(api_client)
    request_body = ['request_body_example'] # List[str] | 

    try:
        # Delete many experiments
        api_response = api_instance.delete_many_experiments(request_body)
        print("The response of DefaultApi->delete_many_experiments:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->delete_many_experiments: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_body** | [**List[str]**](str.md)|  | 

### Return type

**List[str]**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json, text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Resources deleted successfully |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_many_locations**
> List[str] delete_many_locations(request_body)

Delete many locations

Deletes many locations by their IDs and returns array of deleted UUIDs.

Locations represent physical places where experiments are conducted. Each location belongs to a project and can contain multiple samples and experiments.

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import spice_client
from spice_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = spice_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = spice_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with spice_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = spice_client.DefaultApi(api_client)
    request_body = ['request_body_example'] # List[str] | 

    try:
        # Delete many locations
        api_response = api_instance.delete_many_locations(request_body)
        print("The response of DefaultApi->delete_many_locations:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->delete_many_locations: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_body** | [**List[str]**](str.md)|  | 

### Return type

**List[str]**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json, text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Resources deleted successfully |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_many_projects**
> List[str] delete_many_projects(request_body)

Delete many projects

Deletes many projects by their IDs and returns array of deleted UUIDs.

Projects provide a way to organise locations hierarchically. Each project can contain multiple locations and provides visual organization through color coding.

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import spice_client
from spice_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = spice_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = spice_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with spice_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = spice_client.DefaultApi(api_client)
    request_body = ['request_body_example'] # List[str] | 

    try:
        # Delete many projects
        api_response = api_instance.delete_many_projects(request_body)
        print("The response of DefaultApi->delete_many_projects:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->delete_many_projects: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_body** | [**List[str]**](str.md)|  | 

### Return type

**List[str]**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json, text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Resources deleted successfully |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_many_samples**
> List[str] delete_many_samples(request_body)

Delete many samples

Deletes many samples by their IDs and returns array of deleted UUIDs.

This resource manages samples associated with experiments.

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import spice_client
from spice_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = spice_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = spice_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with spice_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = spice_client.DefaultApi(api_client)
    request_body = ['request_body_example'] # List[str] | 

    try:
        # Delete many samples
        api_response = api_instance.delete_many_samples(request_body)
        print("The response of DefaultApi->delete_many_samples:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->delete_many_samples: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_body** | [**List[str]**](str.md)|  | 

### Return type

**List[str]**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json, text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Resources deleted successfully |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_many_tray_configurations**
> List[str] delete_many_tray_configurations(request_body)

Delete many tray_configurations

Deletes many tray_configurations by their IDs and returns array of deleted UUIDs.

This endpoint manages tray configurations, which define the setup of trays used in experiments.

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import spice_client
from spice_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = spice_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = spice_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with spice_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = spice_client.DefaultApi(api_client)
    request_body = ['request_body_example'] # List[str] | 

    try:
        # Delete many tray_configurations
        api_response = api_instance.delete_many_tray_configurations(request_body)
        print("The response of DefaultApi->delete_many_tray_configurations:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->delete_many_tray_configurations: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_body** | [**List[str]**](str.md)|  | 

### Return type

**List[str]**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json, text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Resources deleted successfully |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_many_treatments**
> List[str] delete_many_treatments(request_body)

Delete many treatments

Deletes many treatments by their IDs and returns array of deleted UUIDs.

Treatments are applied to samples during experiments to study their effects on ice nucleation.

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import spice_client
from spice_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = spice_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = spice_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with spice_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = spice_client.DefaultApi(api_client)
    request_body = ['request_body_example'] # List[str] | 

    try:
        # Delete many treatments
        api_response = api_instance.delete_many_treatments(request_body)
        print("The response of DefaultApi->delete_many_treatments:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->delete_many_treatments: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_body** | [**List[str]**](str.md)|  | 

### Return type

**List[str]**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json, text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Resources deleted successfully |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_one_asset**
> delete_one_asset(id)

Delete one asset

Deletes one asset by its ID.

This resource represents assets stored in S3, including metadata such as file size, type, and upload details.

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import spice_client
from spice_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = spice_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = spice_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with spice_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = spice_client.DefaultApi(api_client)
    id = 'id_example' # str | 

    try:
        # Delete one asset
        api_instance.delete_one_asset(id)
    except Exception as e:
        print("Exception when calling DefaultApi->delete_one_asset: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 

### Return type

void (empty response body)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Resource deleted successfully |  -  |
**404** | Resource not found |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_one_experiment**
> delete_one_experiment(id)

Delete one experiment

Deletes one experiment by its ID.

Experiments track ice nucleation testing sessions with associated data and results.

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import spice_client
from spice_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = spice_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = spice_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with spice_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = spice_client.DefaultApi(api_client)
    id = 'id_example' # str | 

    try:
        # Delete one experiment
        api_instance.delete_one_experiment(id)
    except Exception as e:
        print("Exception when calling DefaultApi->delete_one_experiment: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 

### Return type

void (empty response body)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Resource deleted successfully |  -  |
**404** | Resource not found |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_one_location**
> delete_one_location(id)

Delete one location

Deletes one location by its ID.

Locations represent physical places where experiments are conducted. Each location belongs to a project and can contain multiple samples and experiments.

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import spice_client
from spice_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = spice_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = spice_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with spice_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = spice_client.DefaultApi(api_client)
    id = 'id_example' # str | 

    try:
        # Delete one location
        api_instance.delete_one_location(id)
    except Exception as e:
        print("Exception when calling DefaultApi->delete_one_location: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 

### Return type

void (empty response body)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Resource deleted successfully |  -  |
**404** | Resource not found |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_one_project**
> delete_one_project(id)

Delete one project

Deletes one project by its ID.

Projects provide a way to organise locations hierarchically. Each project can contain multiple locations and provides visual organization through color coding.

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import spice_client
from spice_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = spice_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = spice_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with spice_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = spice_client.DefaultApi(api_client)
    id = 'id_example' # str | 

    try:
        # Delete one project
        api_instance.delete_one_project(id)
    except Exception as e:
        print("Exception when calling DefaultApi->delete_one_project: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 

### Return type

void (empty response body)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Resource deleted successfully |  -  |
**404** | Resource not found |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_one_sample**
> delete_one_sample(id)

Delete one sample

Deletes one sample by its ID.

This resource manages samples associated with experiments.

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import spice_client
from spice_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = spice_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = spice_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with spice_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = spice_client.DefaultApi(api_client)
    id = 'id_example' # str | 

    try:
        # Delete one sample
        api_instance.delete_one_sample(id)
    except Exception as e:
        print("Exception when calling DefaultApi->delete_one_sample: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 

### Return type

void (empty response body)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Resource deleted successfully |  -  |
**404** | Resource not found |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_one_tray_configuration**
> delete_one_tray_configuration(id)

Delete one tray_configuration

Deletes one tray_configuration by its ID.

This endpoint manages tray configurations, which define the setup of trays used in experiments.

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import spice_client
from spice_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = spice_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = spice_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with spice_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = spice_client.DefaultApi(api_client)
    id = 'id_example' # str | 

    try:
        # Delete one tray_configuration
        api_instance.delete_one_tray_configuration(id)
    except Exception as e:
        print("Exception when calling DefaultApi->delete_one_tray_configuration: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 

### Return type

void (empty response body)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Resource deleted successfully |  -  |
**404** | Resource not found |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_one_treatment**
> delete_one_treatment(id)

Delete one treatment

Deletes one treatment by its ID.

Treatments are applied to samples during experiments to study their effects on ice nucleation.

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import spice_client
from spice_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = spice_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = spice_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with spice_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = spice_client.DefaultApi(api_client)
    id = 'id_example' # str | 

    try:
        # Delete one treatment
        api_instance.delete_one_treatment(id)
    except Exception as e:
        print("Exception when calling DefaultApi->delete_one_treatment: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 

### Return type

void (empty response body)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Resource deleted successfully |  -  |
**404** | Resource not found |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_all_assets**
> List[AssetList] get_all_assets(filter=filter, range=range, page=page, per_page=per_page, sort=sort, sort_by=sort_by, order=order)

Get all assets

Retrieves all assets.

This resource represents assets stored in S3, including metadata such as file size, type, and upload details.

Additional sortable columns: 
- experiment_id
- original_filename
- s3_key
- size_bytes
- uploaded_by
- uploaded_at
- created_at
- last_updated
- type
- role
- processing_status.

Additional filterable columns: 
- experiment_id
- original_filename
- s3_key
- uploaded_by
- is_deleted
- type
- role
- processing_status
- processing_message.

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import spice_client
from spice_client.models.asset_list import AssetList
from spice_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = spice_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = spice_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with spice_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = spice_client.DefaultApi(api_client)
    filter = '{\"id\":\"550e8400-e29b-41d4-a716-446655440000\",\"name\":\"example\",\"q\":\"search text\"}' # str | JSON-encoded filter for querying resources.  This parameter supports various filtering options: - Free text search: `{\"q\": \"search text\"}` - Filtering by a single ID: `{\"id\": \"550e8400-e29b-41d4-a716-446655440000\"}` - Filtering by multiple IDs: `{\"id\": [\"550e8400-e29b-41d4-a716-446655440000\", \"550e8400-e29b-41d4-a716-446655440001\"]}` - Filtering on other columns: `{\"name\": \"example\"}` (optional)
    range = '[0,9]' # str | Range for pagination in the format \"[start, end]\".  Example: `[0,9]` (optional)
    page = 1 # int | Page number for standard REST pagination (1-based).  Example: `1` (optional)
    per_page = 10 # int | Number of items per page for standard REST pagination.  Example: `10` (optional)
    sort = '[\"id\", \"ASC\"]' # str | Sort order for the results in the format `[\"column\", \"order\"]`.  Example: `[\"id\", \"ASC\"]` (optional)
    sort_by = 'title' # str | Sort column for standard REST format.  Example: `title` (optional)
    order = 'ASC' # str | Sort order for standard REST format (ASC or DESC).  Example: `ASC` (optional)

    try:
        # Get all assets
        api_response = api_instance.get_all_assets(filter=filter, range=range, page=page, per_page=per_page, sort=sort, sort_by=sort_by, order=order)
        print("The response of DefaultApi->get_all_assets:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_all_assets: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **filter** | **str**| JSON-encoded filter for querying resources.  This parameter supports various filtering options: - Free text search: &#x60;{\&quot;q\&quot;: \&quot;search text\&quot;}&#x60; - Filtering by a single ID: &#x60;{\&quot;id\&quot;: \&quot;550e8400-e29b-41d4-a716-446655440000\&quot;}&#x60; - Filtering by multiple IDs: &#x60;{\&quot;id\&quot;: [\&quot;550e8400-e29b-41d4-a716-446655440000\&quot;, \&quot;550e8400-e29b-41d4-a716-446655440001\&quot;]}&#x60; - Filtering on other columns: &#x60;{\&quot;name\&quot;: \&quot;example\&quot;}&#x60; | [optional] 
 **range** | **str**| Range for pagination in the format \&quot;[start, end]\&quot;.  Example: &#x60;[0,9]&#x60; | [optional] 
 **page** | **int**| Page number for standard REST pagination (1-based).  Example: &#x60;1&#x60; | [optional] 
 **per_page** | **int**| Number of items per page for standard REST pagination.  Example: &#x60;10&#x60; | [optional] 
 **sort** | **str**| Sort order for the results in the format &#x60;[\&quot;column\&quot;, \&quot;order\&quot;]&#x60;.  Example: &#x60;[\&quot;id\&quot;, \&quot;ASC\&quot;]&#x60; | [optional] 
 **sort_by** | **str**| Sort column for standard REST format.  Example: &#x60;title&#x60; | [optional] 
 **order** | **str**| Sort order for standard REST format (ASC or DESC).  Example: &#x60;ASC&#x60; | [optional] 

### Return type

[**List[AssetList]**](AssetList.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | List of resources |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_all_experiments**
> List[ExperimentList] get_all_experiments(filter=filter, range=range, page=page, per_page=per_page, sort=sort, sort_by=sort_by, order=order)

Get all experiments

Retrieves all experiments.

Experiments track ice nucleation testing sessions with associated data and results.

Additional sortable columns: 
- name
- username
- performed_at
- temperature_ramp
- temperature_start
- temperature_end
- remarks
- tray_configuration_id
- created_at
- last_updated.

Additional filterable columns: 
- name
- username
- performed_at
- temperature_ramp
- temperature_start
- temperature_end
- is_calibration
- remarks
- tray_configuration_id.

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import spice_client
from spice_client.models.experiment_list import ExperimentList
from spice_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = spice_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = spice_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with spice_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = spice_client.DefaultApi(api_client)
    filter = '{id=550e8400-e29b-41d4-a716-446655440000, name=example, q=search text}' # str | JSON-encoded filter for querying resources.  This parameter supports various filtering options: - Free text search: `{\"q\": \"search text\"}` - Filtering by a single ID: `{\"id\": \"550e8400-e29b-41d4-a716-446655440000\"}` - Filtering by multiple IDs: `{\"id\": [\"550e8400-e29b-41d4-a716-446655440000\", \"550e8400-e29b-41d4-a716-446655440001\"]}` - Filtering on other columns: `{\"name\": \"example\"}` (optional)
    range = '[0,9]' # str | Range for pagination in the format \"[start, end]\".  Example: `[0,9]` (optional)
    page = 1 # int | Page number for standard REST pagination (1-based).  Example: `1` (optional)
    per_page = 10 # int | Number of items per page for standard REST pagination.  Example: `10` (optional)
    sort = '[\"id\", \"ASC\"]' # str | Sort order for the results in the format `[\"column\", \"order\"]`.  Example: `[\"id\", \"ASC\"]` (optional)
    sort_by = 'title' # str | Sort column for standard REST format.  Example: `title` (optional)
    order = 'ASC' # str | Sort order for standard REST format (ASC or DESC).  Example: `ASC` (optional)

    try:
        # Get all experiments
        api_response = api_instance.get_all_experiments(filter=filter, range=range, page=page, per_page=per_page, sort=sort, sort_by=sort_by, order=order)
        print("The response of DefaultApi->get_all_experiments:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_all_experiments: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **filter** | **str**| JSON-encoded filter for querying resources.  This parameter supports various filtering options: - Free text search: &#x60;{\&quot;q\&quot;: \&quot;search text\&quot;}&#x60; - Filtering by a single ID: &#x60;{\&quot;id\&quot;: \&quot;550e8400-e29b-41d4-a716-446655440000\&quot;}&#x60; - Filtering by multiple IDs: &#x60;{\&quot;id\&quot;: [\&quot;550e8400-e29b-41d4-a716-446655440000\&quot;, \&quot;550e8400-e29b-41d4-a716-446655440001\&quot;]}&#x60; - Filtering on other columns: &#x60;{\&quot;name\&quot;: \&quot;example\&quot;}&#x60; | [optional] 
 **range** | **str**| Range for pagination in the format \&quot;[start, end]\&quot;.  Example: &#x60;[0,9]&#x60; | [optional] 
 **page** | **int**| Page number for standard REST pagination (1-based).  Example: &#x60;1&#x60; | [optional] 
 **per_page** | **int**| Number of items per page for standard REST pagination.  Example: &#x60;10&#x60; | [optional] 
 **sort** | **str**| Sort order for the results in the format &#x60;[\&quot;column\&quot;, \&quot;order\&quot;]&#x60;.  Example: &#x60;[\&quot;id\&quot;, \&quot;ASC\&quot;]&#x60; | [optional] 
 **sort_by** | **str**| Sort column for standard REST format.  Example: &#x60;title&#x60; | [optional] 
 **order** | **str**| Sort order for standard REST format (ASC or DESC).  Example: &#x60;ASC&#x60; | [optional] 

### Return type

[**List[ExperimentList]**](ExperimentList.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | List of resources |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_all_locations**
> List[LocationList] get_all_locations(filter=filter, range=range, page=page, per_page=per_page, sort=sort, sort_by=sort_by, order=order)

Get all locations

Retrieves all locations.

Locations represent physical places where experiments are conducted. Each location belongs to a project and can contain multiple samples and experiments.

Additional sortable columns: 
- name
- comment
- project_id
- created_at
- last_updated.

Additional filterable columns: 
- name
- comment
- project_id.

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import spice_client
from spice_client.models.location_list import LocationList
from spice_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = spice_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = spice_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with spice_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = spice_client.DefaultApi(api_client)
    filter = '{id=550e8400-e29b-41d4-a716-446655440000, name=example, q=search text}' # str | JSON-encoded filter for querying resources.  This parameter supports various filtering options: - Free text search: `{\"q\": \"search text\"}` - Filtering by a single ID: `{\"id\": \"550e8400-e29b-41d4-a716-446655440000\"}` - Filtering by multiple IDs: `{\"id\": [\"550e8400-e29b-41d4-a716-446655440000\", \"550e8400-e29b-41d4-a716-446655440001\"]}` - Filtering on other columns: `{\"name\": \"example\"}` (optional)
    range = '[0,9]' # str | Range for pagination in the format \"[start, end]\".  Example: `[0,9]` (optional)
    page = 1 # int | Page number for standard REST pagination (1-based).  Example: `1` (optional)
    per_page = 10 # int | Number of items per page for standard REST pagination.  Example: `10` (optional)
    sort = '[\"id\", \"ASC\"]' # str | Sort order for the results in the format `[\"column\", \"order\"]`.  Example: `[\"id\", \"ASC\"]` (optional)
    sort_by = 'title' # str | Sort column for standard REST format.  Example: `title` (optional)
    order = 'ASC' # str | Sort order for standard REST format (ASC or DESC).  Example: `ASC` (optional)

    try:
        # Get all locations
        api_response = api_instance.get_all_locations(filter=filter, range=range, page=page, per_page=per_page, sort=sort, sort_by=sort_by, order=order)
        print("The response of DefaultApi->get_all_locations:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_all_locations: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **filter** | **str**| JSON-encoded filter for querying resources.  This parameter supports various filtering options: - Free text search: &#x60;{\&quot;q\&quot;: \&quot;search text\&quot;}&#x60; - Filtering by a single ID: &#x60;{\&quot;id\&quot;: \&quot;550e8400-e29b-41d4-a716-446655440000\&quot;}&#x60; - Filtering by multiple IDs: &#x60;{\&quot;id\&quot;: [\&quot;550e8400-e29b-41d4-a716-446655440000\&quot;, \&quot;550e8400-e29b-41d4-a716-446655440001\&quot;]}&#x60; - Filtering on other columns: &#x60;{\&quot;name\&quot;: \&quot;example\&quot;}&#x60; | [optional] 
 **range** | **str**| Range for pagination in the format \&quot;[start, end]\&quot;.  Example: &#x60;[0,9]&#x60; | [optional] 
 **page** | **int**| Page number for standard REST pagination (1-based).  Example: &#x60;1&#x60; | [optional] 
 **per_page** | **int**| Number of items per page for standard REST pagination.  Example: &#x60;10&#x60; | [optional] 
 **sort** | **str**| Sort order for the results in the format &#x60;[\&quot;column\&quot;, \&quot;order\&quot;]&#x60;.  Example: &#x60;[\&quot;id\&quot;, \&quot;ASC\&quot;]&#x60; | [optional] 
 **sort_by** | **str**| Sort column for standard REST format.  Example: &#x60;title&#x60; | [optional] 
 **order** | **str**| Sort order for standard REST format (ASC or DESC).  Example: &#x60;ASC&#x60; | [optional] 

### Return type

[**List[LocationList]**](LocationList.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | List of resources |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_all_projects**
> List[ProjectList] get_all_projects(filter=filter, range=range, page=page, per_page=per_page, sort=sort, sort_by=sort_by, order=order)

Get all projects

Retrieves all projects.

Projects provide a way to organise locations hierarchically. Each project can contain multiple locations and provides visual organization through color coding.

Additional sortable columns: 
- name
- note
- colour
- created_at
- last_updated.

Additional filterable columns: 
- name
- note
- colour.

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import spice_client
from spice_client.models.project_list import ProjectList
from spice_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = spice_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = spice_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with spice_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = spice_client.DefaultApi(api_client)
    filter = '{id=550e8400-e29b-41d4-a716-446655440000, name=example, q=search text}' # str | JSON-encoded filter for querying resources.  This parameter supports various filtering options: - Free text search: `{\"q\": \"search text\"}` - Filtering by a single ID: `{\"id\": \"550e8400-e29b-41d4-a716-446655440000\"}` - Filtering by multiple IDs: `{\"id\": [\"550e8400-e29b-41d4-a716-446655440000\", \"550e8400-e29b-41d4-a716-446655440001\"]}` - Filtering on other columns: `{\"name\": \"example\"}` (optional)
    range = '[0,9]' # str | Range for pagination in the format \"[start, end]\".  Example: `[0,9]` (optional)
    page = 1 # int | Page number for standard REST pagination (1-based).  Example: `1` (optional)
    per_page = 10 # int | Number of items per page for standard REST pagination.  Example: `10` (optional)
    sort = '[\"id\", \"ASC\"]' # str | Sort order for the results in the format `[\"column\", \"order\"]`.  Example: `[\"id\", \"ASC\"]` (optional)
    sort_by = 'title' # str | Sort column for standard REST format.  Example: `title` (optional)
    order = 'ASC' # str | Sort order for standard REST format (ASC or DESC).  Example: `ASC` (optional)

    try:
        # Get all projects
        api_response = api_instance.get_all_projects(filter=filter, range=range, page=page, per_page=per_page, sort=sort, sort_by=sort_by, order=order)
        print("The response of DefaultApi->get_all_projects:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_all_projects: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **filter** | **str**| JSON-encoded filter for querying resources.  This parameter supports various filtering options: - Free text search: &#x60;{\&quot;q\&quot;: \&quot;search text\&quot;}&#x60; - Filtering by a single ID: &#x60;{\&quot;id\&quot;: \&quot;550e8400-e29b-41d4-a716-446655440000\&quot;}&#x60; - Filtering by multiple IDs: &#x60;{\&quot;id\&quot;: [\&quot;550e8400-e29b-41d4-a716-446655440000\&quot;, \&quot;550e8400-e29b-41d4-a716-446655440001\&quot;]}&#x60; - Filtering on other columns: &#x60;{\&quot;name\&quot;: \&quot;example\&quot;}&#x60; | [optional] 
 **range** | **str**| Range for pagination in the format \&quot;[start, end]\&quot;.  Example: &#x60;[0,9]&#x60; | [optional] 
 **page** | **int**| Page number for standard REST pagination (1-based).  Example: &#x60;1&#x60; | [optional] 
 **per_page** | **int**| Number of items per page for standard REST pagination.  Example: &#x60;10&#x60; | [optional] 
 **sort** | **str**| Sort order for the results in the format &#x60;[\&quot;column\&quot;, \&quot;order\&quot;]&#x60;.  Example: &#x60;[\&quot;id\&quot;, \&quot;ASC\&quot;]&#x60; | [optional] 
 **sort_by** | **str**| Sort column for standard REST format.  Example: &#x60;title&#x60; | [optional] 
 **order** | **str**| Sort order for standard REST format (ASC or DESC).  Example: &#x60;ASC&#x60; | [optional] 

### Return type

[**List[ProjectList]**](ProjectList.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | List of resources |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_all_samples**
> List[SampleList] get_all_samples(filter=filter, range=range, page=page, per_page=per_page, sort=sort, sort_by=sort_by, order=order)

Get all samples

Retrieves all samples.

This resource manages samples associated with experiments.

Additional sortable columns: 
- name
- type
- start_time
- stop_time
- flow_litres_per_minute
- total_volume
- material_description
- extraction_procedure
- filter_substrate
- suspension_volume_litres
- air_volume_litres
- water_volume_litres
- initial_concentration_gram_l
- well_volume_litres
- remarks
- longitude
- latitude
- location_id
- created_at
- last_updated.

Additional filterable columns: 
- name
- type
- flow_litres_per_minute
- total_volume
- material_description
- extraction_procedure
- filter_substrate
- suspension_volume_litres
- air_volume_litres
- water_volume_litres
- initial_concentration_gram_l
- well_volume_litres
- remarks
- location_id.

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import spice_client
from spice_client.models.sample_list import SampleList
from spice_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = spice_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = spice_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with spice_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = spice_client.DefaultApi(api_client)
    filter = '{id=550e8400-e29b-41d4-a716-446655440000, name=example, q=search text}' # str | JSON-encoded filter for querying resources.  This parameter supports various filtering options: - Free text search: `{\"q\": \"search text\"}` - Filtering by a single ID: `{\"id\": \"550e8400-e29b-41d4-a716-446655440000\"}` - Filtering by multiple IDs: `{\"id\": [\"550e8400-e29b-41d4-a716-446655440000\", \"550e8400-e29b-41d4-a716-446655440001\"]}` - Filtering on other columns: `{\"name\": \"example\"}` (optional)
    range = '[0,9]' # str | Range for pagination in the format \"[start, end]\".  Example: `[0,9]` (optional)
    page = 1 # int | Page number for standard REST pagination (1-based).  Example: `1` (optional)
    per_page = 10 # int | Number of items per page for standard REST pagination.  Example: `10` (optional)
    sort = '[\"id\", \"ASC\"]' # str | Sort order for the results in the format `[\"column\", \"order\"]`.  Example: `[\"id\", \"ASC\"]` (optional)
    sort_by = 'title' # str | Sort column for standard REST format.  Example: `title` (optional)
    order = 'ASC' # str | Sort order for standard REST format (ASC or DESC).  Example: `ASC` (optional)

    try:
        # Get all samples
        api_response = api_instance.get_all_samples(filter=filter, range=range, page=page, per_page=per_page, sort=sort, sort_by=sort_by, order=order)
        print("The response of DefaultApi->get_all_samples:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_all_samples: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **filter** | **str**| JSON-encoded filter for querying resources.  This parameter supports various filtering options: - Free text search: &#x60;{\&quot;q\&quot;: \&quot;search text\&quot;}&#x60; - Filtering by a single ID: &#x60;{\&quot;id\&quot;: \&quot;550e8400-e29b-41d4-a716-446655440000\&quot;}&#x60; - Filtering by multiple IDs: &#x60;{\&quot;id\&quot;: [\&quot;550e8400-e29b-41d4-a716-446655440000\&quot;, \&quot;550e8400-e29b-41d4-a716-446655440001\&quot;]}&#x60; - Filtering on other columns: &#x60;{\&quot;name\&quot;: \&quot;example\&quot;}&#x60; | [optional] 
 **range** | **str**| Range for pagination in the format \&quot;[start, end]\&quot;.  Example: &#x60;[0,9]&#x60; | [optional] 
 **page** | **int**| Page number for standard REST pagination (1-based).  Example: &#x60;1&#x60; | [optional] 
 **per_page** | **int**| Number of items per page for standard REST pagination.  Example: &#x60;10&#x60; | [optional] 
 **sort** | **str**| Sort order for the results in the format &#x60;[\&quot;column\&quot;, \&quot;order\&quot;]&#x60;.  Example: &#x60;[\&quot;id\&quot;, \&quot;ASC\&quot;]&#x60; | [optional] 
 **sort_by** | **str**| Sort column for standard REST format.  Example: &#x60;title&#x60; | [optional] 
 **order** | **str**| Sort order for standard REST format (ASC or DESC).  Example: &#x60;ASC&#x60; | [optional] 

### Return type

[**List[SampleList]**](SampleList.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | List of resources |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_all_tray_configurations**
> List[TrayConfigurationList] get_all_tray_configurations(filter=filter, range=range, page=page, per_page=per_page, sort=sort, sort_by=sort_by, order=order)

Get all tray_configurations

Retrieves all tray_configurations.

This endpoint manages tray configurations, which define the setup of trays used in experiments.

Additional sortable columns: 
- name
- experiment_default
- created_at
- last_updated.

Additional filterable columns: 
- name
- experiment_default.

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import spice_client
from spice_client.models.tray_configuration_list import TrayConfigurationList
from spice_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = spice_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = spice_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with spice_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = spice_client.DefaultApi(api_client)
    filter = '{id=550e8400-e29b-41d4-a716-446655440000, name=example, q=search text}' # str | JSON-encoded filter for querying resources.  This parameter supports various filtering options: - Free text search: `{\"q\": \"search text\"}` - Filtering by a single ID: `{\"id\": \"550e8400-e29b-41d4-a716-446655440000\"}` - Filtering by multiple IDs: `{\"id\": [\"550e8400-e29b-41d4-a716-446655440000\", \"550e8400-e29b-41d4-a716-446655440001\"]}` - Filtering on other columns: `{\"name\": \"example\"}` (optional)
    range = '[0,9]' # str | Range for pagination in the format \"[start, end]\".  Example: `[0,9]` (optional)
    page = 1 # int | Page number for standard REST pagination (1-based).  Example: `1` (optional)
    per_page = 10 # int | Number of items per page for standard REST pagination.  Example: `10` (optional)
    sort = '[\"id\", \"ASC\"]' # str | Sort order for the results in the format `[\"column\", \"order\"]`.  Example: `[\"id\", \"ASC\"]` (optional)
    sort_by = 'title' # str | Sort column for standard REST format.  Example: `title` (optional)
    order = 'ASC' # str | Sort order for standard REST format (ASC or DESC).  Example: `ASC` (optional)

    try:
        # Get all tray_configurations
        api_response = api_instance.get_all_tray_configurations(filter=filter, range=range, page=page, per_page=per_page, sort=sort, sort_by=sort_by, order=order)
        print("The response of DefaultApi->get_all_tray_configurations:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_all_tray_configurations: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **filter** | **str**| JSON-encoded filter for querying resources.  This parameter supports various filtering options: - Free text search: &#x60;{\&quot;q\&quot;: \&quot;search text\&quot;}&#x60; - Filtering by a single ID: &#x60;{\&quot;id\&quot;: \&quot;550e8400-e29b-41d4-a716-446655440000\&quot;}&#x60; - Filtering by multiple IDs: &#x60;{\&quot;id\&quot;: [\&quot;550e8400-e29b-41d4-a716-446655440000\&quot;, \&quot;550e8400-e29b-41d4-a716-446655440001\&quot;]}&#x60; - Filtering on other columns: &#x60;{\&quot;name\&quot;: \&quot;example\&quot;}&#x60; | [optional] 
 **range** | **str**| Range for pagination in the format \&quot;[start, end]\&quot;.  Example: &#x60;[0,9]&#x60; | [optional] 
 **page** | **int**| Page number for standard REST pagination (1-based).  Example: &#x60;1&#x60; | [optional] 
 **per_page** | **int**| Number of items per page for standard REST pagination.  Example: &#x60;10&#x60; | [optional] 
 **sort** | **str**| Sort order for the results in the format &#x60;[\&quot;column\&quot;, \&quot;order\&quot;]&#x60;.  Example: &#x60;[\&quot;id\&quot;, \&quot;ASC\&quot;]&#x60; | [optional] 
 **sort_by** | **str**| Sort column for standard REST format.  Example: &#x60;title&#x60; | [optional] 
 **order** | **str**| Sort order for standard REST format (ASC or DESC).  Example: &#x60;ASC&#x60; | [optional] 

### Return type

[**List[TrayConfigurationList]**](TrayConfigurationList.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | List of resources |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_all_treatments**
> List[TreatmentList] get_all_treatments(filter=filter, range=range, page=page, per_page=per_page, sort=sort, sort_by=sort_by, order=order)

Get all treatments

Retrieves all treatments.

Treatments are applied to samples during experiments to study their effects on ice nucleation.

Additional sortable columns: 
- name
- notes
- sample_id
- created_at
- last_updated
- enzyme_volume_litres.

Additional filterable columns: 
- name
- notes
- sample_id
- enzyme_volume_litres.

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import spice_client
from spice_client.models.treatment_list import TreatmentList
from spice_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = spice_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = spice_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with spice_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = spice_client.DefaultApi(api_client)
    filter = '{id=550e8400-e29b-41d4-a716-446655440000, name=example, q=search text}' # str | JSON-encoded filter for querying resources.  This parameter supports various filtering options: - Free text search: `{\"q\": \"search text\"}` - Filtering by a single ID: `{\"id\": \"550e8400-e29b-41d4-a716-446655440000\"}` - Filtering by multiple IDs: `{\"id\": [\"550e8400-e29b-41d4-a716-446655440000\", \"550e8400-e29b-41d4-a716-446655440001\"]}` - Filtering on other columns: `{\"name\": \"example\"}` (optional)
    range = '[0,9]' # str | Range for pagination in the format \"[start, end]\".  Example: `[0,9]` (optional)
    page = 1 # int | Page number for standard REST pagination (1-based).  Example: `1` (optional)
    per_page = 10 # int | Number of items per page for standard REST pagination.  Example: `10` (optional)
    sort = '[\"id\", \"ASC\"]' # str | Sort order for the results in the format `[\"column\", \"order\"]`.  Example: `[\"id\", \"ASC\"]` (optional)
    sort_by = 'title' # str | Sort column for standard REST format.  Example: `title` (optional)
    order = 'ASC' # str | Sort order for standard REST format (ASC or DESC).  Example: `ASC` (optional)

    try:
        # Get all treatments
        api_response = api_instance.get_all_treatments(filter=filter, range=range, page=page, per_page=per_page, sort=sort, sort_by=sort_by, order=order)
        print("The response of DefaultApi->get_all_treatments:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_all_treatments: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **filter** | **str**| JSON-encoded filter for querying resources.  This parameter supports various filtering options: - Free text search: &#x60;{\&quot;q\&quot;: \&quot;search text\&quot;}&#x60; - Filtering by a single ID: &#x60;{\&quot;id\&quot;: \&quot;550e8400-e29b-41d4-a716-446655440000\&quot;}&#x60; - Filtering by multiple IDs: &#x60;{\&quot;id\&quot;: [\&quot;550e8400-e29b-41d4-a716-446655440000\&quot;, \&quot;550e8400-e29b-41d4-a716-446655440001\&quot;]}&#x60; - Filtering on other columns: &#x60;{\&quot;name\&quot;: \&quot;example\&quot;}&#x60; | [optional] 
 **range** | **str**| Range for pagination in the format \&quot;[start, end]\&quot;.  Example: &#x60;[0,9]&#x60; | [optional] 
 **page** | **int**| Page number for standard REST pagination (1-based).  Example: &#x60;1&#x60; | [optional] 
 **per_page** | **int**| Number of items per page for standard REST pagination.  Example: &#x60;10&#x60; | [optional] 
 **sort** | **str**| Sort order for the results in the format &#x60;[\&quot;column\&quot;, \&quot;order\&quot;]&#x60;.  Example: &#x60;[\&quot;id\&quot;, \&quot;ASC\&quot;]&#x60; | [optional] 
 **sort_by** | **str**| Sort column for standard REST format.  Example: &#x60;title&#x60; | [optional] 
 **order** | **str**| Sort order for standard REST format (ASC or DESC).  Example: &#x60;ASC&#x60; | [optional] 

### Return type

[**List[TreatmentList]**](TreatmentList.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | List of resources |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_one_asset**
> Asset get_one_asset(id)

Get one asset

Retrieves one asset by its ID.

This resource represents assets stored in S3, including metadata such as file size, type, and upload details.

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import spice_client
from spice_client.models.asset import Asset
from spice_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = spice_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = spice_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with spice_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = spice_client.DefaultApi(api_client)
    id = 'id_example' # str | 

    try:
        # Get one asset
        api_response = api_instance.get_one_asset(id)
        print("The response of DefaultApi->get_one_asset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_one_asset: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 

### Return type

[**Asset**](Asset.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The requested resource |  -  |
**404** | Resource not found |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_one_experiment**
> Experiment get_one_experiment(id)

Get one experiment

Retrieves one experiment by its ID.

Experiments track ice nucleation testing sessions with associated data and results.

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import spice_client
from spice_client.models.experiment import Experiment
from spice_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = spice_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = spice_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with spice_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = spice_client.DefaultApi(api_client)
    id = 'id_example' # str | 

    try:
        # Get one experiment
        api_response = api_instance.get_one_experiment(id)
        print("The response of DefaultApi->get_one_experiment:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_one_experiment: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 

### Return type

[**Experiment**](Experiment.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The requested resource |  -  |
**404** | Resource not found |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_one_location**
> Location get_one_location(id)

Get one location

Retrieves one location by its ID.

Locations represent physical places where experiments are conducted. Each location belongs to a project and can contain multiple samples and experiments.

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import spice_client
from spice_client.models.location import Location
from spice_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = spice_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = spice_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with spice_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = spice_client.DefaultApi(api_client)
    id = 'id_example' # str | 

    try:
        # Get one location
        api_response = api_instance.get_one_location(id)
        print("The response of DefaultApi->get_one_location:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_one_location: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 

### Return type

[**Location**](Location.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The requested resource |  -  |
**404** | Resource not found |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_one_project**
> Project get_one_project(id)

Get one project

Retrieves one project by its ID.

Projects provide a way to organise locations hierarchically. Each project can contain multiple locations and provides visual organization through color coding.

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import spice_client
from spice_client.models.project import Project
from spice_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = spice_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = spice_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with spice_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = spice_client.DefaultApi(api_client)
    id = 'id_example' # str | 

    try:
        # Get one project
        api_response = api_instance.get_one_project(id)
        print("The response of DefaultApi->get_one_project:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_one_project: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 

### Return type

[**Project**](Project.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The requested resource |  -  |
**404** | Resource not found |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_one_sample**
> Sample get_one_sample(id)

Get one sample

Retrieves one sample by its ID.

This resource manages samples associated with experiments.

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import spice_client
from spice_client.models.sample import Sample
from spice_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = spice_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = spice_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with spice_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = spice_client.DefaultApi(api_client)
    id = 'id_example' # str | 

    try:
        # Get one sample
        api_response = api_instance.get_one_sample(id)
        print("The response of DefaultApi->get_one_sample:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_one_sample: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 

### Return type

[**Sample**](Sample.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The requested resource |  -  |
**404** | Resource not found |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_one_tray_configuration**
> TrayConfiguration get_one_tray_configuration(id)

Get one tray_configuration

Retrieves one tray_configuration by its ID.

This endpoint manages tray configurations, which define the setup of trays used in experiments.

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import spice_client
from spice_client.models.tray_configuration import TrayConfiguration
from spice_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = spice_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = spice_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with spice_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = spice_client.DefaultApi(api_client)
    id = 'id_example' # str | 

    try:
        # Get one tray_configuration
        api_response = api_instance.get_one_tray_configuration(id)
        print("The response of DefaultApi->get_one_tray_configuration:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_one_tray_configuration: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 

### Return type

[**TrayConfiguration**](TrayConfiguration.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The requested resource |  -  |
**404** | Resource not found |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_one_treatment**
> Treatment get_one_treatment(id)

Get one treatment

Retrieves one treatment by its ID.

Treatments are applied to samples during experiments to study their effects on ice nucleation.

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import spice_client
from spice_client.models.treatment import Treatment
from spice_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = spice_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = spice_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with spice_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = spice_client.DefaultApi(api_client)
    id = 'id_example' # str | 

    try:
        # Get one treatment
        api_response = api_instance.get_one_treatment(id)
        print("The response of DefaultApi->get_one_treatment:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_one_treatment: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 

### Return type

[**Treatment**](Treatment.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The requested resource |  -  |
**404** | Resource not found |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_ui_config**
> str get_ui_config()

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import spice_client
from spice_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = spice_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = spice_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with spice_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = spice_client.DefaultApi(api_client)

    try:
        api_response = api_instance.get_ui_config()
        print("The response of DefaultApi->get_ui_config:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_ui_config: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**str**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Web UI configuration |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **healthz**
> str healthz()

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import spice_client
from spice_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = spice_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = spice_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with spice_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = spice_client.DefaultApi(api_client)

    try:
        api_response = api_instance.healthz()
        print("The response of DefaultApi->healthz:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->healthz: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**str**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Kubernetes health check |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_one_asset**
> Asset update_one_asset(id, asset_update)

Update one asset

Updates one asset by its ID.

This resource represents assets stored in S3, including metadata such as file size, type, and upload details.

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import spice_client
from spice_client.models.asset import Asset
from spice_client.models.asset_update import AssetUpdate
from spice_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = spice_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = spice_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with spice_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = spice_client.DefaultApi(api_client)
    id = 'id_example' # str | 
    asset_update = spice_client.AssetUpdate() # AssetUpdate | 

    try:
        # Update one asset
        api_response = api_instance.update_one_asset(id, asset_update)
        print("The response of DefaultApi->update_one_asset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->update_one_asset: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **asset_update** | [**AssetUpdate**](AssetUpdate.md)|  | 

### Return type

[**Asset**](Asset.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json, text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Resource updated successfully |  -  |
**404** | Resource not found |  -  |
**409** | Duplicate record |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_one_experiment**
> Experiment update_one_experiment(id, experiment_update)

Update one experiment

Updates one experiment by its ID.

Experiments track ice nucleation testing sessions with associated data and results.

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import spice_client
from spice_client.models.experiment import Experiment
from spice_client.models.experiment_update import ExperimentUpdate
from spice_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = spice_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = spice_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with spice_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = spice_client.DefaultApi(api_client)
    id = 'id_example' # str | 
    experiment_update = spice_client.ExperimentUpdate() # ExperimentUpdate | 

    try:
        # Update one experiment
        api_response = api_instance.update_one_experiment(id, experiment_update)
        print("The response of DefaultApi->update_one_experiment:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->update_one_experiment: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **experiment_update** | [**ExperimentUpdate**](ExperimentUpdate.md)|  | 

### Return type

[**Experiment**](Experiment.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json, text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Resource updated successfully |  -  |
**404** | Resource not found |  -  |
**409** | Duplicate record |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_one_location**
> Location update_one_location(id, location_update)

Update one location

Updates one location by its ID.

Locations represent physical places where experiments are conducted. Each location belongs to a project and can contain multiple samples and experiments.

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import spice_client
from spice_client.models.location import Location
from spice_client.models.location_update import LocationUpdate
from spice_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = spice_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = spice_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with spice_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = spice_client.DefaultApi(api_client)
    id = 'id_example' # str | 
    location_update = spice_client.LocationUpdate() # LocationUpdate | 

    try:
        # Update one location
        api_response = api_instance.update_one_location(id, location_update)
        print("The response of DefaultApi->update_one_location:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->update_one_location: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **location_update** | [**LocationUpdate**](LocationUpdate.md)|  | 

### Return type

[**Location**](Location.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json, text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Resource updated successfully |  -  |
**404** | Resource not found |  -  |
**409** | Duplicate record |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_one_project**
> Project update_one_project(id, project_update)

Update one project

Updates one project by its ID.

Projects provide a way to organise locations hierarchically. Each project can contain multiple locations and provides visual organization through color coding.

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import spice_client
from spice_client.models.project import Project
from spice_client.models.project_update import ProjectUpdate
from spice_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = spice_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = spice_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with spice_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = spice_client.DefaultApi(api_client)
    id = 'id_example' # str | 
    project_update = spice_client.ProjectUpdate() # ProjectUpdate | 

    try:
        # Update one project
        api_response = api_instance.update_one_project(id, project_update)
        print("The response of DefaultApi->update_one_project:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->update_one_project: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **project_update** | [**ProjectUpdate**](ProjectUpdate.md)|  | 

### Return type

[**Project**](Project.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json, text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Resource updated successfully |  -  |
**404** | Resource not found |  -  |
**409** | Duplicate record |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_one_sample**
> Sample update_one_sample(id, sample_update)

Update one sample

Updates one sample by its ID.

This resource manages samples associated with experiments.

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import spice_client
from spice_client.models.sample import Sample
from spice_client.models.sample_update import SampleUpdate
from spice_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = spice_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = spice_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with spice_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = spice_client.DefaultApi(api_client)
    id = 'id_example' # str | 
    sample_update = spice_client.SampleUpdate() # SampleUpdate | 

    try:
        # Update one sample
        api_response = api_instance.update_one_sample(id, sample_update)
        print("The response of DefaultApi->update_one_sample:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->update_one_sample: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **sample_update** | [**SampleUpdate**](SampleUpdate.md)|  | 

### Return type

[**Sample**](Sample.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json, text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Resource updated successfully |  -  |
**404** | Resource not found |  -  |
**409** | Duplicate record |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_one_tray_configuration**
> TrayConfiguration update_one_tray_configuration(id, tray_configuration_update)

Update one tray_configuration

Updates one tray_configuration by its ID.

This endpoint manages tray configurations, which define the setup of trays used in experiments.

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import spice_client
from spice_client.models.tray_configuration import TrayConfiguration
from spice_client.models.tray_configuration_update import TrayConfigurationUpdate
from spice_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = spice_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = spice_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with spice_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = spice_client.DefaultApi(api_client)
    id = 'id_example' # str | 
    tray_configuration_update = spice_client.TrayConfigurationUpdate() # TrayConfigurationUpdate | 

    try:
        # Update one tray_configuration
        api_response = api_instance.update_one_tray_configuration(id, tray_configuration_update)
        print("The response of DefaultApi->update_one_tray_configuration:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->update_one_tray_configuration: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **tray_configuration_update** | [**TrayConfigurationUpdate**](TrayConfigurationUpdate.md)|  | 

### Return type

[**TrayConfiguration**](TrayConfiguration.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json, text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Resource updated successfully |  -  |
**404** | Resource not found |  -  |
**409** | Duplicate record |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_one_treatment**
> Treatment update_one_treatment(id, treatment_update)

Update one treatment

Updates one treatment by its ID.

Treatments are applied to samples during experiments to study their effects on ice nucleation.

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import spice_client
from spice_client.models.treatment import Treatment
from spice_client.models.treatment_update import TreatmentUpdate
from spice_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = spice_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = spice_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with spice_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = spice_client.DefaultApi(api_client)
    id = 'id_example' # str | 
    treatment_update = spice_client.TreatmentUpdate() # TreatmentUpdate | 

    try:
        # Update one treatment
        api_response = api_instance.update_one_treatment(id, treatment_update)
        print("The response of DefaultApi->update_one_treatment:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->update_one_treatment: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **treatment_update** | [**TreatmentUpdate**](TreatmentUpdate.md)|  | 

### Return type

[**Treatment**](Treatment.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json, text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Resource updated successfully |  -  |
**404** | Resource not found |  -  |
**409** | Duplicate record |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

