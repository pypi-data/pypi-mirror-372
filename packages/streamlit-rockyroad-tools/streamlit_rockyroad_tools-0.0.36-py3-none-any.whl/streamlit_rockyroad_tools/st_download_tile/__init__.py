import os
import streamlit.components.v1 as components
from typing import Optional, Callable, Any, List, Dict

# Create a _RELEASE constant to switch between development and production modes
_RELEASE = True

if not _RELEASE:
    _component_func = components.declare_component(
        "st_download_tile",
        url="http://localhost:3000",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend", "build")
    _component_func = components.declare_component("st_download_tile", path=build_dir)


def st_download_tile(
    title: Optional[str] = None,
    body: Optional[str] = None,
    url: Optional[str] = None,
    key: Optional[str] = None,
    on_click: Optional[Callable[..., Any]] = None,
    args: Optional[List] = None,
    kwargs: Optional[Dict] = None,
) -> Optional[dict]:
    """
    A Streamlit component that displays a simple download tile with an optional title, body, and URL.

    Parameters
    ----------
    title : str, optional
        Title displayed as an <h3> element.
    body : str, optional
        Body displayed as a <p> element. Supports HTML content.
    url : str, optional
        Optional URL associated with the download action.
    key : str, optional
        Streamlit key for the component instance.
    on_click : callable, optional
        Callback executed when the download icon or text is clicked.
    args : list, optional
        Positional args forwarded to on_click.
    kwargs : dict, optional
        Keyword args forwarded to on_click.

    Returns
    -------
    dict or None
        Returns a dictionary with 'clicked': True and a timestamp when clicked; otherwise None.
    """
    # Handle the on_click callback similar to st_navigation_tile
    if callable(on_click):
        args = args or []
        kwargs = kwargs or {}

        def create_callback(callback, *cb_args, **cb_kwargs):
            def wrapper(_=None):
                return callback(*cb_args, **cb_kwargs)
            return wrapper

        on_click = create_callback(on_click, *args, **kwargs)

    component_value = _component_func(
        title=title or "",
        body=body or "",
        url=url or "",
        key=key,
        on_change=on_click if callable(on_click) else None,
    )

    return component_value
