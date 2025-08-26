from __future__ import annotations

from dataclasses import dataclass
from configargparse import ArgumentParser

from edc_python.common import Util


@dataclass(frozen=True)
class ConnectorConfig:
    public_url: str = ""
    management_url_path: str = ""
    api_version: str = ""
    dsp_url: str = ""
    header_api_key: str = ""
    bpn: str = ""

    @property
    def management_url(self) -> str:
        return Util.add_url_path(Util.add_url_path(self.public_url, self.management_url_path), self.api_version)

    def __contains__(self, key):
        return key in self.__dict__

    @staticmethod
    def add_args(p: ArgumentParser):
        p.add_argument("--public_url", env_var="PUBLIC_URL", type=str, help="The connectors public *endpoint url.")
        p.add_argument("--management_url_path", env_var="MANAGEMENT_URL_PATH", type=str, help="The url path to the management endpoint without api version.")
        p.add_argument("--api_version", env_var="API_VERSION", type=str, help="The EDC api version as part of the full management url.")
        p.add_argument("--dsp_url", env_var="DSP_URL", type=str, help="The connectors dataspace protocol url.")
        p.add_argument("--header_api_key", env_var="HEADER_API_KEY", type=str, help="The the x-api-key you have to put in the header of the rest call.")
        p.add_argument("--bpn", env_var="BPN", type=str, help="The connector's business partner number.")
