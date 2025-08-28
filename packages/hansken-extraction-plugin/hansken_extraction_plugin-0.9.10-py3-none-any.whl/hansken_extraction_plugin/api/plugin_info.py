"""This module contains all definitions to describe metadata of a plugin, a.k.a. PluginInfo."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


@dataclass(frozen=True)
class Author:
    """
    The author of an Extraction Plugin.

    This information can be retrieved by an end-user from Hansken.
    """

    name: str
    email: str
    organisation: str


class MaturityLevel(Enum):
    """This class represents the maturity level of an extraction plugin."""

    PROOF_OF_CONCEPT = 0
    READY_FOR_TEST = 1
    PRODUCTION_READY = 2


@dataclass(frozen=True)
class PluginId:
    """Identifier of a plugin, consisting of domain, category and name. Needs to be unique among all tools/plugins."""

    domain: str
    category: str
    name: str

    def __str__(self):
        return f'{self.domain}/{self.category}/{self.name}'.lower()


@dataclass(frozen=True)
class PluginResources:
    """PluginResources contains information about how many resources will be used for a plugin."""

    maximum_cpu: Optional[float] = None
    """
    CPU resources are measured in cpu units. One cpu is equivalent to 1 vCPU/Core for cloud providers and 1 hyperthread
    on bare-metal Intel processors. Also, fractional requests are allowed. A plugin that asks 0.5 CPU uses half as
    much CPU as one that asks for 1 CPU.
    """
    maximum_memory: Optional[int] = None
    """Max usable memory for a plugin, measured in megabytes."""
    maximum_workers: Optional[int] = None
    """The number of concurrent workers(i.e. traces that can be processed)."""

    def __post_init__(self):
        if self.maximum_cpu is not None and self.maximum_cpu < 0:
            raise ValueError(f'maximum_cpu cannot be < 0: {self.maximum_cpu}')
        if self.maximum_memory is not None and self.maximum_memory < 0:
            raise ValueError(f'maximum_memory cannot be < 0: {self.maximum_memory}')
        if self.maximum_workers is not None and self.maximum_workers < 0:
            raise ValueError(f'maximum_workers cannot be < 0: {self.maximum_workers}')


@dataclass(frozen=True)
class TransformerLabel:
    """
    TransformerLabel contains information about a transformer method that a plugin provides.

    It is mainly used for storing the properties (name, arguments, return type) of a transformer in PluginInfo objects.
    Unlike the Transformer class it does not contain the actual function reference to the transformer itself.
    """

    """The method name of the transformer. For example: my_method"""
    method_name: str

    """The parameters of the function where the key is the parameter name and the value is the type of the parameter."""
    parameters: Dict[str, str]

    """The return type of the parameter. See api.Transformer class for supported types."""
    return_type: str


@dataclass
class PluginInfo:
    """
    This information is used by Hansken to identify and run the plugin.

    Note that the build_plugin.py build script is used to build a plugin docker image with PluginInfo docker labels.
    """

    id: PluginId  #: a plugin's unique identifier, see PluginId
    version: str  #: version of the plugin
    description: str  #: short description of the functionality of the plugin
    author: Author  #: the plugin's author, see Author
    maturity: MaturityLevel  #: maturity level, see MaturityLevel
    matcher: str  #: this matcher selects the traces offered to the plugin
    webpage_url: str  #: plugin url
    license: Optional[str] = None  #: license of this plugin
    deferred_iterations: int = 1  #: number of deferred iterations (1 to 20), nly for deferred plugins (optional)
    resources: Optional[PluginResources] = None  #: resources to be reserved for a plugin (optional)

    """Populated dynamically in pack.plugin_info by collecting all @transformer methods. Do not assign manually."""
    transformers: List[TransformerLabel] = field(default_factory=list)

    def __post_init__(self):
        if not 1 <= self.deferred_iterations <= 20:
            raise ValueError(f'Invalid value for deferred_iterations: {self.deferred_iterations}. '
                             f'Valid values are 1 =< 20.')

    @staticmethod
    def from_dict(data: dict):
        """Create a PluginInfo object from a dictionary."""
        return PluginInfo(
            id=PluginId(domain=data['id']['domain'], category=data['id']['category'], name=data['id']['name']),
            version=data['version'],
            description=data['description'],
            author=Author(name=data['author']['name'],
                          email=data['author']['email'],
                          organisation=data['author']['organisation']),
            maturity=MaturityLevel[data['maturity'].split('.')[-1]],
            matcher=data['matcher'],
            webpage_url=data['webpage_url'],
            license=data.get('license'),
            deferred_iterations=data.get('deferred_iterations', 1),
            resources=PluginResources(
                maximum_cpu=data['resources'].get('maximum_cpu'),
                maximum_memory=data['resources'].get('maximum_memory'),
                maximum_workers=data['resources'].get('maximum_workers')
            ) if 'resources' in data else None,
            transformers=[
                TransformerLabel(
                    method_name=transformer['method_name'],
                    parameters=transformer['parameters'],
                    return_type=transformer['return_type']
                ) for transformer in data.get('transformers', [])
            ]
        )
