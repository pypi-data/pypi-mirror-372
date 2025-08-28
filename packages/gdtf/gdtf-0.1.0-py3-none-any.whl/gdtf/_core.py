from pathlib import Path
from typing import (Tuple, List, Union, Optional,
                    Literal, Iterable, Dict, Generic, TypeVar, Callable)
import math
from dataclasses import dataclass, field
from enum import Enum
import json


T = TypeVar('T')


class Container(Generic[T]):
    """
    an array of items with protected write-access

    this class is used for model data's read-only structures.
    """

    def __init__(self):
        self._items: List[T] = []

    def __getitem__(self, idx: Union[int, str]) -> T:
        return self._items[idx]

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)

    def find(self, predicate: Callable[[T], bool]):
        for item in self:
            if predicate(item):
                return item
        return None


class Vec:

    """
    a simple 3d vector class

    assumes left-handed axes with z-up, x-forward, y-right (as in UE5)

    assumes *meters* as unit of measurement!!
    """

    @classmethod
    def __vec_length__(cls, vector: Tuple[float, float, float]):
        return math.sqrt(vector[0]**2 + vector[1]**2 + vector[2]**2)

    @classmethod
    def __decompose_vector__(cls, vector: Tuple[float, float, float]) -> Tuple[float, Tuple[float, float, float]]:
        """
        decompose the vector into its length and direction (a unit-length vector)
        """
        length = cls.__vec_length__(vector)
        if math.isclose(length, 0., abs_tol=1e-8):
            return 0., (0., 0., 0.)

        return length, (vector[0]/length, vector[1]/length, vector[2]/length)

    def __init__(self, xyz: Tuple[float, float, float]):
        self.__co__ = xyz
        self.__length__, self.__direction__ = None, None

    @classmethod
    def create(cls, *args, **kwargs):
        """
        allows to create a vector in a variety of ways but is pretty slow
        """

        # create either positionally or with keyword args - other is not allowed
        if args and kwargs:
            raise ValueError(f'Vec must be created either with positional args or with keyword args, mixing is not allowed')

        if args:
            if len(args) == 1 and isinstance(args[0], (float, int)):
                number = float(args[0])
                return Vec((number, number, number))
            elif len(args) == 3 and all([isinstance(a, (float, int)) for a in args]):
               return Vec((float(args[0]), float(args[1]), float(args[2])))
            else:
                raise ValueError(f'Vec can be zero-initialized, initialized with one float positional arg, or with three float positional args, received {args} instead')
        elif kwargs:
            if all([type(kwargs.get(expected_key, None)) in (float, int) for expected_key in
                      {'up', 'forward', 'right'}]):
                return Vec(
                    (
                        float(kwargs['forward']),
                        float(kwargs['right']),
                        float(kwargs['up'])
                    )
                )

            else:
                raise ValueError(f'expected "up", "right", "forward" keyword arguments')
        else:
            return Vec.zero

    @property
    def x(self) -> float:
        return self.__co__[0]

    @property
    def y(self) -> float:
        return self.__co__[1]

    @property
    def z(self) -> float:
        return self.__co__[2]

    @property
    def up(self) -> float:
        return self.z

    @property
    def right(self) -> float:
        return self.y

    @property
    def forward(self) -> float:
        return self.x

    def is_uniform(self):
        """
        true if all coordinates of this vector are equal to each other (with tolerance)
        """
        return all([math.isclose(self.x, coord, abs_tol=1e-8) for coord in self])

    def __mul__(self, number_or_vector: Union[float, 'Vec']) -> 'Vec':
        if type(number_or_vector) in (float, int):
            return Vec((
                self.x * number_or_vector, self.y * number_or_vector, self.z * number_or_vector
            ))
        elif type(number_or_vector) is Vec:
            return self.cross(number_or_vector)

    def __add__(self, other: 'Vec') -> 'Vec':
        return Vec((self.x + other.x, self.y + other.y, self.z + other.z))

    def __sub__(self, other: 'Vec') -> 'Vec':
        return self + other * -1

    def __truediv__(self, number: float) -> 'Vec':
        return self * (1. / number)

    def __str__(self):
        return f'Vec({self.x}, {self.y}, {self.z})'

    def __repr__(self):
        return str(self)

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z

    def __getitem__(self, idx: int):
        if idx not in (0, 1, 2):
            raise ValueError('vector can be indexed with int in (0-2)')
        return self.__co__[idx]

    def __eq__(self, other: 'Vec'):
        if type(other) is not Vec:
            return False
        return all([math.isclose(self.__co__[idx], other.__co__[idx], abs_tol=1e-6) for idx in range(3)])

    @staticmethod
    def to_json(obj: 'Vec', **_):
        """
        if all coords of this vector are equal, the vector will be serialized as a single number, otherwise as a list
        """
        if obj.is_uniform():
            return obj.x
        else:
            return list(obj)

    @staticmethod
    def from_json(json_value, cls, **_):
        """
        the json value can be a list of floats/ints or a single float/int - in this case a vector with three equal coords will be created
        """
        if type(json_value) in (int, float):
            return Vec((json_value, json_value, json_value))
        elif isinstance(json_value, list) and len(json_value) == 3 and all([type(co) in (float, int) for co in json_value]):
            return Vec((json_value[0], json_value[1], json_value[2]))
        else:
            raise ValueError('json value should be a list of three numbers or a single number for creation of a vector')

    def cross(self, other: 'Vec') -> 'Vec':
        return Vec((
            self.y * other.z - self.z * other.y,
            - self.x * other.z + self.z * other.x,
            self.x * other.y - self.y * other.x
        ))

    def dot(self, other: 'Vec') -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z

    def is_unit_length(self):
        return math.isclose(self.length, 1., abs_tol=1e-9)

    def is_normalized(self):
        """
        an alias for 'is_unit_length'
        """
        return self.is_unit_length()

    def is_zero(self):
        return math.isclose(self.length, 0., abs_tol=1e-9)

    @property
    def length(self):
        if self.__length__ is None:
            self.__length__, self.__direction__ = self.__decompose_vector__(self.__co__)
        return self.__length__

    @property
    def norm(self) -> 'Vec':
        if self.__length__ is None:
            self.__length__, self.__direction__ = self.__decompose_vector__(self.__co__)
        return Vec((self.__direction__[0], self.__direction__[1], self.__direction__[2]))

    @property
    def direction(self) -> 'Vec':
        """
        alias for 'norm'
        """
        return self.norm

    def angle(self, other: 'Vec'):
        """
        computes the angle between self and another vector
        """

        if self.is_zero() or other.is_zero():
            raise ValueError('cannot compute angle between vectors: one of the vectors has zero-length')

        return math.acos(
            self.dot(other) / (self.length * other.length)
        )


V = Vec
Vec.zero = Vec((0., 0., 0.))


class Quat:

    """
    a minimal quaternion class. Implements quaternion multiplication and lets
    extract a rotation from a quaternion, if possible

    this is not json-serializable, because the rotations in the serialized models
    should be stored as the 'Rotation' instances
    """

    def __init__(self, re: float, im: Vec):
        self.re = re
        self.im = im

    def extract_rotation(self) -> Optional['Rotation']:
        """
        calculates rotation implied in this quaternion (is not guaranteed to exist for every quaternion)
        """
        angle_implied_by_real_part = math.acos(self.re) * 2
        angle_implied_by_imaginary_part = math.asin(self.im.length) * 2

        if not math.isclose(angle_implied_by_real_part, angle_implied_by_imaginary_part, abs_tol=1e-6):
            return None

        return Rotation(angle=angle_implied_by_real_part, axis=self.im.direction)

    def __mul__(self, other: 'Quat') -> 'Quat':
        """
        an implementation of quaternion multiplication
        """
        ...

    def __iter__(self):
        yield self.re
        yield self.im[0]
        yield self.im[1]
        yield self.im[2]


Q = Quat


class Rotation:

    def __init__(self, angle: float, axis: Vec):
        self.angle = angle

        if angle != 0. and axis.is_zero():
            raise ValueError('rotations around degenerate axes are not allowed')
        self.axis = axis.direction # always normalize

    def __eq__(self, other):
        if not type(other) is Rotation:
            return False

        return math.isclose(self.angle, other.angle, abs_tol=1e-9) and self.axis == other.axis

    @property
    def rotating_quaternion(self) -> Quat:
        """
        returns a quaternion that embeds this rotation
        """
        return Quat(re=math.cos(self.angle / 2), im=self.axis * math.sin(self.angle / 2))


R = Rotation


class Transform:

    def __init__(self,
                 location: Vec=Vec((0., 0., 0.)),
                 rotation: Rotation=Rotation(angle=0., axis=Vec.zero),
                 scale: Vec=Vec((1., 1., 1.))):
        self.location = location
        self.rotation = rotation
        self.scale = scale

    def __eq__(self, other):
        if type(other) is not Transform:
            return False

        return self.location == other.location and \
            self.rotation == other.rotation and \
            self.scale == other.scale


T = Transform


class BoundingBox:
    def __init__(self, min_vert=Vec.zero, max_vert=Vec.zero):
        self.min: Vec = min_vert
        self.max: Vec = max_vert

    @property
    def extent(self) -> Vec:
        return self.max - self.min

    @property
    def height(self) -> float:
        return self.extent.up

    @property
    def width(self) -> float:
        return self.extent.right

    @property
    def depth(self) -> float:
        return self.extent.forward

    @property
    def vol(self) -> float:
        extent = self.extent
        return extent.x * extent.y * extent.z


BB = BoundingBox


@dataclass
class UV:
    u: float
    v: float

    def __iter__(self):
        yield self.u
        yield self.v

    def __len__(self):
        return 2

    @staticmethod
    def to_json(val: 'UV', **_):
        return [val.u, val.v]

    @staticmethod
    def from_json(val, cls, **_):
        if type(val) is list and len(val) == 2:
            return UV(val[0], val[1])
        raise ValueError(f'UV can be serialized from a list of len=2, received {val} instead')


@dataclass
class FaceCornerDataObjectBase:

    """
    a base class for data that is saved per face and per corner, for example: normals, tangents, UVs, colors
    """

    face: int
    corner: int
    data: object


class RGBa:

    """
    an RGBa class with an optional alpha-channel. pixels might be represented as floats 0.-1. or 8-bit ints (0-255)
    """

    r: Union[int, float]
    g: Union[int, float]
    b: Union[int, float]
    a: Optional[Union[int, float]]

    def __init__(self, r: Union[int, float], g: Union[int, float], b: Union[int, float], a: Union[int, float]=None):
        if type(r) is int:
            self.__dtype__ = int
        elif type(r) is float:
            self.__dtype__ = float
        else:
            raise ValueError(f'an RGBa color must be instantiated from floats or ints, received {type(r)} instead')

        if self.__dtype__ is float:
            vals = [r, g, b, a] if a is not None else [r, g, b]
            assert all([type(channel) is float for channel in vals]), 'Expected floats'
            assert all([0. <= channel <= 1. for channel in vals]), 'Color floats must be between 0. and 1.'
        else:
            vals = [r, g, b, a] if a is not None else [r, g, b]
            assert all([type(channel) is int for channel in vals]), 'Expected ints'
            assert all([0 <= channel <= 255 for channel in vals]), 'Color ints must be between 0 and 255'

        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def has_alpha(self) -> bool:
        return self.a is not None

    @property
    def i8(self):
        if self.__dtype__ is int:
            return RGBa(self.r, self.g, self.b, self.a)
        else:
            return RGBa(
                r=round(self.r * 255),
                g=round(self.g * 255),
                b=round(self.b * 255),
                a=round(self.a * 255) if self.a is not None else self.a
            )

    @property
    def f(self):
        if self.__dtype__ is float:
            return RGBa(self.r, self.g, self.b, self.a)
        else:
            return RGBa(
                r=self.r / 255.,
                g=self.g / 255.,
                b=self.b / 255.,
                a=self.a / 255. if self.a is not None else self.a
            )

    @property
    def rgb(self):
        """
        strips the alpha channel away
        """
        return RGBa(self.r, self.g, self.b, None)

    def is_greyscale(self):
        if self.__dtype__ is int:
            return self.r == self.g == self.b
        else:
            return math.isclose(self.r, self.g, abs_tol=1e-6) and math.isclose(self.r, self.b, abs_tol=1e-6)

    def is_black(self):
        if self.__dtype__ is int:
            return self.r == self.g == self.b == 0
        else:
            return self.is_greyscale() and math.isclose(self.r, 0., abs_tol=1e-6)

    def is_white(self):
        if self.__dtype__ is int:
            return self.r == self.g == self.b == 255
        else:
            return self.is_greyscale() and math.isclose(self.r, 1., abs_tol=1e-6)

    def __iter__(self):
        yield self.r
        yield self.g
        yield self.b
        if self.a is not None:
            yield self.a

    def __len__(self):
        return 3 if self.a is None else 4

    def __getitem__(self, idx: int):
        return [self.r, self.g, self.b, self.a][idx]

    def __eq__(self, other: Union['RGBa', Iterable]):
        if type(other) is not RGBa:
            try:
                other = RGBa(*other)
            except Exception:
                return False

        if self.__dtype__ != other.__dtype__:
            return False

        if self.__dtype__ is int:
            return list(self) == list(other)
        else:
            return all([math.isclose(self[idx], other[idx], abs_tol=1e-6) for idx in range(len(self))])


@dataclass
class VertexNormal(FaceCornerDataObjectBase):
    data: Vec

    @property
    def normal(self) -> Vec:
        return self.data


@dataclass
class VertexTangent(FaceCornerDataObjectBase):
    data: Vec

    @property
    def tangent(self) -> Vec:
        return self.data


@dataclass
class VertexUV(FaceCornerDataObjectBase):
    data: UV

    @property
    def uv(self) -> UV:
        return self.data


@dataclass
class VertexColor(FaceCornerDataObjectBase):
    data: RGBa

    @property
    def color(self) -> RGBa:
        return self.data


@dataclass
class VertexColorLayer:
    name: str
    vcolors: List[VertexColor]


@dataclass
class UVMap:
    name: str
    uvs: List[VertexUV]


@dataclass
class VertexGroup:
    name: str
    weights: List[Tuple[int, float]]


@dataclass
class Mesh:

    """
    polygonal mesh
    """

    name: str
    coords: List[Vec]
    faces: List[Tuple[int, ...]]
    normals: List[VertexNormal]
    uv_maps: List[UVMap]
    tangents: List[VertexTangent] = field(default_factory=list)
    vertex_color_layers: List[VertexColorLayer] = field(default_factory=list)
    vgroups: List[VertexGroup] = field(default_factory=list)
    materials: List[str] = field(default_factory=list) # list of material names (actual materials are kept at the file-level)
    material_indices: List[int] = field(default_factory=list) # per-face material ids (id is offset into the 'materials' array)

    @property
    def json(self):
        json_dict = {
            'name': self.name,
            'coords': [list(v) for v in self.coords],
            'faces': [list(f) for f in self.faces],
            'normals': [[vnorm.face, vnorm.corner, list(vnorm.normal)] for vnorm in self.normals],
            'uv_maps': [{'name': uv_map.name, 'uvs': [[uv.face, uv.corner, list(uv.data)] for uv in uv_map.uvs]} for uv_map in self.uv_maps]
        }

        if self.tangents:
            json_dict['tangents'] = [[vtang.face, vtang.corner, list(vtang.data)] for vtang in self.tangents]

        if self.vertex_color_layers:
            json_dict['vertex_color_layers'] = [{'name': vcolor_layer.name, 'colors': [[vcolor.face, vcolor.corner, list(vcolor.color)] for vcolor in vcolor_layer.vcolors]} for vcolor_layer in self.vertex_color_layers]

        if self.vgroups:
            json_dict['vgroups'] = [{'name': vgroup.name, 'weights': [list(vweight) for vweight in vgroup.weights]} for vgroup in self.vgroups]

        if self.materials:
            json_dict['materials'] = self.materials

        if len(self.materials) > 1: # material indices make no sense if there are not more than 1 material for this mesh
            json_dict['material_indices'] = self.material_indices

        return json.dumps(json_dict)

    @classmethod
    def from_json(cls, json_string: str):
        json_dict: dict = json.loads(json_string)
        mesh = cls(
            name=json_dict['name'],
            coords=[Vec(tuple(co)) for co in json_dict['coords']],
            faces=[tuple(f) for f in json_dict['faces']],
            normals=[VertexNormal(vnorm[0], vnorm[1], Vec(tuple(vnorm[2]))) for vnorm in json_dict['normals']],
            uv_maps=[UVMap(name=uv_map['name'], uvs=[VertexUV(vuv[0], vuv[1], UV(vuv[2][0], vuv[2][1])) for vuv in uv_map['uvs']]) for uv_map in json_dict['uv_maps']]
        )

        if json_dict.get('tangents', None):
            mesh.tangents = [VertexTangent(vtang[0], vtang[1], Vec(tuple(vtang[2]))) for vtang in json_dict['tangents']]

        if json_dict.get('vertex_color_layers', None):
            mesh.vertex_color_layers = [VertexColorLayer(name=vcollayer['name'], vcolors=[VertexColor(vcol[0], vcol[1], RGBa(vcol[2][0], vcol[2][1], vcol[2][2], vcol[2][3])) for vcol in vcollayer['colors']]) for vcollayer in json_dict['vertex_color_layers']]

        if json_dict.get('vgroups', None):
            mesh.vgroups = [VertexGroup(name=vgroup['name'], weights=[tuple(weight) for weight in vgroup['weights']]) for vgroup in json_dict['vgroups']]

        if json_dict.get('materials', None):
            mesh.materials = json_dict['materials']

        if json_dict.get('material_indices', None):
            mesh.material_indices = json_dict['material_indices']

        return mesh

    @property
    def bbox(self) -> BoundingBox:
        return BoundingBox(
            min_vert=Vec.create(
                forward=min([v.forward for v in self.coords]),
                right=min([v.right for v in self.coords]),
                up=min([v.up for v in self.coords])
            ),
            max_vert=Vec.create(
                forward=max([v.forward for v in self.coords]),
                right=max([v.right for v in self.coords]),
                up=max([v.up for v in self.coords])
            )
        )

    @property
    def poly_count(self) -> int:
        return len(self.faces)

    @property
    def tri_count(self) -> int:
        tris_per_poly = [len(poly) - 2 for poly in self.faces]
        return sum(tris_per_poly)


@dataclass
class SceneObject:
    """
    a scene object points to a mesh, and specifies the transform for the mesh
    """
    mesh_id: str # id of the mesh to use, must be present in the file
    transform: Transform


@dataclass
class Scene:
    """
    in obj-on-steroids, scenes are a bunch of meshes specifically placed.
    one obj-on-steroids file can contain arbitrarily many scenes.
    """
    name: str # name of this scene
    scene_objects: List[SceneObject]
    tags: List[str] = field(default_factory=list) # an optional array of tags
    udfs: Dict[str, object] = field(default_factory=dict) # user-defined fields


@dataclass
class GameStaticMesh:
    LODs: List[Mesh]
    collision_mesh: Optional[Mesh]
    convex_collision_hulls: List[Mesh] # optional, contains positioned objects


class Channels:
    R: 'Channels'
    G: 'Channels'
    B: 'Channels'
    A: 'Channels'
    RG: 'Channels'
    GB: 'Channels'
    BA: 'Channels'
    RGB: 'Channels'
    GBA: 'Channels'
    RGBA: 'Channels'

    _char_to_idx_channel_map_ = {
        'r': 0,
        'g': 1,
        'b': 2,
        'a': 3
    }

    def __init__(self, channels: Union[Iterable, str, int]):
        if type(channels) is str:
            channels = channels.lower()

        if type(channels) is int:
            channels = [channels]

        try:
            channels_set = set(channels)
        except TypeError:
            raise ValueError(f'cannot create Channels from the supplied set, should be iterable of string')

        if channels_set.issubset({0, 1, 2, 3}):
            self.channel_idcs = channels_set
        elif channels_set.issubset({'r', 'g', 'b', 'a'}):
            self.channel_idcs = set([self._char_to_idx_channel_map_[set_member] for set_member in channels_set])
        else:
            raise ValueError(f'expected an iterable containing (0, 1, 2, 3) or ("r", "g", "b", "a")')

    def __add__(self, other: 'Channels'):
        channel_idx_intersection = self.channel_idcs.intersection(other.channel_idcs)

        if len(channel_idx_intersection) != 0:
            raise ValueError(f'cannot add {self} and {other} because of conflicting channels: {channel_idx_intersection}')

        channel_idx_union = self.channel_idcs.union(other.channel_idcs)

        if not channel_idx_union.issubset({0, 1, 2, 3}):
            raise ValueError(f'attempted to add an invalid Channels object, indices should be in [0, 1, 2, 3]')

        return Channels(channel_idx_union)

    @property
    def ordered_list(self):
        lst = list(self.channel_idcs)
        return sorted(lst)

    @property
    def code(self) -> Literal['r', 'g', 'b', 'a', 'rg', 'gb', 'ba', 'rgb', 'gba', 'rgba']:
        channel_code_idx = {
            'r': 0,
            'g': 1,
            'b': 2,
            'a': 3
        }

        return ''.join([channel_code for channel_code in channel_code_idx if channel_code_idx[channel_code] in self.channel_idcs])

    def __str__(self) -> str:
        return self.code

    def __len__(self) -> int:
        return len(self.channel_idcs)

    def __eq__(self, other: Union['Channels', Iterable]):
        if type(other) is Channels:
            return self.channel_idcs == other.channel_idcs
        else:
            try:
                other = Channels(other)
                return self.channel_idcs == other.channel_idcs
            except TypeError:
                return False


Channels.R = Channels(0)
Channels.G = Channels(1)
Channels.B = Channels(2)
Channels.A = Channels(3)
Channels.RG = Channels.R + Channels.G
Channels.GB = Channels.G + Channels.B
Channels.BA = Channels.B + Channels.A
Channels.RGB = Channels.R + Channels.G + Channels.B
Channels.GBA = Channels.G + Channels.B + Channels.A
Channels.RGBA = Channels.R + Channels.G + Channels.B + Channels.A


class SurfaceDataTypeDataType(Enum):
    BOOL = (0, 1)       # only 0 or 1 (for example, black-and-white masks)
    FLOAT = (1, 1)      # opacity, roughness, ambient occlusion and co
    VEC2 = (2, 2)       # more rare, for example, flow maps
    VEC3 = (3, 3)       # rgb colors or vectors of length 3 (like normal maps)

    def __init__(self, idx: int, channel_requirement: int):
        self.id = idx
        self.channel_requirement = channel_requirement  # how many channels in an image file are required to store this dtype


BOOL = SurfaceDataTypeDataType.BOOL
FLOAT = SurfaceDataTypeDataType.FLOAT
VEC2 = SurfaceDataTypeDataType.VEC2
VEC3 = SurfaceDataTypeDataType.VEC3


class SurfaceDataType:
    def __init__(self, name: str, dtype: SurfaceDataTypeDataType=None):
        self.name = name
        self.dtype = dtype

    def __eq__(self, other: 'SurfaceDataType'):
        return self.name == other.name and self.dtype == other.dtype


class SurfaceDataTypes:
    COLOR = SurfaceDataType('color', VEC3)
    NORMALS = SurfaceDataType('norm', VEC3)
    AMBIENT_OCCLUSION = SurfaceDataType('amb_occl', FLOAT)
    OPACITY = SurfaceDataType('opacity', FLOAT)
    OPACITY_MASK = SurfaceDataType('opacity_mask', BOOL)
    METALNESS = SurfaceDataType('metal', FLOAT)
    ROUGHNESS = SurfaceDataType('rough', FLOAT)
    SPECULAR = SurfaceDataType('spec', FLOAT)
    GLOSS = SurfaceDataType('gloss', FLOAT)
    HEIGHT = SurfaceDataType('height', FLOAT)
    CURVATURE = SurfaceDataType('curvature', FLOAT)
    EMISSION = SurfaceDataType('emission', VEC3)
    SUBSURFACE = SurfaceDataType('subsurface', FLOAT)
    SUBSURFACE_COLOR = SurfaceDataType('subsurface_color', VEC3)
    IOR = SurfaceDataType('ior', FLOAT)
    CLEARCOAT = SurfaceDataType('clearcoat', FLOAT)
    EDGE_WEAR = SurfaceDataType('edge_wear', FLOAT)
    CAVITY = SurfaceDataType('cavity', FLOAT)


class SurfaceMap:
    """
    is a self-aware surface texture pointer. 'Pointer' is used here in the sense that this object does not
    store actual data. Instead, it contains certain metadata and points to the image and channels storing actual pixels

    it knows what type of surface data it represents, and which model/uv set it is bound to (if any)
    """

    name: str
    surface_data_type: Union[str, SurfaceDataType]
    source_img: str  # name of the image file where the surface map is stored, image should be in the same dir as the surface map yml
    source_channels: Channels # which channels it is stored inside the source image
    mesh_id: Optional[str] # authored for this mesh specifically
    uv_layout_id: Optional[str] # authored for this uv layout specifically
    tags: List[str] # list of user-defined tags

    def __init__(self,
                 name: str,
                 surface_data_type: Union[str, SurfaceDataType],
                 source_img: str,
                 source_channels: Channels,
                 mesh_id: str=None,
                 uv_layout_id: str=None):
        self.name = name

        if type(surface_data_type) is str:
            self.surface_data_type = SurfaceDataType(surface_data_type)
        else:
            self.surface_data_type = surface_data_type

        self.source_img = source_img
        self.source_channels = source_channels

        if self.surface_data_type.dtype.channel_requirement != len(self.source_channels):
            raise ValueError(f'surface data type {surface_data_type} cannot be stored in {len(self.source_channels)} channels')

        self.mesh_id = mesh_id
        self.uv_layout_id = uv_layout_id
        self.tags = []


class Material:
    name: str # this material's name

    shader: str  # shader defines how maps and parameters should be wired together in a game engine to produce an actual material
                 # in unreal engine, the shader string can be used to select a correct master material for the instance

    maps: List[str] # names of surface maps used in this material


class Driver:

    def get_supported_extensions(self) -> Tuple[str]:
        ...

    def get_name(self) -> str:
        ...

    def Import(self, from_file: Path) -> 'ModelData':
        ...

    def export(self, scene: 'ModelData', destination: Path) -> Path:
        ...


__drivers__: List[Driver] = []


def find_driver_for_extension(extension: str) -> Optional[Driver]:
    extension = extension.replace('.', '')
    for driver in __drivers__:
        if extension in [supported_extension.replace('.', '') for supported_extension in driver.get_supported_extensions()]:
            return driver

    return None


def register_driver(driver_cls_or_obj: Union[Driver, type]):
    if type(driver_cls_or_obj) is type and issubclass(driver_cls_or_obj, Driver):
        __drivers__.append(driver_cls_or_obj())
    elif isinstance(driver_cls_or_obj, Driver):
        __drivers__.append(driver_cls_or_obj)
    else:
        raise ValueError('expected a Driver object or a Driver subclass')


@dataclass
class ModelData:
    meshes: Container[Mesh] = field(default_factory=Container)
    skeletons: Container[object] = field(default_factory=Container)
    animations: Container[object] = field(default_factory=Container)
    surface_maps: Container[SurfaceMap] = field(default_factory=Container)
    materials: Container[Material] = field(default_factory=Container)
    scenes: Container[Scene] = field(default_factory=Container)

    def add_mesh(self, mesh: Mesh):
        if self.meshes.find(lambda m: m.name == mesh.name) is not None:
            raise KeyError(f'mesh with name {mesh.name} already exists')
        mesh.model_data = self
        self.meshes._items.append(mesh)

    def add_scene(self, scene: Scene):
        # validate that all scene objects point to valid meshes
        for scene_object in scene.scene_objects:
            if self.meshes.find(lambda m: m.name == scene_object.mesh_id) is None:
                raise KeyError(f'mesh "{scene_object.mesh_id}" referenced by scene "{scene.name}" does not exist')

        # scene must have unique names
        if self.scenes.find(lambda s: s.name == scene.name) is not None:
            raise KeyError(f'scene with name "{scene.name}" already exists')

        scene.model_data = self
        self.scenes._items.append(scene)


    def export(self, destination: Path) -> Path:
        """
        saves to hard drive

        when saving as a 3rd party format, the corresponding driver is required
        """
        suffix = destination.suffix

        driver = find_driver_for_extension(suffix)
        if driver:
            return driver.export(self, destination)
        else:
            raise NotImplementedError(f'cannot export to destination "{destination}": could not find driver for extension "{suffix}"')

    @classmethod
    def Import(cls, file: Path) -> 'ModelData':
        """
        import from a file

        when importing from a 3rd party format, the corresponding driver is required
        """
        suffix = file.suffix

        driver = find_driver_for_extension(suffix)
        if driver:
            return driver.Import(from_file=file)
        else:
            raise NotImplementedError(f'cannot import from source "{file}": could not find driver for extension "{suffix}"')


class MeshPrimitives:

    @staticmethod
    def cube(scale_width: float=1., scale_depth: float=1., scale_height: float=1.):
        # creates a polygonal (faces are quads) unit-volume cube, if no scaling is applied
        coord_template = [
            Vec((-0.5, -0.5, 0.5)),
            Vec((-0.5, -0.5, -0.5)),
            Vec((0.5, -0.5, 0.5)),
            Vec((0.5, -0.5, -0.5)),
            Vec((-0.5, 0.5, 0.5)),
            Vec((-0.5, 0.5, -0.5)),
            Vec((0.5, 0.5, 0.5)),
            Vec((0.5, 0.5, -0.5))
        ]

        # apply the scaling
        coords = [Vec((co.x * scale_depth, co.y * scale_width, co.z * scale_height)) for co
                  in coord_template]

        faces = [
            (0, 4, 6, 2),
            (3, 2, 6, 7),
            (7, 6, 4, 5),
            (5, 1, 3, 7),
            (1, 0, 2, 3),
            (5, 4, 0, 1)
        ]

        # auto-compute vertex normals (aligned with face normals for a given face
        normals = []
        for face_idx in range(len(faces)):
            face = faces[face_idx]
            face_normal = (coords[face[1]] - coords[face[0]]).cross(
                coords[face[2]] - coords[face[0]]
            ).norm

            for corner in face:
                normals.append(VertexNormal(
                    face=face_idx, corner=corner, data=face_normal
                ))

        uvs = [
            VertexUV(0, 0, UV(0.625, 0.5)),
            VertexUV(0, 1, UV(0.875, 0.5)),
            VertexUV(0, 2, UV(0.875, 0.75)),
            VertexUV(0, 3, UV(0.625, 0.75)),
            VertexUV(1, 0, UV(0.375, 0.75)),
            VertexUV(1, 1, UV(0.625, 0.75)),
            VertexUV(1, 2, UV(0.625, 1.0)),
            VertexUV(1, 3, UV(0.375, 1.0)),
            VertexUV(2, 0, UV(0.375, 0.0)),
            VertexUV(2, 1, UV(0.625, 0.0)),
            VertexUV(2, 2, UV(0.625, 0.25)),
            VertexUV(2, 3, UV(0.375, 0.25)),
            VertexUV(3, 0, UV(0.125, 0.5)),
            VertexUV(3, 1, UV(0.375, 0.5)),
            VertexUV(3, 2, UV(0.375, 0.75)),
            VertexUV(3, 3, UV(0.125, 0.75)),
            VertexUV(4, 0, UV(0.375, 0.5)),
            VertexUV(4, 1, UV(0.625, 0.5)),
            VertexUV(4, 2, UV(0.625, 0.75)),
            VertexUV(4, 3, UV(0.375, 0.75)),
            VertexUV(5, 0, UV(0.375, 0.25)),
            VertexUV(5, 1, UV(0.625, 0.25)),
            VertexUV(5, 2, UV(0.625, 0.5)),
            VertexUV(5, 3, UV(0.375, 0.5))
        ]

        return Mesh(name='cube',
                    coords=coords,
                    faces=faces,
                    normals=normals,
                    uv_maps=[UVMap(name='UVMap', uvs=uvs)],
                    materials=['Material'])
