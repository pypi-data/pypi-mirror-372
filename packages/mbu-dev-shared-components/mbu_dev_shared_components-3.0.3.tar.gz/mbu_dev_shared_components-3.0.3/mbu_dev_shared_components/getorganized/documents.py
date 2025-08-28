"""This module..."""
import requests
from mbu_dev_shared_components.getorganized.auth import get_ntlm_go_api_credentials


def get_document_metadata(api_endpoint: str, api_username: str, api_password: str) -> requests.Response:
    """
    Sends a GET request to fetch metadata for a given document in GO

    Parameters:
    api_endpoint (str): GetOrganized API endpoint.
    api_username (str): The API username for GetOrganized API.
    api_password (str): The API password for GetOrganized API.

    Returns:
    requests.Response: The response object from the API.
    """

    headers = {"Content-Type": "application/json"}

    response = requests.request(method='GET', url=api_endpoint, headers=headers, auth=get_ntlm_go_api_credentials(api_username, api_password), timeout=60)

    return response


def upload_file_to_case(file_data: str, api_endpoint: str, api_username: str, api_password: str) -> requests.Response:
    """
    Uploads a file to a case by sending file data as a JSON payload to a specific API endpoint.
    The function uses NTLM authentication and expects an environment variable for the API base URL.

    Parameters:
    file_data (str): A JSON string containing file data and associated case information to be uploaded.
    api_endpoint (str): GetOrganized API endpoint.
    api_username (str): The API username for GetOrganized API.
    api_password (str): The API password for GetOrganized API.

    Returns:
    requests.Response: The response object from the API.

    Raises:
    requests.RequestException: If the HTTP request fails for any reason.
    """
    headers = {'Content-Type': 'application/json'}
    response = requests.request(method='POST', url=api_endpoint, headers=headers, json=file_data, auth=get_ntlm_go_api_credentials(api_username, api_password), timeout=60)

    return response


def mark_file_as_case_record(documents_id: list, api_endpoint: str, api_username: str, api_password: str) -> requests.Response:
    """
    Marks one or more documents by their IDs as case records in the system via a POST request to a specific API endpoint.
    This operation modifies the status of the documents to reflect their new role as official case records.
    The function constructs the JSON payload by encapsulating the document IDs within a list under the 'DocumentIds' key.

    Parameters:
    documents_id (list): A list of integers representing document IDs that should be marked as case records.
    api_endpoint (str): GetOrganized API endpoint.
    api_username (str): The API username for GetOrganized API.
    api_password (str): The API password for GetOrganized API.

    Returns:
    Dict[str, Any]: The JSON response from the API, which includes the status of the operation and potentially updated document details.

    Raises:
    requests.RequestException: If the HTTP request fails for any reason.
    """
    headers = {'Content-Type': 'application/json'}
    payload = {"DocumentIds": documents_id}

    response = requests.request(method='POST', url=api_endpoint, headers=headers, json=payload, auth=get_ntlm_go_api_credentials(api_username, api_password), timeout=60)
    response.raise_for_status()

    return response


def finalize_file(documents_id: list, api_endpoint: str, api_username: str, api_password: str) -> requests.Response:
    """
    Marks one or more documents by their IDs as finalized in the system via a POST request to a specific API endpoint.
    This operation modifies the status of the documents to reflect their new role as finalized case records.
    The function constructs the JSON payload by encapsulating the document IDs within a list under the 'DocumentIds' key.

    Parameters:
    documents_id (list): A list of integers representing document IDs that should be marked as case records.
    api_endpoint (str): GetOrganized API endpoint.
    api_username (str): The API username for GetOrganized API.
    api_password (str): The API password for GetOrganized API.

    Returns:
    Dict[str, Any]: The JSON response from the API, which includes the status of the operation and potentially updated document details.

    Raises:
    requests.RequestException: If the HTTP request fails for any reason.
    """
    headers = {'Content-Type': 'application/json'}
    payload = {
        "DocumentIds": documents_id,
        "ShouldCloseOpenTasks": False
    }

    response = requests.request(method='POST', url=api_endpoint, headers=headers, json=payload, auth=get_ntlm_go_api_credentials(api_username, api_password), timeout=60)
    response.raise_for_status()

    return response


def search_documents(search_term: str, api_endpoint: str, api_username: str, api_password: str) -> requests.Response:
    """
    Looks for documents in GetOrganized related to the specified search term

    Parameters:
    search_term (str): The phrase/term to be searched for in GetOrganized.
    api_endpoint (str): GetOrganized API endpoint.
    api_username (str): The API username for GetOrganized API.
    api_password (str): The API password for GetOrganized API.

    Returns:
    requests.Response: The response object from the API.

    Raises:
    requests.RequestException: If the HTTP request fails for any reason.
    """

    payload = {
        "SearchPhrase": search_term,
        "AdditionalColumns": [],
        "ResultLimit": 500,
        "StartRow": 0
    }

    headers = {'Content-Type': 'application/json'}

    response = requests.request(method='POST', url=api_endpoint, headers=headers, json=payload, auth=get_ntlm_go_api_credentials(api_username, api_password), timeout=60)

    return response


def modern_search(page_index, search_term: str, start_date, end_date, only_items: bool, case_type_prefix: str, api_endpoint: str, api_username: str, api_password: str) -> requests.Response:
    """
    Looks for documents in GetOrganized related to the specified search term

    Parameters:
    search_term (str): The phrase/term to be searched for in GetOrganized.
    api_endpoint (str): GetOrganized API endpoint.
    api_username (str): The API username for GetOrganized API.
    api_password (str): The API password for GetOrganized API.

    Returns:
    requests.Response: The response object from the API.

    Raises:
    requests.RequestException: If the HTTP request fails for any reason.
    """

    payload = {
        "QueryPageIndex": page_index,
        "PageSize": 500,
        "QueryPhrase": f"{search_term}",
        "QueryType": "DocumentLibrary",
        "TrimToOpenedCases": False,
        "ResultTypeName": "Dokumenter",
        "SearchContentDefinitionEntryType": 0,
        "AdditionalSelectColumns": [],
        "ResultTypeListNameOrType": None,
        "ResultTypeSearchOnlyItems": only_items,
        "ResultTypeQueryFilter": None,
        "CaseQueryFieldCollection": [
            {
                "DisplayName": "Sag oprettet",
                "Guid": None,
                "InternalName": "Created",
                "Type": "SPFieldType.DateTime",
                "Value": f"{start_date}T22:00:00.000Z",
                "ToValue": f"{end_date}T22:00:00.000Z",
                "IsTaxId": False,
                "DecodeCrawledName": False,
                "IsOrCondition": None,
                "MappedName": "CCMCreatedCASEPROP"
            }
        ],
        "QueryFieldCollection": [],
        "CaseTypePrefixes": [
            f"{case_type_prefix}"
        ],
        "SortDirection1": 1,
        "ResultViewSortOrder1": 2,
        "ResultViewSortOrder2": 2,
        "QueryScope": 0
    }

    headers = {'Content-Type': 'application/json'}

    response = requests.request(method='POST', url=api_endpoint, headers=headers, json=payload, auth=get_ntlm_go_api_credentials(api_username, api_password), timeout=60)

    return response
