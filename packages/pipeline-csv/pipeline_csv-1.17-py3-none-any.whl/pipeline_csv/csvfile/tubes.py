"""Tubes iterator interface for csv file."""
from math import pi

from .. import Error, TypeHorWeld
from ..orientation import Orientation
from .defect import Defect


def summary_text(objects, names):
    """Return summary text for given items."""
    items = {}
    for item in objects:
        code = int(item.object_code)
        if code in items:
            items[code] += 1
        else:
            items[code] = 1

    return ', '.join(["{}: {}".format(names.get(key, '??'), items[key]) for key in sorted(items.keys())])


class Tube:  # pylint: disable=too-many-instance-attributes
    """Represent one pipe."""

    def __init__(self, row, stream, auto_number):
        """Construct new tube object from csv row with given data stream state."""
        self.row = row
        self.dist = int(row.dist_od)
        self.auto_number = auto_number
        self.stream = stream

        self.length = None
        self.thick = None
        self.category = None
        self.diameter = self.stream.diameter

        self.is_diameter_change = None
        self.is_thick_change = None
        self.is_category_change = False

        self.seams = []
        self.lineobjects = []
        self.defects = []
        self.categories = []
        self.thicks = []
        self.diameters = []

    def __str__(self):
        """Return as text."""
        return "Tube diam {} len {} wall {}".format(
          self.diameter,
          self.length,
          self.thick
        )

    def minutes2mm(self, minutes):
        """Translate angle minutes to mm."""
        return int(self.diameter * pi * minutes / 720)

    def finalize(self, dist):
        """Finalize tube data at given dist."""
        self.length = int(dist) - self.dist
        self.thick = self.stream.thick
        self.category = self.stream.category

        if self.stream.diameter != self.diameter:
            self.is_diameter_change = self.stream.diameter if self.stream.diameter else None

    def add_object(self, row):  # pylint: disable=too-complex
        """Add data to tube from csv row."""
        if row.is_defect:
            self.defects.append(Defect(row, self))

        elif row.is_lineobj:
            self.lineobjects.append(row)

        elif row.is_seam:
            self.seams.append(row)

        elif row.is_category:
            category = row.depth_max
            if self.stream.category != category:
                self.stream.category = category
                self.is_category_change = True
            self.categories.append(row)

        elif row.is_diam:
            diameter = row.depth_max

            if self.diameter is None:
                self.diameter = diameter

            if self.stream.diameter != diameter:
                self.stream.diameter = diameter
            self.diameters.append(row)

        elif row.is_thick:
            thick = int(row.depth_max)
            if self.stream.thick != thick:
                self.is_thick_change = self.stream.thick
                self.stream.thick = thick
            self.thicks.append(row)

        else:
            raise Error("Tube at dist {} has wrong row: {}".format(self.dist, str(row)))

    def set_geo(self, latitude, longtitude, altitude):
        """Set geo coords for tube."""
        self.row.set_geo(latitude, longtitude, altitude)

    @property
    def latitude(self):
        """Tube start latitude."""
        return self.row.latitude

    @property
    def longtitude(self):
        """Tube start longtitude."""
        return self.row.longtitude

    @property
    def altitude(self):
        """Tube start altitude."""
        return self.row.altitude

    @property
    def radius(self):
        """Return tube curve radius."""
        return self.row.depth_min

    def set_radius(self, val):
        """Set tube curve radius."""
        self.row.depth_min = val

    @property
    def min_diam(self):
        """Return optional minimal pipe diameter as string (mm)."""
        return self.row.depth_max

    @min_diam.setter
    def min_diam(self, value):
        """Set optional minimal pipe diameter as string (mm)."""
        self.row.depth_max = value

    @property
    def number(self):
        """Tube custom or auto number."""
        num = self.row.object_name.strip()
        if not num:
            num = self.auto_number
        return num

    @property
    def summary(self):
        """Return string with summary for given tube."""
        defect_names = {}
        if self.defects:
            defect_names = self.defects[0].row.defekts_dict()

        line_names = {}
        if self.lineobjects:
            line_names = self.lineobjects[0].__class__.lineobj_dict()

        return ', '.join([i for i in [
          summary_text([defect.row for defect in self.defects], defect_names),
          summary_text(self.lineobjects, line_names)
        ] if i])

    @property
    def typ(self):
        """Return pipe type according pipe seams data."""
        if not self.seams:
            return TypeHorWeld.UNKNOWN

        return int(self.seams[0].object_code)

    @property
    def seam1(self):
        """Return orientation for longditual and spiral first pipe seam."""
        ornt = None
        if (len(self.seams) > 0) and (self.typ in [TypeHorWeld.HORIZONTAL, TypeHorWeld.SECOND, TypeHorWeld.SPIRAL]):
            text = self.seams[0].orient_td
            ornt = Orientation.from_csv(text) if text else None

        return ornt

    @property
    def seam2(self):
        """Return orientation for longditual and spiral second pipe seam."""
        ornt = None
        if (len(self.seams) > 0) and (self.typ == TypeHorWeld.SECOND):
            text = self.seams[0].orient_bd
            ornt = Orientation.from_csv(text) if text else None
        elif len(self.seams) > 1:
            text = self.seams[-1].orient_td
            ornt = Orientation.from_csv(text) if text else None

        return ornt

    @property
    def seam_info(self):
        """Return text string with seams orientation."""
        return ' / '.join([str(i) for i in [self.seam1, self.seam2] if i])

    def features(self):
        """Return defects and lineobjects of the pipe, arranged by distance."""
        return sorted(self.lineobjects + [defect.row for defect in self.defects], key=lambda i: i.dist)

    @property
    def to_seam_data(self):
        """Return True if distance to pipe seams can be calculated."""
        return (self.seam1 or self.seam2) and (self.typ in [TypeHorWeld.HORIZONTAL, TypeHorWeld.SECOND])
