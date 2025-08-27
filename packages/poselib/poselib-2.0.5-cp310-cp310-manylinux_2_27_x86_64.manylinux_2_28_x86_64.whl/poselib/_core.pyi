"""
This library provides a collection of minimal solvers for camera pose estimation.
"""

from __future__ import annotations
import collections.abc
import numpy
import numpy.typing
import typing

__all__: list[str] = [
    "BundleOptions",
    "Camera",
    "CameraPose",
    "Image",
    "ImagePair",
    "PairwiseMatches",
    "RansacOptions",
    "essential_matrix_5pt",
    "essential_matrix_8pt",
    "estimate_1D_radial_absolute_pose",
    "estimate_absolute_pose",
    "estimate_absolute_pose_pnpl",
    "estimate_fundamental",
    "estimate_generalized_absolute_pose",
    "estimate_generalized_relative_pose",
    "estimate_homography",
    "estimate_hybrid_pose",
    "estimate_relative_pose",
    "estimate_shared_focal_relative_pose",
    "focals_from_fundamental",
    "focals_from_fundamental_iterative",
    "gen_relpose_6pt",
    "gen_relpose_upright_4pt",
    "gp3p",
    "gp4ps",
    "gp4ps_camposeco",
    "gp4ps_kukelova",
    "motion_from_homography",
    "p1p2ll",
    "p2p1ll",
    "p2p2pl",
    "p3ll",
    "p3p",
    "p4pf",
    "p5lp_radial",
    "p6lp",
    "refine_absolute_pose",
    "refine_absolute_pose_pnpl",
    "refine_fundamental",
    "refine_generalized_absolute_pose",
    "refine_generalized_relative_pose",
    "refine_homography",
    "refine_relative_pose",
    "relpose_5pt",
    "relpose_8pt",
    "relpose_upright_3pt",
    "relpose_upright_planar_2pt",
    "relpose_upright_planar_3pt",
    "shared_focal_relpose_6pt",
    "ugp2p",
    "ugp3ps",
    "ugp4pl",
    "up1p2pl",
    "up2p",
    "up4pl",
]

class Camera:
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(
        self,
        arg0: str,
        arg1: collections.abc.Sequence[typing.SupportsFloat],
        arg2: typing.SupportsInt,
        arg3: typing.SupportsInt,
    ) -> None: ...
    def __repr__(self) -> str: ...
    def focal(self) -> float:
        """
        Returns the camera focal length.
        """
    def focal_x(self) -> float:
        """
        Returns the camera focal_x.
        """
    def focal_y(self) -> float:
        """
        Returns the camera focal_y.
        """
    def initialize_from_txt(self, arg0: str) -> int:
        """
        Initialize camera from a cameras.txt line
        """
    def model_name(self) -> str:
        """
        Returns the camera model name.
        """
    def principal_point(
        self,
    ) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        Returns the camera principal point.
        """
    def project(
        self, arg0: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"]
    ) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[m, 2]"]: ...
    def project_with_jac(
        self, arg0: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"]
    ) -> tuple[
        typing.Annotated[numpy.typing.NDArray[numpy.float64], "[m, 2]"],
        list[typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 2]"]],
    ]: ...
    def unproject(
        self, arg0: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"]
    ) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[m, 2]"]: ...
    @property
    def height(self) -> int: ...
    @height.setter
    def height(self, arg0: typing.SupportsInt) -> None: ...
    @property
    def model_id(self) -> int: ...
    @model_id.setter
    def model_id(self, arg0: typing.SupportsInt) -> None: ...
    @property
    def params(self) -> list[float]: ...
    @params.setter
    def params(self, arg0: collections.abc.Sequence[typing.SupportsFloat]) -> None: ...
    @property
    def width(self) -> int: ...
    @width.setter
    def width(self, arg0: typing.SupportsInt) -> None: ...

class CameraPose:
    def __init__(self) -> None: ...
    def __repr__(self) -> str: ...
    def center(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[3, 1]"]:
        """
        Returns the camera center (c=-R^T*t).
        """
    @property
    def R(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[3, 3]"]: ...
    @R.setter
    def R(
        self, arg1: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[3, 3]"]
    ) -> None: ...
    @property
    def Rt(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[3, 4]"]: ...
    @Rt.setter
    def Rt(
        self, arg1: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[3, 4]"]
    ) -> None: ...
    @property
    def q(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[4, 1]"]: ...
    @q.setter
    def q(
        self, arg0: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[4, 1]"]
    ) -> None: ...
    @property
    def t(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[3, 1]"]: ...
    @t.setter
    def t(
        self, arg0: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[3, 1]"]
    ) -> None: ...

class Image:
    camera: Camera
    pose: CameraPose
    def __init__(self) -> None: ...
    def __repr__(self) -> str: ...

class ImagePair:
    camera1: Camera
    camera2: Camera
    pose: CameraPose
    def __init__(self) -> None: ...
    def __repr__(self) -> str: ...

class PairwiseMatches:
    def __init__(self) -> None: ...
    def __repr__(self) -> str: ...
    @property
    def cam_id1(self) -> int: ...
    @cam_id1.setter
    def cam_id1(self, arg0: typing.SupportsInt) -> None: ...
    @property
    def cam_id2(self) -> int: ...
    @cam_id2.setter
    def cam_id2(self, arg0: typing.SupportsInt) -> None: ...
    @property
    def x1(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[m, 2]"]: ...
    @x1.setter
    def x1(
        self, arg0: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"]
    ) -> None: ...
    @property
    def x2(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[m, 2]"]: ...
    @x2.setter
    def x2(
        self, arg0: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"]
    ) -> None: ...

def BundleOptions(opt: dict = {}) -> dict:
    """
    Options for non-linear refinement.
    """

def RansacOptions(opt: dict = {}) -> dict:
    """
    Options for RANSAC.
    """

def essential_matrix_5pt(
    x1: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    x2: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
) -> list[typing.Annotated[numpy.typing.NDArray[numpy.float64], "[3, 3]"]]: ...
def essential_matrix_8pt(
    x1: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    x2: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[3, 3]"]: ...
def estimate_1D_radial_absolute_pose(
    points2D: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"],
    points3D: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    ransac_opt: dict = {},
    bundle_opt: dict = {},
    initial_pose: CameraPose | None = None,
) -> tuple[CameraPose, dict]:
    """
    Absolute pose estimation for the 1D radial camera model with non-linear refinement.
    """

@typing.overload
def estimate_absolute_pose(
    points2D: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"],
    points3D: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    camera: Camera,
    ransac_opt: dict = {},
    bundle_opt: dict = {},
    initial_pose: CameraPose | None = None,
) -> tuple[CameraPose, dict]:
    """
    Absolute pose estimation with non-linear refinement.
    """

@typing.overload
def estimate_absolute_pose(
    points2D: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"],
    points3D: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    camera_dict: dict,
    ransac_opt: dict = {},
    bundle_opt: dict = {},
    initial_pose: CameraPose | None = None,
) -> tuple[CameraPose, dict]:
    """
    Absolute pose estimation with non-linear refinement.
    """

@typing.overload
def estimate_absolute_pose_pnpl(
    points2D: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"],
    points3D: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    lines2D_1: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"],
    lines2D_2: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"],
    lines3D_1: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    lines3D_2: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    camera: Camera,
    ransac_opt: dict = {},
    bundle_opt: dict = {},
    initial_pose: CameraPose | None = None,
) -> tuple[CameraPose, dict]:
    """
    Absolute pose estimation with non-linear refinement from points and lines.
    """

@typing.overload
def estimate_absolute_pose_pnpl(
    points2D: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"],
    points3D: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    lines2D_1: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"],
    lines2D_2: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"],
    lines3D_1: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    lines3D_2: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    camera_dict: dict,
    ransac_opt: dict = {},
    bundle_opt: dict = {},
    initial_pose: CameraPose | None = None,
) -> tuple[CameraPose, dict]:
    """
    Absolute pose estimation with non-linear refinement from points and lines.
    """

def estimate_fundamental(
    points2D_1: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"],
    points2D_2: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"],
    ransac_opt: dict = {},
    bundle_opt: dict = {},
    initial_F: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[3, 3]"]
    | None = None,
) -> tuple[typing.Annotated[numpy.typing.NDArray[numpy.float64], "[3, 3]"], dict]:
    """
    Fundamental matrix estimation with non-linear refinement. Note: if you have known intrinsics you should use estimate_relative_pose instead!
    """

@typing.overload
def estimate_generalized_absolute_pose(
    points2D: collections.abc.Sequence[
        typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"]
    ],
    points3D: collections.abc.Sequence[
        typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"]
    ],
    camera_ext: collections.abc.Sequence[CameraPose],
    cameras: collections.abc.Sequence[Camera],
    ransac_opt: dict = {},
    bundle_opt: dict = {},
    initial_pose: CameraPose | None = None,
) -> tuple[CameraPose, dict]:
    """
    Generalized absolute pose estimation with non-linear refinement.
    """

@typing.overload
def estimate_generalized_absolute_pose(
    points2D: collections.abc.Sequence[
        typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"]
    ],
    points3D: collections.abc.Sequence[
        typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"]
    ],
    camera_ext: collections.abc.Sequence[CameraPose],
    camera_dicts: collections.abc.Sequence[dict],
    ransac_opt: dict = {},
    bundle_opt: dict = {},
    initial_pose: CameraPose | None = None,
) -> tuple[CameraPose, dict]:
    """
    Generalized absolute pose estimation with non-linear refinement.
    """

@typing.overload
def estimate_generalized_relative_pose(
    matches: collections.abc.Sequence[PairwiseMatches],
    camera1_ext: collections.abc.Sequence[CameraPose],
    cameras1: collections.abc.Sequence[Camera],
    camera2_ext: collections.abc.Sequence[CameraPose],
    cameras2: collections.abc.Sequence[Camera],
    ransac_opt: dict = {},
    bundle_opt: dict = {},
    initial_pose: CameraPose | None = None,
) -> tuple[CameraPose, dict]:
    """
    Generalized relative pose estimation with non-linear refinement.
    """

@typing.overload
def estimate_generalized_relative_pose(
    matches: collections.abc.Sequence[PairwiseMatches],
    camera1_ext: collections.abc.Sequence[CameraPose],
    camera1_dict: collections.abc.Sequence[dict],
    camera2_ext: collections.abc.Sequence[CameraPose],
    camera2_dict: collections.abc.Sequence[dict],
    ransac_opt: dict = {},
    bundle_opt: dict = {},
    initial_pose: CameraPose | None = None,
) -> tuple[CameraPose, dict]:
    """
    Generalized relative pose estimation with non-linear refinement.
    """

def estimate_homography(
    points2D_1: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"],
    points2D_2: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"],
    ransac_opt: dict = {},
    bundle_opt: dict = {},
    initial_H: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[3, 3]"]
    | None = None,
) -> tuple[typing.Annotated[numpy.typing.NDArray[numpy.float64], "[3, 3]"], dict]:
    """
    Homography matrix estimation with non-linear refinement.
    """

@typing.overload
def estimate_hybrid_pose(
    points2D: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"],
    points3D: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    matches_2D_2D: collections.abc.Sequence[PairwiseMatches],
    camera: Camera,
    map_ext: collections.abc.Sequence[CameraPose],
    map_cameras: collections.abc.Sequence[Camera],
    ransac_opt: dict = {},
    bundle_opt: dict = {},
    initial_pose: CameraPose | None = None,
) -> tuple[CameraPose, dict]:
    """
    Hybrid camera pose estimation (both 2D-3D and 2D-2D correspondences to the map) with non-linear refinement.
    """

@typing.overload
def estimate_hybrid_pose(
    points2D: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"],
    points3D: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    matches_2D_2D: collections.abc.Sequence[PairwiseMatches],
    camera_dict: dict,
    map_ext: collections.abc.Sequence[CameraPose],
    map_camera_dicts: collections.abc.Sequence[dict],
    ransac_opt: dict = {},
    bundle_opt: dict = {},
    initial_pose: CameraPose | None = None,
) -> tuple[CameraPose, dict]:
    """
    Hybrid camera pose estimation (both 2D-3D and 2D-2D correspondences to the map) with non-linear refinement.
    """

@typing.overload
def estimate_relative_pose(
    points2D_1: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"],
    points2D_2: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"],
    camera1: Camera,
    camera2: Camera,
    ransac_opt: dict = {},
    bundle_opt: dict = {},
    initial_pose: CameraPose | None = None,
) -> tuple[CameraPose, dict]:
    """
    Relative pose estimation with non-linear refinement.
    """

@typing.overload
def estimate_relative_pose(
    points2D_1: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"],
    points2D_2: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"],
    camera1_dict: dict,
    camera2_dict: dict,
    ransac_opt: dict = {},
    bundle_opt: dict = {},
    initial_pose: CameraPose | None = None,
) -> tuple[CameraPose, dict]:
    """
    Relative pose estimation with non-linear refinement.
    """

def estimate_shared_focal_relative_pose(
    points2D_1: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"],
    points2D_2: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"],
    pp: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"] = ...,
    ransac_opt: dict = {},
    bundle_opt: dict = {},
    initial_image_pair: ImagePair | None = None,
) -> tuple[ImagePair, dict]:
    """
    Relative pose estimation with unknown equal focal lengths with non-linear refinement.
    """

def focals_from_fundamental(
    F: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[3, 3]"],
    pp1: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"],
    pp2: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"],
) -> tuple[Camera, Camera]: ...
@typing.overload
def focals_from_fundamental_iterative(
    F: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[3, 3]"],
    camera1: Camera,
    camera2: Camera,
    max_iters: typing.SupportsInt = 50,
    weights: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[4, 1]"] = ...,
) -> tuple[Camera, Camera, int]: ...
@typing.overload
def focals_from_fundamental_iterative(
    F: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[3, 3]"],
    camera1_dict: dict,
    camera2_dict: dict,
    max_iters: typing.SupportsInt = 50,
    weights: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[4, 1]"] = ...,
) -> tuple[Camera, Camera, int]: ...
def gen_relpose_6pt(
    p1: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    x1: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    p2: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    x2: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
) -> list[CameraPose]: ...
def gen_relpose_upright_4pt(
    p1: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    x1: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    p2: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    x2: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
) -> list[CameraPose]: ...
def gp3p(
    p: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    x: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    X: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
) -> list[CameraPose]: ...
def gp4ps(
    p: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    x: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    X: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    filter_solutions: bool,
) -> tuple[list[CameraPose], list[float]]: ...
def gp4ps_camposeco(
    p: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    x: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    X: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
) -> tuple[list[CameraPose], list[float]]: ...
def gp4ps_kukelova(
    p: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    x: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    X: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    filter_solutions: bool,
) -> tuple[list[CameraPose], list[float]]: ...
def motion_from_homography(
    H: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[3, 3]"],
) -> tuple[
    list[CameraPose], typing.Annotated[numpy.typing.NDArray[numpy.float64], "[m, 3]"]
]: ...
def p1p2ll(
    xp: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    Xp: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    l: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    X: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    V: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
) -> list[CameraPose]: ...
def p2p1ll(
    xp: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    Xp: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    l: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    X: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    V: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
) -> list[CameraPose]: ...
def p2p2pl(
    xp: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    Xp: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    x: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    X: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    V: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
) -> list[CameraPose]: ...
def p3ll(
    l: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    X: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    V: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
) -> list[CameraPose]: ...
def p3p(
    x: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    X: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
) -> list[CameraPose]: ...
def p4pf(
    x: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"],
    X: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    filter_solutions: bool,
) -> tuple[list[CameraPose], list[float]]: ...
def p5lp_radial(
    l: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    X: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
) -> list[CameraPose]: ...
def p6lp(
    l: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    X: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
) -> list[CameraPose]: ...
@typing.overload
def refine_absolute_pose(
    points2D: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"],
    points3D: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    initial_pose: CameraPose,
    camera: Camera,
    bundle_options: dict = {},
) -> tuple[CameraPose, dict]:
    """
    Absolute pose non-linear refinement.
    """

@typing.overload
def refine_absolute_pose(
    points2D: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"],
    points3D: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    initial_pose: CameraPose,
    camera_dict: dict,
    bundle_options: dict = {},
) -> tuple[CameraPose, dict]:
    """
    Absolute pose non-linear refinement.
    """

@typing.overload
def refine_absolute_pose_pnpl(
    points2D: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"],
    points3D: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    lines2D_1: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"],
    lines2D_2: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"],
    lines3D_1: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    lines3D_2: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    initial_pose: CameraPose,
    camera: Camera,
    bundle_opt: dict = {},
    line_bundle_opt: dict = {},
) -> tuple[CameraPose, dict]:
    """
    Absolute pose non-linear refinement from points and lines.
    """

@typing.overload
def refine_absolute_pose_pnpl(
    points2D: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"],
    points3D: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    lines2D_1: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"],
    lines2D_2: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"],
    lines3D_1: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    lines3D_2: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    initial_pose: CameraPose,
    camera_dict: dict,
    bundle_opt: dict = {},
    line_bundle_opt: dict = {},
) -> tuple[CameraPose, dict]:
    """
    Absolute pose non-linear refinement from points and lines.
    """

def refine_fundamental(
    points2D_1: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"],
    points2D_2: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"],
    initial_F: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[3, 3]"],
    bundle_options: dict = {},
) -> tuple[typing.Annotated[numpy.typing.NDArray[numpy.float64], "[3, 3]"], dict]:
    """
    Fundamental matrix non-linear refinement.
    """

@typing.overload
def refine_generalized_absolute_pose(
    points2D: collections.abc.Sequence[
        typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"]
    ],
    points3D: collections.abc.Sequence[
        typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"]
    ],
    initial_pose: CameraPose,
    camera_ext: collections.abc.Sequence[CameraPose],
    cameras: collections.abc.Sequence[Camera],
    bundle_opt: dict = {},
) -> tuple[CameraPose, dict]:
    """
    Generalized absolute pose non-linear refinement.
    """

@typing.overload
def refine_generalized_absolute_pose(
    points2D: collections.abc.Sequence[
        typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"]
    ],
    points3D: collections.abc.Sequence[
        typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"]
    ],
    initial_pose: CameraPose,
    camera_ext: collections.abc.Sequence[CameraPose],
    camera_dicts: collections.abc.Sequence[dict],
    bundle_opt: dict = {},
) -> tuple[CameraPose, dict]:
    """
    Generalized absolute pose non-linear refinement.
    """

@typing.overload
def refine_generalized_relative_pose(
    matches: collections.abc.Sequence[PairwiseMatches],
    initial_pose: CameraPose,
    camera1_ext: collections.abc.Sequence[CameraPose],
    cameras1: collections.abc.Sequence[Camera],
    camera2_ext: collections.abc.Sequence[CameraPose],
    cameras2: collections.abc.Sequence[Camera],
    bundle_opt: dict = {},
) -> tuple[CameraPose, dict]:
    """
    Generalized relative pose non-linear refinement.
    """

@typing.overload
def refine_generalized_relative_pose(
    matches: collections.abc.Sequence[PairwiseMatches],
    initial_pose: CameraPose,
    camera1_ext: collections.abc.Sequence[CameraPose],
    camera1_dict: collections.abc.Sequence[dict],
    camera2_ext: collections.abc.Sequence[CameraPose],
    camera2_dict: collections.abc.Sequence[dict],
    bundle_opt: dict = {},
) -> tuple[CameraPose, dict]:
    """
    Generalized relative pose non-linear refinement.
    """

def refine_homography(
    points2D_1: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"],
    points2D_2: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"],
    initial_H: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[3, 3]"],
    bundle_options: dict = {},
) -> tuple[typing.Annotated[numpy.typing.NDArray[numpy.float64], "[3, 3]"], dict]:
    """
    Homography non-linear refinement.
    """

@typing.overload
def refine_relative_pose(
    points2D_1: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"],
    points2D_2: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"],
    initial_pose: CameraPose,
    camera1: Camera,
    camera2: Camera,
    bundle_options: dict = {},
) -> tuple[CameraPose, dict]:
    """
    Relative pose non-linear refinement.
    """

@typing.overload
def refine_relative_pose(
    points2D_1: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"],
    points2D_2: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 2]"],
    initial_pose: CameraPose,
    camera1_dict: dict,
    camera2_dict: dict,
    bundle_options: dict = {},
) -> tuple[CameraPose, dict]:
    """
    Relative pose non-linear refinement.
    """

def relpose_5pt(
    x1: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    x2: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
) -> list[CameraPose]: ...
def relpose_8pt(
    x1: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    x2: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
) -> list[CameraPose]: ...
def relpose_upright_3pt(
    x1: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    x2: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
) -> list[CameraPose]: ...
def relpose_upright_planar_2pt(
    x1: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    x2: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
) -> list[CameraPose]: ...
def relpose_upright_planar_3pt(
    x1: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    x2: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
) -> list[CameraPose]: ...
def shared_focal_relpose_6pt(
    x1: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    x2: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
) -> list[ImagePair]: ...
def ugp2p(
    p: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    x: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    X: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
) -> list[CameraPose]: ...
def ugp3ps(
    p: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    x: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    X: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    filter_solutions: bool,
) -> tuple[list[CameraPose], list[float]]: ...
def ugp4pl(
    p: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    x: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    X: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    V: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
) -> list[CameraPose]: ...
def up1p2pl(
    xp: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    Xp: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    x: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    X: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    V: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
) -> list[CameraPose]: ...
def up2p(
    x: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    X: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
) -> list[CameraPose]: ...
def up4pl(
    x: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    X: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
    V: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 3]"],
) -> list[CameraPose]: ...

__version__: str = "2.0.5"
