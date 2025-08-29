import os
import json
import time
import requests
import backoff
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
from .config import config, Config
from .formatters import FORMATTERS
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport


class BioprocessIntelligenceClient:
    def __init__(self, api_url: str, username: str = None, password: str = None, 
                 microsoft_id_token: Optional[str] = None, output_format: str = 'text', verify: bool = True):
        """Initialize the client
        
        Args:
            api_url: URL of the GraphQL API
            username: Username for authentication (required if not using microsoft_id_token)
            password: Password for authentication (required if not using microsoft_id_token)
            microsoft_id_token: Microsoft AAD ID token for social login (alternative to username/password)
            output_format: Format for command output. One of: 'text', 'json', 'yaml', 'table'
            verify: Whether to verify SSL certificates for HTTPS requests (default True)
        
        Note:
            Either username/password OR microsoft_id_token must be provided, but not both.
        """
        
        # Create a new Config instance instead of using the global one
        self.config = Config()
        # Set values from constructor arguments
        self.config.api_url = api_url.strip()
        self.config.username = (username or "").strip()
        self.config.password = (password or "").strip()
        self._microsoft_id_token = microsoft_id_token
        self.formatter = FORMATTERS[output_format]
        self.session = requests.Session()
        self.verify = verify
        self._refresh_token = None
        self._refresh_token_expires_at = None
        self._token_expires_at = None
        
        # Validate authentication parameters
        if not microsoft_id_token and (not username or not password):
            raise ValueError("Either username/password OR microsoft_id_token must be provided")
        if microsoft_id_token and (username or password):
            raise ValueError("Cannot use both username/password and microsoft_id_token authentication")
        
        self._authenticate()
        # Added to cache process topic associations for update and retrieval
        self._process_topic_map = {}

    def _authenticate(self):
        """Choose the appropriate authentication flow"""
        if self._microsoft_id_token:
            self._authenticate_social()
        else:
            self._authenticate_password()

    @backoff.on_exception(backoff.expo, 
                          (requests.exceptions.RequestException, requests.exceptions.HTTPError),
                          max_tries=3,
                          max_time=30)
    def _authenticate_password(self):
        """Authenticate with username/password and get JWT token"""
        mutation = """
            mutation tokenAuth($username: String!, $password: String!) {
                tokenAuth(username: $username, password: $password) {
                    token
                    refreshToken
                }
            }
        """
        
        variables = {
            'username': self.config.username,
            'password': self.config.password
        }
        
        try:
            response = self._execute_query(mutation, variables, skip_auth_check=True)
            token_data = response.get('data', {}).get('tokenAuth', {})
            
            if not token_data.get('token'):
                raise Exception('No token received in authentication response')
                
            self.config.token = token_data['token']
            self._refresh_token = token_data.get('refreshToken')
            
            # JWT tokens from the backend expire after 15 minutes
            # Set expiry time to 14 minutes to refresh before expiration
            self._token_expires_at = datetime.now() + timedelta(minutes=14)
            # Assume refresh token is valid for 7 days (standard)
            self._refresh_token_expires_at = datetime.now() + timedelta(days=7)
            
        except Exception as e:
            raise Exception(f'Authentication failed: {str(e)}. Please verify your credentials and API URL.') from e

    @backoff.on_exception(backoff.expo, 
                          (requests.exceptions.RequestException, requests.exceptions.HTTPError),
                          max_tries=3,
                          max_time=30)
    def _authenticate_social(self):
        """Authenticate with Microsoft ID token via SocialLogin"""
        mutation = """
        mutation SocialLogin($idToken: String!) {
            socialLogin(idToken: $idToken) {
                success
                token
                refreshToken
                refreshExpiresIn
                error
                payload
            }
        }
        """
        
        variables = {
            "idToken": self._microsoft_id_token
        }
        
        try:
            response = self._execute_query(mutation, variables, skip_auth_check=True)
            auth_data = response.get("data", {}).get("socialLogin", {})
            
            if not auth_data.get("success"):
                error_msg = auth_data.get("error", "unknown error")
                raise Exception(f"Microsoft authentication failed: {error_msg}")
            
            self.config.token = auth_data["token"]
            self._refresh_token = auth_data.get("refreshToken")
            
            # JWT access tokens from the backend expire after 15 minutes
            # Set expiry time to 14 minutes to refresh before expiration
            self._token_expires_at = datetime.now() + timedelta(minutes=14)
            
            # Handle refresh token expiry from Microsoft auth response
            refresh_expires_in = auth_data.get("refreshExpiresIn")
            if refresh_expires_in:
                # refreshExpiresIn is typically in seconds
                self._refresh_token_expires_at = datetime.now() + timedelta(seconds=refresh_expires_in)
            else:
                # Default to 7 days if not provided
                self._refresh_token_expires_at = datetime.now() + timedelta(days=7)
            
        except Exception as e:
            raise Exception(f'Microsoft authentication failed: {str(e)}. Please verify your Microsoft ID token and API URL.') from e

    @backoff.on_exception(backoff.expo, 
                          (requests.exceptions.RequestException, requests.exceptions.HTTPError),
                          max_tries=3,
                          max_time=30)
    def _refresh_access_token(self):
        """Refresh the access token using the refresh token with exponential backoff"""
        if not self._refresh_token:
            # If no refresh token, re-authenticate
            self._authenticate()
            return
            
        # Check if refresh token is expired
        if self._refresh_token_expires_at and datetime.now() >= self._refresh_token_expires_at:
            # Refresh token is expired, need to re-authenticate
            self._authenticate()
            return
            
        mutation = """
            mutation refreshToken($refreshToken: String!) {
                refreshToken(refreshToken: $refreshToken) {
                    token
                    refreshToken
                }
            }
        """
        
        variables = {
            'refreshToken': self._refresh_token
        }
        
        try:
            response = self._execute_query(mutation, variables, skip_auth_check=True)
            token_data = response.get('data', {}).get('refreshToken', {})
            
            if not token_data.get('token'):
                # Refresh token is expired or invalid, re-authenticate
                self._authenticate()
                return
                
            self.config.token = token_data['token']
            if token_data.get('refreshToken'):
                self._refresh_token = token_data['refreshToken']
                # Reset refresh token expiry if we got a new one
                if self._microsoft_id_token:
                    # For Microsoft auth, maintain the original expiry unless we get updated info
                    pass
                else:
                    # For password auth, assume 7 days from now
                    self._refresh_token_expires_at = datetime.now() + timedelta(days=7)
            
            # Reset access token expiry time to 14 minutes from now
            self._token_expires_at = datetime.now() + timedelta(minutes=14)
            
        except Exception:
            # If refresh fails after backoff retries, try re-authenticating
            self._authenticate()

    def _ensure_valid_token(self):
        """Ensure the current token is valid, refresh if necessary"""
        if not self.config.token or not self._token_expires_at:
            self._authenticate()
            return
            
        # Check if token is close to expiring (within 1 minute)
        if datetime.now() >= (self._token_expires_at - timedelta(minutes=1)):
            self._refresh_access_token()

    @backoff.on_exception(backoff.expo, 
                          requests.exceptions.RequestException,
                          max_tries=3,
                          max_time=30,
                          giveup=lambda e: isinstance(e, requests.exceptions.HTTPError) and 400 <= e.response.status_code < 500)
    def _execute_query(self, query, variables: Dict = None, skip_auth_check: bool = False) -> Dict:
        """Execute a GraphQL query or mutation with automatic token refresh and exponential backoff."""
        
        # Ensure we have a valid token unless explicitly skipping auth check
        if not skip_auth_check:
            self._ensure_valid_token()
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        if self.config.token:
            headers['Authorization'] = f'JWT {self.config.token}'

        # Ensure CSRF token if required
        self.session.get(self.config.api_url, verify=self.verify)
        csrf_token = self.session.cookies.get('csrftoken')
        if csrf_token:
            headers['X-CSRFToken'] = csrf_token

        # Check if query is a `gql` instance
        query_payload = query if isinstance(query, str) else str(query)
        
        request_data = {
            'query': query_payload,
            'variables': variables
        }

        try:
            response = self.session.post(self.config.api_url, json=request_data, headers=headers, verify=self.verify)
            response.raise_for_status()
            json_data = response.json()
            
            if 'errors' in json_data:
                # Check if it's a token expiration error
                for error in json_data['errors']:
                    error_msg = error.get('message', '').lower()
                    if 'signature has expired' in error_msg or 'not logged in' in error_msg:
                        if not skip_auth_check:
                            # Try refreshing the token and retry once
                            self._refresh_access_token()
                            headers['Authorization'] = f'JWT {self.config.token}'
                            
                            # Retry the request with new token
                            response = self.session.post(self.config.api_url, json=request_data, headers=headers, verify=self.verify)
                            response.raise_for_status()
                            json_data = response.json()
                            
                            # If still errors after refresh, raise them
                            if 'errors' in json_data:
                                raise Exception(f"GraphQL errors: {json_data['errors']}")
                            break
                else:
                    # No auth-related errors, raise the original errors
                    raise Exception(f"GraphQL errors: {json_data['errors']}")
            
            return json_data
        except requests.exceptions.HTTPError as e:
            # Try to extract more detailed error information from the response
            error_detail = ""
            try:
                error_json = response.json()
                if 'errors' in error_json and error_json['errors']:
                    error_detail = f". Details: {json.dumps(error_json['errors'])}"
            except:
                pass
            print(f"Request data: {json.dumps(request_data)}")
            raise Exception(f"HTTP request failed: {str(e)}{error_detail}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"HTTP request failed: {str(e)}")

    def list_teams(self, raw: bool = True, output_format: Optional[str] = None) -> Union[str, List[Dict[str, Any]]]:
        """Get list of teams"""
        query = """
            query {
                teams {
                    id
                    name
                    description
                }
            }
        """
        response = self._execute_query(query)
        data = response['data']['teams']
        
        if output_format:
            formatter = FORMATTERS[output_format]
            return formatter.format(data)
        return data

    def list_collections(self, team_id: Optional[str] = None, raw: bool = True, output_format: Optional[str] = None) -> Union[str, List[Dict[str, Any]]]:
        """Get list of collections (topics), optionally filtered by team"""
        query = """
            query($teamId: ID) {
                topics(teamId: $teamId) {
                    id
                    name
                    description
                }
            }
        """
        variables = {'teamId': team_id} if team_id else {}
        response = self._execute_query(query, variables)
        data = response['data']['topics']
        
        if output_format:
            formatter = FORMATTERS[output_format]
            return formatter.format(data)
        return data

    def list_processes(self, collection_id: Optional[str] = None, topic_id: Optional[str] = None, raw: bool = True, output_format: Optional[str] = None) -> Union[str, Dict[str, Any]]:
        """Get list of processes, optionally filtered by topic
        
        Args:
            topic_id: Optional ID of topic to filter by
        Returns:
            Dict containing 'processes' list and 'totalCount'
        """
        # Allow alias 'topic_id' for collection_id
        if topic_id is not None and collection_id is None:
            collection_id = topic_id
        query = """
            query processes($topicId: ID) {
                processes(topicId: $topicId) {
                    processes {
                        id
                        name
                    }
                    totalCount
                }
            }
        """

        # the graphql endpoint expects topicId, but we will use collection_id
        variables = {'topicId': collection_id} if collection_id else {}
        response = self._execute_query(query, variables)
        data = response['data']['processes']
        
        if output_format:
            formatter = FORMATTERS[output_format]
            return formatter.format(data)
        # If result is a list of processes, add the topic field from cached mapping
        if isinstance(data, list):
            for proc in data:
                if 'topic' not in proc or not isinstance(proc['topic'], dict):
                    topic_value = self._process_topic_map.get(proc['id'], '')
                    proc['topic'] = {"id": topic_value} if topic_value else {}
        return data

    def get_process(self, process_id: Optional[str] = None, name: Optional[str] = None, collection_id: Optional[str] = None, raw: bool = True, output_format: Optional[str] = None) -> Union[str, Dict[str, Any]]:
        """Get detailed information about a specific process
        
        Args:
            process_id: ID of the process to retrieve (either process_id or name and collection_id must be provided)
            name: Name of the process to retrieve (either process_id or name and collection_id must be provided)
            collection_id: ID of the collection to retrieve (either process_id or name and collection_id must be provided)
        Returns:
            Dict containing process details including metadata, parameters, variables and calculators
        """
        query = """
            query GetProcess($id: ID, $name: String, $topicId: ID) {
                process(id: $id, name: $name, topicId: $topicId) {
                    id
                    name
                    description
                    startTime
                    endTime
                    lastUpdated
                }
            }
        """

        variables = {
            'id': process_id,
            'name': name,
            'topicId': collection_id
        }

        result = self._execute_query(query, variables)
        process_data = result.get('data', {}).get('process', {})
        # Include the topic from cache if it exists
        # Include the topic from cache if it exists
        topic_value = self._process_topic_map.get(process_data['id'], '')
        process_data['topic'] = {"id": topic_value} if topic_value else {}
        
        if output_format:
            formatter = FORMATTERS[output_format]
            return formatter.format(process_data)
        return process_data

    def create_process(self, collection_id: str, name: str, description: Optional[str] = None, start_time: Optional[str] = None, end_time: Optional[str] = None) -> Dict[str, Any]:
        """Create a new process
        
        Args:
            collection_id: ID of the collection to create the process in
            name: Name of the process
            description: Optional description
            start_time: Optional start time in ISO format
            end_time: Optional end time in ISO format
        
        Returns:
            Created process data
        """
        mutation = """
            mutation createProcess($input: CreateProcessInputType!) {
                createProcess(input: $input) {
                    process {
                        id
                        name
                        description
                        startTime
                        endTime
                    }
                }
            }
        """

        variables = {
            'input': {
                'topicId': collection_id,
                'name': name,
                'description': description,
                'startTime': start_time,
                'endTime': end_time
            }
        }

        response = self._execute_query(mutation, variables)
        process = response['data']['createProcess']['process']
        # Add the topic field for client consistency and cache it
        process['topic'] = {"id": collection_id}
        self._process_topic_map[process['id']] = collection_id
        return process

    def update_process(self, process_id: str, name: Optional[str] = None, description: Optional[str] = None, start_time: Optional[str] = None, end_time: Optional[str] = None) -> Dict[str, Any]:
        """Update an existing process
        
        Args:
            process_id: ID of the process to update
            name: Optional new name
            description: Optional new description
            start_time: Optional new start time in ISO format
            end_time: Optional new end time in ISO format
        
        Returns:
            Updated process data
        """

        # First, get the current process to ensure we have the topic_id in our cache
        try:
            current_process = self.get_process(process_id, raw=True)
            if 'topic' in current_process and 'id' in current_process['topic']:
                self._process_topic_map[process_id] = current_process['topic']['id']
        except Exception:
            # If we can't get the current process, we'll continue anyway
            pass
            
        mutation = """
            mutation updateProcess($input: UpdateProcessInputType!) {
                updateProcess(input: $input) {
                    process {
                        id
                        name
                        description
                        startTime
                        endTime
                    }
                }
            }
        """
        # Build input with only non-None values to avoid sending null values to the API
        input_data = {'id': process_id}  # Using 'id' instead of 'processId' as required by the API
        if name is not None:
            input_data['name'] = name
        if description is not None:
            input_data['description'] = description
        if start_time is not None:
            input_data['startTime'] = start_time
        if end_time is not None:
            input_data['endTime'] = end_time
            
        variables = {
            'input': input_data
        }
        response = self._execute_query(mutation, variables)
        process = response['data']['updateProcess']['process']
        # Preserve the original topic from cache if available
        topic_value = self._process_topic_map.get(process['id'], '')
        process['topic'] = {"id": topic_value} if topic_value else {}
        return process

    def delete_process(self, process_id: str) -> bool:
        """Delete a process
        
        Args:
            process_id: ID of the process to delete
        
        Returns:
            True if successful
        """
        mutation = """
            mutation deleteProcess($id: ID!) {
                deleteProcess(id: $id) {
                    ok
                    id
                }
            }
        """

        variables = {'id': process_id}

        response = self._execute_query(mutation, variables)
        return response['data']['deleteProcess']['ok']

    # Team Management
    def create_team(self, name: str, description: Optional[str] = None, raw: bool = True, output_format: Optional[str] = None) -> Union[str, Dict[str, Any]]:
        """Create a new team
        
        Args:
            name: Name of the team
            description: Optional description
            raw: Return raw data instead of formatted output
            output_format: Optional output format
        
        Returns:
            Created team data
        """
        mutation = """
            mutation createTeam($input: CreateTeamInputType!) {
                createTeam(input: $input) {
                    team {
                        id
                        name
                        description
                        owner {
                            id
                            username
                        }
                    }
                }
            }
        """

        variables = {
            'input': {
                'name': name,
                'description': description
            }
        }

        response = self._execute_query(mutation, variables)
        team_data = response['data']['createTeam']['team']
        
        if output_format:
            formatter = FORMATTERS[output_format]
            return formatter.format(team_data)
        return team_data

    def update_team(self, team_id: str, name: Optional[str] = None, description: Optional[str] = None, raw: bool = True, output_format: Optional[str] = None) -> Union[str, Dict[str, Any]]:
        """Update an existing team
        
        Args:
            team_id: ID of the team to update
            name: Optional new name
            description: Optional new description
            raw: Return raw data instead of formatted output
            output_format: Optional output format
        
        Returns:
            Updated team data
        """
        mutation = """
            mutation updateTeam($input: UpdateTeamInputType!) {
                updateTeam(input: $input) {
                    team {
                        id
                        name
                        description
                        owner {
                            id
                            username
                        }
                    }
                }
            }
        """

        variables = {
            'input': {
                'id': team_id,
                'name': name,
                'description': description
            }
        }

        # Remove None values
        variables['input'] = {k: v for k, v in variables['input'].items() if v is not None}

        response = self._execute_query(mutation, variables)
        team_data = response['data']['updateTeam']['team']
        
        if output_format:
            formatter = FORMATTERS[output_format]
            return formatter.format(team_data)
        return team_data

    def delete_team(self, team_id: str) -> bool:
        """Delete a team
        
        Args:
            team_id: ID of the team to delete
        
        Returns:
            True if successful
        """
        mutation = """
            mutation deleteTeam($id: ID!) {
                deleteTeam(id: $id) {
                    ok
                    id
                }
            }
        """

        variables = {'id': team_id}

        response = self._execute_query(mutation, variables)
        return response['data']['deleteTeam']['ok']

    def add_user_to_team(self, team_id: str, username: str, permission: Optional[str] = None, raw: bool = True, output_format: Optional[str] = None) -> Union[str, bool]:
        """Add a user to a team
        
        Args:
            team_id: ID of the team
            username: Username to add
            permission: Optional permission level ('read', 'read and write', 'owner')
            raw: Return raw data instead of formatted output
            output_format: Optional output format
        
        Returns:
            True if successful
        """
        mutation = """
            mutation addUserToTeam($input: AddUserToTeamInputType!) {
                addUserToTeam(input: $input) {
                    ok
                }
            }
        """

        variables = {
            'input': {
                'teamId': team_id,
                'userName': username,
                'permission': permission
            }
        }

        response = self._execute_query(mutation, variables)
        result = response['data']['addUserToTeam']['ok']
        
        if output_format:
            formatter = FORMATTERS[output_format]
            return formatter.format({'ok': result})
        return result

    def remove_user_from_team(self, team_id: str, user_id: str, raw: bool = True, output_format: Optional[str] = None) -> Union[str, bool]:
        """Remove a user from a team
        
        Args:
            team_id: ID of the team
            user_id: ID of the user to remove
            raw: Return raw data instead of formatted output
            output_format: Optional output format
        
        Returns:
            True if successful
        """
        mutation = """
            mutation removeUserFromTeam($input: RemoveUserFromTeamInputType!) {
                removeUserFromTeam(input: $input) {
                    ok
                }
            }
        """

        variables = {
            'input': {
                'teamId': team_id,
                'userId': user_id
            }
        }

        response = self._execute_query(mutation, variables)
        result = response['data']['removeUserFromTeam']['ok']
        
        if output_format:
            formatter = FORMATTERS[output_format]
            return formatter.format({'ok': result})
        return result

    def update_user_team_permissions(self, team_id: str, user_id: str, permission: str, raw: bool = True, output_format: Optional[str] = None) -> Union[str, bool]:
        """Update a user's permissions in a team
        
        Args:
            team_id: ID of the team
            user_id: ID of the user
            permission: New permission level ('read', 'read and write', 'owner')
            raw: Return raw data instead of formatted output
            output_format: Optional output format
        
        Returns:
            True if successful
        """
        mutation = """
            mutation updateUserTeamPermissions($input: UpdateUserTeamPermissionsInputType!) {
                updateUserTeamPermissions(input: $input) {
                    ok
                }
            }
        """

        variables = {
            'input': {
                'teamId': team_id,
                'userId': user_id,
                'permission': permission
            }
        }

        response = self._execute_query(mutation, variables)
        result = response['data']['updateUserTeamPermissions']['ok']
        
        if output_format:
            formatter = FORMATTERS[output_format]
            return formatter.format({'ok': result})
        return result

    # Topic (Collection) Management
    def create_collection(self, name: str, team_id: str, description: Optional[str] = None, raw: bool = True, output_format: Optional[str] = None) -> Union[str, Dict[str, Any]]:
        """Create a new collection
        
        Args:
            name: Name of the collection
            team_id: ID of the team to create the collection in
            description: Optional description
            raw: Return raw data instead of formatted output
            output_format: Optional output format
        
        Returns:
            Created collection data
        """
        mutation = """
            mutation createTopic($input: CreateTopicInputType!) {
                createTopic(input: $input) {
                    topic {
                        id
                        name
                        description
                        team {
                            id
                            name
                        }
                    }
                }
            }
        """

        variables = {
            'input': {
                'name': name,
                'teamId': team_id,
                'description': description
            }
        }

        response = self._execute_query(mutation, variables)
        collection_data = response['data']['createTopic']['topic']
        
        if output_format:
            formatter = FORMATTERS[output_format]
            return formatter.format(collection_data)
        return collection_data

    def update_collection(self, collection_id: str, name: Optional[str] = None, description: Optional[str] = None,
                    permission_mode: Optional[str] = None, organization_data_standards_enabled: Optional[bool] = None,
                    team_data_standards_enabled: Optional[bool] = None, raw: bool = True, output_format: Optional[str] = None) -> Union[str, Dict[str, Any]]:
        """Update an existing collection
        
        Args:
            collection_id: ID of the collection to update
            name: Optional new name
            description: Optional new description
            permission_mode: Optional permission mode
            organization_data_standards_enabled: Optional organization data standards flag
            team_data_standards_enabled: Optional team data standards flag
            raw: Return raw data instead of formatted output
            output_format: Optional output format
        
        Returns:
            Updated collection data
        """
        mutation = """
            mutation updateTopic($input: UpdateTopicInputType!) {
                updateTopic(input: $input) {
                    topic {
                        id
                        name
                        description
                        team {
                            id
                            name
                        }
                    }
                }
            }
        """

        variables = {
            'input': {
                'id': collection_id,
                'name': name,
                'description': description,
                'permissionMode': permission_mode,
                'organizationDataStandardsEnabled': organization_data_standards_enabled,
                'teamDataStandardsEnabled': team_data_standards_enabled
            }
        }

        # Remove None values
        variables['input'] = {k: v for k, v in variables['input'].items() if v is not None}

        response = self._execute_query(mutation, variables)
        collection_data = response['data']['updateTopic']['topic']
        
        if output_format:
            formatter = FORMATTERS[output_format]
            return formatter.format(collection_data)
        return collection_data

    def delete_collection(self, collection_id: str) -> bool:
        """Delete a collection
        
        Args:
            collection_id: ID of the collection to delete
        
        Returns:
            True if successful
        """
        mutation = """
            mutation deleteTopic($id: ID!) {
                deleteTopic(id: $id) {
                    ok
                    id
                }
            }
        """

        variables = {'id': collection_id}

        response = self._execute_query(mutation, variables)
        return response['data']['deleteTopic']['ok']

    
    
    def import_excels(self, collection_id: str, file_paths: List[str], timezone: str = 'UTC') -> Dict[str, Any]:
        mutation = gql("""
        mutation ImportExcels($files: [Upload!]!, $topicId: ID!, $timezone: String!) {
            importExcels(input: {files: $files, topicId: $topicId, timezone: $timezone}) {
                ok
                backgroundTaskId
            }
        }
        """)

        headers = {
            'Authorization': f'JWT {self.config.token}',
            'Accept': 'application/json'
        }

        csrf_token = self.session.cookies.get('csrftoken')
        if csrf_token:
            headers['X-CSRFToken'] = csrf_token

        transport = RequestsHTTPTransport(
            url=self.config.api_url,
            headers=headers,
            use_json=False  # Important for multipart form-data
        )

        client = Client(transport=transport, fetch_schema_from_transport=False)

        # Open all files and store in a dictionary
        file_objects = {str(idx): open(path, "rb") for idx, path in enumerate(file_paths)}

        try:
            variables = {
                "files": list(file_objects.values()),  # File objects must be passed as separate variables
                "topicId": collection_id,  # FIXED: Corrected to "topicId"
                "timezone": timezone
            }

            result = client.execute(
                mutation,
                variable_values=variables,
                upload_files=True  # Enables multipart file uploads
            )
            return result['importExcels']

        finally:
            # Close all opened files to prevent resource leaks
            for f in file_objects.values():
                f.close()

    
    def import_yamls(self, collection_id: str, file_paths: List[str], timezone: str = 'UTC') -> Dict[str, Any]:
        mutation = gql("""
        mutation ImportYamls($files: [Upload!]!, $topicId: ID!, $timezone: String!) {
            importYamls(input: {files: $files, topicId: $topicId, timezone: $timezone}) {
                ok
                backgroundTaskId
            }
        }
        """)

        headers = {
            'Authorization': f'JWT {self.config.token}',
            'Accept': 'application/json'
        }

        csrf_token = self.session.cookies.get('csrftoken')
        if csrf_token:
            headers['X-CSRFToken'] = csrf_token

        transport = RequestsHTTPTransport(
            url=self.config.api_url,
            headers=headers,
            use_json=False  # Important for multipart form-data
        )

        client = Client(transport=transport, fetch_schema_from_transport=False)

        # Open all files and store in a dictionary
        file_objects = {str(idx): open(path, "rb") for idx, path in enumerate(file_paths)}

        try:
            variables = {
                "files": list(file_objects.values()),  # File objects must be passed as separate variables
                "topicId": collection_id,  # FIXED: Corrected to "topicId"
                "timezone": timezone
            }

            result = client.execute(
                mutation,
                variable_values=variables,
                upload_files=True  # Enables multipart file uploads
            )
            return result['importYamls']

        finally:
            # Close all opened files to prevent resource leaks
            for f in file_objects.values():
                f.close()


    def import_process_from_yaml(
        self,
        collection_id: str,
        content: str,
        timezone: str = 'UTC'
    ) -> Dict[str, any]:
        mutation = gql("""
        mutation ImportProcessFromYaml(
          $content: String!, 
          $topicId: ID!, 
          $timezone: String!
        ) {
          importProcessFromYaml(
            content: $content, 
            topicId: $topicId, 
            timezone: $timezone
          ) {
            ok
            backgroundTaskId
          }
        }
        """)

        # build headers (JWT + CSRF if present)
        headers = {
            'Authorization': f'JWT {self.config.token}',
            'Accept': 'application/json',
        }
        csrf_token = self.session.cookies.get('csrftoken')
        if csrf_token:
            headers['X-CSRFToken'] = csrf_token

        # JSON transport (no multipart needed)
        transport = RequestsHTTPTransport(
            url=self.config.api_url,
            headers=headers,
            use_json=True
        )
        client = Client(
            transport=transport,
            fetch_schema_from_transport=False
        )

        variables = {
            "content": content,
            "topicId": collection_id,
            "timezone": timezone
        }

        result = client.execute(
            mutation,
            variable_values=variables
        )
        return result['importProcessFromYaml']

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        query = """
        query GetBackgroundTaskStatus($id: ID!) {
            backgroundTask(id: $id) {
                status
                progress
                statusMessage
                outputMessage
                completionDate
            }
        }
        """

        variables = {"id": task_id}
        
        result = self._execute_query(query, variables)  # No need to strip query
        return result.get('data', {}).get('backgroundTask', {})
        
    def monitor_background_task(self, task_id: str, polling_interval: int = 1) -> Dict[str, Any]:
        """Monitor a background task until it completes, fails, or issues a warning.
        
        Args:
            task_id: ID of the background task to monitor
            polling_interval: Time in seconds between status checks (default: 5)
            
        Returns:
            Final task status information, including extracted process name if available
        """
        import re

        print(f"Monitoring background task ID: {task_id}")
        process_name = None

        while True:
            status_response = self.get_task_status(task_id)
            status = status_response.get("status", "UNKNOWN")
            progress = status_response.get("progress", 0)
            message = status_response.get("statusMessage", "No message")  # Robust default

            # Try to extract process name from the status message
            if not process_name and message:
                match = re.search(r":\s*([^\s]+)$", message)
                if match:
                    process_name = match.group(1)

            print(f"Task {task_id} status: {status} ({progress}% complete) - {message}")

            if status in ["COMPLETED", "FAILED", "WARNING"]:
                # Task has finished
                result = status_response.copy()
                if process_name:
                    result["processName"] = process_name
                return result

            time.sleep(polling_interval)  # Wait before checking again
    
    def import_lexicon(self, yaml_file_path: Optional[str] = None, data_standard_ids: Optional[List[str]] = None, 
                      target_collection_id: Optional[str] = None, target_team_id: Optional[str] = None, 
                      target_organization: bool = False, delete_missing: bool = False) -> Dict[str, Any]:
        """Import lexicon (data standards) into an organization, team, or collection.
        
        Args:
            yaml_file_path: Optional path to a YAML file containing lexicon data
            data_standard_ids: Optional list of data standard IDs to copy
            target_collection_id: Optional ID of the target collection (topic)
            target_team_id: Optional ID of the target team
            target_organization: Optional flag to import into the organization
            delete_missing: Optional flag to delete missing data standards
            
        Returns:
            Dict containing operation status and background task ID if applicable
            
        Note:
            At least one of yaml_file_path or data_standard_ids must be provided.
            Exactly one of target_collection_id, target_team_id, or target_organization must be True.
        """
        # Validate input parameters
        if yaml_file_path is None and (data_standard_ids is None or len(data_standard_ids) == 0):
            raise ValueError("Either yaml_file_path or data_standard_ids must be provided")
            
        target_count = sum(1 for x in [target_collection_id, target_team_id, target_organization] if x)
        if target_count != 1:
            raise ValueError("Exactly one of target_collection_id, target_team_id, or target_organization must be specified")
            
        mutation = gql("""
        mutation CopyDataStandards($input: CopyDataStandardsInputType!) {
            copyDataStandards(input: $input) {
                ok
                backgroundTaskId
            }
        }
        """)

        headers = {
            'Authorization': f'JWT {self.config.token}',
            'Accept': 'application/json'
        }

        csrf_token = self.session.cookies.get('csrftoken')
        if csrf_token:
            headers['X-CSRFToken'] = csrf_token

        transport = RequestsHTTPTransport(
            url=self.config.api_url,
            headers=headers,
            use_json=False  # Important for multipart form-data
        )

        client = Client(transport=transport, fetch_schema_from_transport=False)

        # Prepare input variables - only include the specified target
        input_data = {'deleteMissing': delete_missing}
        
        # Add only the specified target
        if target_collection_id is not None:
            input_data['targetTopicId'] = target_collection_id
        elif target_team_id is not None:
            input_data['targetTeamId'] = target_team_id
        elif target_organization:
            input_data['targetOrganization'] = target_organization
        
        # Remove None values
        input_data = {k: v for k, v in input_data.items() if v is not None}
        
        # Add data standard IDs if provided
        if data_standard_ids:
            input_data['dataStandardIds'] = data_standard_ids
            
        variables = {
            'input': input_data
        }
        
        # Handle file upload if yaml_file_path is provided
        if yaml_file_path:
            file_object = open(yaml_file_path, "rb")
            try:
                variables['input']['yamlFile'] = file_object
                
                result = client.execute(
                    mutation,
                    variable_values=variables,
                    upload_files=True  # Enables multipart file uploads
                )
                return result['copyDataStandards']
            finally:
                file_object.close()
        else:
            # No file upload, just execute the mutation
            result = client.execute(
                mutation,
                variable_values=variables
            )
            return result['copyDataStandards']
