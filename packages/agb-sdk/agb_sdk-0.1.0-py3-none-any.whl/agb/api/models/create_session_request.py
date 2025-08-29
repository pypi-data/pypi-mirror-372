from typing import Optional, Union, List, Dict, Any


class CreateSessionRequest:
    """Request object for creating a session"""

    def __init__(
        self,
        authorization: str = "",
        image_id: str = "",
        session_id: str = "",
        external_user_id: Optional[str] = None,
        labels: Optional[Union[str, List[str]]] = None,
        persistence_data_list: Optional[List[Dict[str, Any]]] = None,
        object_field_data: Optional[Dict[str, Any]] = None
    ):
        self.authorization = authorization
        self.image_id = image_id
        self.session_id = session_id
        self.external_user_id = external_user_id
        self.labels = labels
        self.persistence_data_list = persistence_data_list
        self.object_field_data = object_field_data

    def get_body(self) -> Dict[str, Any]:
        """Convert request object to dictionary format"""
        body = {}

        if self.session_id:
            body["sessionId"] = self.session_id

        if self.external_user_id:
            body["externalUserId"] = self.external_user_id

        if self.labels:
            # If labels is a list, convert to comma-separated string
            if isinstance(self.labels, list):
                body["labels"] = ",".join(self.labels)
            else:
                body["labels"] = self.labels

        if self.persistence_data_list:
            body["persistenceDataList"] = self.persistence_data_list

        if self.object_field_data:
            body["objectFieldData"] = self.object_field_data

        return body


    def get_params(self) -> Dict[str, Any]:
        """Get query parameters"""
        params = {}
        if self.image_id:
            params["imageId"] = self.image_id
        return params
