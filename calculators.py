"""
Calculator classes for component loss calculations
"""
import math
import pandas as pd
from data_models import CoilParameters, SystemParameters


class ComponentCalculator:
    """Handles calculations for different components"""
    
    @staticmethod
    def calculate_coil_inductance(coil: CoilParameters) -> float:
        """Calculate coil inductance using Wheeler's formula"""
        inner_inches = coil.inner_diameter / 25.4
        width_inches = (coil.wire_spacing / 25.4 + coil.wire_diameter / 25.4) * coil.turns
        avg_radius = (inner_inches + width_inches) / 2
        
        inductance = ((avg_radius ** 2) * coil.turns ** 2) / (8 * avg_radius + 11 * width_inches) * 10**(-6)
        return inductance
    
    @staticmethod
    def calculate_coil_resistance(coil: CoilParameters, resistance_per_unit: float) -> float:
        """Calculate coil resistance"""
        return coil.wire_length * resistance_per_unit


class MOSFETLossCalculator:
    """Handles MOSFET loss calculations"""
    
    @staticmethod
    def calculate_conduction_loss(rdson: float, id_rms: float) -> float:
        """Calculate conduction loss"""
        return rdson * id_rms ** 2
    
    @staticmethod
    def calculate_switching_loss(tr: float, tf: float, vds: float, ids: float, frequency: float) -> float:
        """Calculate switching loss"""
        return (vds * ids * (tr + tf) * frequency) / 2
    
    @staticmethod
    def calculate_gate_loss(qg: float, vgs_max: float, frequency: float) -> float:
        """Calculate gate loss"""
        return qg * vgs_max * frequency
    
    @staticmethod
    def calculate_reverse_recovery_loss(qrr: float, vsd: float, frequency: float) -> float:
        """Calculate reverse recovery loss"""
        return (qrr * vsd * frequency) / 2
    
    @classmethod
    def calculate_total_loss(cls, mosfet_data: pd.Series, system_params: SystemParameters, frequency: float) -> float:
        """Calculate total MOSFET loss"""
        rdson = mosfet_data.iloc[4] * 10**(-3)
        vsd = mosfet_data.iloc[5]
        vgs_max = mosfet_data.iloc[6]
        tr = mosfet_data.iloc[7] * 10**(-9)
        tf = mosfet_data.iloc[8] * 10**(-9)
        qg = mosfet_data.iloc[9] * 10**(-9)
        qrr = mosfet_data.iloc[10] * 10**(-9)
        
        conduction_loss = cls.calculate_conduction_loss(rdson, system_params.id_rms)
        switching_loss = cls.calculate_switching_loss(tr, tf, system_params.vds, system_params.ids, frequency)
        gate_loss = cls.calculate_gate_loss(qg, vgs_max, frequency)
        reverse_recovery_loss = cls.calculate_reverse_recovery_loss(qrr, vsd, frequency)
        
        total_loss = (conduction_loss + switching_loss + gate_loss + reverse_recovery_loss) * system_params.mosfet_count
        return total_loss


class DiodeLossCalculator:
    """Handles diode loss calculations"""
    
    @staticmethod
    def calculate_conduction_loss(rd: float, vf: float, id_eff: float, id_mean: float) -> float:
        """Calculate diode conduction loss"""
        return rd * id_eff**2 + vf * id_mean
    
    @staticmethod
    def calculate_switching_loss(qc: float, vd: float, frequency: float) -> float:
        """Calculate diode switching loss"""
        return qc * vd * frequency
    
    @staticmethod
    def calculate_reverse_recovery_loss(qrr: float, vd: float, frequency: float) -> float:
        """Calculate diode reverse recovery loss"""
        return (qrr * vd * frequency) / 2
    
    @classmethod
    def calculate_total_loss(cls, diode_data: pd.Series, system_params: SystemParameters, frequency: float) -> float:
        """Calculate total diode loss"""
        vf = diode_data.iloc[4]
        qrr = 0  # Assuming 0 for reverse recovery charge
        c_d = diode_data.iloc[5] * 10**(-12)
        
        qc = system_params.vd * c_d
        rd = vf / system_params.id_mean
        
        conduction_loss = cls.calculate_conduction_loss(rd, vf, system_params.id_eff, system_params.id_mean)
        switching_loss = cls.calculate_switching_loss(qc, system_params.vd, frequency)
        reverse_recovery_loss = cls.calculate_reverse_recovery_loss(qrr, system_params.vd, frequency)
        
        total_loss = (conduction_loss + switching_loss + reverse_recovery_loss) * system_params.diode_count
        return total_loss


class CoilLossCalculator:
    """Handles coil loss calculations"""
    
    @staticmethod
    def calculate_efficiency(system_params: SystemParameters, frequency: float, 
                           tx_inductance: float, rx_inductance: float,
                           tx_resistance: float, rx_resistance: float) -> float:
        """Calculate coil efficiency"""
        k = system_params.coupling_coefficient
        req = system_params.equivalent_resistance
        
        numerator = req * tx_inductance * rx_inductance * (2 * math.pi * frequency * k)**2
        denominator = ((rx_resistance + req) * 
                      (tx_resistance * (rx_resistance + req) + 
                       (2 * math.pi * frequency * k)**2 * tx_inductance * rx_inductance))
        
        return numerator / denominator
    
    @classmethod
    def calculate_loss(cls, system_params: SystemParameters, frequency: float,
                      tx_inductance: float, rx_inductance: float,
                      tx_resistance: float, rx_resistance: float) -> float:
        """Calculate coil loss"""
        efficiency = cls.calculate_efficiency(system_params, frequency, tx_inductance, rx_inductance,
                                            tx_resistance, rx_resistance)
        coil_power = system_params.vds * system_params.i_coil
        return coil_power * (1 - efficiency)
