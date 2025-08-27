"""
Stlin - Streamlit Lineage Component

A Streamlit component for rendering data lineage from Cognite Data Fusion.
"""

import os
import hashlib
import json
from typing import Optional, Dict, Any, List, Union
import streamlit.components.v1 as components

# Create a _component_func which will call the frontend component.
_component_func = components.declare_component(
    "stlin",
    path=os.path.join(os.path.dirname(__file__), "frontend", "build"),
)


def render_lineage(
    data: List[Dict[str, Any]],
    focus_mode: bool = True,
    side_bar_width: Optional[int] = 300,
    height: Optional[int] = 800,
    key: Optional[str] = None,
) -> Union[List[Dict[str, Any]], None]:
    """
    Render a data lineage diagram with interactive selection capabilities.

    Parameters
    ----------
    data : list
        List of transformation dictionaries containing lineage information.
        Each transformation should have:
        - externalId: unique identifier
        - name: display name
        - sources: list of source object identifiers
        - destinations: list of destination object identifiers
        - Additional fields like query, lastFinishedJob, etc.
    focus_mode : bool, default True
        Whether to show only the direct lineage path (focus mode) or full graph.
        When True, only shows nodes in the propagation chain of selected node.
    side_bar_width : int, default 300
        Initial width of the navigation sidebar in pixels. Users can resize it.
    height : int, default 800
        Height of the component in pixels.
    key : str, optional
        Unique component key. If not provided, a key will be automatically generated
        based on a hash of the data content to ensure re-rendering when data changes.

    Returns
    -------
    list or None
        - For transformation nodes: returns the transformation record
        - For data object nodes: returns all transformations that have this node
          in their sources or destinations
        - Returns empty list if nothing is selected

    Examples
    --------
    >>> import streamlit as st
    >>> from stlin import render_lineage
    >>> import json
    >>>
    >>> # Load lineage data
    >>> with open("lineage_data.json", "r") as f:
    ...     lineage_data = json.load(f)
    >>>
    >>> # Render lineage and get selected data
    >>> selected_data = render_lineage(
    ...     data=lineage_data,
    ...     focus_mode=True,
    ...     side_bar_width=300,
    ...     height=800
    ... )
    >>>
    >>> if selected_data:
    ...     st.write(f"Selected: {selected_data}")
    """

    # Generate a unique key based on data hash if no key is provided
    if key is None:
        try:
            # Create a hash of the data content
            data_str = json.dumps(data, sort_keys=True, default=str)
            data_hash = hashlib.md5(data_str.encode()).hexdigest()[:8]
            key = f"lineage_{data_hash}"
        except (TypeError, ValueError):
            # Fallback to a simple key if hashing fails
            key = "lineage_default"

    component_value = _component_func(
        data=data,
        focus_mode=focus_mode,
        side_bar_width=side_bar_width,
        height=height,
        key=key,
        default=[],
    )

    return component_value


# Make render_lineage available at package level
__all__ = ["render_lineage"]
