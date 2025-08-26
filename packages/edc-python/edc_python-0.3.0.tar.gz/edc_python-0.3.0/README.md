# edc_python
Provides a python library that helps you handling the edc tractus x api.

With this library you can manage all your EDC connectors.
As a provider you can create assets, policies or contracts and 
as a consumer yoe can query catalogs, manage EDR's (Endpoint Data Reference) and transfer data.

# How-To

## Dokumentation
- [swaggerhub Tractus-X EDC](https://app.swaggerhub.com/apis/eclipse-tractusx-bot/tractusx-edc)

## Connector-Configs
Make a copy of the template config file [connector_config.template.yaml](src/edc_python/connector_config.template.yaml) and fill it out like this:
```yaml
public_url: https://con-entity-1.my.connector.com
management_url_path: management
api_version: v3
dsp_url: https://con-entity-1.my.connector.com/api/v1/dsp
header_api_key: api-123
bpn: BPN000001
```

## Connectors
Initialize connectors like this:
```shell
try:
    provider_connector = Connector.create_connector_from_config_file('connector_config.provider.yaml')
    consumer_connector = Connector.create_connector_from_config_file('connector_config.consumer.yaml')
except Exception as e:
    logger.error("Error initialzing connectors: %s", e)
    sys.exit(1)
```


- ![image](https://github.com/user-attachments/assets/35b4c2d7-12f6-4e2e-8132-e76c45ea685f)
