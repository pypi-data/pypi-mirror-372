"""Csv file data row."""
from .. import Error, ObjectClass, TypeHorWeld
from ..orientation import Orientation

COMMON = {
  ObjectClass.WELD: "Weld",
  ObjectClass.THICK: "Wall thickness change",
  ObjectClass.PIPELINE_CATEGORY: "Category",
  ObjectClass.DIAM: "Diameter change",
}

SEAM = {
  TypeHorWeld.HORIZONTAL: "Single",
  TypeHorWeld.SECOND: "Double",
  TypeHorWeld.NO_WELD: "Seamless ",
  TypeHorWeld.SPIRAL: "Spiral",
  TypeHorWeld.UNKNOWN: "Unknown",
}


def to_int(text):
    """Convert text to int."""
    if not text:
        return None

    return int(round(float(text.strip().replace(',', '.')), 0))


def reverse_orient(orient_str):
    """Reverse orientation of string in format "hours,minutes"."""
    if not orient_str:
        return orient_str

    hours_str = orient_str
    minutes_str = '0'
    if ',' in orient_str:
        hours_str, minutes_str = orient_str.split(',')

    if hours_str == '12':
        hours_str = '0'

    if len(minutes_str) == 1:
        minutes_str += '0'

    minutes = 60 - int(minutes_str)
    hours = 12 - int(hours_str)
    if minutes == 60:
        minutes = 0
    else:
        hours -= 1

    if minutes < 10:
        minutes = '0{}'.format(minutes)

    return "{},{}".format(hours, minutes)


class Depth:
    """Units for defekt depth."""

    PercentWallThickness = 0
    HundredthsOfMillimeter = 1


class Row:  # pylint: disable=too-many-instance-attributes, too-many-public-methods
    """Row of csv file."""

    depth_units = Depth.PercentWallThickness

    @staticmethod
    def get_bool(val):
        """Bool value for csv."""
        return 'True' if val else 'False'

    @staticmethod
    def name_seam(code):
        """Return text for seam object_code_t field."""
        return SEAM[code]

    @staticmethod
    def name_object(code):
        """Return text for object_code_t field."""
        return COMMON[code]

    @staticmethod
    def defekts_dict():
        """Return dict of available defekts types."""
        return {}

    @staticmethod
    def lineobj_dict():
        """Return dict of available lineobject types."""
        return {}

    @staticmethod
    def markers_default():
        """Return list of lineobject types that use as markers by default."""
        return []

    @staticmethod
    def markers_reverse():
        """Return dict of markers for reverse."""
        return {}

    @staticmethod
    def comment_reverse():
        """Return dict of comment substrings for reverse."""
        return {}

    @staticmethod
    def mloss_codes():
        """Return list of available metal loss defect codes."""
        return []

    @staticmethod
    def dents_codes():
        """Return list of available dent defect codes."""
        return []

    @staticmethod
    def atweld_codes():
        """Return list of available at weld defect codes."""
        return []

    @staticmethod
    def atseam_codes():
        """Return list of available at seam defect codes."""
        return []

    @staticmethod
    def valve_codes():
        """Return list of available valve like obect codes."""
        return []

    def __init__(self):
        """Create empty csv row object."""
        self.dist_od = None
        self.type_object = None
        self.object_code = 0
        self.object_name = ''
        self.object_code_t = ''
        self.is_marker_int = False
        self.length = ''
        self.width = ''
        self.depth_min = ''
        self.depth_max = ''
        self.orient_td = ''
        self.orient_bd = ''
        self.mpoint_orient = ''
        self.mpoint_dist = ''
        self.type_def = ''
        self.dist_ml = ''
        self.dist_mr = ''
        self.dist_stl = ''
        self.dist_str = ''
        self.link_stl = ''
        self.link_str = ''
        self.link_ml = ''
        self.link_mr = ''
        self.comments = ''
        self.latitude = ''
        self.longtitude = ''
        self.altitude = ''

    def __str__(self):
        """As text."""
        return ';'.join([str(i) for i in self.values()])

    @property
    def marker(self):
        """Return string for marker feature."""
        return self.get_bool(self.is_marker_int)

    @marker.setter
    def marker(self, val):
        """Set internal field based on string for marker feature."""
        self.is_marker_int = False
        if val == self.get_bool(True):
            self.is_marker_int = True

    @property
    def is_marker(self):
        """Return marker feature as bool."""
        return self.is_lineobj and self.is_marker_int

    @property
    def dist(self):
        """Return object distance as integer mm."""
        return int(self.dist_od)

    @property
    def obj_id(self):
        """Return optional object ID as string."""
        return self.dist_ml

    @obj_id.setter
    def obj_id(self, value):
        """Set optional object ID as string."""
        self.dist_ml = '' if value is None else str(value).strip()

    @property
    def min_diam(self):
        """Return optional minimal pipe diameter as string (mm)."""
        return self.depth_max

    @min_diam.setter
    def min_diam(self, value):
        """Set optional minimal pipe diameter as string (mm)."""
        self.depth_max = value

    @staticmethod
    def get_minutes(text):
        """Restore full integer minute from text 'hours,minites'."""
        val = Orientation.from_csv(text)

        if val is None:
            return None

        return val.as_minutes

    @property
    def orient1(self):
        """Return start orientation as integer minutes or None."""
        return self.get_minutes(self.orient_td)

    @property
    def orient2(self):
        """Return end orientation as integer minutes or None."""
        return self.get_minutes(self.orient_bd)

    def set_geo(self, latitude, longtitude, altitude):
        """Set geo coords for object."""
        if latitude and longtitude and altitude:
            self.latitude = latitude
            self.longtitude = longtitude
            self.altitude = altitude

        return self

    @classmethod
    def with_dist(cls, distanse, obj_id='', latitude='', longtitude='', altitude=''):
        """Construct row as common object with dist and geo."""
        obj = cls()
        obj.dist_od = int(distanse)
        obj.obj_id = obj_id

        return obj.set_geo(latitude, longtitude, altitude)

    @classmethod
    def as_common(cls, distanse, typ, obj_id='', latitude='', longtitude='', altitude=''):
        """Construct row as common object."""
        obj = cls.with_dist(distanse, obj_id=obj_id, latitude=latitude, longtitude=longtitude, altitude=altitude)
        obj.type_object = typ
        obj.object_code_t = cls.name_object(obj.type_object)

        return obj

    @classmethod
    def as_weld(cls, distanse, min_diam=None, obj_id='', custom_number='', latitude='', longtitude='', altitude=''):
        """Construct row as weld object."""
        obj = cls.as_common(
          distanse, ObjectClass.WELD,
          obj_id=obj_id,
          latitude=latitude, longtitude=longtitude, altitude=altitude
        )

        if custom_number:
            obj.object_name = custom_number

        if min_diam:
            obj.min_diam = min_diam

        return obj

    @classmethod
    def as_thick(cls, distanse, thick, obj_id='', latitude='', longtitude='', altitude=''):
        """Construct row as thickness change object."""
        obj = cls.as_common(
          distanse, ObjectClass.THICK,
          obj_id=obj_id,
          latitude=latitude, longtitude=longtitude, altitude=altitude
        )
        obj.depth_max = thick
        return obj

    @classmethod
    def as_diam(cls, distanse, diam_start, diam_end, obj_id='', latitude='', longtitude='', altitude=''):
        """Construct row as diameter change object."""
        obj = cls.as_common(
          distanse, ObjectClass.DIAM,
          obj_id=obj_id,
          latitude=latitude, longtitude=longtitude, altitude=altitude
        )
        obj.depth_min = diam_start
        obj.depth_max = diam_end
        return obj

    @classmethod
    def as_category(cls, distanse, category, obj_id='', latitude='', longtitude='', altitude=''):
        """Construct row as pipeline category object."""
        obj = cls.as_common(
          distanse, ObjectClass.PIPELINE_CATEGORY,
          obj_id=obj_id,
          latitude=latitude, longtitude=longtitude, altitude=altitude
        )
        obj.depth_max = category
        return obj

    @classmethod
    def as_seam(cls, distanse, typ, orient1, orient2, obj_id=''):
        """Construct row as seam object with given typ."""
        if typ not in SEAM:
            raise Error("Wrong seam type: {}".format(typ))

        obj = cls.with_dist(distanse, obj_id=obj_id, latitude='', longtitude='', altitude='')
        obj.type_object = ObjectClass.HOR_WELD
        obj.object_code = typ
        obj.object_code_t = cls.name_seam(obj.object_code)

        if obj.object_code in [TypeHorWeld.HORIZONTAL, TypeHorWeld.SPIRAL, TypeHorWeld.SECOND]:
            obj.orient_td = str(orient1)

        if obj.object_code in [TypeHorWeld.SECOND]:
            obj.orient_bd = str(orient2)

        return obj

    def set_anomaly(self, typ, orient1, orient2, length, width, comment, custom_data):
        """Set shared defekt/lineobj properties and custom data."""
        self.object_code = typ
        if orient1:
            self.orient_td = str(orient1)
        if orient2:
            self.orient_bd = str(orient2)

        self.length = length
        self.width = width
        self.comments = comment
        self.set_custom(custom_data)

    @classmethod
    def as_lineobj(  # pylint: disable=too-many-locals
      cls, distanse, typ, name, is_marker, comment,
      length='', width='', orient1=None, orient2=None,
      obj_id='', latitude='', longtitude='', altitude='',
      custom_data=''
    ):
        """Construct row as line object."""
        lineobj = cls.lineobj_dict()
        if typ not in lineobj:
            raise Error("Wrong lineobj type: {}".format(typ))

        obj = cls.with_dist(distanse, obj_id=obj_id, latitude=latitude, longtitude=longtitude, altitude=altitude)
        obj.type_object = ObjectClass.MARKER
        obj.set_anomaly(typ, orient1, orient2, length, width, comment, custom_data)

        obj.object_code_t = lineobj[obj.object_code]
        obj.object_name = name
        obj.is_marker_int = is_marker

        return obj

    @classmethod
    def as_defekt(  # pylint: disable=too-many-locals,too-many-arguments
      cls, distanse, typ, side, length, width, depth, orient1, orient2, mp_orient, mp_dist, comment,
      obj_id='', latitude='', longtitude='', altitude='', custom_data=''
    ):
        """Construct row as defekt object."""
        defekts = cls.defekts_dict()
        if typ not in defekts:
            raise Error("Wrong defekt type: {}".format(typ))

        depth_int = to_int(depth)

        obj = cls.with_dist(distanse, obj_id=obj_id, latitude=latitude, longtitude=longtitude, altitude=altitude)
        obj.type_object = ObjectClass.DEFEKT
        obj.set_anomaly(typ, orient1, orient2, length, width, comment, custom_data)

        obj.object_code_t = defekts[obj.object_code]
        obj.depth_min = depth_int
        obj.depth_max = depth_int
        obj.type_def = side

        if mp_orient:
            obj.mpoint_orient = str(mp_orient)
        if mp_dist:
            obj.mpoint_dist = mp_dist

        return obj

    @classmethod
    def from_csv_row(cls, row):
        """Construct from csv row."""
        obj = cls()

        obj.dist_od = row[0]
        obj.type_object = row[1]
        obj.object_code = row[2]
        obj.object_name = row[3]
        obj.object_code_t = row[4]
        obj.marker = row[5]
        obj.length = row[6]
        obj.width = row[7]
        obj.depth_min = row[8]
        obj.depth_max = row[9]
        obj.orient_td = row[10]
        obj.orient_bd = row[11]
        obj.mpoint_orient = row[12]
        obj.mpoint_dist = row[13]
        obj.type_def = row[14]
        obj.dist_ml = row[15]
        obj.dist_mr = row[16]
        obj.dist_stl = row[17]
        obj.dist_str = row[18]
        obj.link_stl = row[19]
        obj.link_str = row[20]
        obj.link_ml = row[21]
        obj.link_mr = row[22]
        obj.comments = row[23]
        obj.latitude = row[24]
        obj.longtitude = row[25]
        obj.altitude = row[26]

        return obj

    def values(self):
        """Column values for row."""
        return [
          self.dist_od,
          self.type_object,
          self.object_code,
          self.object_name,
          self.object_code_t,
          self.marker,
          self.length,
          self.width,
          self.depth_min,
          self.depth_max,
          self.orient_td,
          self.orient_bd,
          self.mpoint_orient,
          self.mpoint_dist,
          self.type_def,
          self.dist_ml,
          self.dist_mr,
          self.dist_stl,
          self.dist_str,
          self.link_stl,
          self.link_str,
          self.link_ml,
          self.link_mr,
          self.comments,
          self.latitude,
          self.longtitude,
          self.altitude,
        ]

    def copy(self):
        """Create copy of row."""
        obj = Row()

        obj.dist_od, \
            obj.type_object, \
            obj.object_code, \
            obj.object_name, \
            obj.object_code_t, \
            obj.marker, \
            obj.length, \
            obj.width, \
            obj.depth_min, \
            obj.depth_max, \
            obj.orient_td, \
            obj.orient_bd, \
            obj.mpoint_orient, \
            obj.mpoint_dist, \
            obj.type_def, \
            obj.dist_ml, \
            obj.dist_mr, \
            obj.dist_stl, \
            obj.dist_str, \
            obj.link_stl, \
            obj.link_str, \
            obj.link_ml, \
            obj.link_mr, \
            obj.comments, \
            obj.latitude, \
            obj.longtitude, \
            obj.altitude = self.values()

        return obj

    @property
    def custom_data(self):
        """Return custom data for row."""
        return self.dist_mr

    def set_custom(self, data):
        """Set custom data for row."""
        self.dist_mr = data

    @property
    def is_category(self):
        """Row is pipeline category object."""
        return int(self.type_object) == ObjectClass.PIPELINE_CATEGORY

    @property
    def is_thick(self):
        """Row is wall thick change object."""
        return int(self.type_object) == ObjectClass.THICK

    @property
    def is_diam(self):
        """Row is diameter change object."""
        return int(self.type_object) == ObjectClass.DIAM

    @property
    def is_weld(self):
        """Row is weld object."""
        return int(self.type_object) == ObjectClass.WELD

    @property
    def is_defect(self):
        """Row is defect object."""
        return int(self.type_object) == ObjectClass.DEFEKT

    @property
    def is_lineobj(self):
        """Row is line object."""
        return int(self.type_object) == ObjectClass.MARKER

    @property
    def is_seam(self):
        """Row is seam object."""
        return int(self.type_object) == ObjectClass.HOR_WELD

    @property
    def is_valve(self):
        """Return True if item is valve like object."""
        return self.is_lineobj and (int(self.object_code) in self.valve_codes())

    def reverse(self, total_length):
        """Reverse dist, orientation and start point if objects with length."""
        my_length = 0
        if self.length:
            my_length = int(self.length)

        self.dist_od = str(total_length - int(self.dist_od) - my_length)

        if self.mpoint_dist:
            self.mpoint_dist = str(total_length - int(self.mpoint_dist))
        # self.dist_str, self.dist_stl = self.dist_stl, self.dist_str
        # self.link_stl, self.link_str = self.link_str, self.link_stl
        # self.link_ml, self.link_mr = self.link_mr, self.link_ml

        # orientatations
        self.orient_td = reverse_orient(self.orient_td)
        self.orient_bd = reverse_orient(self.orient_bd)

        if int(self.type_object) != ObjectClass.HOR_WELD:
            tmp = self.orient_bd
            self.orient_bd = self.orient_td
            self.orient_td = tmp

        self.mpoint_orient = reverse_orient(self.mpoint_orient)

        # object type
        if int(self.type_object) == ObjectClass.MARKER:
            object_code = int(self.object_code)
            self.object_code = str(self.markers_reverse().get(object_code, object_code))
        elif int(self.type_object) == ObjectClass.DIAM:
            self.depth_min, self.depth_max = self.depth_max, self.depth_min

        # comments
        for key, val in self.comment_reverse().items():
            if key in self.comments:
                self.comments = self.comments.replace(key, val)
                break
