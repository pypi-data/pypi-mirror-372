from pydantic import BaseModel
from typing import Optional
from flask import url_for


class Link(BaseModel):
    rel: str
    type: str
    title: Optional[str] = None
    href: str


def make_link(rel: str, route: str, title: Optional[str] = None, type: str = "application/json", **args):
    kwargs = {"title": title} if title else {}  # do not pass none title, to know if it has been set or not
    return Link(rel=rel, type=type, href=url_for(route, **args, _external=True), **kwargs)
