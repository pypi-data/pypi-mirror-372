import httpx
from altscore.common.http_errors import raise_for_status_improved, retry_on_401, retry_on_401_async
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from altscore.borrower_central.model.generics import GenericSyncResource, GenericAsyncResource, \
    GenericSyncModule, GenericAsyncModule
from altscore.borrower_central.model.deal_steps import DealStepDTO


# DTO for current step in a deal
class StepDataDTO(BaseModel):
    """Data transfer object for a step in a deal"""
    step_id: str = Field(alias="stepId")
    order: int = Field(alias="order")
    key: str = Field(alias="key")
    label: Optional[str] = Field(alias="label", default=None)
    created_at: str = Field(alias="createdAt")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


# DTO for deals
class DealDTO(BaseModel):
    """Data transfer object for deals"""
    id: str = Field(alias="id")
    external_id: Optional[str] = Field(alias="externalId", default=None)
    name: str = Field(alias="name")
    description: Optional[str] = Field(alias="description", default=None)
    status: Optional[str] = Field(alias="status", default=None)
    current_step: Optional[StepDataDTO] = Field(alias="currentStep", default=None)
    tags: List[str] = Field(alias="tags", default=[])
    risk_rating: Optional[str] = Field(alias="riskRating", default=None)
    created_at: str = Field(alias="createdAt")
    updated_at: Optional[str] = Field(alias="updatedAt", default=None)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class CreateDealRequest(BaseModel):
    """Model for creating a new deal"""
    name: str = Field(alias="name")
    description: Optional[str] = Field(alias="description", default=None)
    status: Optional[str] = Field(alias="status", default=None)
    external_id: Optional[str] = Field(alias="externalId", default=None)
    tags: List[str] = Field(alias="tags", default=[])
    risk_rating: Optional[str] = Field(alias="riskRating", default=None)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class UpdateDealRequest(BaseModel):
    """Model for updating a deal"""
    name: Optional[str] = Field(alias="name", default=None)
    description: Optional[str] = Field(alias="description", default=None)
    status: Optional[str] = Field(alias="status", default=None)
    tags: Optional[List[str]] = Field(alias="tags", default=None)
    risk_rating: Optional[str] = Field(alias="riskRating", default=None)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class ExternalIdRequest(BaseModel):
    """Model for setting an external ID"""
    external_id: str = Field(alias="externalId")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class PutCurrentStepRequest(BaseModel):
    """Model for setting the current step of a deal"""
    key: str = Field(alias="key")
    comment: Optional[str] = Field(alias="comment", default=None)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


# Resource classes for deals
class DealSync(GenericSyncResource):
    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "deals", header_builder, renew_token, DealDTO.parse_obj(data))

    @retry_on_401
    def get_current_step(self):
        """
        Get the current step for a deal
        
        Returns:
            DealStepDTO: The current step
        """
        from altscore.borrower_central.model.deal_steps import DealStepSync

        with httpx.Client(base_url=self.base_url) as client:
            response = client.get(
                f"{self.base_url}/v1/deals/{self.data.id}/steps/current",
                headers=self._header_builder()
            )
            raise_for_status_improved(response)
            return DealStepSync(
                base_url=self.base_url,
                header_builder=self._header_builder,
                renew_token=self.renew_token,
                data=response.json()
            )

    @retry_on_401
    def set_current_step(self, key: str, comment: Optional[str] = None):
        """
        Set the current step for a deal
        
        Args:
            key: The key of the step to set as current
            comment: Optional comment for the step change
            
        Returns:
            None
        """
        with httpx.Client(base_url=self.base_url) as client:
            request_data = PutCurrentStepRequest(key=key, comment=comment)
            response = client.put(
                f"{self.base_url}/v1/deals/{self.data.id}/steps/current",
                json=request_data.dict(by_alias=True, exclude_none=True),
                headers=self._header_builder()
            )
            raise_for_status_improved(response)

    @retry_on_401
    def get_steps(self):
        """
        Get all steps for this deal
        
        Returns:
            List[DealStepDTO]: List of all steps for this deal
        """
        from altscore.borrower_central.model.deal_steps import DealStepDTO

        with httpx.Client(base_url=self.base_url) as client:
            response = client.get(
                f"{self.base_url}/v1/deals/{self.data.id}/steps",
                headers=self._header_builder()
            )
            raise_for_status_improved(response)
            return [DealStepDTO.parse_obj(data) for data in response.json()]


class DealAsync(GenericAsyncResource):
    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "deals", header_builder, renew_token, DealDTO.parse_obj(data))

    @retry_on_401_async
    async def get_current_step(self):
        """
        Get the current step for a deal
        
        Returns:
            DealStepDTO: The current step
        """
        from altscore.borrower_central.model.deal_steps import DealStepAsync

        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.get(
                f"{self.base_url}/v1/deals/{self.data.id}/steps/current",
                headers=self._header_builder()
            )
            raise_for_status_improved(response)
            return DealStepAsync(
                base_url=self.base_url,
                header_builder=self._header_builder,
                renew_token=self.renew_token,
                data=response.json()
            )

    @retry_on_401_async
    async def set_current_step(self, key: str, comment: Optional[str] = None):
        """
        Set the current step for a deal
        
        Args:
            key: The key of the step to set as current
            comment: Optional comment for the step change
            
        Returns:
            None
        """
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            request_data = PutCurrentStepRequest(key=key, comment=comment)
            response = await client.put(
                f"{self.base_url}/v1/deals/{self.data.id}/steps/current",
                json=request_data.dict(by_alias=True, exclude_none=True),
                headers=self._header_builder()
            )
            raise_for_status_improved(response)

    @retry_on_401_async
    async def get_steps(self):
        """
        Get all steps for this deal
        
        Returns:
            List[DealStepDTO]: List of all steps for this deal
        """
        from altscore.borrower_central.model.deal_steps import DealStepDTO

        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.get(
                f"{self.base_url}/v1/deals/{self.data.id}/steps",
                headers=self._header_builder()
            )
            raise_for_status_improved(response)
            return [DealStepDTO.parse_obj(data) for data in response.json()]


# Module for deals - synchronous
class DealsSyncModule(GenericSyncModule):
    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         sync_resource=DealSync,
                         retrieve_data_model=DealDTO,
                         create_data_model=CreateDealRequest,
                         update_data_model=UpdateDealRequest,
                         resource="deals")

    @retry_on_401
    def set_external_id(self, deal_id: str, external_id: str):
        """
        Set an external ID for a deal
        
        Args:
            deal_id: The ID of the deal
            external_id: The external ID to set
            
        Returns:
            None
        """
        request_data = ExternalIdRequest(externalId=external_id)

        with httpx.Client(base_url=self.altscore_client._borrower_central_base_url) as client:
            response = client.put(
                f"/v1/deals/{deal_id}/external-id",
                json=request_data.dict(by_alias=True, exclude_none=True),
                headers=self.build_headers(),
                timeout=120,
            )
            raise_for_status_improved(response)
            return None

    @retry_on_401
    def query_by_borrower_id(self, borrower_id: str, page: int = 1, per_page: int = 10):
        """
        Find deals by borrower ID
        
        Args:
            borrower_id: The ID of the borrower to filter by
            page: Page number for pagination
            per_page: Number of results per page
            
        Returns:
            Dict with deals and pagination info
        """
        with httpx.Client(base_url=self.altscore_client._borrower_central_base_url) as client:
            response = client.get(
                f"/v1/deals",
                params={
                    "borrower-id": borrower_id,
                    "page": page,
                    "per-page": per_page
                },
                headers=self.build_headers(),
                timeout=120,
            )
            raise_for_status_improved(response)
            return response.json()

    @retry_on_401
    def query_by_status(self, status: str, page: int = 1, per_page: int = 10):
        """
        Find deals by status
        
        Args:
            status: The status to filter by
            page: Page number for pagination
            per_page: Number of results per page
            
        Returns:
            Dict with deals and pagination info
        """
        with httpx.Client(base_url=self.altscore_client._borrower_central_base_url) as client:
            response = client.get(
                f"/v1/deals",
                params={
                    "status": status,
                    "page": page,
                    "per-page": per_page
                },
                headers=self.build_headers(),
                timeout=120,
            )
            raise_for_status_improved(response)
            return response.json()


# Module for deals - asynchronous
class DealsAsyncModule(GenericAsyncModule):
    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         async_resource=DealAsync,
                         retrieve_data_model=DealDTO,
                         create_data_model=CreateDealRequest,
                         update_data_model=UpdateDealRequest,
                         resource="deals")

    @retry_on_401_async
    async def set_external_id(self, deal_id: str, external_id: str):
        """
        Set an external ID for a deal
        
        Args:
            deal_id: The ID of the deal
            external_id: The external ID to set
            
        Returns:
            None
        """
        request_data = ExternalIdRequest(externalId=external_id)

        async with httpx.AsyncClient(base_url=self.altscore_client._borrower_central_base_url) as client:
            response = await client.put(
                f"/v1/deals/{deal_id}/external-id",
                json=request_data.dict(by_alias=True, exclude_none=True),
                headers=self.build_headers(),
                timeout=120,
            )
            await raise_for_status_improved(response)
            return None

    @retry_on_401_async
    async def query_by_borrower_id(self, borrower_id: str, page: int = 1, per_page: int = 10):
        """
        Find deals by borrower ID
        
        Args:
            borrower_id: The ID of the borrower to filter by
            page: Page number for pagination
            per_page: Number of results per page
            
        Returns:
            Dict with deals and pagination info
        """
        async with httpx.AsyncClient(base_url=self.altscore_client._borrower_central_base_url) as client:
            response = await client.get(
                f"/v1/deals",
                params={
                    "borrower-id": borrower_id,
                    "page": page,
                    "per-page": per_page
                },
                headers=self.build_headers(),
                timeout=120,
            )
            await raise_for_status_improved(response)
            return response.json()

    @retry_on_401_async
    async def query_by_status(self, status: str, page: int = 1, per_page: int = 10):
        """
        Find deals by status
        
        Args:
            status: The status to filter by
            page: Page number for pagination
            per_page: Number of results per page
            
        Returns:
            Dict with deals and pagination info
        """
        async with httpx.AsyncClient(base_url=self.altscore_client._borrower_central_base_url) as client:
            response = await client.get(
                f"/v1/deals",
                params={
                    "status": status,
                    "page": page,
                    "per-page": per_page
                },
                headers=self.build_headers(),
                timeout=120,
            )
            await raise_for_status_improved(response)
            return response.json()
