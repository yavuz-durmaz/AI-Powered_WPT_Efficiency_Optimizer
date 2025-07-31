"""
Optimization engine for the AI-Powered WPT Efficiency Optimizer
"""
import pandas as pd
from typing import List, Tuple, Callable, Optional
from pyswarm import pso

from data_models import SystemParameters, OptimizationResults
from calculators import ComponentCalculator, MOSFETLossCalculator, DiodeLossCalculator, CoilLossCalculator


class OptimizationEngine:
    """Handles the optimization process"""
    
    def __init__(self, system_params: SystemParameters, mosfet_df: pd.DataFrame, 
                 diode_df: pd.DataFrame, progress_callback: Optional[Callable[[float], None]] = None,
                 detailed_output_callback: Optional[Callable[[str], None]] = None):
        self.system_params = system_params
        self.mosfet_df = mosfet_df
        self.diode_df = diode_df
        self.progress_callback = progress_callback
        self.detailed_output_callback = detailed_output_callback
        
        # Calculate coil parameters
        self.tx_inductance = ComponentCalculator.calculate_coil_inductance(system_params.tx_coil)
        self.rx_inductance = ComponentCalculator.calculate_coil_inductance(system_params.rx_coil)
        self.tx_resistance = ComponentCalculator.calculate_coil_resistance(system_params.tx_coil, system_params.r1_unit)
        self.rx_resistance = ComponentCalculator.calculate_coil_resistance(system_params.rx_coil, system_params.r2_unit)
        
        # Results storage
        self.best_mosfet_idx = 0
        self.best_diode_idx = 0
        self.best_mosfet_loss = float('inf')
        self.best_diode_loss = float('inf')
        self.best_coil_loss = float('inf')
        
        # Counter for detailed output
        self.evaluation_count = 0
    
    def _add_detailed_output(self, text: str):
        """Add text to detailed output if callback is available"""
        if self.detailed_output_callback:
            self.detailed_output_callback(text)
    
    def objective_function(self, frequencies: List[float]) -> float:
        """Objective function for PSO optimization"""
        frequency = frequencies[0]
        self.evaluation_count += 1
        
        # Add frequency evaluation header
        self._add_detailed_output(f"\n{'='*20}\n")
        self._add_detailed_output(f"EVALUATION #{self.evaluation_count}\nFREQUENCY: {frequency:.3f} Hz\n")
        self._add_detailed_output(f"{'='*20}\n\n")
        
        # Calculate losses for all MOSFETs and find minimum
        mosfet_losses = []
        self._add_detailed_output("\nMOSFET ANALYSIS:\n" + "-"*20 + "\n")
        
        for idx, mosfet_row in self.mosfet_df.iterrows():
            # Get MOSFET parameters
            mosfet_name = mosfet_row.iloc[0]
            mosfet_price = mosfet_row.iloc[1]
            rdson = mosfet_row.iloc[4] * 10**(-3)
            vsd = mosfet_row.iloc[5]
            vgs_max = mosfet_row.iloc[6]
            tr = mosfet_row.iloc[7] * 10**(-9)
            tf = mosfet_row.iloc[8] * 10**(-9)
            qg = mosfet_row.iloc[9] * 10**(-9)
            qrr = mosfet_row.iloc[10] * 10**(-9)
            
            # Calculate individual losses
            conduction_loss = MOSFETLossCalculator.calculate_conduction_loss(rdson, self.system_params.id_rms)
            switching_loss = MOSFETLossCalculator.calculate_switching_loss(tr, tf, self.system_params.vds, self.system_params.ids, frequency)
            gate_loss = MOSFETLossCalculator.calculate_gate_loss(qg, vgs_max, frequency)
            reverse_recovery_loss = MOSFETLossCalculator.calculate_reverse_recovery_loss(qrr, vsd, frequency)
            
            # Total loss for this MOSFET
            mosfet_total_loss = (conduction_loss + switching_loss + gate_loss + reverse_recovery_loss) * self.system_params.mosfet_count
            price_performance = mosfet_total_loss * 0.5 + 0.5 * (mosfet_price / 20)
            
            # Add detailed output for this MOSFET
            self._add_detailed_output(f"MOSFET: {mosfet_name}\n")
            self._add_detailed_output(f"  Conduction Loss: {conduction_loss:.3f} W\n")
            self._add_detailed_output(f"  Switching Loss: {switching_loss:.3f} W\n")
            self._add_detailed_output(f"  Gate Loss: {gate_loss:.3f} W\n")
            self._add_detailed_output(f"  Reverse Recovery Loss: {reverse_recovery_loss:.3f} W\n")
            self._add_detailed_output(f"  Total Loss ({self.system_params.mosfet_count} units): {mosfet_total_loss:.3f} W\n")
            self._add_detailed_output(f"  Price/Performance Value: {price_performance:.3f}\n")
            self._add_detailed_output("-" * 40 + "\n")
            
            mosfet_losses.append(price_performance)
        
        # Calculate losses for all diodes and find minimum
        diode_losses = []
        self._add_detailed_output("\nDIODE ANALYSIS:\n" + "-"*40 + "\n")
        
        for idx, diode_row in self.diode_df.iterrows():
            # Get diode parameters
            diode_name = diode_row.iloc[0]
            diode_price = diode_row.iloc[1]
            vf = diode_row.iloc[4]
            c_d = diode_row.iloc[5] * 10**(-12)
            
            # Calculate diode parameters
            qrr = 0  # Assuming 0 for reverse recovery charge
            qc = self.system_params.vd * c_d
            rd = vf / self.system_params.id_mean
            
            # Calculate individual losses
            conduction_loss = DiodeLossCalculator.calculate_conduction_loss(rd, vf, self.system_params.id_eff, self.system_params.id_mean)
            switching_loss = DiodeLossCalculator.calculate_switching_loss(qc, self.system_params.vd, frequency)
            reverse_recovery_loss = DiodeLossCalculator.calculate_reverse_recovery_loss(qrr, self.system_params.vd, frequency)
            
            # Total loss for this diode
            diode_total_loss = (conduction_loss + switching_loss + reverse_recovery_loss) * self.system_params.diode_count
            price_performance = diode_total_loss * 0.5 + 0.5 * (diode_price / 20)
            
            # Add detailed output for this diode
            self._add_detailed_output(f"DIODE: {diode_name}\n")
            self._add_detailed_output(f"  Conduction Loss: {conduction_loss:.3f} W\n")
            self._add_detailed_output(f"  Switching Loss: {switching_loss:.3f} W\n")
            self._add_detailed_output(f"  Reverse Recovery Loss: {reverse_recovery_loss:.3f} W\n")
            self._add_detailed_output(f"  Total Loss ({self.system_params.diode_count} units): {diode_total_loss:.3f} W\n")
            self._add_detailed_output(f"  Price/Performance Value: {price_performance:.3f}\n")
            self._add_detailed_output("-" * 40 + "\n")
            
            diode_losses.append(price_performance)
        
        # Calculate coil loss
        coil_loss = CoilLossCalculator.calculate_loss(
            self.system_params, frequency, self.tx_inductance, self.rx_inductance,
            self.tx_resistance, self.rx_resistance
        )
        
        # Add coil loss output
        self._add_detailed_output(f"\nCOIL ANALYSIS:\n")
        self._add_detailed_output(f"  Coil Loss: {coil_loss:.3f} W\n")
        
        # Store best results
        min_mosfet_loss = min(mosfet_losses)
        min_diode_loss = min(diode_losses)
        total_loss = min_mosfet_loss + min_diode_loss + coil_loss
        
        # Add summary for this frequency
        self._add_detailed_output(f"\nFREQUENCY {frequency:.3f} Hz SUMMARY:\n")
        self._add_detailed_output(f"  Best MOSFET Value: {min_mosfet_loss:.3f}\n")
        self._add_detailed_output(f"  Best Diode Value: {min_diode_loss:.3f}\n")
        self._add_detailed_output(f"  Coil Loss: {coil_loss:.3f} W\n")
        self._add_detailed_output(f"  Total Objective: {total_loss:.3f}\n")
        
        if min_mosfet_loss < self.best_mosfet_loss:
            self.best_mosfet_loss = min_mosfet_loss
            self.best_mosfet_idx = mosfet_losses.index(min_mosfet_loss)
            self._add_detailed_output(f"\n  >>> NEW BEST MOSFET: {self.mosfet_df.iloc[self.best_mosfet_idx, 0]}\n")
        
        if min_diode_loss < self.best_diode_loss:
            self.best_diode_loss = min_diode_loss
            self.best_diode_idx = diode_losses.index(min_diode_loss)
            self._add_detailed_output(f"\n  >>> NEW BEST DIODE: {self.diode_df.iloc[self.best_diode_idx, 0]}\n")
        
        self.best_coil_loss = coil_loss
        
        if self.progress_callback:
            progress_value = min(0.7, 0.3 + (self.evaluation_count * 0.4 / 100))  # Gradual progress
            self.progress_callback(progress_value)
        
        return total_loss
    
    def optimize(self) -> Tuple[float, float]:
        """Run PSO optimization"""
        df = pd.read_excel('input_values.xlsx')
        lower_bounds = [int(df.iloc[21, 1])]
        upper_bounds = [int(df.iloc[22, 1])]
        pso_swarm_size = int(df.iloc[23, 1])
        pso_max_iter = int(df.iloc[24, 1])
        pso_min_step = float(df.iloc[25, 1])
        
        self._add_detailed_output(f"PSO AI Optimization Parameters:\n")
        self._add_detailed_output(f"  Frequency Range: {lower_bounds[0]} - {upper_bounds[0]} Hz\n")
        self._add_detailed_output(f"  Swarm Size: {pso_swarm_size}\n")
        self._add_detailed_output(f"  Max Iterations: {pso_max_iter}\n")
        self._add_detailed_output(f"  Min Step: {pso_min_step}\n\n")
        
        best_frequency, best_loss = pso(
            self.objective_function, 
            lower_bounds, 
            upper_bounds, 
            swarmsize=pso_swarm_size, 
            maxiter=pso_max_iter, 
            minstep=pso_min_step, 
            minfunc=False
        )
        
        # Add final optimization results to detailed output
        self._add_detailed_output(f"\n{'='*20}\n")
        self._add_detailed_output(f"Optimization Completed!\n")
        self._add_detailed_output(f"{'='*20}\n")
        self._add_detailed_output(f"Best Frequency: {best_frequency[0]:.3f} Hz\n")
        self._add_detailed_output(f"Best Total Loss: {best_loss:.3f} W\n")
        self._add_detailed_output(f"Best MOSFET: {self.mosfet_df.iloc[self.best_mosfet_idx, 0]}\n")
        self._add_detailed_output(f"Best Diode: {self.diode_df.iloc[self.best_diode_idx, 0]}\n")
        
        return best_frequency[0], best_loss
    
    def get_results(self) -> OptimizationResults:
        """Get optimization results"""
        coil_power = self.system_params.vds * self.system_params.i_coil
        system_efficiency = ((coil_power - self.best_coil_loss) / 
                           (coil_power + self.best_mosfet_loss + self.best_diode_loss)) * 100
        
        return OptimizationResults(
            best_frequency=0.0,  # Will be set by caller
            best_loss=0.0,       # Will be set by caller
            best_mosfet_name=self.mosfet_df.iloc[self.best_mosfet_idx, 0],
            best_diode_name=self.diode_df.iloc[self.best_diode_idx, 0],
            mosfet_loss=self.best_mosfet_loss,
            diode_loss=self.best_diode_loss,
            coil_loss=self.best_coil_loss,
            tx_inductance=self.tx_inductance,
            rx_inductance=self.rx_inductance,
            tx_resistance=self.tx_resistance,
            rx_resistance=self.rx_resistance,
            system_efficiency=system_efficiency
        )