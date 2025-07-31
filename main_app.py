"""
Main application class for the AI-Powered WPT Efficiency Optimizer
"""
import customtkinter
import os
from PIL import Image
from typing import Optional

from data_loader import DataLoader
from optimization_engine import OptimizationEngine
from ui_components import NavigationFrame, HomeFrame, ResultsDisplay
from data_models import OptimizationResults


class WirelessPowerTransmissionApp(customtkinter.CTk):
    """Main application class"""
    
    def __init__(self):
        super().__init__()
        self._setup_window()
        self._load_images()
        self._create_widgets()
        self._setup_layout()
        self._show_home_frame()
    
    def _setup_window(self):
        """Setup main window properties"""
        self.title("AI-Powered WPT Efficiency Optimizer")
        self.geometry("900x750")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_images", "app_icon.ico")
        self.iconbitmap(icon_path)
    
    def _load_images(self):
        """Load application images"""
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_images")
        
        self.logo_image = customtkinter.CTkImage(
            Image.open(os.path.join(image_path, "logo.png")), 
            size=(180, 180)
        )
        self.large_test_image = customtkinter.CTkImage(
            Image.open(os.path.join(image_path, "large_test_image.png")), 
            size=(590, 180)
        )
        self.home_image = customtkinter.CTkImage(
            light_image=Image.open(os.path.join(image_path, "home_dark.png")),
            dark_image=Image.open(os.path.join(image_path, "home_light.png")), 
            size=(20, 20)
        )
    
    def _create_widgets(self):
        """Create all UI widgets"""
        # Navigation frame
        self.navigation_frame = NavigationFrame(
            self,                  # parent
            self,                  # main_window
            self.logo_image,       # logo
            self.home_image,       # home icon
            self._on_home_button_click 
        )
        
        # Main content area
        self.slider_progressbar_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.slider_progressbar_frame.grid_columnconfigure(0, weight=1)
        self.slider_progressbar_frame.grid_rowconfigure(3, weight=1)
        
        self.progress_bar = customtkinter.CTkProgressBar(self.slider_progressbar_frame)
        
        # Labels for textboxes
        self.results_label = customtkinter.CTkLabel(self, text="Optimization Results", font=customtkinter.CTkFont(size=14, weight="bold"))
        self.test_label = customtkinter.CTkLabel(self, text="Detailed Analysis", font=customtkinter.CTkFont(size=14, weight="bold"))
        self.output_textbox = customtkinter.CTkTextbox(self, width=250)
        self.test_textbox = customtkinter.CTkTextbox(self, width=250, height=200)
        
        # Home frame
        self.home_frame = HomeFrame(
            self, 
            self.large_test_image, 
            self._start_analysis
        )
    
    def _setup_layout(self):
        """Setup widget layout"""
        # Navigation frame
        self.navigation_frame.grid(row=0, column=0, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.navigation_frame.grid_columnconfigure(0, weight=1) 

        # Main content area
        self.slider_progressbar_frame.grid(row=1, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.progress_bar.grid(row=2, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
        
        # Labels and textboxes
        self.results_label.grid(row=2, column=1, padx=(20, 10), pady=(10, 0), sticky="w")
        self.output_textbox.grid(row=3, column=1, padx=(20, 10), pady=(0, 10), sticky="ew")
        
        self.test_label.grid(row=2, column=0, padx=(20, 10), pady=(10, 0), sticky="w")
        self.test_textbox.grid(row=3, column=0, padx=(20, 10), pady=(0, 10), sticky="ew")
    
    def _show_home_frame(self):
        """Show home frame and reset progress bar"""
        self.progress_bar.set(0)
        self._on_home_button_click()
    
    def _on_home_button_click(self):
        """Handle home button click"""
        self.navigation_frame.highlight_home_button()
        self.home_frame.grid(row=0, column=1, sticky="nsew")
        self.home_frame.grid_rowconfigure(0, weight=1)
        self.home_frame.grid_columnconfigure(0, weight=1)

    def _update_progress(self, value: float):
        """Update progress bar"""
        self.progress_bar.set(value)
        self.update_idletasks()
    
    def _add_detailed_output(self, text: str):
        """Add text to the test textbox"""
        self.test_textbox.insert("end", text)
        self.update_idletasks()
    
    def _start_analysis(self):
        """Start the optimization analysis"""
        self.output_textbox.delete("0.0", "end")
        self.test_textbox.delete("0.0", "end")
        self.output_textbox.insert("0.0", "Starting Analysis...\n\n")
        self.test_textbox.insert("0.0", "All possibilites :\n")
        
        self.progress_bar.start()
        self._update_progress(0.1)
        
        try:
            # Load data
            system_params = DataLoader.load_system_parameters()
            if system_params is None:
                self.results_textbox.insert("end", "Error: Could not load system parameters\n")
                self._update_progress(1.0)
                self.progress_bar.stop()
                return
            
            mosfet_df, diode_df = DataLoader.load_component_databases()
            if mosfet_df is None or diode_df is None:
                self.results_textbox.insert("end", "Error: Could not load component databases\n")
                self._update_progress(1.0)
                self.progress_bar.stop()
                return
            
            self._update_progress(0.2)
            
            # Create optimization engine with detailed output callback
            optimizer = OptimizationEngine(
                system_params, 
                mosfet_df, 
                diode_df, 
                progress_callback=self._update_progress,
                detailed_output_callback=self._add_detailed_output
            )
            
            # Run optimization
            best_frequency, best_loss = optimizer.optimize()
            
            self._update_progress(0.8)
            
            # Get results
            results = optimizer.get_results()
            results.best_frequency = best_frequency
            results.best_loss = best_loss
            
            # Display results
            self._display_results(results, system_params)
            
            self._update_progress(1.0)
            self.progress_bar.stop()
            
        except Exception as e:
            self.results_textbox.insert("end", f"\nError during analysis: {str(e)}\n")
            self.progress_bar.stop()
    
    def _display_results(self, results: OptimizationResults, system_params):
        """Display optimization results"""
        self.output_textbox.delete("0.0", "end")
        formatted_results = ResultsDisplay.format_results(results, system_params)
        self.output_textbox.insert("0.0", formatted_results)