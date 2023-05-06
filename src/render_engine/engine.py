from datetime import datetime
from email import utils

from jinja2 import (
    ChoiceLoader,
    Environment,
    FileSystemLoader,
    PackageLoader,
    pass_environment,
    select_autoescape,
)

from .collection import Collection

render_engine_templates_loader = ChoiceLoader(
    [
        FileSystemLoader("templates"),
        PackageLoader("render_engine", "render_engine_templates"),
    ]
)

engine = Environment(
    loader=render_engine_templates_loader,
    autoescape=select_autoescape(["xml"]),
    lstrip_blocks=True,
    trim_blocks=True,
)


def to_pub_date(value: datetime):
    """
    Parse information from the given class object.
    """
    return utils.format_datetime(value)
engine.filters["to_pub_date"] = to_pub_date

@pass_environment
def format_datetime(env: Environment, value: str) -> str:
    """
    Parse information from the given class object.
    """
    return datetime.strftime(value, env.globals.get("DATETIME_FORMAT", "%d %b %Y %H:%M %Z"))
engine.filters["format_datetime"] = format_datetime

@pass_environment
def url_for(env: Environment, value: str, page: int=0) -> str:
    """Look for the route in the route_list and return the url for the page."""
    routes = env.globals.get("routes")
    route = value.split(".", maxsplit=1)

    if len(route) == 2 and type(route) == list:
        collection, route = route
        if collection:= routes.get(collection, None):
            for page in collection:
                if getattr(page, page._reference) == route:
                    return page.url_for()

    else: 
        route = routes.get(value)
        if isinstance(route, Collection):
            return list(route.archives)[page].url_for()
        return route.url_for()


    raise ValueError(f"{value} is not a valid route.")
engine.filters["url_for"] = url_for
