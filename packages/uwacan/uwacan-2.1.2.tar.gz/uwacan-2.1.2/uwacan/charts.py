# ruff: noqa
import struct
import numpy as np
from pathlib import Path

from . import positional


class OESUfileError(RuntimeError): ...


class OESUrecord:
    @classmethod
    def from_record_data(cls, record_type, record_data):
        match record_type:
            case 1:
                return HeaderSencVersion(record_data)
            case 2:
                return HeaderName(record_data)
            case 3:
                return HeaderPublishDate(record_data)
            case 4:
                return HeaderEdition(record_data)
            case 5:
                return HeaderUpdateDate(record_data)
            case 6:
                return HeaderUpdate(record_data)
            case 7:
                return HeaderNativeScale(record_data)
            case 8:
                return HeaderSencCreateDate(record_data)
            case 9:
                return HeaderSoundingDatum(record_data)
            case 98:
                return OESUrecord("CELL_COVR_RECORD")
            case 99:
                return OESUrecord("CELL_NOCOVR_RECORD")
            case 100:
                return CellExtent(record_data)
            case 101:
                return OESUrecord("CELL_TXTDSC_INFO_FILE_RECORD")
            case 200:
                return ServerStatus(record_data)
            case 64:
                return FeatureIdRecord(record_data)
            case 65:
                return FeatureAttributeRecord(record_data)
            case 80:
                return FeatureGeometryPoint(record_data)
            case 81:
                return FeatureGeometryLine(record_data)
            case 82:
                return FeatureGeometryArea(record_data)
            case 83:
                return FeatureGeometryMultipoint(record_data)
            case 84:
                return OESUrecord("FEATURE_GEOMETRY_RECORD_AREA_EXT")
            case 85:
                return OESUrecord("VECTOR_EDGE_NODE_TABLE_EXT_RECORD")
            case 86:
                return OESUrecord("VECTOR_CONNECTED_NODE_TABLE_EXT_RECORD")
            case 96:
                return VectorEdgeNodeTable(record_data)
            case 97:
                return VectorConnectedNodeTable(record_data)
            case _:
                raise OESUfileError(f"Unknown OESU record type {record_type}")
                # return None

    def __init__(self, record_type_name):
        self.record_type_name = record_type_name

    def __repr__(self):
        return f"Uninplemented OESU record type {self.record_type_name}"


# class Header(OESUrecord):
#     __slots__ = ('record_type', 'record_size')
#     unpacker = struct.Struct('=HI')

#     def __init__(self, data):
#         self.record_type, self.record_size = self.unpacker.unpack(data)

#     def __str__(self):
#         return f'RecordHeader: record type {self.record_type}, {self.record_size} bytes'


class OESUHeader(OESUrecord): ...


class OESUGeometry(OESUrecord): ...


class HeaderSencVersion(OESUHeader):
    __slots__ = ("version",)
    unpacker = struct.Struct("=H")

    def __init__(self, data):
        (self.version,) = self.unpacker.unpack(data)

    def __repr__(self):
        return f"HeaderSencVersion: {self.version}"


class HeaderName(OESUHeader):
    __slots__ = ("name",)

    def __init__(self, data):
        self.name = data.decode()

    def __repr__(self):
        return f"HeaderName: {self.name}"


class HeaderPublishDate(OESUHeader):
    __slots__ = ("date",)

    def __init__(self, data):
        self.date = data.decode()

    def __repr__(self):
        return f"HeaderPublishDate: {self.date}"


class HeaderEdition(OESUHeader):
    __slots__ = ("edition",)
    unpacker = struct.Struct("=H")

    def __init__(self, data):
        (self.edition,) = self.unpacker.unpack(data)

    def __repr__(self):
        return f"HeaderEdition: {self.edition}"


class HeaderUpdateDate(OESUHeader):
    __slots__ = ("date",)

    def __init__(self, data):
        self.date = data.decode()

    def __repr__(self):
        return f"HeaderUpdateDate: {self.date}"


class HeaderUpdate(OESUHeader):
    __slots__ = ("update",)
    unpacker = struct.Struct("=H")

    def __init__(self, data):
        (self.update,) = self.unpacker.unpack(data)

    def __repr__(self):
        return f"HeaderUpdate: {self.update}"


class HeaderNativeScale(OESUHeader):
    __slots__ = ("scale",)
    unpacker = struct.Struct("=I")

    def __init__(self, data):
        (self.scale,) = self.unpacker.unpack(data)

    def __repr__(self):
        return f"HeaderNativeScale: {self.scale}"


class HeaderSencCreateDate(OESUHeader):
    __slots__ = ("date",)

    def __init__(self, data):
        self.date = data.decode()

    def __repr__(self):
        return f"HeaderSencCreateDate: {self.date}"


class HeaderSoundingDatum(OESUHeader):
    __slots__ = ("datum",)

    def __init__(self, data):
        self.datum = data.decode()

    def __repr__(self):
        return f"HeaderSoundingDatum: {self.datum}"


class CellExtent(OESUHeader):
    __slots__ = (
        "sw_lat",
        "sw_lon",
        "nw_lat",
        "nw_lon",
        "ne_lat",
        "ne_lon",
        "se_lat",
        "se_lon",
    )
    unpacker = struct.Struct("=dddddddd")

    def __init__(self, data):
        (
            self.sw_lat,
            self.sw_lon,
            self.nw_lat,
            self.nw_lon,
            self.ne_lat,
            self.ne_lon,
            self.se_lat,
            self.se_lon,
        ) = self.unpacker.unpack(data)

    def __repr__(self):
        return f"CellExtent: SW: {self.sw_lat, self.sw_lon}, NW: {self.nw_lat, self.nw_lon},  NE: {self.ne_lat, self.ne_lon}, SE: {self.se_lat, self.se_lon}"


class FeatureIdRecord(OESUrecord):
    __slots__ = ("type_code", "id", "primitive")
    unpacker = struct.Struct("=HHB")

    def __init__(self, data):
        self.type_code, self.id, self.primitive = self.unpacker.unpack(data)

    def __repr__(self):
        return f"FeatureID: type code {self.type_code}, id {self.id}, primitive {self.primitive}"


class FeatureAttributeRecord(OESUrecord):
    __slots__ = ("type_code", "value_type", "value")
    unpacker = struct.Struct("=HB")
    int_unpacker = struct.Struct("=I")
    float_unpacker = struct.Struct("=d")

    def __init__(self, data):
        desc, value = data[:3], data[3:]
        self.type_code, self.value_type = self.unpacker.unpack(desc)
        if self.value_type == 0:
            (self.value,) = self.int_unpacker.unpack(value)
        elif self.value_type == 2:
            (self.value,) = self.float_unpacker.unpack(value)
        elif self.value_type == 4:
            self.value = value.decode()
        else:
            raise NotImplementedError(f"Value type `{self.value_type}` not implemented")

    def __repr__(self):
        return f"FeatureAttributeRecord: type = {self.type_code}, value = {self.value}"


class FeatureGeometryPoint(OESUGeometry):
    __slots__ = ("latitude", "longitude")
    unpacker = struct.Struct("=dd")

    def __init__(self, data):
        self.latitude, self.longitude = self.unpacker.unpack(data)

    def __repr__(self):
        return f"FeatureGeometryPoint: ({self.latitude}, {self.longitude})"


class LineElement(OESUGeometry):
    __slots__ = (
        "start_connected_node",
        "edge_vector",
        "end_connected_node",
        "reversed",
    )
    unpacker = struct.Struct("=iiii")

    def __init__(self, data):
        (
            self.start_connected_node,
            self.edge_vector,
            self.end_connected_node,
            self.reversed,
        ) = self.unpacker.unpack(data)

    def __repr__(self):
        return f"LineElement: start node {self.start_connected_node}, end node {self.end_connecded_node}, edge vector {self.edge_vector}, reversed {self.reversed}"


class FeatureGeometryLine(OESUGeometry):
    __slots__ = (
        "extent_south",
        "extent_north",
        "extent_west",
        "extent_east",
        "n_lines",
        "line_elements",
    )
    unpacker = struct.Struct("=ddddI")

    def __init__(self, data):
        desc, payload = data[: self.unpacker.size], data[self.unpacker.size :]
        (
            self.extent_south,
            self.extent_north,
            self.extent_west,
            self.extent_east,
            self.n_lines,
        ) = self.unpacker.unpack(desc)

        self.line_elements = [
            LineElement(payload[idx : idx + LineElement.unpacker.size])
            for idx in range(0, self.n_lines * LineElement.unpacker.size, LineElement.unpacker.size)
        ]

    def __repr__(self):
        return f"FeatureGeometryLine: ({self.extent_south} S, {self.extent_north} N, {self.extent_west} W, {self.extent_east} E)"


class FeatureGeometryArea(OESUGeometry):
    __slots__ = (
        "extent_south",
        "extent_north",
        "extent_west",
        "extent_east",
        "n_contours",
        "n_triprim",
        "n_edges",
        "line_elements",
    )
    unpacker = struct.Struct("=ddddIII")

    def __init__(self, data):
        desc, payload = data[: self.unpacker.size], data[self.unpacker.size :]
        (
            self.extent_south,
            self.extent_north,
            self.extent_west,
            self.extent_east,
            self.n_contours,
            self.n_triprim,
            self.n_edges,
        ) = self.unpacker.unpack(desc)

        idx = 4 * self.n_contours
        for idx_vert in range(self.n_triprim):
            # payload[idx]  # some uint8, don't know what it means
            idx += 1
            (n_verts,) = struct.unpack("=I", payload[idx : idx + 4])
            idx += 4
            # coords = struct.unpack('=dddd', payload[idx:idx+32])
            idx += 32
            # verts = struct.unpack('=' + n_verts * 'ff', payload[idx:idx + n_verts * 8])
            idx += n_verts * 8

        self.line_elements = []
        for idx_line in range(self.n_edges):
            # self.line_elements.append(self.line_unpacker.unpack(payload[idx:idx + self.line_unpacker.size]))
            self.line_elements.append(LineElement(payload[idx : idx + LineElement.unpacker.size]))
            idx += LineElement.unpacker.size

        assert idx == len(payload)

    def __repr__(self):
        return f"FeatureGeometryArea: ({self.extent_south} S, {self.extent_north} N, {self.extent_west} W, {self.extent_east} E)"


class FeatureGeometryMultipoint(OESUGeometry):
    __slots__ = (
        "extent_south",
        "extent_north",
        "extent_west",
        "extent_east",
        "n_points",
        "points",
    )
    unpacker = struct.Struct("=ddddI")

    def __init__(self, data):
        desc, payload = data[: self.unpacker.size], data[self.unpacker.size :]
        (
            self.extent_south,
            self.extent_north,
            self.extent_west,
            self.extent_east,
            self.n_points,
        ) = self.unpacker.unpack(desc)

        self.points = np.frombuffer(
            payload,
            dtype=[
                ("easting", "float32"),
                ("northing", "float32"),
                ("depth", "float32"),
            ],
        )

    def __repr__(self):
        return f"FeatureGeometryMultipoint: ({self.extent_south} S, {self.extent_north} N, {self.extent_west} W, {self.extent_east} E), {self.n_points} points."


class VectorEdgeNodeTable(OESUrecord):
    def __init__(self, data):  # , reference_latitude, reference_longitude):
        (num_edges,) = struct.unpack("=i", data[:4])
        idx = 4
        self._edges = {}
        # TODO: use position classes
        for n_idx in range(num_edges):
            feature_idx, n_points = struct.unpack("=ii", data[idx : idx + 8])
            points = np.frombuffer(
                data[idx + 8 : idx + 8 + n_points * 8],
                dtype=[("easting", "float32"), ("northing", "float32")],
            )
            # lat, lon = positional.local_mercator_to_wgs84(
            #     easting=points['easting'],
            #     northing=points['northing'],
            #     reference_latitude=reference_latitude,
            #     reference_longitude=reference_longitude,
            # )
            # points = np.stack([lat, lon], axis=1).view([('latitude', 'float32'), ('longitude', 'float32')]).squeeze()
            self._edges[feature_idx] = points
            idx += 8 + n_points * 8

    def convert_to_wgs84(self, reference_latitude, reference_longitude):
        for feature_idx, mercator in self._edges.items():
            lat, lon = positional.local_mercator_to_wgs84(
                easting=mercator["easting"],
                northing=mercator["northing"],
                reference_latitude=reference_latitude,
                reference_longitude=reference_longitude,
            )
            coordinates = (
                np.stack([lat, lon], axis=1).view([("latitude", "float32"), ("longitude", "float32")]).squeeze()
            )
            self._edges[feature_idx] = coordinates

    def __getitem__(self, idx):
        return self._edges[idx]

    def __repr__(self):
        return f"VectorEdgeNodeTable: {len(self._edges)} edges"


class VectorConnectedNodeTable(OESUrecord):
    def __init__(self, data):  # , reference_latitude, reference_longitude):
        (num_nodes,) = struct.unpack("=i", data[:4])
        unpacked_data = np.frombuffer(
            data[4:],
            dtype=[
                ("feature_idx", "int32"),
                ("easting", "float32"),
                ("northing", "float32"),
            ],
        )
        self._nodes = unpacked_data[["easting", "northing"]]
        # TODO: use position classes
        # lat, lon = positional.local_mercator_to_wgs84(
        #         easting=unpacked_data['easting'],
        #         northing=unpacked_data['northing'],
        #         reference_latitude=reference_latitude,
        #         reference_longitude=reference_longitude,
        #     )
        # self._nodes = np.stack([lat, lon], axis=1).view([('latitude', 'float32'), ('longitude', 'float32')]).squeeze()
        self._feature_indices = dict(zip(unpacked_data["feature_idx"], np.arange(num_nodes)))

    def convert_to_wgs84(self, reference_latitude, reference_longitude):
        lat, lon = positional.local_mercator_to_wgs84(
            easting=self._nodes["easting"],
            northing=self._nodes["northing"],
            reference_latitude=reference_latitude,
            reference_longitude=reference_longitude,
        )
        self._nodes = np.stack([lat, lon], axis=1).view([("latitude", "float32"), ("longitude", "float32")]).squeeze()

    def __getitem__(self, idx):
        return self._nodes[self._feature_indices[idx]]

    def __repr__(self):
        return f"VectorConnectedNodeTable: {len(self._nodes)} nodes"

    # old implementation of the node table, storing each (east, north) in a dict
    # idx = 4
    # self.nodes = {}
    # for n_idx in range(self.n_nodes):
    #     # this is probably faster with numpy frombuffer, if i have understood the data layout correctly
    #     feature_idx, northing, easting = struct.unpack('=iff', data[idx:idx+12])
    #     self.nodes[feature_idx] = (northing, easting)
    #     idx += 12

    # def __getitem__(self, idx):
    # return self.nodes[idx]


class ServerStatus(OESUHeader):
    __slots__ = (
        "server_status",
        "decrypt_status",
        "expire_status",
        "expire_days_remaining",
        "grace_days_allowed",
        "grace_days_remaining",
    )
    unpacker = struct.Struct("=HHHHHH")

    def __init__(self, data):
        (
            self.server_status,
            self.decrypt_status,
            self.expire_status,
            self.expire_days_remaining,
            self.grace_days_allowed,
            self.grace_days_remaining,
        ) = self.unpacker.unpack(data)

    def __repr__(self):
        return "ServerStatus"


class S57Feature:
    _type_codes = {
        1: "Administration area (Named)",
        2: "Airport / airfield",
        3: "Anchor berth",
        4: "Anchorage area",
        5: "Beacon, cardinal",
        6: "Beacon, isolated danger",
        7: "Beacon, lateral",
        8: "Beacon, safe water",
        9: "Beacon, special purpose/general",
        10: "Berth",
        11: "Bridge",
        12: "Building, single",
        13: "Built-up area",
        14: "Buoy, cardinal",
        15: "Buoy, installation",
        16: "Buoy, isolated danger",
        17: "Buoy, lateral",
        18: "Buoy, safe water",
        19: "Buoy, special purpose/general",
        20: "Cable area",
        21: "Cable, overhead",
        22: "Cable, submarine",
        23: "Canal",
        25: "Cargo transshipment area",
        26: "Causeway",
        27: "Caution area",
        28: "Checkpoint",
        29: "Coastguard station",
        30: "Coastline",
        31: "Contiguous zone",
        32: "Continental shelf area",
        33: "Control point",
        34: "Conveyor",
        35: "Crane",
        36: "Current - non - gravitational",
        37: "Custom zone",
        38: "Dam",
        39: "Daymark",
        40: "Deep water route centerline",
        41: "Deep water route part",
        42: "Depth area",
        43: "Depth contour",
        44: "Distance mark",
        45: "Dock area",
        46: "Dredged area",
        47: "Dry dock",
        48: "Dumping ground",
        49: "Dyke",
        50: "Exclusive Economic Zone",
        51: "Fairway",
        52: "Fence/wall",
        53: "Ferry route",
        54: "Fishery zone",
        55: "Fishing facility",
        56: "Fishing ground",
        57: "Floating dock",
        58: "Fog signal",
        59: "Fortified structure",
        60: "Free port area",
        61: "Gate",
        62: "Gridiron",
        63: "Harbour area (administrative)",
        64: "Harbour facility",
        65: "Hulk",
        66: "Ice area",
        67: "Incineration area",
        68: "Inshore traffic zone",
        69: "Lake",
        71: "Land area",
        72: "Land elevation",
        73: "Land region",
        74: "Landmark",
        75: "Light",
        76: "Light float",
        77: "Light vessel",
        78: "Local magnetic anomaly",
        79: "Lock basin",
        80: "Log pond",
        81: "Magnetic variation",
        82: "Marine farm/culture",
        83: "Military practice area",
        84: "Mooring/warping facility",
        85: "Navigation line",
        86: "Obstruction",
        87: "Offshore platform",
        88: "Offshore production area",
        89: "Oil barrier",
        90: "Pile",
        91: "Pilot boarding place",
        92: "Pipeline area",
        93: "Pipeline, overhead",
        94: "Pipeline, submarine/on land",
        95: "Pontoon",
        96: "Precautionary area",
        97: "Production / storage area",
        98: "Pylon/bridge support",
        99: "Radar line",
        100: "Radar range",
        101: "Radar reflector",
        102: "Radar station",
        103: "Radar transponder beacon",
        104: "Radio calling-in point",
        105: "Radio station",
        106: "Railway",
        107: "Rapids",
        108: "Recommended route centerline",
        109: "Recommended track",
        110: "Recommended Traffic Lane Part",
        111: "Rescue station",
        112: "Restricted area",
        113: "Retro-reflector",
        114: "River",
        116: "Road",
        117: "Runway",
        118: "Sand waves",
        119: "Sea area / named water area",
        120: "Sea-plane landing area",
        121: "Seabed area",
        122: "Shoreline Construction",
        123: "Signal station, traffic",
        124: "Signal station, warning",
        125: "Silo / tank",
        126: "Slope topline",
        127: "Sloping ground",
        128: "Small craft facility",
        129: "Sounding",
        130: "Spring",
        132: "Straight territorial sea baseline",
        133: "Submarine transit lane",
        134: "Swept Area",
        135: "Territorial sea area",
        136: "Tidal stream - harmonic prediction",
        137: "Tidal stream - non-harmonic prediction",
        138: "Tidal stream panel data",
        139: "Tidal stream - time series",
        140: "Tide - harmonic prediction",
        141: "Tide - non-harmonic prediction",
        142: "Tidal stream - time series",
        143: "Tideway",
        144: "Top mark",
        145: "Traffic Separation Line",
        146: "Traffic Separation Scheme  Boundary",
        147: "Traffic Separation Scheme Crossing",
        148: "Traffic Separation Scheme  Lane part",
        149: "Traffic Separation Scheme  Roundabout",
        150: "Traffic Separation Zone",
        151: "Tunnel",
        152: "Two-way route  part",
        153: "Underwater rock / awash rock",
        154: "Unsurveyed area",
        155: "Vegetation",
        156: "Water turbulence",
        157: "Waterfall",
        158: "Weed/Kelp",
        159: "Wreck",
        300: "Accuracy of data",
        301: "Compilation scale of data",
        302: "Coverage",
        303: "Horizontal datum of data",
        304: "Horizontal datum shift parameters",
        305: "Nautical publication information",
        306: "Navigational system of marks",
        307: "Production information",
        308: "Quality of data",
        309: "Sounding datum",
        310: "Survey reliability",
        311: "Units of measurement of data",
        312: "Vertical datum of data",
        400: "Aggregation",
        401: "Association",
        402: "Stacked on/stacked under",
        500: "Cartographic area",
        501: "Cartographic line",
        502: "Cartographic symbol",
        503: "Compass",
        504: "Text",
    }

    # @classmethod
    # def from_record(cls, record, chart_file):
    #     match record.type_code:
    #         case 30: return CoastLine(record, chart_file)
    #         case 71:  # land area
    #             # if the geometry is a point, this is a visible rock
    #             # if the geometry is an area, this is land.
    #             # the land can sometimes be named
    #             ...
    #         case 153:  # underwater rock
    #             # underwater rocks has an attribute 187: water level effekt
    #             # if the value of that attribute is 3, this is a rock completly below the surface
    #             # if the value is 5, the rock is sometimes visible in the surface
    #             ...
    #         case _: return cls(record, chart_file)

    @classmethod
    def from_record(cls, feature_id, geometry, attributes, chart_file):
        match feature_id.type_code:
            case 30:
                record = CoastLine(feature_id, chart_file)
            case 43:
                record = DepthContour(feature_id, chart_file)
            case 71:
                if isinstance(geometry, FeatureGeometryPoint):
                    record = VisibleRock(feature_id, chart_file)
                else:
                    record = LandArea(feature_id, chart_file)
            case 129:
                record = Sounding(feature_id, chart_file)
            case 153:
                for attr in attributes:
                    if attr.type_code == 187:
                        if attr.value == 3:
                            record = UnderwaterRock(feature_id, chart_file)
                        elif attr.value == 5:
                            record = SubmergedRock(feature_id, chart_file)
                        else:
                            raise NotImplementedError("Unknown rock type")
                        break
                else:
                    raise NotImplementedError("Unknown rock type")
            case _:
                record = cls(feature_id, chart_file)
        if geometry is not None:
            record.geometry = geometry
        if attributes is not None:
            for attribute in attributes:
                record.attach_attribute(attribute)
        return record

    def __init__(self, record, chart_file):
        self.chart_file = chart_file
        self.type_code = record.type_code
        self.id = record.id
        self.primitive = record.primitive
        self.attributes = []

    @property
    def geometry(self):
        return self._geometry

    @geometry.setter
    def geometry(self, value):
        if getattr(self, "_geometry", None) is not None:
            raise ValueError("An S57 feature should have only one geometry")
        self._geometry = value

    def attach_attribute(self, record):
        attribute = S57Attribute.from_record(record, self)
        self.attributes.append(attribute)
        return attribute

    def assemble_line_geometry(self, line_elements):
        edge_nodes = self.chart_file._edge_nodes
        connected_nodes = self.chart_file._connected_nodes

        # We go through the line elements and check which other line elements they are connected to
        # If the start connected node of one element matches the end connected node of another element,
        # they are on the same segment. We build a list of segments by going through each element
        # and checking if it matches an already started segment.
        line_segments = []
        for line_element in line_elements:
            new_segment = True
            for line_segment in line_segments:
                # At the moment we assume that a single element can be part of
                # multple segments. I'm not sure that will ever happen.
                # If we can assume that each element will only be used once, we could
                # break out from the segment loop when we find the first match.
                if line_element.start_connected_node == line_segment[-1].end_connected_node:
                    line_segment.append(line_element)
                    new_segment = False
                elif line_element.end_connected_node == line_segment[0].start_connected_node:
                    line_segment.insert(0, line_element)
                    new_segment = False
            if new_segment:
                line_segments.append([line_element])

        # We have all line segments, but we need to collect their positions.
        # Each line element has a start connected node, and some also have an
        # edge vector that shold be included.
        # The end connected node will be included as the start connected node
        # in the next line element, except for the last one which we add after the element loop.

        # TODO: use position objects
        # This implementation is the original one where you get a list of list of tuple. Fast, but not very user friendly
        # lines = []
        # for line_segment in line_segments:
        #     line = []
        #     for line_element in line_segment:
        #         connected_node = connected_nodes[line_element.start_connected_node]
        #         line.append(connected_node)
        #         if line_element.edge_vector != 0:
        #             edge_vector = edge_nodes[line_element.edge_vector]
        #             if edge_vector.ndim == 0:
        #                 line.append(edge_vector.item())
        #             elif line_element.reversed:
        #                 line.extend(edge_vector[::-1])
        #             else:
        #                 line.extend(edge_vector)
        #         line.append(connected_nodes[line_element.end_connected_node])
        #     lines.append(line)
        # return lines

        # This keeps the coordinates from connected nodes and edge vectors as numpy structured arrays.
        # This seems to be reasonable fast. The output will be a list of numpy arrays.
        # These lists can then later be concatenated to something else, depending on what is needed.
        # This is probably fine on this level, since a user will not really interact with the S57 feature directly,
        # but request various features from the chart file or chart collection.
        lines = []
        for line_segment in line_segments:
            line = []
            for line_element in line_segment:
                start_node = connected_nodes[line_element.start_connected_node]
                line.append([start_node])
                if line_element.edge_vector != 0:
                    edge_vector = edge_nodes[line_element.edge_vector]
                    if edge_vector.ndim == 0:
                        edge_vector = edge_vector.reshape(1)
                    elif line_element.reversed:
                        edge_vector = edge_vector[::-1]
                    line.append(edge_vector)
                end_node = connected_nodes[line_element.end_connected_node]
                line.append([end_node])
            lines.append(np.concatenate(line))
        return lines

        # This implementation extracts the lat&lon frmo each point and stacks them
        # in numpy arrays. The two numpy arrays can then either be stacked as a
        # numpy structured array (fast-ish) or to a Line object (xarray, slow).
        # lines = []
        # for line_segment in line_segments:
        #     latitude = []
        #     longitude = []
        #     for line_element in line_segment:
        #         start_node = connected_nodes[line_element.start_connected_node]
        #         latitude.append([start_node['latitude']])
        #         longitude.append([start_node['longitude']])
        #         if line_element.edge_vector != 0:
        #             edge_vector = edge_nodes[line_element.edge_vector]
        #             if edge_vector.ndim == 0:
        #                 edge_vector = edge_vector.reshape(1)
        #             elif line_element.reversed:
        #                 edge_vector = edge_vector[::-1]
        #             latitude.append(edge_vector['latitude'])
        #             longitude.append(edge_vector['longitude'])
        #         end_node = connected_nodes[line_element.end_connected_node]
        #         latitude.append([end_node['latitude']])
        #         longitude.append([end_node['longitude']])
        #     # lines.append(positional.Line(
        #     #     latitude=np.concatenate(latitude),
        #     #     longitude=np.concatenate(longitude),
        #     # ))
        #     latitude = np.concatenate(latitude)
        #     longitude = np.concatenate(longitude)
        #     lines.append(
        #         np.stack([latitude, longitude], axis=1)
        #         .view(dtype=[('latitude', 'float32'), ('longitude', 'float32')])
        #         .squeeze()
        #     )
        # return lines

    def __repr__(self):
        if self.type_code in self._type_codes:
            return f"{self._type_codes[self.type_code]}"
        return f"Unknown S57 feature, code {self.type_code}"


class SingleLineGeometryMixin:
    @property
    def geometry(self):
        lines = self.assemble_line_geometry(self._geometry.line_elements)
        if len(lines) != 1:
            raise OESUfileError("Coast line features should have only one line")
        return lines[0]

    @geometry.setter
    def geometry(self, value):
        self._geometry = value


class CoastLine(SingleLineGeometryMixin, S57Feature): ...


class LandArea(S57Feature): ...


class UnderwaterRock(S57Feature): ...


class SubmergedRock(S57Feature): ...


class VisibleRock(S57Feature): ...


class DepthContour(SingleLineGeometryMixin, S57Feature):
    def attach_attribute(self, record):
        attribute = super().attach_attribute(record)
        if attribute.type_code == 174:
            self.depth = attribute.value


class Sounding(S57Feature): ...


class S57Attribute:
    _type_codes = {
        1: "Agency responsible for production",
        2: "Beacon shape",
        3: "Building shape",
        4: "Buoy shape",
        5: "Buried depth",
        6: "Call sign",
        7: "Category of airport/airfield",
        8: "Category of anchorage",
        9: "Category of bridge",
        10: "Category of built-up area",
        11: "Category of cable",
        12: "Category of canal",
        13: "Category of cardinal mark",
        14: "Category of checkpoint",
        15: "Category of coastline",
        16: "Category of control point",
        17: "Category of conveyor",
        18: "Category of coverage",
        19: "Category of crane",
        20: "Category of dam",
        21: "Category of distance mark",
        22: "Category of dock",
        23: "Category of dumping ground",
        24: "Category of  fence/wall",
        25: "Category of ferry",
        26: "Category of  fishing  facility",
        27: "Category of  fog signal",
        28: "Category of  fortified structure",
        29: "Category of gate",
        30: "Category of harbour facility",
        31: "Category of hulk",
        32: "Category of  ice",
        33: "Category of installation buoy",
        34: "Category of land region",
        35: "Category of landmark",
        36: "Category of lateral mark",
        37: "Category of light",
        38: "Category of marine farm/culture",
        39: "Category of military practice area",
        40: "Category of mooring/warping facility",
        41: "Category of navigation line",
        42: "Category of obstruction",
        43: "Category of offshore platform",
        44: "Category of oil barrier",
        45: "Category of pile",
        46: "Category of pilot boarding place",
        47: "Category of pipeline / pipe",
        48: "Category of production area",
        49: "Category of pylon",
        50: "Category of quality of data",
        51: "Category of radar station",
        52: "Category of radar transponder beacon",
        53: "Category of radio station",
        54: "Category of recommended track",
        55: "Category of rescue station",
        56: "Category of restricted area",
        57: "Category of road",
        58: "Category of runway",
        59: "Category of sea area",
        60: "Category of shoreline construction",
        61: "Category of signal station, traffic",
        62: "Category of signal station, warning",
        63: "Category of silo/tank",
        64: "Category of slope",
        65: "Category of small craft facility",
        66: "Category of special purpose mark",
        67: "Category of Traffic Separation Scheme",
        68: "Category of vegetation",
        69: "Category of water turbulence",
        70: "Category of weed/kelp",
        71: "Category of wreck",
        72: "Category of zone of confidence data",
        73: "Character spacing",
        74: "Character specification",
        75: "Colour",
        76: "Colour pattern",
        77: "Communication channel",
        78: "Compass size",
        79: "Compilation date",
        80: "Compilation scale",
        81: "Condition",
        82: "Conspicuous, Radar",
        83: "Conspicuous, visual",
        84: "Current velocity",
        85: "Date end",
        86: "Date start",
        87: "Depth range value 1",
        88: "Depth range value 2",
        89: "Depth units",
        90: "Elevation",
        91: "Estimated range of transmission",
        92: "Exhibition condition of light",
        93: "Exposition of sounding",
        94: "Function",
        95: "Height",
        96: "Height/length units",
        97: "Horizontal accuracy",
        98: "Horizontal clearance",
        99: "Horizontal length",
        100: "Horizontal width",
        101: "Ice factor",
        102: "Information",
        103: "Jurisdiction",
        104: "Justification - horizontal",
        105: "Justification - vertical",
        106: "Lifting capacity",
        107: "Light characteristic",
        108: "Light visibility",
        109: "Marks navigational - System of",
        110: "Multiplicity of lights",
        111: "Nationality",
        112: "Nature of construction",
        113: "Nature of surface",
        114: "Nature of surface - qualifying terms",
        115: "Notice to Mariners date",
        116: "Object name",
        117: "Orientation",
        118: "Periodic date end",
        119: "Periodic date start",
        120: "Pictorial representation",
        121: "Pilot district",
        122: "Producing country",
        123: "Product",
        124: "Publication reference",
        125: "Quality of sounding measurement",
        126: "Radar wave length",
        127: "Radius",
        128: "Recording date",
        129: "Recording indication",
        130: "Reference year for magnetic variation",
        131: "Restriction",
        132: "Scale maximum",
        133: "Scale minimum",
        134: "Scale value one",
        135: "Scale value two",
        136: "Sector limit one",
        137: "Sector limit two",
        138: "Shift parameters",
        139: "Signal frequency",
        140: "Signal generation",
        141: "Signal group",
        142: "Signal period",
        143: "Signal sequence",
        144: "Sounding accuracy",
        145: "Sounding distance - maximum",
        146: "Sounding distance - minimum",
        147: "Source date",
        148: "Source indication",
        149: "Status",
        150: "Survey authority",
        151: "Survey date - end",
        152: "Survey date - start",
        153: "Survey type",
        154: "Symbol scaling factor",
        155: "Symbolization code",
        156: "Technique of sounding measurement",
        157: "Text string",
        158: "Textual description",
        159: "Tidal stream - panel values",
        160: "Tidal stream, current - time series values",
        161: "Tide - accuracy of water level",
        162: "Tide - high and low water values",
        163: "Tide - method of tidal prediction",
        164: "Tide - time and height differences",
        165: "Tide, current - time interval of values",
        166: "Tide - time series values",
        167: "Tide - value of harmonic constituents",
        168: "Time end",
        169: "Time start",
        170: "Tint",
        171: "Topmark/daymark shape",
        172: "Traffic flow",
        173: "Value of annual change in magnetic variation",
        174: "Value of depth contour",
        175: "Value of local magnetic anomaly",
        176: "Value of magnetic variation",
        177: "Value of maximum range",
        178: "Value of nominal range",
        179: "Value of sounding",
        180: "Vertical accuracy",
        181: "Vertical clearance",
        182: "Vertical clearance, closed",
        183: "Vertical clearance, open",
        184: "Vertical clearance, safe",
        185: "Vertical datum",
        186: "Vertical length",
        187: "Water level effect",
        188: "Category of Tidal stream",
        189: "Positional accuracy units",
        300: "Information in national language",
        301: "Object name in national language",
        302: "Pilot district in national language",
        303: "Text string in national language",
        304: "Textual description in national language",
        400: "Horizontal datum",
        401: "Positional Accuracy",
        402: "Quality of position",
    }

    @classmethod
    def from_record(cls, record, feature):
        match record.type_code:
            case _:
                return cls(record, feature)

    def __init__(self, record, feature):
        self.type_code = record.type_code
        self.value = record.value
        self.feature = feature

    def __repr__(self):
        if self.type_code in self._type_codes:
            return f"{self._type_codes[self.type_code]} = {self.value}"
        return f"Unknown S57 attribute, code {self.type_code}, value {self.value}"


class OESUFile:
    _header_decoder = struct.Struct("=HI")

    def __init__(self, filepath, header_only=False, verbosity=0):
        self.filepath = filepath
        self.verbosity = verbosity
        self.parse_file(header_only=header_only)

    def _records_in_file(self):
        """Generator to parse through file and yield records"""
        with open(self.filepath, "rb") as file:
            while len(raw_header := file.read(self._header_decoder.size)) == self._header_decoder.size:
                record_type, record_size = self._header_decoder.unpack(raw_header)
                data_size = record_size - self._header_decoder.size
                if self.verbosity >= 2:
                    print(f"{record_type = }, {record_size = }")
                if data_size < 0:
                    if self.verbosity >= 1:
                        print(f"{record_type = } has total size {record_size} ({data_size} data bytes)")
                    continue
                record_data = file.read(data_size)
                record = OESUrecord.from_record_data(record_type, record_data)
                yield record

        yield False

    def _features_in_file(self, header_only=False):
        """Generator to over features in the file"""
        records = self._records_in_file()
        record = None

        while True:
            if record is None:
                # No leftover record data to handle
                record = next(records)
                if record is False:
                    # This is our break condition, we had handled all records
                    # and there is nothing left in the file
                    return

            match record:
                case None:
                    pass
                case OESUHeader():
                    yield record
                    record = None
                case FeatureIdRecord():
                    if header_only:
                        return
                    feature_id = record
                    geometry = None
                    attributes = []
                    while True:
                        record = next(records)
                        match record:
                            case None:
                                pass
                            case FeatureAttributeRecord():
                                attributes.append(record)
                            case OESUGeometry():
                                if geometry is not None:
                                    raise OESUfileError("Multiple geometries for feature")
                                geometry = record
                            case _:
                                break
                    # We've got record data that does not belong to this feature. Assemble and yield this s57 feature,
                    # but keep the `record` that we just parsed - it will be handled the next loop iteration
                    yield S57Feature.from_record(
                        feature_id=feature_id,
                        geometry=geometry,
                        attributes=attributes,
                        chart_file=self,
                    )
                case VectorEdgeNodeTable() | VectorConnectedNodeTable():
                    center = self.center
                    record.convert_to_wgs84(
                        reference_latitude=center.latitude.item(),
                        reference_longitude=center.longitude.item(),
                    )
                    yield record
                    record = None
                case OESUrecord():
                    if self.verbosity >= 1:
                        print(record)
                    record = None

            # match record_type:
            #     case 1:
            #         yield HeaderSencVersion(record_data)
            #         record_type = record_data = None
            #     case 2:
            #         yield HeaderName(record_data)
            #         record_type = record_data = None
            #     case 3:
            #         yield HeaderPublishDate(record_data)
            #         record_type = record_data = None
            #     case 4:
            #         yield HeaderEdition(record_data)
            #         record_type = record_data = None
            #     case 5:
            #         yield HeaderUpdateDate(record_data)
            #         record_type = record_data = None
            #     case 6:
            #         yield HeaderUpdate(record_data)
            #         record_type = record_data = None
            #     case 7:
            #         yield HeaderNativeScale(record_data)
            #         record_type = record_data = None
            #     case 8:
            #         yield HeaderSencCreateDate(record_data)
            #         record_type = record_data = None
            #     case 9:
            #         yield HeaderSoundingDatum(record_data)
            #         record_type = record_data = None
            #     case 98 | 99:
            #         # 98 -> CELL_COVR_RECORD
            #         # 99 -> CELL_NOCOVR_RECORD
            #         if self.verbosity >= 1:
            #             print('Coverage records not implemented')
            #     case 100:
            #         yield CellExtent(record_data)
            #         record_type = record_data = None
            #     case 101:
            #         # 101 -> CELL_TXTDSC_INFO_FILE_RECORD
            #         if self.verbosity >= 1:
            #             print('External info files not implemented')
            #     case 200:
            #         yield ServerStatus(record_data)
            #         record_type = record_data = None
            #     case 64:
            #         if header_only:
            #             return
            #         feature_id = FeatureIdRecord(record_data)
            #         geometry = None
            #         attributes = []
            #         while True:
            #             record_type, record_data = next(records)
            #             match record_type:
            #                 case 65:
            #                     attributes.append(FeatureAttributeRecord(record_data))
            #                 case 80:
            #                     if geometry is not None:
            #                         raise OESUfileError("Multiple geometries for feature")
            #                     geometry = FeatureGeometryPoint(record_data)
            #                 case 81:
            #                     if geometry is not None:
            #                         raise OESUfileError("Multiple geometries for feature")
            #                     geometry = FeatureGeometryLine(record_data)
            #                 case 82:
            #                     if geometry is not None:
            #                         raise OESUfileError("Multiple geometries for feature")
            #                     geometry = FeatureGeometryArea(record_data)
            #                 case 83:
            #                     if geometry is not None:
            #                         raise OESUfileError("Multiple geometries for feature")
            #                     geometry = FeatureGeometryMultipoint(record_data)
            #                 case 84 | 85 | 86:
            #                     # 84 -> FEATURE_GEOMETRY_RECORD_AREA_EXT
            #                     # 85 -> VECTOR_EDGE_NODE_TABLE_EXT_RECORD
            #                     # 86 -> VECTOR_CONNECTED_NODE_TABLE_EXT_RECORD
            #                     if self.verbosity >= 1:
            #                         print('External geometry not implemented')
            #                 case _:
            #                     break
            #         # We've got record data that does not belong to this feature.
            #         yield S57Feature.from_record(feature_id=feature_id, geometry=geometry, attributes=attributes, chart_file=self)
            #     case 96:
            #         center = self.center
            #         yield VectorEdgeNodeTable(record_data, reference_latitude=center.latitude.item(), reference_longitude=center.longitude.item())
            #         record_type = record_data = None
            #     case 97:
            #         yield VectorConnectedNodeTable(record_data, reference_latitude=center.latitude.item(), reference_longitude=center.longitude.item())
            #         record_type = record_data = None
            #     case _:
            #         if self.verbosity >= 1:
            #             print(f'Record type {record_type} not implemented')

        # with open(self.filepath, 'rb') as file:
        #     while len(raw_header := file.read(header_decoder.size)) == header_decoder.size:
        #         record_type, record_size = header_decoder.unpack(raw_header)
        #         data_size = record_size - header_decoder.size
        #         if self.verbosity >= 2:
        #             print(f"{record_type = }, {record_size = }")
        #         if data_size < 0:
        #             if self.verbosity >= 1:
        #                 print(f"{record_type = } has total size {record_size} ({data_size} data bytes)")
        #             continue
        #         record_data = file.read(data_size)

        #         match record_type:
        #             case 1:
        #                 yield HeaderSencVersion(record_data)
        #             case 2:
        #                 yield HeaderName(record_data)
        #             case 3:
        #                 yield HeaderPublishDate(record_data)
        #             case 4:
        #                 yield HeaderEdition(record_data)
        #             case 5:
        #                 yield HeaderUpdateDate(record_data)
        #             case 6:
        #                 yield HeaderUpdate(record_data)
        #             case 7:
        #                 yield HeaderNativeScale(record_data)
        #             case 8:
        #                 yield HeaderSencCreateDate(record_data)
        #             case 9:
        #                 yield HeaderSoundingDatum(record_data)
        #             case 98 | 99:
        #                 # 98 -> CELL_COVR_RECORD
        #                 # 99 -> CELL_NOCOVR_RECORD
        #                 if self.verbosity >= 1:
        #                     print('Coverage records not implemented')
        #             case 100:
        #                 yield CellExtent(record_data)
        #             case 101:
        #                 # 101 -> CELL_TXTDSC_INFO_FILE_RECORD
        #                 if self.verbosity >= 1:
        #                     print('External info files not implemented')
        #             case 200:
        #                 yield ServerStatus(record_data)
        #             case 64:
        #                 if header_only:
        #                     break
        #                 # We're starting to parse a new feature
        #                 # If we are already parsing a feature, it is done and we shold return it

        #                 feature_id = FeatureIdRecord(record_data)
        #                 geometry = None
        #                 attributes = []
        #             case 65:
        #                 attributes.append(FeatureAttributeRecord(record_data))
        #             case 80:
        #                 if geometry is not None:
        #                     raise OESUfileError("Multiple geometries for feature")
        #                 geometry = FeatureGeometryPoint(record_data)
        #             case 81:
        #                 if geometry is not None:
        #                     raise OESUfileError("Multiple geometries for feature")
        #                 geometry = FeatureGeometryLine(record_data)
        #             case 82:
        #                 if geometry is not None:
        #                     raise OESUfileError("Multiple geometries for feature")
        #                 geometry = FeatureGeometryArea(record_data)
        #             case 83:
        #                 if geometry is not None:
        #                     raise OESUfileError("Multiple geometries for feature")
        #                 geometry = FeatureGeometryMultipoint(record_data)

    def parse_file(self, header_only=False):
        self._header_only = header_only
        self._features = []
        self._headers = {}

        self._coastlines = []
        self._depth_contours = {}

        self._visible_rocks = []
        self._underwater_rocks = []
        self._submerged_rocks = []

        self._soundings = []

        for feature in self._features_in_file(header_only=header_only):
            match feature:
                case HeaderSencVersion():
                    self._headers["senc_version"] = feature
                case HeaderName():
                    self._headers["name"] = feature
                case HeaderPublishDate():
                    self._headers["publish_date"] = feature
                case HeaderEdition():
                    self._headers["edition"] = feature
                case HeaderUpdateDate():
                    self._headers["update_date"] = feature
                case HeaderUpdate():
                    self._headers["update"] = feature
                case HeaderNativeScale():
                    self._headers["native_scale"] = feature
                case HeaderSencCreateDate():
                    self._headers["senc_create_date"] = feature
                case HeaderSoundingDatum():
                    self._headers["sounding_datum"] = feature
                case CellExtent():
                    self._headers["extent"] = feature
                case ServerStatus():
                    self._headers["server_status"] = feature
                case VectorEdgeNodeTable():
                    self._edge_nodes = feature
                case VectorConnectedNodeTable():
                    self._connected_nodes = feature
                case CoastLine():
                    self._coastlines.append(feature)
                case DepthContour():
                    if feature.depth not in self._depth_contours:
                        self._depth_contours[feature.depth] = []
                    self._depth_contours[feature.depth].append(feature)
                case VisibleRock():
                    self._visible_rocks.append(feature)
                case SubmergedRock():
                    self._submerged_rocks.append(feature)
                case UnderwaterRock():
                    self._underwater_rocks.append(feature)
                case Sounding():
                    self._soundings.append(feature)
                case S57Feature():
                    self._features.append(feature)
                case _:
                    raise TypeError(f"Unknown feature type {type(feature).__name__}")

    # def parse_file(self, header_only=False):
    #     self._header_only = header_only
    #     header_decoder = struct.Struct('=HI')
    #     self._features = {}
    #     self._headers = {}
    #     self._coastlines = {}

    #     with open(self.filepath, 'rb') as file:
    #         while len(raw_header := file.read(header_decoder.size)) == header_decoder.size:
    #             record_type, record_size = header_decoder.unpack(raw_header)
    #             data_size = record_size - header_decoder.size
    #             if self.verbosity >= 2:
    #                 print(f"{record_type = }, {record_size = }")
    #             if data_size < 0:
    #                 if self.verbosity >= 1:
    #                     print(f"{record_type = } has total size {record_size} ({data_size} data bytes)")
    #                 continue
    #             record_data = file.read(data_size)

    #             match record_type:
    #                 case 1:
    #                     self._headers["senc_version"] = HeaderSencVersion(record_data)
    #                 case 2:
    #                     self._headers["name"] = HeaderName(record_data)
    #                 case 3:
    #                     self._headers["publish_date"] = HeaderPublishDate(record_data)
    #                 case 4:
    #                     self._headers["edition"] = HeaderEdition(record_data)
    #                 case 5:
    #                     self._headers["update_date"] = HeaderUpdateDate(record_data)
    #                 case 6:
    #                     self._headers["update"] = HeaderUpdate(record_data)
    #                 case 7:
    #                     self._headers["native_scale"] = HeaderNativeScale(record_data)
    #                 case 8:
    #                     self._headers["senc_create_date"] = HeaderSencCreateDate(record_data)
    #                 case 9:
    #                     self._headers["sounding_datum"] = HeaderSoundingDatum(record_data)
    #                 case 98 | 99:
    #                     # 98 -> CELL_COVR_RECORD
    #                     # 99 -> CELL_NOCOVR_RECORD
    #                     if self.verbosity >= 1:
    #                         print('Coverage records not implemented')
    #                 case 100:
    #                     self._headers["extent"] = CellExtent(record_data)
    #                 case 101:
    #                     # 101 -> CELL_TXTDSC_INFO_FILE_RECORD
    #                     if self.verbosity >= 1:
    #                         print('External info files not implemented')
    #                 case 200:
    #                     self._headers["server_status"] = ServerStatus(record_data)
    #                 case 64:
    #                     if header_only:
    #                         break
    #                         # TODO: we need some way to read rest of the file at a later point.
    #                         # Usecase is to first scan the headers of all chart files in a directory,
    #                         # then only read geometry and features for those that are of interest
    #                         # for a specific area.
    #                     feature_id = FeatureIdRecord(record_data)
    #                     # TODO: i think we might want to consider separating the features in reasonable categories here.
    #                     # The alternative is to go through the feature list later, but I cannot come up with a convincing
    #                     # argument to delay the split?
    #                     current_feature = S57Feature.from_record(feature_id, self)
    #                     match current_feature:
    #                         case CoastLine():
    #                             self._coastlines[current_feature.id] = current_feature
    #                         case _:
    #                             self._features[current_feature.id] = current_feature

    #                 case 65:
    #                     feature_attribute = FeatureAttributeRecord(record_data)
    #                     current_feature.attach_attribute(feature_attribute)
    #                 case 80:
    #                     geometry = FeatureGeometryPoint(record_data)
    #                     current_feature.geometry = geometry
    #                 case 81:
    #                     geometry = FeatureGeometryLine(record_data)
    #                     current_feature.geometry = geometry
    #                 case 82:
    #                     geometry = FeatureGeometryArea(record_data)
    #                     current_feature.geometry = geometry
    #                 case 83:
    #                     geometry = FeatureGeometryMultipoint(record_data)
    #                     current_feature.geometry = geometry
    #                 case 84 | 85 | 86:
    #                     # 84 -> FEATURE_GEOMETRY_RECORD_AREA_EXT
    #                     # 85 -> VECTOR_EDGE_NODE_TABLE_EXT_RECORD
    #                     # 86 -> VECTOR_CONNECTED_NODE_TABLE_EXT_RECORD
    #                     if self.verbosity >= 1:
    #                         print('External geometry not implemented')
    #                 case 96:
    #                     center = self.center
    #                     self._edge_nodes = VectorEdgeNodeTable(record_data, reference_latitude=center.latitude.item(), reference_longitude=center.longitude.item())
    #                 case 97:
    #                     self._connected_nodes = VectorConnectedNodeTable(record_data, reference_latitude=center.latitude.item(), reference_longitude=center.longitude.item())
    #                 case _:
    #                     if self.verbosity >= 1:
    #                         print(f'Record type {record_type} not implemented')

    @property
    def center(self):
        return self.bounding_box.center

    @property
    def bounding_box(self):
        try:
            extent = self._headers["extent"]
        except KeyError:
            raise OESUfileError(f"File {self.filepath} has no chart extent recorded")

        west = max(extent.sw_lon, extent.nw_lon)
        south = min(extent.se_lat, extent.sw_lat)
        east = min(extent.se_lon, extent.ne_lon)
        north = max(extent.ne_lat, extent.nw_lat)

        return positional.BoundingBox(west=west, south=south, east=east, north=north)

    @property
    def scale(self):
        try:
            scale = self._headers["native_scale"]
        except KeyError:
            raise OESUfileError(f"File {self.filepath} has no scale recorded")
        return scale.scale

    def coast_lines(self, mode="delimited line"):
        """Get the coast lines in this chart

        The output modes are:

        `'delimited line'`
            This outputs a single `Line` object with latitude and longitude properties.
            These properties are xarray objects, with a `nan` between each individual coastline.
        `'joined line'`
            This outputs a single `Line` object with latitude and longitude properties.
            These properties are xarray objects, with nothing delimiting the individual coastlines.
        `'raw'`
            This outputs a list with all coast lines in the chart file.
            Each line is a numpy structured array, with `'latutude'` and `'longitude'` fields.
        """
        if self._header_only:
            self.parse_file(header_only=False)
        return _merge_lines((feature.geometry for feature in self._coastlines), mode=mode)

    def depth_contours(self, mode="delimited line"):
        if self._header_only:
            self.parse_file(header_only=False)
        merged = {}
        for depth, contours in self._depth_contours.items():
            merged[depth] = _merge_lines((contour.geometry for contour in contours), mode=mode)
        return merged

    def soundings(self, mode="line"):
        if self._header_only:
            self.parse_file(header_only=False)
        points = [sounding.geometry.points for sounding in self._soundings]
        points = np.concatenate(points)
        if mode == "raw":
            return points
        line = positional.Line(points)
        line.depth = points["depth"]
        return line


def _merge_lines(lines, mode="delimited line"):
    if mode == "raw":
        if not isinstance(lines, list):
            lines = list(lines)
        return lines
    if mode == "delimited line":
        delimited = True
    elif mode == "joined line":
        delimited = False
    else:
        raise ValueError(f"Unknown line mode `{mode}`")

    lines = iter(lines)
    first = next(lines)
    delimiter = np.full(shape=1 if delimited else 0, fill_value=np.nan, dtype=first.dtype)
    to_merge = [first]
    for line in lines:
        to_merge.append(delimiter)
        to_merge.append(line)
    return positional.Line(np.concatenate(to_merge))


class OESUCollection:
    @classmethod
    def read_folder(cls, path, bounding_box=None, scales=None):
        path = Path(path)
        chart_files = []
        for path in path.glob("*.oesu"):
            chart_file = OESUFile(path, header_only=True)

            if bounding_box is not None:
                if not chart_file.bounding_box.overlaps(bounding_box):
                    continue

            if scales is not None:
                if chart_file.scale not in scales:
                    continue

            chart_files.append(chart_file)
        return cls(chart_files)

    def __init__(self, chart_files):
        self.chart_files = chart_files

    def coast_lines(self, mode="delimited line"):
        lines = []
        for chart in self.chart_files:
            lines.extend(chart.coast_lines(mode="raw"))
        return _merge_lines(lines, mode=mode)

    def depth_contours(self, mode="delimited line"):
        lines = {}
        for chart in self.chart_files:
            chart_lines = chart.depth_contours(mode="raw")
            for depth, line in chart_lines.items():
                if depth not in lines:
                    lines[depth] = []
                lines[depth].extend(line)
        merged = {}
        for depth, line in lines.items():
            merged[depth] = _merge_lines(line, mode=mode)
        return merged

    def soundings(self, mode="line"):
        points = [chart.soundings(mode="raw") for chart in self.chart_files]
        points = np.concatenate(points)
        if mode == "raw":
            return points
        line = positional.Line(points)
        line.depth = points["depth"]
        return line

    @property
    def bounding_box(self):
        # Initial such that comparision with the first chart selects the first chart
        west = 180
        south = 90
        east = -180
        north = -90
        for chart in self.chart_files:
            bb = chart.bounding_box
            west = min(west, bb.west)
            south = min(south, bb.south)
            east = max(east, bb.east)
            north = max(north, bb.north)
        return positional.BoundingBox(west=west, south=south, east=east, north=north)

    def plot_chart_overview(self):
        from .visualization import make_chart

        fig = make_chart(center=self.bounding_box.center, zoom=self.bounding_box.zoom_level())
        features = []
        for chart in self.chart_files:
            features.append(chart.bounding_box.to_geojson())
        layers = [
            {
                "source": {"type": "FeatureCollection", "features": features},
                "type": "fill",
                "color": "rgba(163, 22, 19, 0.5)",
            }
        ]
        fig.update_layout(mapbox_layers=layers)
        fig.add_scattermapbox(lat=[], lon=[], showlegend=False)
        return fig
