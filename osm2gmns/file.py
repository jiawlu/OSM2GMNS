'''
this script is adopted from esy-osm-pbf (https://pypi.org/project/esy-osm-pbf/)

esy.osm.pbf.file
================

Provides classes and functions to work with the OpenStreetMap Protocol Buffers
format. It decodes string tag maps into Python dictionaries as well as scaling
longitude and latitude coordinates.
'''

import sys, zlib, struct, itertools

from collections import namedtuple

from . import osmformat_pb2, fileformat_pb2


if sys.version_info.major >= 3:
    from itertools import accumulate
elif sys.version_info.major == 2 and sys.version_info.minor >= 7:
    # itertools.accumulate is not available in python 2.7
    import operator

    def accumulate(iterable, func=operator.add):
        'Return running totals'
        it = iter(iterable)
        total = next(it)
        yield total
        for element in it:
            total = func(total, element)
            yield total
else:
    raise RuntimeError('Unsupported python version')



def decode_strmap(primitive_block):
    '''Decodes the bytes in the stringtable of `primitive_block` to UTF-8.'''
    return tuple(s.decode('utf8') for s in primitive_block.stringtable.s)


def iter_blocks(file):
    '''Iterates tuples ``(offset, header)`` for each block in the `file`.'''
    ofs = 0
    while True:
        file.seek(ofs)
        data = file.read(4)
        if len(data) < 4:
            return
        header_size, = struct.unpack('>I', data)
        header = fileformat_pb2.BlobHeader()
        header.ParseFromString(file.read(header_size))
        ofs += 4 + header_size
        yield ofs, header
        ofs += header.datasize


def read_blob(file, ofs, header):
    '''Read and decompress a openstreetmap blob from `file`.'''
    file.seek(ofs)
    blob = fileformat_pb2.Blob()
    blob.ParseFromString(file.read(header.datasize))
    if blob.raw:
        return blob.raw
    elif blob.zlib_data:
        return zlib.decompress(blob.zlib_data)
    else:
        raise ValueError('lzma blob not supported')


def parse_tags(strmap, keys_vals):
    '''
    Parse tags from the key/value tuples `keys_vals` and strings from
    `strmap` into a dictionary.
    '''
    tags = {}
    is_value = False
    for idx in keys_vals:
        if idx == 0:
            yield tags
            tags = {}
        elif is_value:
            tags[key] = strmap[idx]
            is_value = False
        else:
            key = strmap[idx]
            is_value = True


def iter_nodes(block, strmap, group):
    dense = group.dense
    if not dense:
        raise ValueError('Only dense nodes are supported')
    granularity = block.granularity or 100
    lat_offset = block.lat_offset or 0
    lon_offset = block.lon_offset or 0
    coord_scale = 0.000000001
    id = lat = lon = tag_pos = 0
    for did, dlat, dlon, tags in zip(
            dense.id, dense.lat, dense.lon,
            parse_tags(strmap, dense.keys_vals)):
        id += did
        lat += coord_scale * (lat_offset + granularity * dlat)
        lon += coord_scale * (lon_offset + granularity * dlon)
        yield (id, tags, (lon, lat))


def iter_ways(block, strmap, group):
    for way in group.ways:
        tags = {
            strmap[k]: strmap[v]
            for k, v in zip(way.keys, way.vals)
        }
        refs = tuple(accumulate(way.refs))
        yield way.id, refs, tags


def iter_relations(block, strmap, group):
    namemap = {}
    for relation in group.relations:
        tags = {
            strmap[k]: strmap[v]
            for k, v in zip(relation.keys, relation.vals)
        }
        refs = tuple(accumulate(relation.memids))
        members = [
            (
                ref,
                namemap.setdefault(
                    rel_type, osmformat_pb2.Relation.MemberType.Name(rel_type)),
                strmap[sid]
            )
            for ref, rel_type, sid in zip(
                    refs, relation.types, relation.roles_sid)
        ]

        yield relation.id, members, tags


Node = namedtuple('Node', ('id', 'tags', 'lonlat'))
Node.__doc__ = '''
A OpenStreetMap `node <https://wiki.openstreetmap.org/wiki/Node>`_.
'''
Node.id.__doc__ = 'Identifier of the node.'
Node.tags.__doc__ = 'A dictonary mapping from tag names to values.'
Node.lonlat.__doc__ = 'A tuple ``(longitude, latitude)`` of coordinates.'

Way = namedtuple('Way', ('id', 'tags', 'refs'))
Way.__doc__ = '''
A OpenStreetMap `way <https://wiki.openstreetmap.org/wiki/Way>`_.
'''
Way.id.__doc__ = 'Identifier of the way.'
Way.tags.__doc__ = 'A dictonary mapping from tag names to values.'
Way.refs.__doc__ = 'A tuple of node identifiers representing this way.'

Relation = namedtuple('Relation', ('id', 'tags', 'members'))
Relation.__doc__ = '''
A OpenStreetMap `relation <https://wiki.openstreetmap.org/wiki/Relation>`_.
'''
Relation.id.__doc__ = 'Identifier of the relation.'
Relation.tags.__doc__ = 'A dictonary mapping from tag names to values.'
Relation.members.__doc__ = '''
A tuple with ``(ref, member_type, role)`` entries describing the relation.
``ref`` is an OSM entry identifier, ``member_type`` is the type of the
referenced entry (either the :class:`Node`, :class:`Way` or :class:`Relation`
type) and ``role`` is a string describing the role.
'''


def iter_primitive_block(primitive_block):
    '''
    Iterates over the entries of a OpenStreetMap primitive block.
    '''
    strmap = decode_strmap(primitive_block)
    for group in primitive_block.primitivegroup:
        for id, tags, lonlat in iter_nodes(primitive_block, strmap, group):
            yield Node(id, tags, lonlat)

        for id, refs, tags in iter_ways(primitive_block, strmap, group):
            yield Way(id, tags, refs)

        for id, members, tags in iter_relations(primitive_block, strmap, group):
            yield Relation(id, tags, members)


class Block(object):
    def __init__(self, file, ofs, header):
        self.file, self.ofs, self.header = file, ofs, header

    def __iter__(self):
        primitive_block = osmformat_pb2.PrimitiveBlock()
        primitive_block.ParseFromString(
            read_blob(self.file.file, self.ofs, self.header))
        return iter_primitive_block(primitive_block)


class File(object):
    '''
    Provides access to OpenStreetMap ``.pbf`` files.

    Iterates over entries (or :attr:`blocks`) of a ``.pbf`` file.
    '''

    def __init__(self, file):
        if isinstance(file, str):
            self.file = open(file, 'rb')
        elif isinstance(file, Path):
            self.file = file.open('rb')
        elif isinstance(file, io.IOBase):
            self.file = file
        else:
            raise ValueError('Unsupported file object {}'.format(file))

    def __enter__(self):
        return self

    def __exit__(self, exc_type=None, exc_value=None, exc_trace=None):
        if hasattr(self.file, 'close'):
            self.file.close()

    def __iter__(self):
        '''
        Iterates over all entries of a ``.pbf`` file.
        '''
        for block in self.blocks:
            yield from block

    @property
    def blocks(self):
        '''
        Iterates over all blocks in a ``.pbf`` file.
        '''
        for ofs, header in iter_blocks(self.file):
            yield Block(self, ofs, header)
