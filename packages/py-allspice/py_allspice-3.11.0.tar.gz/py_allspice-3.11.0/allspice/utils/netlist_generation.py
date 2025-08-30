from __future__ import annotations

import warnings
from dataclasses import dataclass
from logging import Logger
from typing import Union

from allspice.utils.core import get_all_pcb_components

from ..allspice import AllSpice
from ..apiobject import Content, Ref, Repository


@dataclass
class PcbComponent:
    designator: str
    pins: list[ComponentPin]


@dataclass
class ComponentPin:
    designator: str
    net: str


@dataclass
class NetlistEntry:
    """
    .. deprecated:: 3.10.0
    """

    net: str
    pins: list[str]

    def __post_init__(self):
        warnings.warn(
            "NetlistEntry is deprecated and will be removed in a future version.",
            DeprecationWarning,
            2,
        )


Netlist = dict[str, set[str]]
"""
Mapping of net names to sets of pin designators.
"""


def generate_netlist(
    allspice_client: AllSpice,
    repository: Repository,
    pcb_file: Union[Content, str],
    ref: Ref = "main",
) -> Netlist:
    """
    Generate a netlist for an PCB project.

    :param allspice_client: The AllSpice client to use.
    :param repository: The repository to generate the netlist for.
    :param pcbfile: The PCB document file. This can be a Content
        object returned by the AllSpice API, or a string containing the path to
        the file in the repo.
    :param ref: The ref, i.e. branch, commit or git ref from which to take the
        project files. Defaults to "main".
    :return: A list of netlist entries.
    """

    allspice_client.logger.info(f"Generating netlist for {repository.name=} on {ref=}")
    allspice_client.logger.info(f"Fetching {pcb_file=}")

    if isinstance(pcb_file, Content):
        pcb_file_path = pcb_file.path
    else:
        pcb_file_path = pcb_file

    pcb_components = _extract_all_pcb_components(
        allspice_client.logger,
        repository,
        ref,
        pcb_file_path,
    )

    return _group_netlist_entries(pcb_components)


def _extract_all_pcb_components(
    logger: Logger,
    repository: Repository,
    ref: Ref,
    pcb_file: str,
) -> list[PcbComponent]:
    """
    Extract all the components from a Pcb file in the repo.
    """

    components = []
    component_instances = get_all_pcb_components(repository, ref, pcb_file)

    for component in component_instances.values():
        if "designator" not in component:
            logger.warning(f"Component has no designator: {component.get('id')}. Skipping.")
            continue

        pins = []
        for pin in component["pads"].values():
            try:
                designator = pin["designator"]
            except KeyError:
                logger.warning(
                    f"No pad designator: pad in component {component['designator']} has no defined designator."
                )
                continue

            try:
                net = pin["net_name"]
            except KeyError:
                logger.warning(
                    f"Unconnected pad: {designator} in component {component['designator']}."
                )
                continue

            pins.append(ComponentPin(designator=designator, net=net))
        components.append(PcbComponent(designator=component["designator"], pins=pins))

    return components


def _group_netlist_entries(components: list[PcbComponent]) -> dict[str, set[str]]:
    """
    Group connected pins by the net.

    Returns:
        dict[str, set[str]]: A dictionary where the keys are net names and the
        values are sets of the designator of the pin in `component.pin` format.
    """

    netlist_entries_by_net: dict[str, set[str]] = {}

    for component in components:
        for pin in component.pins:
            if pin.net:
                netlist_entries_by_net.setdefault(pin.net, set()).add(
                    component.designator + "." + str(pin.designator)
                )
    return netlist_entries_by_net
