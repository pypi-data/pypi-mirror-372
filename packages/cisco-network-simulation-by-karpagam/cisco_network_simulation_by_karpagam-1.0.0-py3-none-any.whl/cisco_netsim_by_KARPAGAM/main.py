#!/usr/bin/env python3
"""
Cisco Network Simulation by Karpagam - Main GUI Interface
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import subprocess
from pathlib import Path

class KarpagamNetworkToolkit:
    def __init__(self, root):
        self.root = root
        self.root.title("🌐 Cisco Network Simulation by Karpagam")
        self.root.geometry("900x700")
        
        # Variables
        self.input_dir = tk.StringVar()
        self.output_dir = tk.StringVar(value=str(Path.home() / "network_analysis_results"))
        self.status_var = tk.StringVar(value="Ready to analyze network configurations...")
        
        self.create_interface()
        
    def _perform_analysis(self):
        try:
            self.update_status("🔄 Starting network analysis...")
            
            # Create output directory
            os.makedirs(self.output_dir.get(), exist_ok=True)
            
            # Step 1: Parse if selected
            if self.parse_var.get():
                self.update_status("📝 Parsing network configurations...")
                # Use subprocess to run the parser module
                import subprocess
                import sys
                
                parser_cmd = [
                    sys.executable, "-m", 
                    "cisco_netsim_by_KARPAGAM.parser.parsing_module",
                    "--input-dir", self.input_dir.get(),
                    "--output-json", os.path.join(self.output_dir.get(), "parsed_configs.json")
                ]
                subprocess.run(parser_cmd, check=True)
                
            # Step 2: Topology if selected  
            if self.topology_var.get():
                self.update_status("🗺️ Building network topology...")
                topology_cmd = [
                    sys.executable, "-m",
                    "cisco_netsim_by_KARPAGAM.topology.building_topology_graph", 
                    "--input", os.path.join(self.output_dir.get(), "parsed_configs.json"),
                    "--graph-json", os.path.join(self.output_dir.get(), "network_graph.json"),
                    "--topology-png", os.path.join(self.output_dir.get(), "topology.png")
                ]
                subprocess.run(topology_cmd, check=True)
                
            # Continue for other modules...
            
            self.update_status("✅ Analysis complete! Check output directory for results.")
            self.show_completion_message()
            
        except Exception as e:
            self.update_status(f"❌ Error: {str(e)}")
            messagebox.showerror("Analysis Error", f"Error during analysis:\n{str(e)}")
        finally:
            self.root.after(0, self._analysis_finished)

    # ... [rest of your main.py code remains the same]

def main():
    """Main entry point for the package"""
    print("🌐 Cisco Network Simulation by Karpagam")
    print("📋 Starting interactive interface...")
    
    root = tk.Tk()
    app = KarpagamNetworkToolkit(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\n🔄 Shutting down...")

if __name__ == '__main__':
    main()
