"""This module contains util methods to build or label plugins."""
from dataclasses import asdict
import json
import typing

from hansken_extraction_plugin.api.plugin_info import PluginInfo


def _plugin_info_to_labels(plugin_info: PluginInfo, api_version: str) -> typing.Dict[str, str]:
    # maps plugin_info result to labels to be set
    labels = {
        'org.hansken.plugin-info.id': str(plugin_info.id),
        'org.hansken.plugin-info.id-domain': plugin_info.id.domain,
        'org.hansken.plugin-info.id-category': plugin_info.id.category,
        'org.hansken.plugin-info.id-name': plugin_info.id.name,
        'org.hansken.plugin-info.version': str(plugin_info.version),
        'org.hansken.plugin-info.api-version': api_version,
        'org.hansken.plugin-info.description': plugin_info.description,
        'org.hansken.plugin-info.webpage': plugin_info.webpage_url,
        'org.hansken.plugin-info.matcher': plugin_info.matcher,
        # license is set required at some places, optional at others, return as empty string if not set
        'org.hansken.plugin-info.license': plugin_info.license if plugin_info.license else '',
        'org.hansken.plugin-info.maturity-level': plugin_info.maturity.name,
        'org.hansken.plugin-info.author-name': plugin_info.author.name,
        'org.hansken.plugin-info.author-organisation': plugin_info.author.organisation,
        'org.hansken.plugin-info.author-email': plugin_info.author.email,
    }

    # not optional by api, but let's prepare to make it truly optional (as it should be)
    if plugin_info.deferred_iterations:
        labels['org.hansken.plugin-info.deferred-iterations'] = str(plugin_info.deferred_iterations)

    # add optional plugin resources
    if plugin_info.resources and plugin_info.resources.maximum_cpu:
        labels['org.hansken.plugin-info.resource-max-cpu'] = str(plugin_info.resources.maximum_cpu)

    if plugin_info.resources and plugin_info.resources.maximum_memory:
        labels['org.hansken.plugin-info.resource-max-mem'] = str(plugin_info.resources.maximum_memory)

    # If transformers are defined for the plugin, add their signatures as a Docker label as well.
    # This information can be used to find available transformers without having to instantiate a Docker container.
    if plugin_info.transformers and len(plugin_info.transformers) > 0:
        labels['org.hansken.plugin-info.transformers'] = json.dumps(
            [asdict(transformer) for transformer in plugin_info.transformers]
        )

    return labels
