"""
Template for config classes
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ConfigTemplate(BaseModel):
    """
    Template for config classes
    """

    class Config:
        """
        Configuration template
        """

        environment: str = "development"
        database: str = "sqlite"
        database_url: Optional[str] = None
        sql_alchemy_logging: bool = False
        secret_key: str = "secret_key"
        access_token_expire_minutes: int = 30
        access_token_algorithm: str = "HS256"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConfigTemplate":
        """
        Create a ConfigTemplate object from a dictionary

        Args:
            data: A dictionary containing the config data

        Returns:
            ConfigTemplate: A ConfigTemplate object
        """
        return cls.parse_obj(data)

    @classmethod
    def from_list(cls, data: List[Dict[str, Any]]) -> List["ConfigTemplate"]:
        """
        Create a list of ConfigTemplate objects from a list of dictionaries

        Args:
            data: A list of dictionaries containing the config data

        Returns:
            List[ConfigTemplate]: A list of ConfigTemplate objects
        """
        return [cls.from_dict(item) for item in data]
