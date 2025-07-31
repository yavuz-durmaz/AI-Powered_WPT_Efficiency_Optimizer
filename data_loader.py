"""
Data loading utilities for the AI-Powered WPT Efficiency Optimizer
"""
import pandas as pd
from typing import Optional, Tuple
from data_models import CoilParameters, SystemParameters


class DataLoader:
    """Handles loading data from Excel files"""
    
    @staticmethod
    def load_system_parameters(filepath: str = 'input_values.xlsx') -> Optional[SystemParameters]:
        """Load system parameters from Excel file"""
        try:
            df = pd.read_excel(filepath)
            
            tx_coil = CoilParameters(
                turns=int(df.iloc[1, 1]),
                wire_diameter=df.iloc[2, 1],
                wire_spacing=df.iloc[3, 1],
                outer_diameter=df.iloc[4, 1]
            )
            
            rx_coil = CoilParameters(
                turns=int(df.iloc[5, 1]),
                wire_diameter=df.iloc[6, 1],
                wire_spacing=df.iloc[7, 1],
                outer_diameter=df.iloc[8, 1]
            )
            
            return SystemParameters(
                coupling_coefficient=df.iloc[0, 1],
                tx_coil=tx_coil,
                rx_coil=rx_coil,
                equivalent_resistance=df.iloc[9, 1],
                mosfet_count=int(df.iloc[10, 1]),
                diode_count=int(df.iloc[11, 1]),
                id_rms=df.iloc[12, 1],
                vds=df.iloc[13, 1],
                ids=df.iloc[14, 1],
                i_coil=df.iloc[15, 1],
                id_eff=df.iloc[16, 1],
                id_mean=df.iloc[17, 1],
                vd=df.iloc[18, 1],
                r1_unit=df.iloc[19, 1],
                r2_unit=df.iloc[20, 1]
            )
        except Exception as e:
            print(f"Error loading system parameters: {str(e)}")
            return None
    
    @staticmethod
    def load_component_databases(mosfet_filepath: str = 'mosfet_database.xlsx',
                               diode_filepath: str = 'diode_database.xlsx') -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
        """Load MOSFET and diode databases"""
        try:
            mosfet_df = pd.read_excel(mosfet_filepath)
            diode_df = pd.read_excel(diode_filepath)
            return mosfet_df, diode_df
        except Exception as e:
            print(f"Error loading component databases: {str(e)}")
            return None, None
