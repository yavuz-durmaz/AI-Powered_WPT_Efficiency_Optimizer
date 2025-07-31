"""
Data models for the AI-Powered WPT Efficiency Optimizer
"""
from dataclasses import dataclass
import math


@dataclass
class CoilParameters:
    """Data class for coil parameters"""
    turns: int
    wire_diameter: float  # mm
    wire_spacing: float  # mm
    outer_diameter: float  # mm
    
    @property
    def inner_diameter(self) -> float:
        """Calculate inner diameter"""
        return self.outer_diameter - (2 * self.turns * (self.wire_diameter + self.wire_spacing))
    
    @property
    def wire_length(self) -> float:
        """Calculate wire length in meters"""
        return (math.pi * self.turns * (self.outer_diameter + self.inner_diameter)) / 2000


@dataclass
class SystemParameters:
    """Data class for system parameters"""
    coupling_coefficient: float
    tx_coil: CoilParameters
    rx_coil: CoilParameters
    equivalent_resistance: float
    mosfet_count: int
    diode_count: int
    
    # Current and voltage parameters
    id_rms: float
    vds: float
    ids: float
    i_coil: float
    id_eff: float
    id_mean: float
    vd: float
    
    # Resistance per unit
    r1_unit: float
    r2_unit: float


@dataclass
class OptimizationResults:
    """Data class for optimization results"""
    best_frequency: float
    best_loss: float
    best_mosfet_name: str
    best_diode_name: str
    mosfet_loss: float
    diode_loss: float
    coil_loss: float
    tx_inductance: float
    rx_inductance: float
    tx_resistance: float
    rx_resistance: float
    system_efficiency: float