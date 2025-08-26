from typing import Dict
from .connector import Connector
from .common import IdGen

def provide_data(
    public_url: str,
    asset_id: str,
    provider_connector: Connector,
    consumer_connector: Connector
) -> None:
    """
    High-level entrypoint: creates the asset, usage policy, access policy, and contract.
    """
    provider_connector.create_asset(asset_id, public_url)
    provider_connector.create_usage_policy(asset_id)
    provider_connector.create_access_policy(asset_id, consumer_connector)
    provider_connector.create_contract(asset_id)


def verify_provided_data(
    asset_id: str,
    provider_connector: Connector
) -> None:
    """
    """
    # Check assets
    try:
        asset_dict = provider_connector.get_asset_by_id(asset_id)
        print(f'Asset with id {asset_id} exists.')
    except Exception as e:
        print("Unable to retrieve asset with id {asset_id}: %s", e)
    asset_list = provider_connector.get_all_assets()
    print(f'Found {len(asset_list)} assets:')
    for asset in asset_list:
        print(f' - {asset.get("@id")}')
    # Check policies
    try:
        access_policy_dict = provider_connector.get_policy_by_id(IdGen.gen_access_policy_id(asset_id))
        print(f'Access Policy for asset with id {asset_id} exists.')
    except Exception as e:
        print("Unable to retrieve acess policy for asset {asset_id}: %s", e)
    try:
        usage_policy_dict = provider_connector.get_policy_by_id(IdGen.gen_usage_policy_id(asset_id))
        print(f'Usage Policy for asset with id {asset_id} exists.')
    except Exception as e:
        print("Unable to retrieve usage policy for asset {asset_id}: %s", e)
    policy_list = provider_connector.get_all_policies()
    print(f'Found {len(policy_list)} policies:')
    for policy in policy_list:
        print(f' - {policy.get("@id")}')
    # Check contracts
    try:
        contract_dict = provider_connector.get_contract_by_id(IdGen.gen_contract_id(asset_id))
        print(f'Contract for asset with id {asset_id} exists.')
    except Exception as e:
        print("Unable to retrieve contract for asset {asset_id}: %s", e)
    contract_list = provider_connector.get_all_contracts()
    print(f'Found {len(contract_list)} contracts:')
    for contract in contract_list:
        print(f' - {contract.get("@id")}')
 

def get_asset_access(
    asset_id: str,
    provider_connector: Connector,
    consumer_connector: Connector
) -> Dict:
    """
    High-level entrypoint: queries catalogue, negotiates EDR, requests EDR, and reads access details.
    """
    offer_id = consumer_connector.read_policy_id_from_catalog(provider_connector, asset_id)
    consumer_connector.negotiate_edr(offer_id, asset_id, provider_connector)
    transfer_id = consumer_connector.request_edr(asset_id)
    access = consumer_connector.read_edr_details(transfer_id)

    return access
