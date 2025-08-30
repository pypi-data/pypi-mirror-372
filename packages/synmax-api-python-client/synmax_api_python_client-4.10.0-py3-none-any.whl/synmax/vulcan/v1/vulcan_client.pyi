from typing import Literal, Union
from synmax.openapi.client import Result
from datetime import date
class VulcanV1ApiClient:
    def health(self) -> Result:
        """Health check endpoint"""
        ...
    def underconstruction(self) -> Result:
        """Get under construction datacenters with filtering and aggregation"""
        ...
    def lng_projects(self) -> Result:
        """Get LNG projects with filtering and aggregation"""
        ...
    def metadata_history(self) -> Result:
        """Get metadata history for datacenters"""
        ...
    def project_rankings(self) -> Result:
        """Get project rankings based on various criteria"""
        ...