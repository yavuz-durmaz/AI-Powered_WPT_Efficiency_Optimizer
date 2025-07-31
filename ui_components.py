"""
UI components for the AI-Powered WPT Efficiency Optimizer
"""
import customtkinter
import os
from PIL import Image
from typing import Callable, Optional


class NavigationFrame(customtkinter.CTkFrame):
    """Navigation sidebar component"""
    
    def __init__(self, parent, main_window, logo_image, home_image, home_callback: Callable):
        super().__init__(parent, corner_radius=30)
        self.main_window = main_window  # Ana pencere referansı
        self.grid_rowconfigure(4, weight=1)

        self._create_widgets(logo_image)
        self._setup_layout()
    
    def _create_widgets(self, logo_image):
        # Logo
        self.logo_label = customtkinter.CTkLabel(
            self, 
            text="  ", 
            image=logo_image,
            compound="left", 
            font=customtkinter.CTkFont(size=15, weight="bold")
        )
        
        # Appearance mode controls
        self.appearance_mode_label = customtkinter.CTkLabel(
            self, 
            text="Appearance Mode:", 
            anchor="w"
        )
        self.appearance_mode_menu = customtkinter.CTkOptionMenu(
            self, 
            values=["System", "Light", "Dark"],
            command=self._change_appearance_mode
        )
        
        # UI scaling controls
        self.scaling_label = customtkinter.CTkLabel(
            self, 
            text="UI Scale:", 
            anchor="w"
        )
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(
            self, 
            values=["60%", "80%", "100%", "120%", "140%"],
            command=self._change_scaling
        )
        self.scaling_optionemenu.set("100%") 
    
    def _setup_layout(self):
        self.logo_label.grid(row=0, column=0, padx=20, pady=20)
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_menu.grid(row=6, column=0, padx=20, pady=20, sticky="s")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))
    
    def _change_appearance_mode(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)
    
    def _change_scaling(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        self.main_window.geometry(f"{int(900 * new_scaling_float)}x{int(750 * new_scaling_float)}")
        customtkinter.set_widget_scaling(new_scaling_float)
        
        
    def highlight_home_button(self):
        pass  # Home button kaldırıldığı için boş bırakıldı


class HomeFrame(customtkinter.CTkFrame):
    """Home frame component"""
    
    def __init__(self, parent, large_image, start_callback: Callable):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        
        self._create_widgets(large_image, start_callback)
        self._setup_layout()
    
    def _create_widgets(self, large_image, start_callback):
        # Large image
        self.large_image_label = customtkinter.CTkLabel(
            self, 
            text="", 
            image=large_image
        )
        
        # Credits
        self.credits_label = customtkinter.CTkLabel(
            self,
            text="Application developed by\nYavuz Durmaz\nContact: yavuzdurmazresmi@gmail.com",
            font=("Ubuntu", 15),
            justify="center"
        )
        
        # Start analysis button
        self.start_button = customtkinter.CTkButton(
            self, 
            font=customtkinter.CTkFont(size=30), 
            text="Start Analysis",
            corner_radius=15, 
            compound="left", 
            command=start_callback
        )
    
    def _setup_layout(self):
        self.large_image_label.grid(row=0, column=0, padx=20, pady=10)
        self.credits_label.grid(row=4, column=0, padx=20, pady=10)
        self.start_button.grid(row=5, column=0, padx=20, pady=10)


class ResultsDisplay:
    """Handles results display formatting"""
    
    @staticmethod
    def format_results(results, system_params) -> str:
        """Format optimization results for display"""
        summary = f"""Optimization Results :
{'='*40}

Optimal Frequency: {results.best_frequency:.3f} Hz
Total System Loss: {results.best_loss:.3f} W
System Efficiency: {results.system_efficiency:.2f}%

Recommended Components:
• MOSFET: {results.best_mosfet_name}
• Diode: {results.best_diode_name}

Component Losses (for {system_params.mosfet_count} MOSFETs and {system_params.diode_count} diodes):
• MOSFET Loss: {results.mosfet_loss:.3f} W
• Diode Loss: {results.diode_loss:.3f} W  
• Coil Loss: {results.coil_loss:.3f} W

Coil Parameters:
• TX Coil: {results.tx_resistance:.3f} Ω, {results.tx_inductance*1e6:.3f} μH
• RX Coil: {results.rx_resistance:.3f} Ω, {results.rx_inductance*1e6:.3f} μH
• TX Wire Length: {system_params.tx_coil.wire_length:.3f} m
• RX Wire Length: {system_params.rx_coil.wire_length:.3f} m
• TX Inner Diameter: {system_params.tx_coil.inner_diameter:.3f} mm
• RX Inner Diameter: {system_params.rx_coil.inner_diameter:.3f} mm

"""
        return summary
