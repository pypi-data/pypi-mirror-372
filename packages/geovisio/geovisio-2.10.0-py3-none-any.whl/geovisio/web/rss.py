from rfeed import *
from flask import url_for
from flask_babel import gettext as _, get_locale
import datetime
from . import utils


def dbSequencesToGeoRSS(dbSequences):
    """Converts a list of sequences from database into a GeoRSS object"""

    items = []
    urlHome = utils.get_mainpage_url()

    for dbSeq in dbSequences:
        url = utils.get_viewerpage_url() + f"#focus=map&map=18/{dbSeq['y1']}/{dbSeq['x1']}"
        urlJson = url_for("stac_collections.getCollection", _external=True, collectionId=dbSeq["id"])
        urlThumb = url_for("stac_collections.getCollectionThumbnail", _external=True, collectionId=dbSeq["id"])
        desc = _(
            """Sequence "%(name)s" by "%(user)s" was captured on %(date)s.""",
            name=dbSeq["name"],
            user=dbSeq["account_name"],
            date=str(dbSeq["mints"]),
        )
        items.append(
            Item(
                title=dbSeq["name"],
                link=url,
                description=desc,
                author=dbSeq["account_name"],
                guid=Guid(urlJson),
                pubDate=dbSeq["created"],
                enclosure=Enclosure(urlThumb, "", "image/jpeg"),
                extensions=[
                    GeoRSSItem(dbSeq["x1"], dbSeq["y1"]),
                    ContentItem(
                        f"""
					<p>
						<img src="{urlThumb}" /><br />
						{desc}<br />
						<a href="{url}">{_('View on the map')}</a> - <a href="{urlJson}">{_('JSON metadata')}</a>
					</p>
				"""
                    ),
                ],
            )
        )

    return Feed(
        title=_("GeoVisio collections"),
        link=urlHome,
        description=_("List of collections from this GeoVisio server"),
        language=get_locale().language,
        lastBuildDate=datetime.datetime.now(),
        items=items,
        docs="https://cyber.harvard.edu/rss/rss.html",
        generator="GeoVisio",
        image=Image(url_for("viewer_img", _external=True, path="logo.png"), "GeoVisio logo", urlHome),
        extensions=[Content(), GeoRSS()],
    )


class Content(Extension):
    def get_namespace(self):
        return {"xmlns:content": "http://purl.org/rss/1.0/modules/content/"}


class ContentItem(Serializable):
    def __init__(self, content):
        Serializable.__init__(self)
        self.content = content

    def publish(self, handler):
        Serializable.publish(self, handler)
        self._write_element("content:encoded", self.content)


class GeoRSS(Extension):
    """GeoRSS container definition"""

    def get_namespace(self):
        return {"xmlns:georss": "http://www.georss.org/georss"}


class GeoRSSItem(Serializable):
    """GeoRSS item definition"""

    def __init__(self, x, y):
        Serializable.__init__(self)
        self.x = x
        self.y = y

    def publish(self, handler):
        Serializable.publish(self, handler)
        self._write_element("georss:point", f"{str(self.x)} {str(self.y)}")
