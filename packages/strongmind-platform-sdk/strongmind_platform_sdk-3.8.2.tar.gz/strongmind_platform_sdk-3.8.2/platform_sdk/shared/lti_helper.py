from platform_sdk.clients.mapper_client import IDMapperClient


def set_domain_lti_secrets_from_mapper(config, token, domain):
    """Get all domains and their secrets and add them to the config for LTI"""
    mapper_client = IDMapperClient({"token": token, "domain": domain})
    domains = mapper_client.get_domains()
    for domain in domains:
        if not domain.is_disabled:
            config['consumers'].update({domain.key: {'secret': domain.secret}})
