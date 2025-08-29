#  Copyright (c) 2024 Ubiterra Corporation. All rights reserved.
#  #
#  This ZoneVu Python SDK software is the property of Ubiterra Corporation.
#  You shall use it only in accordance with the terms of the ZoneVu Service Agreement.
#  #
#  This software is made available on PyPI for download and use. However, it is NOT open source.
#  Unauthorized copying, modification, or distribution of this software is strictly prohibited.
#  #
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
#  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
#  PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
#  FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#  ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
#
#
#

"""
Well log curve definition and samples.

Metadata for a measured curve and optional sampled data arrays.
"""

from typing import Optional, Iterator, Tuple
from dataclasses import dataclass, field
from dataclasses_json import config
from ...datamodels.DataModel import DataModel
import numpy as np
from strenum import StrEnum



class AppMnemonicCodeEnum(StrEnum):
    """Common application mnemonic codes for curves (DEPT, GR, ROP, etc.)."""
    NotSet = "NotSet"
    DEPT = "DEPT"  # Hole depth (MD)
    GR = "GR"  # Gamma ray
    ROP = "ROP"  # Rate of penetration
    WOB = "WOB"  # Weight on bit
    INCL = "INCL"  # Inclination
    AZIM = "AZIM"  # Azimuth
    GAS = "GAS"  # Total Gas
    BIT = "BIT"  # Bit depth
    GRDEPT = "GRDEPT"  # Gamma ray depth
    DENS = "DENS"  # Density
    RESS = "RESS"  # Shallow Resistivity
    RESM = "RESM"  # Medium Resistivity
    RESD = "RESD"  # Deep Resistivity
    DTC = "DTC"  # Compressional Sonic Travel Time
    DTS = "DTS"  # Shear Sonic Travel Time
    SP = "SP"  # Spontaneous Potential
    # Updated names aligned to C#: keep back-compat aliases
    NPHI = "NPHI"  # Neutron Porosity
    DPHI = "DPHI"  # Density Porosity
    PHIN = "NPHI"  # Back-compat alias
    PHID = "DPHI"  # Back-compat alias
    NMR = "NMR"  # Nuclear Magnetic Resonance
    PE = "PE"  # Photoelectric cross section
    AGR = "AGR"  # Azimuthal Gamma Ray
    # Porosity indicators
    Porosity = "Porosity"  # Effective Porosity (C# enum)
    PHIE = "PHIE"  # Existing code path retained
    SW = "SW"  # Water Saturation
    VSHL = "VSHL"  # Shale Content
    HCP = "HCP"  # HydocarbonPorosity
    # Frac/microseismic and stage metrics
    Prop_per_Stage = "Prop_per_Stage"
    Prop_per_Length = "Prop_per_Length"
    Water_Vol = "Water_Vol"
    Pressure = "Pressure"
    Slurry_Rate = "Slurry_Rate"
    BH_Press = "BH_Press"
    TIME = "TIME"  # Time (UTC)
    Break_Press = "Break_Press"
    Closure_Press = "Closure_Press"
    Closure_Grad = "Closure_Grad"
    Surf_Press = "Surf_Press"
    Max_Surf_Press = "Max_Surf_Press"
    Max_BH_Press = "Max_BH_Press"
    ISIP = "ISIP"
    Frac_Grad = "Frac_Grad"
    Depth_TVD = "Depth_TVD"
    Slurry_Vol = "Slurry_Vol"
    Prop_Conc = "Prop_Conc"
    Max_Prop_Conc = "Max_Prop_Conc"
    BHPSL = "BHPSL"
    User_1 = "User_1"
    User_2 = "User_2"
    User_3 = "User_3"
    User_4 = "User_4"
    User_5 = "User_5"
    User_6 = "User_6"
    User_7 = "User_7"
    User_8 = "User_8"
    User_9 = "User_9"
    User_10 = "User_10"
    User_11 = "User_11"
    User_12 = "User_12"
    User_13 = "User_13"
    User_14 = "User_14"
    User_15 = "User_15"
    User_16 = "User_16"
    User_17 = "User_17"
    User_18 = "User_18"
    User_19 = "User_19"
    User_20 = "User_20"
    FR = "FR"
    Acid = "Acid"
    pH = "pH"
    Target_Depth = "Target_Depth"
    Water_Salinity = "Water_Salinity"
    Max_Dog_Leg = "Max_Dog_Leg"
    Dog_Leg = "Dog_Leg"
    Duration = "Duration"
    Scrn_Out = "Scrn_Out"
    Frac_Hit = "Frac_Hit"
    MSE = "MSE"
    Deprecated_Torque_Torque = "Deprecated_Torque_Torque"
    Deprecated_Slide_Rotate_Slide = "Deprecated_Slide_Rotate_Slide"
    Temp = "Temp"
    SLIDE = "SLIDE"
    TORQUE = "TORQUE"
    # Mudlogs lithology
    Sandstone = "Sandstone"
    Sandstone_Bedded = "Sandstone_Bedded"
    Shaly_Sand = "Shaly_Sand"
    Calcareous_Sandstone = "Calcareous_Sandstone"
    Shale = "Shale"
    Sandy_Shale = "Sandy_Shale"
    Siltstone = "Siltstone"
    Mudstone_Rich = "Mudstone_Rich"
    Mudstone_Lean = "Mudstone_Lean"
    Limestone = "Limestone"
    Shaly_Limestone = "Shaly_Limestone"
    Sandy_Limestone = "Sandy_Limestone"
    Marl = "Marl"
    Dolomite = "Dolomite"
    Shaly_Dolostone = "Shaly_Dolostone"
    Sandy_Dolostone = "Sandy_Dolostone"
    Limestone_Shale = "Limestone_Shale"
    Shale_Sandstone = "Shale_Sandstone"
    Sandstone_Shale = "Sandstone_Shale"
    Shale_Limestone = "Shale_Limestone"
    Anhydrite = "Anhydrite"
    Bentonite = "Bentonite"
    Salt = "Salt"
    Chalk = "Chalk"
    Chert = "Chert"
    Cherty_Shale = "Cherty_Shale"
    Coal = "Coal"
    Breccia = "Breccia"
    Conglomerate = "Conglomerate"
    Basalt = "Basalt"
    Granite = "Granite"
    Igneous = "Igneous"
    Tuff = "Tuff"
    CUT = "CUT"
    FLU = "FLU"
    # Gas Logs
    C1 = "C1"
    C2 = "C2"
    C3 = "C3"
    C4 = "C4"
    C5 = "C5"
    C6 = "C6"
    CO2 = "CO2"
    H2S = "H2S"
    H = "H"
    # XRD Logs
    Quartz = "Quartz"
    K_Spar = "K_Spar"
    Plag = "Plag"
    Calcite = "Calcite"
    Pyrite = "Pyrite"
    TOT_Clay = "TOT_Clay"
    TOT_Carb = "TOT_Carb"
    QTZ_FSPR = "QTZ_FSPR"
    BI = "BI"
    # XRF Logs common channels
    Light_Elements = "Light_Elements"
    Majors = "Majors"
    Majors_LE = "Majors_LE"
    Al = "Al"
    As = "As"
    Ba = "Ba"
    Ca = "Ca"
    Cl = "Cl"
    Co = "Co"
    Cr = "Cr"
    Cu = "Cu"
    Fe = "Fe"
    K = "K"
    Mg = "Mg"
    Mn = "Mn"
    Mo = "Mo"
    Ni = "Ni"
    P = "P"
    Pb = "Pb"
    Rb = "Rb"
    S = "S"
    Si = "Si"
    Sr = "Sr"
    Th = "Th"
    Ti = "Ti"
    U = "U"
    V = "V"
    Zn = "Zn"
    Zr = "Zr"
    # Additional drilling/mudlog attributes
    FLARE = "FLARE"
    Ash = "Ash"
    Calcite_Fracture = "Calcite_Fracture"
    Carbonaceous_Shale = "Carbonaceous_Shale"
    TOC = "TOC"
    Ar = "Ar"
    Br = "Br"
    He = "He"
    Na = "Na"
    Caliper = "Caliper"
    Gypsum = "Gypsum"
    Silty_Dolostone = "Silty_Dolostone"
    Silty_Limestone = "Silty_Limestone"
    Silty_Sandstone = "Silty_Sandstone"
    Silty_Shale = "Silty_Shale"
    SPHI = "SPHI"
    # FR chemicals volumes/mass
    FR_Fluid_Volume = "FR_Fluid_Volume"
    FR_Powder_Mass = "FR_Powder_Mass"
    Biocide_Volume = "Biocide_Volume"
    Clay_Stabilizer_Volume = "Clay_Stabilizer_Volume"
    Scale_Inhibitor_Volume = "Scale_Inhibitor_Volume"
    # Timing/geometry metrics
    Time_To_Max_Injection_Rate = "Time_To_Max_Injection_Rate"
    Frac_Length_Up = "Frac_Length_Up"
    Frac_Length_Down = "Frac_Length_Down"
    Frac_Length_Left = "Frac_Length_Left"
    Frac_Length_Right = "Frac_Length_Right"
    Frac_Wing_Angle = "Frac_Wing_Angle"
    Frac_Quality = "Frac_Quality"
    Target_Top_Tvd_Max = "Target_Top_Tvd_Max"
    Target_Top_Tvd_Avg = "Target_Top_Tvd_Avg"
    Target_Base_Tvd_Max = "Target_Base_Tvd_Max"
    Target_Base_Tvd_Avg = "Target_Base_Tvd_Avg"

    @classmethod
    def _missing_(cls, value):
        return AppMnemonicCodeEnum.NotSet


@dataclass(eq=False)
class Curve(DataModel):
    """Well log curve definition with optional sampled values and units."""
    description: Optional[str] = None
    mnemonic: str = ''
    system_mnemonic: AppMnemonicCodeEnum = field(default_factory=lambda: AppMnemonicCodeEnum.NotSet)
    channel_index: Optional[int] = None
    unit: Optional[str] = None
    depths: Optional[np.ndarray] = field(default=None, metadata=config(encoder=lambda x: None, decoder=lambda x: []))
    samples: Optional[np.ndarray] = field(default=None, metadata=config(encoder=lambda x: None, decoder=lambda x: []))

    def __eq__(self, other: object):
        if not isinstance(other, Curve):
            return False

        fields_same = self.description == other.description and self.mnemonic == other.mnemonic and \
                      self.system_mnemonic == other.system_mnemonic and self.channel_index == other.channel_index and \
                      self.unit == other.unit
        samples_same = False
        if self.samples is None and other.samples is None:
            samples_same = True
        elif self.samples is not None and other.samples is not None:
            samples_same = np.array_equal(self.samples, other.samples)
        same = fields_same and samples_same
        return same

    def get_tuples(self) -> Iterator[Tuple[float, float]]:
        """
        Iterate tuples of (depth, value) from the curve depths and samples arrays
        """
        if self.samples is None or self.depths is None:
            return
        for depth, value in zip(self.depths, self.samples):
            yield depth, value
