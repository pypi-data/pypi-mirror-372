import requests


class Client:
    """Sunbird dcTrack API client version 1.4.7 in Python"""

    def __init__(self, baseUrl: str, username: str = '', password: str = '', apiToken: str = '', httpProxy: str = '', httpsProxy: str = '', sslVerify: bool = True):
        """Provide either a username and password, or an API token to access the dcTrack database with Python."""
        self.__BASE_URL = baseUrl
        self.__USERNAME = username
        self.__PASSWORD = password
        self.__APITOKEN = apiToken
        self.__PROXY = {}
        if httpProxy:
            self.__PROXY['http'] = httpProxy
        if httpsProxy:
            self.__PROXY['https'] = httpsProxy
        self.__VERIFY = sslVerify

    def generateToken(self) -> str:
        """Generate and return an API token."""
        if self.__USERNAME and self.__PASSWORD and not self.__APITOKEN:
            return requests.request('POST', self.__BASE_URL + '/api/v2/authentication/login', auth=(self.__USERNAME, self.__PASSWORD), proxies=self.__PROXY, verify=self.__VERIFY).headers['Authorization'].split()[1]
        else:
            raise Exception('Username/password undefined or token predefined.')

    def __request(self, method: str, endpoint: str, body: dict = None):
        """Internal class method."""
        if not self.__APITOKEN:
            self.__APITOKEN = self.generateToken()
        response = requests.request(method, self.__BASE_URL + '/' + endpoint, json=body, headers={'Authorization': 'Bearer ' + self.__APITOKEN}, proxies=self.__PROXY, verify=self.__VERIFY)
        try:
            return response.json()
        except:
            return {}

    def getItem(self, id: int):
        """Get item details using the item ID. Returns an Item JSON object."""
        return self.__request('GET', '/api/v2/dcimoperations/items/' + str(id) + '?')

    def createItem(self, returnDetails: bool, proceedOnWarning: bool, payload: dict):
        """Create a new item. When returnDetails is set to true, the API call will return the full json payload. If set to false, the call returns only the "id" and "tiName". Returns the newly created item JSON object."""
        return self.__request('POST', '/api/v2/dcimoperations/items?returnDetails=' + str(returnDetails) + '&proceedOnWarning=' + str(proceedOnWarning) + '&', payload)

    def updateItem(self, id: int, returnDetails: bool, proceedOnWarning: bool, payload: dict):
        """Update an existing item. When returnDetails is set to true, the API call will return the full json payload. If set to false, the call returns only the "id" and "tiName"."""
        return self.__request('PUT', '/api/v2/dcimoperations/items/' + str(id) + '?returnDetails=' + str(returnDetails) + '&proceedOnWarning=' + str(proceedOnWarning) + '&', payload)

    def deleteItem(self, id: int, proceedOnWarning: bool):
        """Delete an item using the item ID."""
        return self.__request('DELETE', '/api/v2/dcimoperations/items/' + str(id) + '?proceedOnWarning=' + str(proceedOnWarning) + '&')

    def searchItems(self, pageNumber: int, pageSize: int, payload: dict):
        """Search for items using criteria JSON object. Search criteria can be any of the fields applicable to items, including custom fields. Specify the fields to be included in the response. This API supports pagination. Returns a list of items with the specified information."""
        return self.__request('POST', '/api/v2/quicksearch/items?pageNumber=' + str(pageNumber) + '&pageSize=' + str(pageSize) + '&', payload)

    def getCabinetItems(self, CabinetId: int):
        """Returns a list of Items contained in a Cabinet using the ItemID of the Cabinet. The returned list includes all of the Cabinet's Items including Passive Items."""
        return self.__request('GET', '/api/v2/items/cabinetItems/' + str(CabinetId) + '?')

    def createItemsBulk(self, payload: dict):
        """Add/Update/Delete Items."""
        return self.__request('POST', '/api/v2/dcimoperations/items/bulk?', payload)

    def getMakes(self):
        """Returns a list of makes with basic information."""
        return self.__request('GET', '/api/v2/makes?')

    def createMake(self, payload: dict):
        """Add a new Make. Returns JSON entity containing Make information that was passed in from the Request payload."""
        return self.__request('POST', '/api/v2/makes?', payload)

    def updateMake(self, makeId: int, payload: dict):
        """Modify a Make. Returns JSON entity containing Make information that was passed in from the Request payload."""
        return self.__request('PUT', '/api/v2/makes/' + str(makeId) + '?', payload)

    def deleteMake(self, makeId: int):
        """Delete a Make."""
        return self.__request('DELETE', '/api/v2/makes/' + str(makeId) + '?')

    def getMakesByName(self, makeName: str):
        """Search for a make using the make name. Returns a list of makes with basic information."""
        return self.__request('GET', '/api/v2/dcimoperations/search/makes/' + str(makeName) + '?')

    def getModel(self, modelId: int, usedCounts: bool):
        """Get Model fields for the specified Model ID. usedCounts is an optional parameter that determines if the count of Items for the specified model is returned in the response. If set to "true" the counts will be included in the response, if omitted or set to "false" the item count will not be included in the response."""
        return self.__request('GET', '/api/v2/models/' + str(modelId) + '?usedCounts=' + str(usedCounts) + '&')

    def createModel(self, returnDetails: bool, proceedOnWarning: bool, payload: dict):
        """Add a new Model. Returns JSON entity containing Make information that was passed in from the Request payload. "proceedOnWarning" relates to the warning messages that are thrown in dcTrack when you try to delete custom fields that are in use. The "proceedOnWarning" value can equal either "true" or "false." If "proceedOnWarning" equals "true," business warnings will be ignored. If "proceedOnWarning" equals "false," business warnings will not be ignored. Fields that are not in the payload will remain unchanged."""
        return self.__request('POST', '/api/v2/models?returnDetails=' + str(returnDetails) + '&proceedOnWarning=' + str(proceedOnWarning) + '&', payload)

    def updateModel(self, id: int, returnDetails: bool, proceedOnWarning: bool, payload: dict):
        """Modify an existing Model. Fields that are not in the payload will remain unchanged. Returns a JSON entity containing Make information that was passed in from the Request payload. This API performs as a PUT and not a PATCH. For example, the Request includes the dataPorts list but nothing inside it, the data ports will be removed, or you include a new port in the list , but not the current port on the device, it will remove the port that already exists and create a new port."""
        return self.__request('PUT', '/api/v2/models/' + str(id) + '?returnDetails=' + str(returnDetails) + '&proceedOnWarning=' + str(proceedOnWarning) + '&', payload)

    def modifyModel(self, id: int, returnDetails: bool, proceedOnWarning: bool, payload: dict):
        """Modify an existing Model. This is currently being released as a Beta version for early release and is subject to change."""
        return self.__request('PATCH', '/api/v2/models/' + str(id) + '?returnDetails=' + str(returnDetails) + '&proceedOnWarning=' + str(proceedOnWarning) + '&', payload)

    def deleteModel(self, id: int):
        """Delete a Model using the Model ID."""
        return self.__request('DELETE', '/api/v2/models/' + str(id) + '?')

    def searchModels(self, pageNumber: int, pageSize: int, payload: dict):
        """Search for models by user supplied search criteria. Returns a list of models with the "selectedColumns" returned in the payload. Search by Alias is not supported."""
        return self.__request('POST', '/api/v2/quicksearch/models?pageNumber=' + str(pageNumber) + '&pageSize=' + str(pageSize) + '&', payload)

    def deleteModelImage(self, id: int, orientation: str):
        """Delete a Mode Image using the Model ID and the Image Orientation, where id is the Model Id and orientation is either front or back"""
        return self.__request('DELETE', '/api/v2/models/images/' + str(id) + '/' + str(orientation) + '?')

    def getConnector(self, connectorId: int, usedCount: bool):
        """Get a Connector record by ID. Returns a Connector with all information including Compatible Connectors. The usedCount parameter is optional. If usedCount is true, the response will include the number of times the connector is in use by Models and Items. If false, no counts are returned. If omitted the default is false."""
        return self.__request('GET', '/api/v2/settings/connectors/' + str(connectorId) + '?usedCount=' + str(usedCount) + '&')

    def createConnector(self, payload: dict):
        """Add a new Connector. Returns JSON entity containing Connector information that was passed in from the Request payload."""
        return self.__request('POST', '/api/v2/settings/connectors?', payload)

    def updateConnector(self, connectorId: int, payload: dict):
        """Update an existing Connector. Returns JSON entity containing Connector information that was passed in from the Request payload."""
        return self.__request('PUT', '/api/v2/settings/connectors/' + str(connectorId) + '?', payload)

    def removeConnector(self, payload: dict):
        """Delete one or more Connector records."""
        return self.__request('POST', '/api/v2/settings/connectors/delete?', payload)

    def searchConnectors(self, pageNumber: int, pageSize: int, payload: dict):
        """Search for Connectors using criteria JSON object. Search criteria can be any of the fields applicable to Connector, including custom fields. Specify the fields to be included in the response. This API supports pagination. Returns a list of Connectors with the specified information."""
        return self.__request('POST', '/api/v2/quicksearch/connectors?pageNumber=' + str(pageNumber) + '&pageSize=' + str(pageSize) + '&', payload)

    def deleteConnectorImage(self, connectorId: int):
        """Delete a Connector Image using the Connector ID."""
        return self.__request('DELETE', '/api/v2/settings/connectors/' + str(connectorId) + '/images?')

    def getDataPorts(self, itemId: int):
        """Use the REST API to retrieve details from all data ports on an item. If the operation was successful, a status code 200 is displayed, and the body contains the item's data port details. If the operation failed, an error code is returned."""
        return self.__request('GET', '/api/v2/dcimoperations/items/' + str(itemId) + '/dataports?')

    def getDataPort(self, itemId: int, portId: int):
        """Use the REST API to read the details of an item's data port. To do this, specify the item and item data port ID. If the operation was successful, a status code 200 is displayed, and the body contains the item's data port details. If the operation failed, an error code is returned."""
        return self.__request('GET', '/api/v2/dcimoperations/items/' + str(itemId) + '/dataports/' + str(portId) + '?')

    def createDataPorts(self, itemId: int, payload: dict):
        """Use the REST API to create data ports for an existing item. If ports are already defined for the item because it is included in the Item Models Library, you can use the REST API to create additional ports for the item. Payload contains data port parameter details in json format. All required fields must be included."""
        return self.__request('POST', '/api/v2/dcimoperations/items/' + str(itemId) + '/dataports?', payload)

    def updateDataPort(self, itemId: int, portId: int, payload: dict):
        """Update an item's data port details using the REST API. To do this, specify the item and data port ID, and provide the updated parameter value(s). Payload contains data port parameter details in json format. All required fields must be included."""
        return self.__request('PUT', '/api/v2/dcimoperations/items/' + str(itemId) + '/dataports/' + str(portId) + '?', payload)

    def deleteDataPort(self, itemId: int, portId: int):
        """Delete an item's data port using the REST API by specifying the item ID and data port ID. If the operation is successful, a status code 200 is displayed. If the operation failed, an error code is returned."""
        return self.__request('DELETE', '/api/v2/dcimoperations/items/' + str(itemId) + '/dataports/' + str(portId) + '?')

    def getPowerPorts(self, itemId: int):
        """Use the REST API to retrieve details from all power ports on an item."""
        return self.__request('GET', '/api/v1/items/' + str(itemId) + '/powerports?')

    def getPowerPort(self, itemId: int, portId: int):
        """Use the REST API to retrieve details from one power port on an item."""
        return self.__request('GET', '/api/v1/items/' + str(itemId) + '/powerports/' + str(portId) + '?')

    def updatePowerPort(self, itemId: int, portId: int, proceedOnWarning: bool, payload: dict):
        """Use the REST API to create power ports for an existing item. If ports are already defined for the item because it is included in the Item Models Library, you can use the REST API to create additional ports for the item."""
        return self.__request('PUT', '/api/v1/items/' + str(itemId) + '/powerports/' + str(portId) + '?proceedOnWarning=' + str(proceedOnWarning) + '&', payload)

    def getCompatibleConnector(self, itemId: int, portId: int, connectorId: int):
        """Use the REST API to determine if a Connector is compatible with a specific Power Port."""
        return self.__request('GET', '/api/v1/items/' + str(itemId) + '/powerports/' + str(portId) + '/connectors/' + str(connectorId) + '/isCompatible?')

    def getBreakers(self, panelItemId: int):
        """Get a list of all Breakers for a given Panel Item. Returns JSON entity containing an array of all the Breakers for the specified Panel Item."""
        return self.__request('GET', '/api/v2/dcimoperations/items/' + str(panelItemId) + '/breakers?')

    def getBreaker(self, panelItemId: int, breakerPortId: int):
        """Get a list of all Breakers for a given Panel Item. Returns JSON entity containing information for a single Panel Item Breaker."""
        return self.__request('GET', '/api/v2/dcimoperations/items/' + str(panelItemId) + '/breakers/' + str(breakerPortId) + '?')

    def updateBreaker(self, panelItemId: int, breakerPortId: int, payload: dict):
        """Update a single Breaker for a given Panel Item. Returns JSON entity containing information for the updated Panel Item Breaker. Note: This API performs as a true PUT and not a PATCH. Unlike with a PATCH, you must specify all attributes even if you want to change only one. Attributes that are not included in the Request will be considered as removed."""
        return self.__request('PUT', '/api/v2/dcimoperations/items/' + str(panelItemId) + '/breakers/' + str(breakerPortId) + '?', payload)

    def createBreaker(self, panelItemId: int, payload: dict):
        """Create a single Breaker for a given Panel Item. Returns JSON entity containing information for the created Panel Item Breaker. Note: Breaker State is set based on the connection status of the Breaker. If the breaker is connected it will always be set to "Closed", even if "Open" is specified in the Request."""
        return self.__request('POST', '/api/v2/dcimoperations/items/' + str(panelItemId) + '/breakers?', payload)

    def deleteBreaker(self, panelItemId: int, breakerPortId: int):
        """Delete a Breaker for a given Panel Item. Returns empty JSON."""
        return self.__request('DELETE', '/api/v2/dcimoperations/items/' + str(panelItemId) + '/breakers/' + str(breakerPortId) + '?')

    def createBreakersBulk(self, panelItemId: int, payload: dict):
        """Add/Update/Delete Breakers for a given Panel Item."""
        return self.__request('POST', '/api/v2/dcimoperations/items/' + str(panelItemId) + '/breakers/bulk?', payload)

    def getLocations(self):
        """Returns a list for all Locations."""
        return self.__request('GET', '/api/v1/locations?')

    def getLocation(self, locationId: int):
        """Get a single Location. Returns json containing location data for the specified ID."""
        return self.__request('GET', '/api/v1/locations' + str(locationId) + '?')

    def createLocation(self, proceedOnWarning: bool, payload: dict):
        """Add a Location. Returns the JSON entity containing location info that was passed in. Note: "proceedOnWarning" relates to the warning messages that are thrown in dcTrack when you try to delete custom fields that are in use. The "proceedOnWarning" value can equal either "true" or "false." If "proceedOnWarning" equals "true," business warnings will be ignored. If "proceedOnWarning" equals "false," business warnings will not be ignored."""
        return self.__request('POST', '/api/v1/locations?proceedOnWarning=' + str(proceedOnWarning) + '&', payload)

    def updateLocation(self, locationId: int, proceedOnWarning: bool, payload: dict):
        """Modify Location details for a single Location. Payload contains new location details. You do not have have to provide all details, but only those that you want to modify. Returns JSON entity containing Location information that was passed in from the Request payload."""
        return self.__request('PUT', '/api/v1/locations/' + str(locationId) + '?proceedOnWarning=' + str(proceedOnWarning) + '&', payload)

    def deleteLocation(self, locationId: int):
        """Delete a Location."""
        return self.__request('DELETE', '/api/v1/locations/' + str(locationId) + '?')

    def searchLocations(self, pageNumber: int, pageSize: int, payload: dict):
        """Search for Locations by user supplied search criteria. Returns a list of Locations with the "selectedColumns" returned in the payload."""
        return self.__request('POST', '/api/v2/quicksearch/locations?pageNumber=' + str(pageNumber) + '&pageSize=' + str(pageSize) + '&', payload)

    def getLocationFieldList(self):
        """Returns a list of all Location fields."""
        return self.__request('GET', '/api/v2/quicksearch/locations/locationListFields?')

    def getSublocations(self, locationId: int):
        """Get all sub-locations for a given location in the hierarchy. The locationId is the ID of the location to get the sub-locations for."""
        return self.__request('GET', '/api/v2/subLocations/list/' + str(locationId) + '?')

    def getSublocationsOfType(self, locationId: int, typeCode: str):
        """Get all sub-locations of given type for a given location in the hierarchy. The locationId is the id of the location you are querying the sub-location types for. The type is one of either 5016 and 5017 for rows and aisles respectively."""
        return self.__request('GET', '/api/v2/subLocations/' + str(locationId) + '/type/' + str(typeCode) + '?')

    def getChildSublocations(self, subLocationId: int):
        """Get all child sub-locations for a given sub-location in the hierarchy. The locationId is the ID of the location to fetch the sub-locations for. The subLocationId is the ID of the parent sub-location that you are querying the children of."""
        return self.__request('GET', '/api/v2/subLocations/' + str(subLocationId) + '/children?')

    def getSublocation(self, subLocationId: int):
        """Get details for a given sub-location. The subLocationId is the id of the sub-location you are querying for."""
        return self.__request('GET', '/api/v2/subLocations/' + str(subLocationId) + '?')

    def createSublocation(self, payload: dict):
        """Add a new sub-location to the given location. Returns a list from the Sub-Location Hash."""
        return self.__request('POST', '/api/v2/subLocations?', payload)

    def updateSublocation(self, subLocationId: int, payload: dict):
        """Update a sub-location. Returns a list from the Sub-Location Hash."""
        return self.__request('PUT', '/api/v2/subLocations/' + str(subLocationId) + '?', payload)

    def deleteSublocation(self, subLocationId: int):
        """Deletes the given sub-location. The locationId is the ID of the location that the sub-location belongs to and the subLocationId is the ID of the location you are querying. Returns a success message upon success."""
        return self.__request('DELETE', '/api/v2/subLocations/' + str(subLocationId) + '?')

    def getLocationFavorites(self, username: str):
        """Retrieve a List of Location Favorites for a specific User."""
        return self.__request('GET', '/api/v2/users/' + str(username) + '/favorites/LOCATION?')

    def getLocationFavoritesAllUsers(self):
        """Retrieve a List of Location Favorites for all Users. Returns JSON entity containing Location Favorite information for all users."""
        return self.__request('GET', '/api/v2/users/favorites/LOCATION?')

    def updateLocationFavorites(self, username: str, payload: dict):
        """Assign Location Favorites to a user where username is a valid dcTrack user and "favorite" is either true or false to indicate whether you are assigning or unassigning. JSON entity containing all Location Favorites for the specified user."""
        return self.__request('PUT', '/api/v2/users/' + str(username) + '/favorites?', payload)

    def updateLocationFavoritesAllUsers(self, payload: dict):
        """Assign Location Favorites to a user. To Assign favorites the "favorite" column should be set to true. To Unassign favorites the "favorite" column should be set to false. Returns JSON entity containing all Location Favorites for the specified users."""
        return self.__request('PUT', '/api/v2/users/favorites?', payload)

    def searchCabinetSpace(self, payload: dict):
        """Find Cabinets with available space based on RUs within the specified Locations."""
        return self.__request('POST', '/api/v2/capacity/cabinets/list/search?', payload)

    def searchAvailableRUs(self, payload: dict):
        """Find the starting RUs within a Cabinet with the specified number of contiguous RUs."""
        return self.__request('POST', '/api/v2/items/uposition/available?', payload)

    def getPermission(self, permissionId: int):
        """Get explicit permission by ID. Returns JSON entity containing Permission information for the specified Permission Id."""
        return self.__request('GET', '/api/v2/permissions/explicit/' + str(permissionId) + '?')

    def createPermission(self, payload: dict):
        """Add explicit permission. Returns JSON entity containing Permission information for the added Permission."""
        return self.__request('POST', '/api/v2/permissions/explicit?', payload)

    def updatePermission(self, permissionId: int, payload: dict):
        """Update explicit permission. Returns JSON entity containing Permission information for the updated Permission."""
        return self.__request('PUT', '/api/v2/permissions/explicit/' + str(permissionId) + '?', payload)

    def deletePermission(self, permissionId: int):
        """Delete explicit permission."""
        return self.__request('DELETE', '/api/v2/permissions/explicit/' + str(permissionId) + '?')

    def createPermissionsBulk(self, payload: dict):
        """Add/Update/Delete explicit permissions."""
        return self.__request('POST', '/api/v2/permissions/explicit/bulk?', payload)

    def getPermissions(self):
        """Get all explicit permissions. Returns JSON entity containing Permission information."""
        return self.__request('GET', '/api/v2/permissions/explicit?')

    def getPermissionsByEntityType(self, entityType: str):
        """Get explicit permissions by Entity Type. Returns JSON entity containing Permission information."""
        return self.__request('GET', '/api/v2/permissions/explicit/entityType/' + str(entityType) + '?')

    def getPermissionsByEntityId(self, entityType: str, entityId: int):
        """Get explicit permissions by Entity Type and Entity ID. Returns JSON entity containing Permission information."""
        return self.__request('GET', '/api/v2/permissions/explicit/' + str(entityType) + '/' + str(entityId) + '?')

    def getRecords(self, listType: str, id: int):
        """Get a list of records (options) for use in drop-down lists by indicating a list type and an ID. ID is optional for some list types. Returns a list of records for a given list type."""
        return self.__request('GET', '/api/v2/dcimoperations/lookups/' + str(listType) + '/' + str(id) + '?')

    def getPicklistOptions(self, listType: str):
        """Get a list of records (options) for use in drop-down lists for dcTrack standard fields by list type. Returns a list of records for a given list type."""
        return self.__request('GET', '/api/v2/dcimoperations/picklists/' + str(listType) + '?')

    def updatePicklistOptions(self, listType: str, payload: dict):
        """Update a list of records (options) for use in drop-down lists for dcTrack standard fields by list type. Returns a list of records for a given list type."""
        return self.__request('PUT', '/api/v2/dcimoperations/picklists/' + str(listType) + '?', payload)

    def updateDefaultValue(self, payload: dict):
        """Update the default value for a picklist field."""
        return self.__request('PUT', '/api/v2/settings/lists/defaultValue?', payload)

    def getFieldProperties(self, entity: str):
        """Get the properties for all fields applicable to the Entity."""
        return self.__request('GET', '/api/v2/settings/lists/fieldProperties?entity=' + str(entity) + '&')

    def createRequest(self, payload: dict):
        """Create a request."""
        return self.__request('POST', '/api/v2/dcimoperations/requests?', payload)

    def deleteRequest(self, requestId: int):
        """Cancel a request. Returns Returns request ID canceled."""
        return self.__request('DELETE', '/api/v2/dcimoperations/requests/' + str(requestId) + '?')

    def createRequestBulk(self, payload: dict):
        """Add/Update/Delete Requests in Bulk. The body of the Request should contain the required fields required to perform the specified Method. Returns JSON entity containing data for the Requests."""
        return self.__request('POST', '/api/v2/dcimoperations/requests/bulk?', payload)

    def completeRequest(self, requestId: int, payload: dict):
        """Change request status/stage to Complete using the request ID. Optionally, pass a request body with additional information. Returns request status information."""
        return self.__request('PUT', '/api/v2/dcimoperations/requests/complete/' + str(requestId) + '?', payload)

    def completeWorkOrder(self, workOrderId: int, payload: dict):
        """Complete work order and change work order status/stage to Complete. Optionally, pass a request body with additional information. Returns work order status information."""
        return self.__request('PUT', '/api/v2/dcimoperations/workorders/complete/' + str(workOrderId) + '?', payload)

    def getRequestStatusByItem(self, itemId: int):
        """Get a list of pending request status information for a given item ID. Returns list of request status."""
        return self.__request('GET', '/api/v2/dcimoperations/requests/pending/' + str(itemId) + '?')

    def getRequest(self, requestId: int):
        """Get request status information for a given request ID. Returns full request status information."""
        return self.__request('GET', '/api/v2/dcimoperations/requests/status/' + str(requestId) + '?')

    def searchRequests(self, payload: dict):
        """Get request status information for a given request ID. Returns full request status information."""
        return self.__request('POST', '/api/v2/dcimoperations/search/list/requests?', payload)

    def createDataConnection(self, payload: dict):
        """Create a data connection. Returns the newly created data connection."""
        return self.__request('POST', '/api/v2/connections/dataconnections?', payload)

    def updateDataConnection(self, connectionId: int, payload: dict):
        """Edit a data connection. Returns the newly edited data connection."""
        return self.__request('PUT', '/api/v2/connections/dataconnections/' + str(connectionId) + '?', payload)

    def getDataConnection(self, connectionId: int):
        """Get a data connection and associated details. Requires the ID of the connection you want to retrieve. Returns the requested data connection and associated details."""
        return self.__request('GET', '/api/v2/connections/dataconnections/' + str(connectionId) + '?')

    def getDataConnectionByNode(self, location: str, itemName: str, portName: str):
        """Get data connection details based on the specified location, item name, and port name. The itemName specified in the URL must be either the starting or ending Item in the connection. This API does not support Data Panel Ports. Returns the JSON payload with the requested data connection details."""
        return self.__request('GET', '/api/v2/connections/dataconnections?location=' + str(location) + '&itemName=' + str(itemName) + '&portName=' + str(portName) + '&')

    def deleteDataConnection(self, connectionId: int):
        """Deletes the specified data connection."""
        return self.__request('DELETE', '/api/v2/connections/dataconnections/' + str(connectionId) + '?')

    def createPowerConnection(self, payload: dict):
        """Create a power connection. Returns the newly created power connection."""
        return self.__request('POST', '/api/v2/connections/powerconnections?', payload)

    def updatePowerConnection(self, connectionId: int, payload: dict):
        """Edit a power connection. Returns the newly edited power connection."""
        return self.__request('PUT', '/api/v2/connections/powerconnections/' + str(connectionId) + '?', payload)

    def getPowerConnection(self, connectionId: int):
        """Get a power connection and associated details. Requires the ID of the connection you want to retrieve. Returns the requested power connection and associated details."""
        return self.__request('GET', '/api/v2/connections/powerconnections/' + str(connectionId) + '?')

    def getPowerConnectionByNode(self, location: str, itemName: str, portName: str):
        """Get power connection details based on the specified location, item name, and port name. Returns the JSON payload with the requested power connection details."""
        return self.__request('GET', '/api/v2/connections/powerconnections?location=' + str(location) + '&itemName=' + str(itemName) + '&portName=' + str(portName) + '&')

    def deletePowerConnection(self, connectionId: int):
        """Deletes the specified power connection. Deletes the power connection."""
        return self.__request('DELETE', '/api/v2/connections/powerconnections/' + str(connectionId) + '?')

    def getCircuit(self, circuitType: str, location: str, itemName: str, portName: str):
        """Get power or data circuit details based on the specified circuit type location, item name, and port name. Returns the JSON payload with the requested power or data connection details."""
        return self.__request('GET', '/api/v2/dcimoperations/circuits/' + str(circuitType) + '?location=' + str(location) + '&itemName=' + str(itemName) + '&portName=' + str(portName) + '&')

    def retrievePowerChain(self, locationId: int, payload: dict):
        """Get links and nodes of entire power chain with customizable node details for a specific location. JSON entity containing data for the entire Power Chain for a given Location. The example below illustrates returning all fields by leaving the "selectedColumn" array empty. To limit the columns in the response, list the specific columns."""
        return self.__request('POST', '/api/v2/powerChain/' + str(locationId) + '?', payload)

    def retrievePowerSumForPorts(self, payload: dict):
        """Get power sum for power ports with port ID list."""
        return self.__request('POST', '/api/v2/powerChain/powerSum/bulk?', payload)

    def retrievePowerSumForItems(self, payload: dict):
        """Get power sum for power ports using item ID list."""
        return self.__request('POST', '/api/v2/items/powerSum/bulk?', payload)

    def getActualReadingsByItem(self, itemId: int):
        """Update Actual Readings for Power Ports for an Item."""
        return self.__request('GET', '/api/v2/powerChain/items/actualReadings/' + str(itemId) + '?')

    def retrieveActualReadingsByItems(self, payload: dict):
        """Retrieve Actual Readings for Power Ports for multiple Items."""
        return self.__request('POST', '/api/v2/powerChain/items/actualReadings/bulk?', payload)

    def retrieveActualReadingsByPorts(self, payload: dict):
        """Update Actual Readings for Power Ports on one or more items."""
        return self.__request('POST', '/api/v2/powerChain/ports/actualReadings/bulk?', payload)

    def updateActualReadingsByPort(self, portId: int, payload: dict):
        """Update Actual Readings By Port."""
        return self.__request('PUT', '/api/v2/powerChain/ports/actualReadings/' + str(portId) + '?', payload)

    def getActualReadingsByPort(self, portId: int):
        """Get Actual Readings By Port."""
        return self.__request('GET', '/api/v2/powerChain/ports/actualReadings/' + str(portId) + '?')

    def getTicket(self, ticketId: int):
        """Get Ticket by Ticket ID."""
        return self.__request('GET', '/api/v2/tickets/' + str(ticketId) + '?')

    def createTicket(self, payload: dict):
        """Create a Ticket."""
        return self.__request('POST', '/api/v2/tickets?', payload)

    def updateTicket(self, ticketId: int, payload: dict):
        """Update a Ticket."""
        return self.__request('PUT', '/api/v2/tickets/' + str(ticketId) + '?', payload)

    def deleteTicket(self, ticketId: int, proceedOnWarning: bool):
        """Delete Ticket by Ticket ID."""
        return self.__request('DELETE', '/api/v2/tickets/' + str(ticketId) + '?proceedOnWarning=' + str(proceedOnWarning) + '&')

    def searchTickets(self, pageNumber: int, pageSize: int, payload: dict):
        """Search for Tickets using criteria JSON object. Search criteria can be any of the fields applicable to Tickets, including custom fields. Specify the fields to be included in the response. This API supports pagination. Returns a list of Tickets with the specified information."""
        return self.__request('POST', '/api/v2/quicksearch/tickets?pageNumber=' + str(pageNumber) + '&pageSize=' + str(pageSize) + '&', payload)

    def getTicketFieldList(self):
        """Returns a list of all Ticket fields."""
        return self.__request('GET', '/api/v2/quicksearch/tickets/ticketListFields?')

    def createTicketsBulk(self, payload: dict):
        """Add/Update/Delete Tickets in Bulk. The body of the Request should contain the required fields required to perform the specified Method."""
        return self.__request('POST', '/api/v2/tickets/bulk?', payload)

    def createTicketAssignment(self, entityType: str, payload: dict):
        """Assign Item to Ticket. The entity Ids provided in the Request should be the ID of the entity to be assigned to the Ticket."""
        return self.__request('POST', '/api/v2/tickets/assignment/' + str(entityType) + '/assign?', payload)

    def removeTicketAssignment(self, entityType: str, payload: dict):
        """Unassign Item from Ticket. This API will disassociate multiple Items or Circuits from a Ticket. The Ids provided in the Request should be the IDs of the assignment records."""
        return self.__request('POST', '/api/v2/tickets/assignment/' + str(entityType) + '/unassign?', payload)

    def createCustomField(self, payload: dict):
        """Creates a custom field. Returns the newly created custom field."""
        return self.__request('POST', '/api/v2/settings/lists/customFields?', payload)

    def updateCustomField(self, customFieldId: int, payload: dict):
        """Update the definitions of the specified custom fields. Returns the updated custom field definitions."""
        return self.__request('PUT', '/api/v2/settings/lists/customFields/' + str(customFieldId) + '?', payload)

    def getCustomFields(self, orderPickListsBy: str):
        """Get a list of custom fields. Returns a list of all custom fields."""
        return self.__request('GET', '/api/v2/settings/lists/customFields?orderPickListsBy=' + str(orderPickListsBy) + '&')

    def getCustomField(self, customFieldId: int, orderPickListsBy: str):
        """Get the custom field details for a given customFieldId. Passing a -1 value will return all the labels with null values. Returns a list of custom field details for the specified custom field."""
        return self.__request('GET', '/api/v2/settings/lists/customFields/' + str(customFieldId) + '?orderPickListsBy=' + str(orderPickListsBy) + '&')

    def deleteCustomField(self, customFieldId: int, proceedOnWarning: bool):
        """Deletes the specified custom field and associated pick lists."""
        return self.__request('DELETE', '/api/v2/settings/lists/customFields/' + str(customFieldId) + '?proceedOnWarning=' + str(proceedOnWarning) + '&')

    def getWebhook(self):
        """Returns the current Webhook configuration information."""
        return self.__request('GET', '/api/v2/notifications/config?')

    def updateWebhook(self, payload: dict):
        """Update the Webhook configuration information."""
        return self.__request('PUT', '/api/v2/notifications/config?', payload)

    def deleteWebhook(self):
        """Deletes the Webhook configuration."""
        return self.__request('DELETE', '/api/v2/notifications/config?')

    def getRelationship(self, id: int):
        """Get Relationship details using the Relationship ID."""
        return self.__request('GET', '/api/v2/relationship/' + str(id) + '?')

    def createRelationship(self, payload: dict):
        """Create a new entity link. Returns the newly created item JSON object. Note: Supported entity Types are "PROJECT", "TICKET", "ITEM"."""
        return self.__request('POST', '/api/v2/relationship?', payload)

    def getRelationshipByEntity(self, entityType: str, entityId: int):
        """Search for Entity Links BY Entity Type and Entity ID. Entity Types are "PROJECT", "ITEM". Returns a Project JSON object."""
        return self.__request('GET', '/api/v2/relationship/' + str(entityType) + '/' + str(entityId) + '?')

    def searchRelationships(self, payload: dict):
        """Search for Entity Links. Returns an array of Relationship links for the entity type."""
        return self.__request('POST', '/api/v2/relationship/search?', payload)

    def deleteRelationship(self, id: int):
        """Delete an Entity Link using the Relationship ID."""
        return self.__request('DELETE', '/api/v2/relationship/' + str(id) + '?')

    def getFloormapConfig(self, locationId: int):
        """Get floormap configuration for specific location."""
        return self.__request('GET', '/api/v2/visualization/floormaps/configuration/' + str(locationId) + '?')

    def getFloormapConfigs(self):
        """Get floormap configuration for all locations."""
        return self.__request('GET', '/api/v2/visualization/floormaps/configuration?')

    def updateFloormapConfig(self, locationId: int, payload: dict):
        """Modify floormap configuration for specific location."""
        return self.__request('PUT', '/api/v2/visualization/floormaps/configuration/' + str(locationId) + '?', payload)

    def createFloormapConfigsBulk(self, payload: dict):
        """Modify floormap configurations for multiple locations."""
        return self.__request('POST', '/api/v2/visualization/floormaps/configuration/bulk?', payload)

    def createProject(self, payload: dict):
        """Add a new Project. JSON entity containing Project information that was passed in from the Request payload."""
        return self.__request('POST', '/api/v2/dcimoperations/projects?', payload)

    def updateProject(self, id: int, payload: dict):
        """Modify a Project. JSON entity containing Project information that was passed in from the Request payload."""
        return self.__request('PUT', '/api/v2/dcimoperations/projects/' + str(id) + '?', payload)

    def deleteProject(self, id: int):
        """Delete a Project using the Project ID."""
        return self.__request('DELETE', '/api/v2/dcimoperations/projects/' + str(id) + '?')

    def getProject(self, id: int):
        """Get Project details using the Project ID. Returns a Project JSON object."""
        return self.__request('GET', '/api/v2/dcimoperations/projects/' + str(id) + '?')

    def createPartClass(self, payload: dict):
        """Create Part Classes. Returns JSON entity containing data for the created Part Class."""
        return self.__request('POST', '/api/v2/parts/classes?', payload)

    def updatePartClass(self, classId: int, payload: dict):
        """Update Part Classes. Returns JSON entity containing data for the updated Part Class."""
        return self.__request('PUT', '/api/v2/parts/classes/' + str(classId) + '?', payload)

    def deletePartClass(self, classId: int):
        """Delete Part Class by Class ID."""
        return self.__request('DELETE', '/api/v2/parts/classes/' + str(classId) + '?')

    def getPartClasses(self):
        """Returns a list of Part Classes with basic information."""
        return self.__request('GET', '/api/v2/parts/classes?')

    def createPartClassesBulk(self, payload: dict):
        """Create, Update, Delete Part Classes in Bulk. Returns JSON entity containing a list of response codes."""
        return self.__request('POST', '/api/v2/parts/classes/bulk?', payload)

    def createPartModel(self, payload: dict):
        """Create Part Model. Returns JSON entity containing data for the created Part Model."""
        return self.__request('POST', '/api/v2/partModels?', payload)

    def updatePartModel(self, modelId: int, payload: dict):
        """Update a Part Model. Returns JSON entity containing data for the Updated Part Model."""
        return self.__request('PUT', '/api/v2/partModels/' + str(modelId) + '?', payload)

    def deletePartModel(self, modelId: int):
        """Delete Part Model by Model ID."""
        return self.__request('DELETE', '/api/v2/partModels/' + str(modelId) + '?')

    def getPartModel(self, modelId: int):
        """Get Model by Model ID. Returns JSON entity containing data for a single Model."""
        return self.__request('GET', '/api/v2/partModels/' + str(modelId) + '?')

    def searchPartModels(self, pageNumber: int, pageSize: int, payload: dict):
        """Search for Part Models using criteria JSON object. Search criteria can be any of the fields applicable to Part Models, including custom fields. Specify the field to be included in the response. This API supports pagination. Returns a list of Part Models with the specified information."""
        return self.__request('POST', '/api/v2/quicksearch/parts/models?pageNumber=' + str(pageNumber) + '&pageSize=' + str(pageSize) + '&', payload)

    def deletePartModelImage(self, modelId: int):
        """Delete a Part Model Image using the Part Model ID."""
        return self.__request('DELETE', '/api/v2/partModels/images/' + str(modelId) + '?')

    def createPartModelsBulk(self, payload: dict):
        """Create, Update, Delete Part Models in Bulk. Returns JSON entity containing a list of response codes."""
        return self.__request('POST', '/api/v2/partModels/bulk?', payload)

    def getPartModelFieldList(self):
        """Returns a list of all Part Model fields."""
        return self.__request('GET', '/api/v2/quicksearch/parts/partModelListFields?')

    def createPart(self, payload: dict):
        """Create Part Instance. Returns JSON entity containing data for the created Part Instance."""
        return self.__request('POST', '/api/v2/parts?', payload)

    def getPart(self, partId: int):
        """Get Part Instance by Part ID. Returns JSON entity containing data for a single Part Instance."""
        return self.__request('GET', '/api/v2/parts/' + str(partId) + '?')

    def updatePart(self, partId: int, payload: dict):
        """Update Part Instance. Returns JSON entity containing data for a single Part Instance."""
        return self.__request('PUT', '/api/v2/parts/' + str(partId) + '?', payload)

    def deletePart(self, partId: int):
        """Delete Part Instance. JSON entity containing errors and warnings."""
        return self.__request('DELETE', '/api/v2/parts/' + str(partId) + '?')

    def createPartsBulk(self, payload: dict):
        """Create, Update, Delete Part Instances in Bulk. Returns JSON entity containing a list of response codes."""
        return self.__request('POST', '/api/v2/parts/bulk?', payload)

    def updateStock(self, partId: int, activity: str, payload: dict):
        """Adjust or Transfer Stock where "activity" can be "adjust" or "transfer". Returns JSON entity containing data for the transaction performed."""
        return self.__request('PUT', '/api/v2/parts/' + str(partId) + '/stock/' + str(activity) + '?', payload)

    def createPartAssignment(self, assignmentType: str, payload: dict):
        """Assign Parts to Items or Item Ports where "assignmentType" can be "ITEMS" or "PORTS". Returns JSON entity containing data for the assignment."""
        return self.__request('POST', '/api/v2/parts/assignments/' + str(assignmentType) + '?', payload)

    def getPartFieldList(self):
        """Returns a list of all Part fields."""
        return self.__request('GET', '/api/v2/quicksearch/parts/partListFields?')

    def searchParts(self, pageNumber: int, pageSize: int, payload: dict):
        """Search for Parts using criteria JSON object. Search criteria can be any of the fields applicable to Parts, including custom fields. Specify the field to be included in the response. This API supports pagination. Returns a list of Parts with the specified information."""
        return self.__request('POST', '/api/v2/quicksearch/parts?pageNumber=' + str(pageNumber) + '&pageSize=' + str(pageSize) + '&', payload)

    def getPartTransactionFieldList(self):
        """Returns a list of all Part Transaction fields."""
        return self.__request('GET', '/api/v2/quicksearch/parts/partTransactionListFields?')

    def searchPartTransactions(self, pageNumber: int, pageSize: int, payload: dict):
        """Search for Part Transactions using criteria JSON object. Search criteria can be any of the fields applicable to Part Transactions, including custom fields. Specify the field to be included in the response. This API supports pagination. Returns a list of Part Transactions with the specified information."""
        return self.__request('POST', '/api/v2/quicksearch/parts/transactions?pageNumber=' + str(pageNumber) + '&pageSize=' + str(pageSize) + '&', payload)

    def searchAuditTrail(self, pageNumber: int, pageSize: int, payload: dict):
        """Search for one or more Audit Trail records by user supplied search criteria using the REST API v2. Returns a list of models with the "selectedColumns" returned in the payload."""
        return self.__request('POST', '/api/v2/quicksearch/auditTrail?pageNumber=' + str(pageNumber) + '&pageSize=' + str(pageSize) + '&', payload)

    def getAuditTrailFieldList(self):
        """Returns a list of all Audit Trail fields."""
        return self.__request('GET', '/api/v2/quicksearch/auditTrail/auditTrailListFields?')

    def getCharts(self):
        """Get a list of all available chart widgets in the system."""
        return self.__request('GET', '/api/v2/reports/charts?')

    def getChart(self, id: int):
        """Get chart details by ID."""
        return self.__request('GET', '/api/v2/reports/charts/' + str(id) + '?')

    def retrieveChartData(self, id: int, payload: dict):
        """Get chart data by ID."""
        return self.__request('POST', '/api/v2/reports/charts/' + str(id) + '/data?', payload)

    def retrieveChartDetails(self, id: int, payload: dict):
        """Get a widget's details including a list of parameters."""
        return self.__request('POST', '/api/v2/reports/charts/' + str(id) + '/details?', payload)

    def retrieveChartParameters(self, id: int, payload: dict):
        """Get a listing of parameter pick-list choices. ID is the record id of the widget. Request is a map containing a key with a value containing an array of ids. 404 not found will be returned when parameter is missing or incorrect."""
        return self.__request('POST', '/api/v2/reports/charts/parameters/' + str(id) + '?', payload)
