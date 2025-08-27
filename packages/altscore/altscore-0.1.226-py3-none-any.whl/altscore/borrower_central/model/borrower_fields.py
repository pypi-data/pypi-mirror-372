import httpx
from altscore.common.http_errors import raise_for_status_improved, retry_on_401, retry_on_401_async
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from altscore.borrower_central.model.generics import GenericSyncResource, GenericAsyncResource, \
    GenericSyncModule, GenericAsyncModule
import datetime as dt

class HistoricValue(BaseModel):
    reference_id: str = Field(alias="referenceId")  # this is the id an identifier for the source of the value
    value: Any = Field(alias="value")
    updated_at: str = Field(alias="updatedAt")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class BorrowerFieldAPIDTO(BaseModel):
    id: str = Field(alias="id")
    borrower_id: str = Field(alias="borrowerId")
    key: str = Field(alias="key")
    label: str = Field(alias="label")
    value: Any = Field(alias="value")
    data_type: str = Field(alias="dataType")
    history: List[HistoricValue] = Field(alias="history")
    tags: List[str] = Field(alias="tags", default=[])
    created_at: str = Field(alias="createdAt")
    updated_at: Optional[str] = Field(alias="updatedAt")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class CreateBorrowerFieldDTO(BaseModel):
    borrower_id: str = Field(alias="borrowerId")
    form_id: Optional[str] = Field(alias="formId", default=None)
    reference_id: Optional[str] = Field(alias="referenceId", default=None)
    key: str = Field(alias="key")
    value: Any = Field(alias="value")
    data_type: Optional[str] = Field(alias="dataType", default=None)
    tags: List[str] = Field(alias="tags", default=[])
    updated_at: Optional[dt.datetime] = Field(alias="updatedAt", default=None)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True

    def dict(self, *args, **kwargs):
        base_dict = super().dict(*args, **kwargs)
        date_key = 'updatedAt' if kwargs.get("by_alias") else 'updated_at'
        base_dict[date_key] = self.updated_at.isoformat() if self.updated_at else None
        return base_dict


class UpdateBorrowerFieldDTO(BaseModel):
    borrower_id: str = Field(alias="borrowerId")
    form_id: Optional[str] = Field(alias="formId", default=None)
    reference_id: Optional[str] = Field(alias="referenceId", default=None)
    value: Optional[str] = Field(alias="value")
    data_type: Optional[str] = Field(alias="dataType", default=None)
    tags: List[str] = Field(alias="tags", default=[])
    updated_at: Optional[dt.datetime] = Field(alias="updatedAt", default=None)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True

    def dict(self, *args, **kwargs):
        base_dict = super().dict(*args, **kwargs)
        date_key = 'updatedAt' if kwargs.get("by_alias") else 'updated_at'
        base_dict[date_key] = self.updated_at.isoformat() if self.updated_at else None
        return base_dict


class BorrowerFieldSync(GenericSyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "borrower-fields", header_builder, renew_token, BorrowerFieldAPIDTO.parse_obj(data))


class BorrowerFieldAsync(GenericAsyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "borrower-fields", header_builder, renew_token, BorrowerFieldAPIDTO.parse_obj(data))


class BorrowerFieldsSyncModule(GenericSyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         sync_resource=BorrowerFieldSync,
                         retrieve_data_model=BorrowerFieldAPIDTO,
                         create_data_model=CreateBorrowerFieldDTO,
                         update_data_model=UpdateBorrowerFieldDTO,
                         resource="borrower-fields")

    @retry_on_401
    def find_by_key(self, key: str, borrower_id: str):
        with httpx.Client(base_url=self.altscore_client._borrower_central_base_url) as client:
            fields_found_req = client.get(
                f"/v1/borrower-fields",
                params={
                    "key": key,
                    "borrower-id": borrower_id,
                    "per-page": 1,
                    "page": 1
                },
                headers=self.build_headers(),
                timeout=120,
            )
            raise_for_status_improved(fields_found_req)
            fields_found_data = fields_found_req.json()
            if len(fields_found_data) == 0:
                return None
            else:
                return self.retrieve(fields_found_data[0]["id"])

    def count_distinct_values(self, key: str):
        with httpx.Client(base_url=self.altscore_client._borrower_central_base_url) as client:
            unique_values_req = client.get(
                f"/v1/borrower-fields/queries/count-distinct-values",
                params={
                    "key": key
                },
                headers=self.build_headers(),
                timeout=120
            )
            raise_for_status_improved(unique_values_req)
            return unique_values_req.json()

    def bulk_update_field_values(self, key: str, current_value: str, target_value: str):
        with httpx.Client(base_url=self.altscore_client._borrower_central_base_url) as client:
            response = client.post(
                f"/v1/borrower-fields/commands/bulk-update-values",
                json={
                    "key": key,
                    "currentValue": current_value,
                    "targetValue": target_value
                },
                headers=self.build_headers(),
                timeout=120
            )
            raise_for_status_improved(response)
            return

    @retry_on_401
    def bulk_update_by_borrower_ids(self, borrower_ids: List[str], key: str, new_value: Any, reference_id: Optional[str] = None):
        with httpx.Client(base_url=self.altscore_client._borrower_central_base_url) as client:
            payload = {
                "borrowerIds": borrower_ids,
                "key": key,
                "newValue": new_value
            }
            if reference_id is not None:
                payload["referenceId"] = reference_id
                
            response = client.post(
                f"/v1/borrower-fields/commands/bulk-update-by-borrower-ids",
                json=payload,
                headers=self.build_headers(),
                timeout=120
            )
            raise_for_status_improved(response)
            return

class BorrowerFieldsAsyncModule(GenericAsyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         async_resource=BorrowerFieldAsync,
                         retrieve_data_model=BorrowerFieldAPIDTO,
                         create_data_model=CreateBorrowerFieldDTO,
                         update_data_model=UpdateBorrowerFieldDTO,
                         resource="borrower-fields")

    @retry_on_401_async
    async def find_by_key(self, key: str, borrower_id: str):
        async with httpx.AsyncClient(base_url=self.altscore_client._borrower_central_base_url) as client:
            fields_found_req = await client.get(
                f"/v1/borrower-fields",
                params={
                    "key": key,
                    "borrower-id": borrower_id,
                    "per-page": 1,
                    "page": 1
                },
                headers=self.build_headers(),
                timeout=120,
            )
            raise_for_status_improved(fields_found_req)
            fields_found_data = fields_found_req.json()
            if len(fields_found_data) == 0:
                return None
            else:
                return self.retrieve(fields_found_data[0]["id"])


    async def count_distinct_values(self, key: str):
        async with httpx.AsyncClient(base_url=self.altscore_client._borrower_central_base_url) as client:
            unique_values_req = await client.get(
                f"/v1/borrower-fields/queries/count-distinct-values",
                params={
                    "key": key
                },
                headers=self.build_headers(),
                timeout=120
            )
            raise_for_status_improved(unique_values_req)
            return unique_values_req.json()


    async def bulk_update_field_values(self, key: str, current_value: str, target_value: str):
        async with httpx.AsyncClient(base_url=self.altscore_client._borrower_central_base_url) as client:
            response = await client.post(
                f"/v1/borrower-fields/commands/bulk-update-values",
                json={
                    "key": key,
                    "currentValue": current_value,
                    "targetValue": target_value
                },
                headers=self.build_headers(),
                timeout=120
            )
            raise_for_status_improved(response)
            return

    @retry_on_401_async
    async def bulk_update_by_borrower_ids(self, borrower_ids: List[str], key: str, new_value: Any, reference_id: Optional[str] = None):
        async with httpx.AsyncClient(base_url=self.altscore_client._borrower_central_base_url) as client:
            payload = {
                "borrowerIds": borrower_ids,
                "key": key,
                "newValue": new_value
            }
            if reference_id is not None:
                payload["referenceId"] = reference_id
                
            response = await client.post(
                f"/v1/borrower-fields/commands/bulk-update-by-borrower-ids",
                json=payload,
                headers=self.build_headers(),
                timeout=120
            )
            raise_for_status_improved(response)
            return
