CONST_USAGE_POLICY_AFFIX = "-usage-policy"
CONST_ACCESS_POLICY_AFFIX = "-access-policy"
CONST_CONTRACT_AFFIX = "-contract"

class IdGen:

    @staticmethod
    def gen_usage_policy_id(asset_id: str) -> str:
        return f"{asset_id}-usage-policy"
    
    @staticmethod
    def gen_access_policy_id(asset_id: str) -> str:
        return f"{asset_id}-access-policy"
    
    @staticmethod
    def gen_contract_id(asset_id: str) -> str:
        return f"{asset_id}-contract"
    
    @staticmethod
    def extract_asset_id(composed_id: str) -> str:
        """
        An id composed by any of the generation methods here will be reverted to the asset id.
        """
        return composed_id.replace(CONST_USAGE_POLICY_AFFIX, "").replace(CONST_ACCESS_POLICY_AFFIX, "").replace(CONST_CONTRACT_AFFIX, "")