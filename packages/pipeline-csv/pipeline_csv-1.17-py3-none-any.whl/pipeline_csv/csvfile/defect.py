"""Row with type Defect."""
from pipeline_csv.orientation import Orientation
from .row import Depth


class Anomaly:
    """Anomaly at the pipe."""

    def __init__(self, row, pipe):
        """Create anomaly at the pipe from csv Row."""
        self.row = row
        self.pipe = pipe

        self.orient1 = None
        if self.row.orient_td:
            self.orient1 = Orientation.from_csv(self.row.orient_td)

        self.orient2 = None
        if self.row.orient_bd:
            self.orient2 = Orientation.from_csv(self.row.orient_bd)

    def __str__(self):
        """As text."""
        return '{} at {}'.format(self.row.object_code_t, self.pipe)

    @property
    def length(self):
        """Return object length as integer."""
        if self.row.length:
            return int(self.row.length)
        return 0

    @property
    def code(self):
        """Return object code as integer."""
        return int(self.row.object_code)

    @property
    def to_left_weld(self):
        """Return distance (mm) from left defect border to upstream weld."""
        return self.row.dist - self.pipe.dist

    @property
    def to_right_weld(self):
        """Return distance (mm) from right defect border to downstream weld."""
        return self.pipe.dist + self.pipe.length - self.row.dist - self.length


class Defect(Anomaly):
    """Defect at the pipe."""

    def __init__(self, row, pipe):
        """Create defect at the pipe from csv Row."""
        super().__init__(row, pipe)

        self.orient_mp = None
        if self.row.mpoint_orient:
            self.orient_mp = Orientation.from_csv(self.row.mpoint_orient)

    @property
    def depth_percent(self):
        """Return defekt depth as percent from wall thickness for metal loss or pipe diameter for dents."""
        if not self.row.depth_max:
            return None

        if self.row.depth_units == Depth.PercentWallThickness and (self.is_dent or self.is_metal_loss):
            return float(self.row.depth_max)

        # Depth.HundredthsOfMillimeter
        if self.is_dent:
            return float(self.row.depth_max) / self.pipe.diameter

        return float(self.row.depth_max) / (self.pipe.thick / 10.0)

    @property
    def depth_mm(self):
        """Return defekt depth as mm."""
        if not self.row.depth_max:
            return None

        if self.row.depth_units == Depth.HundredthsOfMillimeter and (self.is_dent or self.is_metal_loss):
            return float(self.row.depth_max) / 100.0

        # Depth.PercentWallThickness
        if self.is_dent:
            return self.pipe.diameter * float(self.row.depth_max) / 100.0

        return (self.pipe.thick / 10.0) * float(self.row.depth_max) / 100.0

    @property
    def number_at_pipe(self):
        """Return object number at pipe as integer."""
        return self.pipe.defects.index(self) + 1

    @property
    def is_metal_loss(self):
        """Return True if metal loss defect."""
        return self.code in self.row.mloss_codes()

    @property
    def is_dent(self):
        """Return True if dent defect."""
        return self.code in self.row.dents_codes()

    @property
    def is_at_weld(self):
        """Return True if weld placed defect."""
        return self.code in self.row.atweld_codes()

    @property
    def is_at_seam(self):
        """Return True if seam placed defect."""
        return self.code in self.row.atseam_codes()

    def _with_mp(prop):  # pylint: disable=no-self-argument
        """Return decorator for property.

        https://stackoverflow.com/questions/1263451/python-decorators-in-classes
        """
        def wrapper(self):
            """Return None if defect does not have maximum depth point, or defect is located on a seam/weld."""
            if self.is_at_weld or self.is_at_seam or (not self.row.mpoint_dist):
                return None
            return prop(self)  # pylint: disable=not-callable

        return wrapper

    @property
    @_with_mp
    def mp_left_weld(self):
        """Return distance (mm) from maximum depth point to upstream weld."""
        return int(self.row.mpoint_dist) - self.pipe.dist

    @property
    @_with_mp
    def mp_right_weld(self):
        """Return distance (mm) from maximum depth point to downstream weld."""
        return self.pipe.dist + self.pipe.length - int(self.row.mpoint_dist)

    @property
    @_with_mp
    def mp_seam(self):
        """Return distance (angle minutes) from maximum depth point to nearest seam."""
        if not self.pipe.to_seam_data:
            return None

        mpoint = Orientation.from_csv(self.row.mpoint_orient)
        dist = mpoint.dist_to(self.pipe.seam1)
        if self.pipe.seam2:
            dist = min(dist, mpoint.dist_to(self.pipe.seam2))

        return self.pipe.minutes2mm(dist)

    @property
    @_with_mp
    def mp_seam_weld(self):
        """Return distance (mm) from maximum depth point to nearest seam/weld.

        If the defect does not have maximum depth point, return None.
        """
        values = [i for i in [self.mp_seam, self.mp_left_weld, self.mp_right_weld] if i is not None]
        return min(values)

    def get_to_seams(self, orient):
        """Return distance (mm) from given orientation to pipe seams."""
        to_seam1, to_seam2 = None, None
        if orient:
            to_seam1 = orient.dist_to(self.pipe.seam1)
            if self.pipe.seam2:
                to_seam2 = orient.dist_to(self.pipe.seam2)

        return (to_seam1, to_seam2)

    @property
    def to_seam(self):
        """Return distance (mm) from defect borders to nearest seam or None if pipe does not have seams."""
        if not self.pipe.to_seam_data:
            return None

        if self.orient1 and self.orient2:
            if self.pipe.seam1.is_inside(self.orient1, self.orient2):
                return 0
            if self.pipe.seam2:
                if self.pipe.seam2.is_inside(self.orient1, self.orient2):
                    return 0

        up_seam1, up_seam2 = self.get_to_seams(self.orient1)
        dn_seam1, dn_seam2 = self.get_to_seams(self.orient2)
        dists = [i for i in [up_seam1, up_seam2, dn_seam1, dn_seam2] if i is not None]
        if not dists:
            return None

        return min(dists)

    @property
    def to_seam_weld(self):
        """Return distance (mm) from defect borders to nearest seam/weld.

        None if pipe does not have seams.
        """
        values = [i for i in [self.to_seam, self.to_left_weld, self.to_right_weld] if i is not None]
        return min(values)

    @property
    def orientation_point(self):
        """Return orientation for defect as point.

        maximum depth point orientation if mp is present
        appropriate orientation if only one from orient1/orient2 is present
        middle point orientation if both orient1 and orient2 is present
        None if no maximum depth point and both orient1 and orient2 is None
        """
        if self.row.mpoint_orient:
            return Orientation.from_csv(self.row.mpoint_orient)

        ornts = [i for i in [self.orient1, self.orient2] if i is not None]

        if len(ornts) == 1:
            return ornts[0]
        if len(ornts) == 2:
            clockwise, _ = self.orient1.dist_to_int(self.orient2)
            ornt = Orientation.from_minutes(self.orient1.as_minutes)
            ornt.add_minutes(int(clockwise / 2))
            return ornt

        return None
