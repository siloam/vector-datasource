from collections import namedtuple
from shapely.geometry import Point
from tilequeue.tile import reproject_lnglat_to_mercator


Feature = namedtuple('Feature', 'fid shape properties')


# simple utility wrapper to generate a Feature at a point. note that the
# position is expected to be in (lon, lat) coordinates.
def point(id, position, tags):
    x, y = reproject_lnglat_to_mercator(*position)
    return Feature(id, Point(x, y), tags)


# utility wrapper to generate a Feature from a lat/lon shape.
def way(id, shape, tags):
    from shapely.ops import transform
    merc_shape = transform(reproject_lnglat_to_mercator, shape)
    return Feature(id, merc_shape, tags)


# the fixture code expects "raw" relations as if they come straight from
# osm2pgsql. the structure is a little cumbersome, so this utility function
# constructs it from a more readable function call.
def relation(id, tags, nodes=None, ways=None, relations=None):
    nodes = nodes or []
    ways = ways or []
    relations = relations or []
    way_off = len(nodes)
    rel_off = way_off + len(ways)
    tags_as_list = []
    for k, v in tags.items():
        tags_as_list.extend((k, v))
    return dict(
        id=id, tags=tags_as_list, way_off=way_off, rel_off=rel_off,
        parts=(nodes + ways + relations))


def tile_diagonal(z, x, y):
    """
    Returns a Shapely LineString which goes from the lower left of the tile
    to the upper right.
    """

    from tilequeue.tile import coord_to_bounds
    from shapely.geometry import LineString
    from ModestMaps.Core import Coordinate

    bounds = coord_to_bounds(Coordinate(zoom=z, column=x, row=y))
    shape = LineString([
        [bounds[0], bounds[1]],
        [bounds[2], bounds[3]],
    ])

    return shape


def tile_box(z, x, y):
    """
    Returns a Shapely Polygon which covers the tile.
    """

    from tilequeue.tile import coord_to_bounds
    from shapely.geometry import box
    from ModestMaps.Core import Coordinate

    bounds = coord_to_bounds(Coordinate(zoom=z, column=x, row=y))
    return box(*bounds)
