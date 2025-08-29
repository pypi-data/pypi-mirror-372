from typing import Dict, Optional, List


class CreateSessionParams:
    """
    Parameters for creating a new session in the AGB cloud environment.

    Attributes:
        labels (Optional[Dict[str, str]]): Custom labels for the Session. These can be
            used for organizing and filtering sessions.
        image_id (Optional[str]): ID of the image to use for the session.
    """

    def __init__(
        self,
        labels: Optional[Dict[str, str]] = None,
        image_id: Optional[str] = None,
    ):
        """
        Initialize CreateSessionParams.

        Args:
            labels (Optional[Dict[str, str]], optional): Custom labels for the Session.
                Defaults to None.
            image_id (Optional[str]): ID of the image to use for the session.
                Defaults to None.
        """
        self.labels = labels or {}
        self.image_id = image_id


class ListSessionParams:
    """
    Parameters for listing sessions with filtering support.

    Attributes:
        labels (Dict[str, str]): Labels to filter by.
    """

    def __init__(
        self,
        labels: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize ListSessionParams.

        Args:
            labels (Optional[Dict[str, str]], optional): Labels to filter by.
                Defaults to None.
        """
        self.labels = labels if labels is not None else {}