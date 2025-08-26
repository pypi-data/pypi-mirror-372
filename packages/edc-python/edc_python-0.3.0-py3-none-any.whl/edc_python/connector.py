from __future__ import annotations
from typing import Dict, Any, List
import json
from pathlib import Path
from edc_python.rest_tools import RestConnector
from edc_python.config import ConnectorConfig, parse_config
from edc_python.common import IdGen
# from rest_tools import RestConfig, RestConnector
# from catalog import Catalog

class Connector(RestConnector):

    @staticmethod
    def create_connector_from_config_file(config_file_path: Path) -> Connector:
        """
        :return: A connector object initialized with the given config file.
        """
        if not config_file_path.exists():
            raise RuntimeError(f"Config file '{config_file_path}' does not exist.")
        
        connector_config = parse_config(config_file_path, ConnectorConfig)
        return Connector(connector_config)

    def __init__(self, config: ConnectorConfig) -> None:
        super().__init__(config)

    def get_business_partner_number(self) -> str:
        return self._config.bpn
    
    def get_dsp_url(self) -> str:
        return self._config.dsp_url    


    # ---------- Provider ----------

    def create_asset(self,
        asset_id: str,
        asset_url: str
    ) -> None:
        """
        POST to the EDC asset-creation endpoint.
        """
        body = {
            "@context": {
                "@vocab": "https://w3id.org/edc/v0.0.1/ns/",
                "cx-common": "https://w3id.org/catenax/ontology/common#",
                "cx-taxo": "https://w3id.org/catenax/taxonomy#",
                "dct": "http://purl.org/dc/terms/"
            },
            "@type": "Asset",
            "@id": asset_id,
            "properties": {"description": "informative description"},
            "dataAddress": {
                "@type": "DataAddress",
                "type": "HttpData",
                "baseUrl": asset_url,
                "proxyQueryParams": "true",
                "proxyPath": "true",
                "proxyMethod": "true",
                "proxyBody": "true"
            },
        }

        if not self._config.header_api_key:
            raise RuntimeError("Provider config does not specify API key.")

        response = self._session.post(
            f"{self._config.management_url}/assets",
            headers={"x-api-key": self._config.header_api_key, "Content-Type": "application/json"},
            json=body,
        )
        if response.status_code != 200:
            text = response.text
            raise RuntimeError(
                f"Asset creation failed with status {response.status_code}: {text}"
            )


    def get_asset_by_id(self, asset_id: str) -> Dict:
        """
        GET an already created asset by its ID.
        """
        header_dict = {
            "x-api-key": self._config.header_api_key,
            "Content-Type": "application/json"
        }
        response = self._session.get(f"{self._config.management_url}/assets/{asset_id}", headers=header_dict)
        if response.status_code != 200:
            raise RuntimeError(f"Unable to get asset with id {asset_id}, status {response.status}: {response.text}")
        return response.json()
    

    def get_all_assets(self,
        offset: int = 0,
        limit: int = 50
    ) -> List:
        """
        Retrieves all created assets by posting a queryspec body to the assets request endpoint.
        """
        body = {
            "@context": {
                "@vocab": "https://w3id.org/edc/v0.0.1/ns/"
            },
            "@type": "QuerySpec",
            "offset": offset,
            "limit": limit,
            "sortOrder": "DESC",
            "sortField": "fieldName",
            "filterExpression": []
        }

        if not self._config.header_api_key:
            raise RuntimeError("Provider config does not specify API key.")
        
        response = self._session.post(
            f"{self._config.management_url}/assets/request",
            headers={"x-api-key": self._config.header_api_key, "Content-Type": "application/json"},
            json=body
        )
        if response.status_code != 200:
            text = response.text
            raise RuntimeError(
                f"Getting all assets failed with status {response.status_code}: {text}"
            )
        
        return response.json()
    

    def create_usage_policy(self,
        asset_id: str
    ) -> None:
        """
        POST to the EDC usage-policy endpoint.
        """
        body = {
            "@context": [
                "https://w3id.org/tractusx/edc/v0.0.1",
                "http://www.w3.org/ns/odrl.jsonld",
                {"@vocab": "https://w3id.org/edc/v0.0.1/ns/"},
            ],
            "@type": "PolicyDefinition",
            "@id": IdGen.gen_usage_policy_id(asset_id),
            "policy": {"@type": "Set"},
        }
        if not self._config.header_api_key:
            raise RuntimeError("Provider config does not specify API key.")

        response = self._session.post(
            f"{self._config.management_url}/policydefinitions",
            headers={"x-api-key": self._config.header_api_key, "Content-Type": "application/json"},
            json=body,
        )
        if response.status_code != 200:
            text = response.text
            raise RuntimeError(
                f"Usage policy creation failed with status {response.status_code}: {text}"
            )


    def create_access_policy(self,
        asset_id: str,
        consumer_connector: Connector
    ) -> None:
        """
        POST to the EDC access-policy endpoint.
        """
        body = {
            "@context": [
                "https://w3id.org/tractusx/edc/v0.0.1",
                "http://www.w3.org/ns/odrl.jsonld",
                {"@vocab": "https://w3id.org/edc/v0.0.1/ns/"},
            ],
            "@type": "PolicyDefinition",
            "@id": IdGen.gen_access_policy_id(asset_id),
            "policy": {
                "@type": "Set",
                "permission": [
                    {
                        "action": "use",
                        "constraint": {
                            "leftOperand": "BusinessPartnerNumber",
                            "operator": "eq",
                            "rightOperand": consumer_connector.get_business_partner_number(),
                        },
                    }
                ],
            },
        }
        if not self._config.header_api_key:
            raise RuntimeError("Provider config does not specify API key.")

        response = self._session.post(
            f"{self._config.management_url}/policydefinitions",
            headers={"x-api-key": self._config.header_api_key, "Content-Type": "application/json"},
            json=body,
        )
        if response.status_code != 200:
            text = response.text
            raise RuntimeError(
                f"Access policy creation failed with status {response.status_code}: {text}"
            )
        
    
    def get_policy_by_id(self, policy_id: str) -> Dict:
        """
        GET an already created policy by asset ID.
        """
        header_dict = {
            "x-api-key": self._config.header_api_key,
            "Content-Type": "application/json"
        }
        response = self._session.get(f"{self._config.management_url}/policydefinitions/{policy_id}", headers=header_dict)
        if response.status_code != 200:
            raise RuntimeError(f"Unable to get policy with id {policy_id}, status {response.status_code}: {response.text}")
        return response.json()


    def get_all_policies(self,
        offset: int = 0,
        limit: int = 50
    ) -> Dict:
        """
        POST to get all already created policies.
        """
        header_dict = {
            "x-api-key": self._config.header_api_key,
            "Content-Type": "application/json"
        }
        body_dict = {
            "@context": {
                "@vocab": "https://w3id.org/edc/v0.0.1/ns/"
            },
            "@type": "QuerySpec",
            "offset": offset,
            "limit": limit,
            "filterExpression": []
        }
        response = self._session.post(f"{self._config.management_url}/policydefinitions/request", headers=header_dict, json=body_dict)
        if response.status_code != 200:
            raise RuntimeError(f"Unable to get policies by QuerySpec, status {response.status_code}: {response.text}")
        return response.json()


    def create_contract(self,
        asset_id: str
    ) -> None:
        """
        POST to the EDC contract-definition endpoint.
        """
        body = {
            "@context": {},
            "@id": IdGen.gen_contract_id(asset_id),
            "@type": "ContractDefinition",
            "accessPolicyId": IdGen.gen_usage_policy_id(asset_id),
            "contractPolicyId": IdGen.gen_access_policy_id(asset_id),
            "assetsSelector": {
                "@type": "CriterionDto",
                "operandLeft": "https://w3id.org/edc/v0.0.1/ns/id",
                "operator": "=",
                "operandRight": asset_id,
            },
        }

        if not self._config.header_api_key:
            raise RuntimeError("Provider config does not specify API key.")

        response = self._session.post(
            f"{self._config.management_url}/contractdefinitions",
            headers={"x-api-key": self._config.header_api_key, "Content-Type": "application/json"},
            json=body,
        )
        if response.status_code != 200:
            text = response.text
            raise RuntimeError(
                f"Contract creation failed with status {response.status_code}: {text}"
            )
    

    def get_contract_by_id(self, contract_id: str) -> Dict:
        """
        GET an already created contract by its ID.
        """
        header_dict = {
            "x-api-key": self._config.header_api_key,
            "Content-Type": "application/json"
        }
        response = self._session.get(f"{self._config.management_url}/contractdefinitions/{contract_id}", headers=header_dict)
        if response.status_code != 200:
            raise RuntimeError(f"Unable to get contract with id {contract_id}, status {response.status_code}: {response.text}")
        return response.json()
    

    def get_all_contracts(self,
        offset: int = 0,
        limit: int = 50
    ) -> Dict:
        """
        POST to get all already created contract definitions.
        """
        header_dict = {
            "x-api-key": self._config.header_api_key,
            "Content-Type": "application/json"
        }
        body_dict = {
            "@context": {
                "@vocab": "https://w3id.org/edc/v0.0.1/ns/"
            },
            "@type": "QuerySpec",
            "offset": offset,
            "limit": limit,
            "filterExpression": []
        }
        response = self._session.post(f"{self._config.management_url}/contractdefinitions/request", headers=header_dict, json=body_dict)
        if response.status_code != 200:
            raise RuntimeError(f"Unable to get contract definitions by QuerySpec, status {response.status_code}: {response.text}")
        return response.json()
    

    # ---------- Consumer ----------

    def query_catalog(self,
        provider_connector: Connector,
        offset: int = 0,
        limit: int = 50
    ) -> List:
        """
        POST to the EDC catalog-request endpoint to retrieve all assets provided for the consumer.
        """
        body: Dict[str, Any] = {
            "@context": {"@vocab": "https://w3id.org/edc/v0.0.1/ns/"},
            "@type": "CatalogRequest",
            "protocol": "dataspace-protocol-http",
            "counterPartyAddress": provider_connector.get_dsp_url(),
            "counterPartyId": provider_connector.get_business_partner_number(),
            "querySpec": {"offset": offset, "limit": limit},
        }
        if not self._config.header_api_key:
            raise RuntimeError("consumer config does not specify API key")

        response = self._session.post(
            f"{self._config.management_url}/catalog/request",
            headers={"x-api-key": self._config.header_api_key, "Content-Type": "application/json"},
            json=body
        )

        if response.status_code != 200:
            text = response.text
            raise RuntimeError(f"catalog request failed [{response.status_code}]: {text}")
        resp_json = response.json()

        return resp_json.get("dcat:dataset", [])


    def read_policy_id_from_catalog(self,
        provider_connector: Connector,
        asset_id: str,
        offset: int = 0,
        limit: int = 50
    ) -> str:
        """
        POST to the EDC catalog-request endpoint to retrieve the offer/policy ID for the given asset.
        """
        # body: Dict[str, Any] = {
        #     "@context": {"@vocab": "https://w3id.org/edc/v0.0.1/ns/"},
        #     "protocol": "dataspace-protocol-http",
        #     "counterPartyAddress": provider_connector.get_dsp_url(),
        #     "counterPartyId": provider_connector.get_business_partner_number(),
        #     "querySpec": {"offset": 0, "limit": 50},
        # }

        # if not self._config.header_api_key:
        #     raise RuntimeError("consumer config does not specify API key")

        # response = self._session.post(
        #     f"{self._config.management_url}/catalog/request",
        #     headers={"x-api-key": self._config.header_api_key, "Content-Type": "application/json"},
        #     json=body
        # )
        # if response.status_code != 200:
        #     text = response.text
        #     raise RuntimeError(f"catalog request failed [{response.status_code}]: {text}")
        # resp_json = response.json()

        dataset = self.query_catalog(provider_connector, offset, limit)

        # Find the offer ID for our asset
        for entry in dataset:  # resp_json.get("dataset", []):
            if entry.get("id") == asset_id:
                policy = entry.get("odrl:hasPolicy", {})
                if not policy:
                    raise RuntimeError(f"No odrl:hasPolicy attribute for asset id '{asset_id}' found in catalog")
                policy_type = policy.get("@type")
                if not policy_type == "odrl:Offer":
                    raise RuntimeError(f"Policy is not of type offer for asset id '{asset_id}' found in catalog")
                offer_id = policy.get("@id")
                if offer_id:
                    return offer_id
        raise RuntimeError(f"No policy for asset id '{asset_id}' found in catalog")


    def negotiate_edr(self,
        offer_id: str,
        asset_id: str,
        provider_connector: Connector
    ) -> None:
        """
        POST to the EDC edrs endpoint to negotiate a contract (EDR).
        """
        body: Dict[str, Any] = {
            "@context": [
                "https://w3id.org/tractusx/policy/v1.0.0",
                "http://www.w3.org/ns/odrl.jsonld",
                {"@vocab": "https://w3id.org/edc/v0.0.1/ns/", "tx": "https://w3id.org/tractusx/v0.0.1/ns/"},
            ],
            "@type": "ContractRequest",
            "counterPartyAddress": provider_connector.get_dsp_url(),
            "protocol": "dataspace-protocol-http",
            "policy": {
                "@id": offer_id,
                "@type": "Offer",
                "assigner": provider_connector.get_business_partner_number(),
                "permission": [
                    {
                        "action": "use",
                        "constraint": {
                            "leftOperand": "tx:BusinessPartnerNumber",
                            "operator": "eq",
                            "rightOperand": self._config.bpn,
                        },
                    }
                ],
                "prohibition": [],
                "obligation": [],
                "target": asset_id,
            },
            "callbackAddresses": [],
        }

        if not self._config.header_api_key:
            raise RuntimeError("consumer config does not specify API key")

        response = self._session.post(
            f"{self._config.management_url}/edrs",
            headers={"x-api-key": self._config.header_api_key, "Content-Type": "application/json"},
            json=body
        )
        if response.status_code != 200:
            text = response.text
            raise RuntimeError(f"EDR negotiation failed [{response.status_code}]: {text}")


    def request_edr(self,
        asset_id: str
    ) -> str:
        """
        POST to the EDC edrs/request endpoint to initiate the transfer and get a transfer ID.
        """
        body: Dict[str, Any] = {
            "@context": {"@vocab": "https://w3id.org/edc/v0.0.1/ns/"},
            "@type": "QuerySpec",
            "filterExpression": [
                {"operandLeft": "assetId", "operator": "=", "operandRight": asset_id}
            ],
            "limit": 50,
            "offset": 0,
        }

        if not self._config.header_api_key:
            raise RuntimeError("consumer config does not specify API key")

        response = self._session.post(
            f"{self._config.management_url}/edrs/request",
            headers={"x-api-key": self._config.header_api_key, "Content-Type": "application/json"},
            json=body
        )
        if response.status_code != 200:
            text = response.text
            raise RuntimeError(f"EDR request failed [{response.status_code}]: {text}")
        resp_json = response.json()

        # Find the transfer id for our asset
        for edr in resp_json:
            if edr.get("assetId") == asset_id:
                transfer_id = edr.get("transferProcessId")
                if transfer_id:
                    return transfer_id
        raise RuntimeError(f"No transfer id found for asset '{asset_id}' in EDR response")


    def read_edr_details(self,
        transfer_id: str
    ) -> Dict:
        """
        GET to the EDC edr-read endpoint to retrieve the AssetAccess details.
        """
        if not self._config.header_api_key:
            raise RuntimeError("consumer config does not specify API key")

        response = self._session.get(
            f"{self._config.management_url}/edrs/{transfer_id}/dataaddress",
            headers={"x-api-key": self._config.header_api_key, "Content-Type": "application/json"}
        )
        if response.status_code != 200:
            text = response.text
            raise RuntimeError(f"EDR read failed [{response.status_code}]: {text}")
        data = response.json()

        return {
            "asset_url": data.get("endpoint"),
            "auth_token": data.get("authorization")
        }
    