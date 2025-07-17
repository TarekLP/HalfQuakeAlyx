import os
import re
import xml.etree.ElementTree as ET
from xml.dom import minidom
import shutil
import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import threading
from PIL import Image, ImageDraw, ImageFont # Import ImageFont for dummy PNGs
import sys # Import the sys module

# No longer needed as WAD extraction is removed
# QUAKE_PALETTE = [...]
# FLATTENED_PALETTE = [...]


def prettify_xml(elem):
    """
    Return a pretty-printed XML string for the Element,
    ensuring no XML declaration is added by minidom and no leading blank lines.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="    ")
    
    # Remove the XML declaration line if it exists and any leading blank lines
    lines = pretty_xml.splitlines()
    cleaned_lines = []
    skip_declaration = True
    for line in lines:
        stripped_line = line.strip()
        if skip_declaration and stripped_line.startswith('<?xml'):
            skip_declaration = False # Found and skipped the declaration
            continue
        if not stripped_line and not cleaned_lines: # Skip leading blank lines
            continue
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines)

def parse_quake_map(map_filepath):
    """
    Parses a Quake .map file to extract brush geometry and texture names.
    This version is more robust in identifying brush blocks within entities.
    It focuses on extracting all brush planes accurately, ignoring entity properties.
    """
    brushes = []          
    unique_textures = set()
    current_brush_planes = []
    
    # State flags
    in_entity_block = False
    in_brush_block = False

    with open(map_filepath, 'r') as f:
        print(f"  Attempting to parse map file: {map_filepath}")
        for line_num, line in enumerate(f, 1):
            stripped_line = line.strip()

            # Skip comments and empty lines
            if not stripped_line or stripped_line.startswith('//'):
                continue

            if stripped_line == '{':
                if not in_entity_block:
                    # This is the start of a new top-level entity block (e.g., worldspawn or func_xxx)
                    in_entity_block = True
                    in_brush_block = False # Assume not in brush yet, waiting for first brush or properties
                else:
                    # This is a nested '{', which indicates the start of a new brush block
                    in_brush_block = True
                    current_brush_planes = [] # Start collecting planes for this new brush
            elif stripped_line == '}':
                if in_brush_block:
                    # End of a brush block
                    if current_brush_planes:
                        brushes.append(current_brush_planes)
                    in_brush_block = False
                    current_brush_planes = [] # Reset for next brush
                elif in_entity_block:
                    # End of an entity block (after all its brushes and properties)
                    in_entity_block = False
            else:
                # If we are inside a brush block, try to parse a plane
                if in_brush_block:
                    # Regex to capture the three points and the texture name.
                    # It's lenient about data after the texture name as we don't need UVs/lightmap.
                    plane_match = re.match(r'\(\s*([\d\.\-]+)\s+([\d\.\-]+)\s+([\d\.\-]+)\s*\)\s*\(\s*([\d\.\-]+)\s+([\d\.\-]+)\s+([\d\.\-]+)\s*\)\s*\(\s*([\d\.\-]+)\s+([\d\.\-]+)\s+([\d\.\-]+)\s*\)\s*([^\s]+).*', stripped_line)
                    if plane_match:
                        p1 = (float(plane_match.group(1)), float(plane_match.group(2)), float(plane_match.group(3)))
                        p2 = (float(plane_match.group(4)), float(plane_match.group(5)), float(plane_match.group(6)))
                        p3 = (float(plane_match.group(7)), float(plane_match.group(8)), float(plane_match.group(9)))
                        texture_name = plane_match.group(10).lower() # Convert to lowercase for consistency

                        current_brush_planes.append({
                            'plane': (p1, p2, p3),
                            'texture': texture_name
                        })
                        unique_textures.add(texture_name)
                    # else:
                        # If a line inside a brush block doesn't match a plane, it's unexpected
                        # but we continue parsing other lines.
                        # print(f"  [WARNING] Line {line_num}: Unexpected content in brush block: '{stripped_line}'")
                # else:
                    # If we are inside an entity block but not a brush block,
                    # this line is likely an entity property ("key" "value").
                    # We ignore these as per user request ("don't need to extract entities").
                    # print(f"  [DEBUG] Line {line_num}: Ignoring entity property: '{stripped_line}'")
    
    # Handle case where the map file might end without proper closing braces for the last brush
    if current_brush_planes:
        brushes.append(current_brush_planes)

    print(f"  Finished parsing {map_filepath}. Found {len(brushes)} brushes and {len(unique_textures)} unique textures.")
    return brushes, list(unique_textures)

def copy_pre_extracted_texture(texture_name, output_dir, extracted_textures_dir):
    """
    Copies a pre-extracted PNG texture from a specified directory to the output materials directory.
    """
    # Sanitize texture_name for filename use (replace non-alphanumeric/underscore with underscore)
    sanitized_texture_name = re.sub(r'[^a-zA-Z0-9_]', '_', texture_name.lstrip('*').lower())

    source_filepath = os.path.join(extracted_textures_dir, f"{sanitized_texture_name}.png")
    destination_filepath = os.path.join(output_dir, f"{sanitized_texture_name}.png")

    os.makedirs(os.path.dirname(destination_filepath), exist_ok=True)

    if os.path.exists(destination_filepath):
        print(f"  Texture '{sanitized_texture_name}.png' already exists in output. Skipping copy.")
        return True

    if not os.path.exists(source_filepath):
        print(f"  [WARNING] Pre-extracted texture '{sanitized_texture_name}.png' not found at '{source_filepath}'.")
        print(f"  Please ensure you manually provide it if it's missing.")
        return False
    
    try:
        shutil.copy2(source_filepath, destination_filepath)
        print(f"  Successfully copied '{source_filepath}' to '{destination_filepath}'.")
        return True
    except Exception as e:
        print(f"  [ERROR] Could not copy texture '{sanitized_texture_name}.png' from '{source_filepath}' to '{destination_filepath}': {e}")
        return False


def create_vmat_file(texture_name, output_dir, png_copied=False):
    """
    Creates a basic .vmat file for a given texture name.
    """
    # Sanitize texture_name for filename use (replace non-alphanumeric/underscore with underscore)
    sanitized_texture_name = re.sub(r'[^a-zA-Z0-9_]', '_', texture_name.lstrip('*').lower())
    
    vmat_content = f"""
// Compiled material for {sanitized_texture_name}
"Material"
{{
    "Shader" "vr_standard.vfx" // Explicitly define the shader

    // Default to opaque, set to 1 if transparent
    "F_TRANSLUCENT" "0" 
    "F_ALPHA_TEST" "0"  

    "Parameters"
    {{
        "g_tColor"
        {{
            "Texture" "materials/{sanitized_texture_name}.png"
        }}
        "g_flDirectionalLightStrength" "1.0"
        "g_flProxyToggle" "1.0"
    }}
"""
    # For transparent textures, you might need specific flags in VMAT
    if texture_name.startswith('{'): # Check original texture name for transparency flag
        vmat_content += """
    "Translucent" "1"
    "BlendMode" "ALPHA_BLEND"
    // "AlphaTest" "1" // Use AlphaTest instead of BlendMode if it's a hard cut-off
"""
    vmat_content += """
}
"""
    vmat_filepath = os.path.join(output_dir, f"{sanitized_texture_name}.vmat") # Use sanitized name
    os.makedirs(os.path.dirname(vmat_filepath), exist_ok=True)
    with open(vmat_filepath, 'w') as f:
        f.write(vmat_content.strip())
    print(f"Created .vmat file: {vmat_filepath}")


def generate_vmap_content(map_data):
    """
    Generates the XML content for a Half-Life: Alyx .vmap file
    from the parsed Quake map data.
    """
    # Add the Source 2 DMX encoding header - MUST be the very first line
    vmap_header = '<!-- DMX encoding keyvalues2_nosoftspace 1 format vmap 6 -->'

    root = ET.Element("map", version="6") # Updated version to "6" for Alyx compatibility

    world_node = ET.SubElement(root, "world", name="world")

    # Define a scaling factor for Quake units to Source 2 units
    # Quake units are 16 units/foot, Source 2 units are 12 units/foot (1 unit/inch)
    # So, 1 Quake unit = 16/12 = 4/3 Source 2 units. To convert from Quake to Source 2, multiply by 3/4 (0.75)
    SCALE_FACTOR = 0.75 

    for brush_idx, brush_planes in enumerate(map_data):
        solid_node = ET.SubElement(world_node, "solid", name=f"brush_{brush_idx}")

        for plane_data in brush_planes:
            side_node = ET.SubElement(solid_node, "side")

            # Quake uses Z-up, Source 2 typically Y-up.
            # Conversion: (x, y, z) -> (x, z, -y)
            p1 = plane_data['plane'][0]
            p2 = plane_data['plane'][1]
            p3 = plane_data['plane'][2]

            # Apply Z-up to Y-up conversion and scaling
            p1_s2 = (p1[0] * SCALE_FACTOR, p1[2] * SCALE_FACTOR, -p1[1] * SCALE_FACTOR)
            p2_s2 = (p2[0] * SCALE_FACTOR, p2[2] * SCALE_FACTOR, -p2[1] * SCALE_FACTOR)
            p3_s2 = (p3[0] * SCALE_FACTOR, p3[2] * SCALE_FACTOR, -p3[1] * SCALE_FACTOR)

            # Format coordinates to a fixed number of decimal places for consistency
            plane_node = ET.SubElement(side_node, "plane",
                                       x1=f"{p1_s2[0]:.6f}", y1=f"{p1_s2[1]:.6f}", z1=f"{p1_s2[2]:.6f}",
                                       x2=f"{p2_s2[0]:.6f}", y2=f"{p2_s2[1]:.6f}", z2=f"{p2_s2[2]:.6f}",
                                       x3=f"{p3_s2[0]:.6f}", y3=f"{p3_s2[1]:.6f}", z3=f"{p3_s2[2]:.6f}")

            # Reference the .vmat file using the sanitized texture name
            sanitized_texture_name = re.sub(r'[^a-zA-Z0-9_]', '_', plane_data['texture'].lstrip('*').lower())
            material_node = ET.SubElement(side_node, "material", name=f"materials/{sanitized_texture_name}.vmat")

            # UV data is highly complex to convert directly from Quake's format.
            # Hammer will likely generate default UVs, or you'll need to manually adjust.
            # For now, rely on Hammer's default or manual adjustment.
            # If you wanted to attempt UVs, it would look something like this within the <side> tag:
            # <uvs u="0 1 0 0" v="0 0 1 0"/>  (example, actual values depend on the texture projection)

    # Prettify the XML tree
    pretty_xml_content = prettify_xml(root)

    # Combine the DMX header with the prettified XML content
    final_vmap_content = f"{vmap_header}\n{pretty_xml_content}"
    return final_vmap_content

def convert_folder(input_folder, output_folder, extracted_textures_dir, console_widget):
    """
    Converts all Quake .map files in the input_folder to Half-Life: Alyx .vmap files
    and generates corresponding .vmat files in the output_folder.
    It now expects textures to be pre-extracted in the 'extracted_textures_dir'.
    Output is redirected to the provided console_widget.
    """
    def print_to_console(s):
        console_widget.insert(tk.END, s + "\n")
        console_widget.see(tk.END) # Auto-scroll to the end
        console_widget.update_idletasks() # Force update GUI

    if not os.path.exists(input_folder):
        print_to_console(f"Error: Input folder '{input_folder}' does not exist.")
        return

    os.makedirs(output_folder, exist_ok=True)
    materials_output_dir = os.path.join(output_folder, "materials")
    os.makedirs(materials_output_dir, exist_ok=True)

    map_files_found = False
    all_unique_textures = set()

    print_to_console(f"\nScanning input folder: '{input_folder}' for .map files...")
    map_files_in_input_folder = []
    for root, dirs, files in os.walk(input_folder):
        print_to_console(f"  Checking directory: {root}")
        print_to_console(f"  Found subdirectories: {dirs}")
        print_to_console(f"  Found files: {files}")
        for file in files:
            if file.lower().endswith(".map"):
                map_files_in_input_folder.append(os.path.join(root, file))

    if not map_files_in_input_folder:
        print_to_console(f"No .map files found in '{input_folder}' or its subdirectories.")
        return

    print_to_console(f"Found {len(map_files_in_input_folder)} .map files:")
    for map_filepath in map_files_in_input_folder:
        print_to_console(f"- {map_filepath}")
        map_files_found = True
        map_name = os.path.splitext(os.path.basename(map_filepath))[0]
        vmap_filepath = os.path.join(output_folder, f"{map_name}.vmap")

        print_to_console(f"\nProcessing {map_filepath}...")
        brushes, unique_textures_in_map = parse_quake_map(map_filepath)
        all_unique_textures.update(unique_textures_in_map)

        if brushes:
            vmap_content = generate_vmap_content(brushes)
            with open(vmap_filepath, 'w') as f:
                f.write(vmap_content)
            print_to_console(f"Generated .vmap file: {vmap_filepath}")
        else:
            print_to_console(f"No brushes found in {map_filepath}. Skipping .vmap generation.")

    if not map_files_found:
        print_to_console(f"No .map files were processed.")
        return

    print_to_console(f"\n--- Copying pre-extracted textures from '{extracted_textures_dir}' and generating .vmat files ---")
    for texture in all_unique_textures:
        png_copied = copy_pre_extracted_texture(texture, materials_output_dir, extracted_textures_dir)
        create_vmat_file(texture, materials_output_dir, png_copied)

    print_to_console("\nConversion process completed. Please review the generated files.")
    print_to_console("\nIMPORTANT NOTES:")
    print_to_console("1. This script provides a simplified conversion. Complex geometry (e.g., curved surfaces, precise UVs) and entities are not fully handled.")
    print_to_console("2. Quake uses a Z-up coordinate system, while Source 2 typically uses Y-up. The script attempts to convert (X,Y,Z) to (X,Z,-Y). You might still need to adjust the map's orientation in Hammer after import.")
    print_to_console("3. Textures are now expected to be pre-extracted as PNG files in the 'wad_extracted' directory.")
    print_to_console("4. For best results, you may need to manually adjust materials and geometry in Half-Life: Alyx's Hammer editor.")


class QuakeVmapConverterApp:
    def __init__(self, master):
        self.master = master
        master.title("Quake .map to Alyx .vmap Converter")

        # Define dark theme colors
        self.bg_dark_gray = "#2B2B2B"
        self.fg_light_gray = "#E0E0E0"
        self.button_bg = "#4A4A4A"
        self.button_fg = "#FFFFFF"
        self.console_bg = "#1E1E1E"
        self.console_text_color = "#BB86FC" # A shade of purple

        master.config(bg=self.bg_dark_gray)

        # Use tk.StringVar for dynamic path updates in Entry widgets
        # Set default input folder to a 'quake_maps_input' subdirectory in the script's directory
        script_dir = os.path.dirname(__file__)
        self.input_folder_var = tk.StringVar(value=os.path.normpath(os.path.join(script_dir, "quake_maps_input")))
        self.output_folder_var = tk.StringVar(value="alyx_vmap_output")
        self.pre_extracted_textures_folder_var = tk.StringVar(value="wad_extracted")

        self.create_widgets()
        self.setup_dummy_files() # Setup dummy files on app start

    def create_widgets(self):
        # Input Folder Selection
        tk.Label(self.master, text="Quake Maps Input Folder:", bg=self.bg_dark_gray, fg=self.fg_light_gray).pack(pady=(10, 0))
        input_frame = tk.Frame(self.master, bg=self.bg_dark_gray)
        input_frame.pack(fill=tk.X, padx=10)
        tk.Entry(input_frame, textvariable=self.input_folder_var, width=50, bg=self.button_bg, fg=self.button_fg, insertbackground=self.fg_light_gray).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(input_frame, text="Browse", command=lambda: self.browse_folder(self.input_folder_var), bg=self.button_bg, fg=self.button_fg, activebackground=self.fg_light_gray, activeforeground=self.button_bg).pack(side=tk.RIGHT)

        # Output Folder Selection
        tk.Label(self.master, text="Alyx VMAP Output Folder:", bg=self.bg_dark_gray, fg=self.fg_light_gray).pack(pady=(10, 0))
        output_frame = tk.Frame(self.master, bg=self.bg_dark_gray)
        output_frame.pack(fill=tk.X, padx=10)
        tk.Entry(output_frame, textvariable=self.output_folder_var, width=50, bg=self.button_bg, fg=self.button_fg, insertbackground=self.fg_light_gray).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(output_frame, text="Browse", command=lambda: self.browse_folder(self.output_folder_var), bg=self.button_bg, fg=self.button_fg, activebackground=self.fg_light_gray, activeforeground=self.button_bg).pack(side=tk.RIGHT)

        # Pre-extracted Textures Folder Selection
        tk.Label(self.master, text="Pre-extracted Textures Folder (wad_extracted):", bg=self.bg_dark_gray, fg=self.fg_light_gray).pack(pady=(10, 0))
        textures_frame = tk.Frame(self.master, bg=self.bg_dark_gray)
        textures_frame.pack(fill=tk.X, padx=10)
        tk.Entry(textures_frame, textvariable=self.pre_extracted_textures_folder_var, width=50, bg=self.button_bg, fg=self.button_fg, insertbackground=self.fg_light_gray).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(textures_frame, text="Browse", command=lambda: self.browse_folder(self.pre_extracted_textures_folder_var), bg=self.button_bg, fg=self.button_fg, activebackground=self.fg_light_gray, activeforeground=self.button_bg).pack(side=tk.RIGHT)

        # Frame for buttons
        button_frame = tk.Frame(self.master, bg=self.bg_dark_gray)
        button_frame.pack(pady=10)

        self.compile_button = tk.Button(button_frame, text="Compile Maps", command=self.start_conversion_thread, bg=self.button_bg, fg=self.button_fg, activebackground=self.fg_light_gray, activeforeground=self.button_bg)
        self.compile_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = tk.Button(button_frame, text="Clear Console", command=self.clear_console, bg=self.button_bg, fg=self.button_fg, activebackground=self.fg_light_gray, activeforeground=self.button_bg)
        self.clear_button.pack(side=tk.LEFT, padx=5)

        # Console output area
        self.console_text = scrolledtext.ScrolledText(self.master, wrap=tk.WORD, height=25, width=80, state='disabled', bg=self.console_bg, fg=self.console_text_color, insertbackground=self.fg_light_gray)
        self.console_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        # Apply tag for console text color (though fg already sets it, this is for consistency/future tags)
        self.console_text.tag_config("console_output", foreground=self.console_text_color)


        # Redirect stdout to the console_text widget
        self.text_redirector = TextRedirector(self.console_text)
        sys.stdout = self.text_redirector
        sys.stderr = self.text_redirector # Also redirect stderr

    def browse_folder(self, path_var):
        """Opens a file dialog to select a folder and updates the StringVar."""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            path_var.set(os.path.normpath(folder_selected))

    def clear_console(self):
        self.console_text.config(state='normal')
        self.console_text.delete(1.0, tk.END)
        self.console_text.config(state='disabled')

    def start_conversion_thread(self):
        self.clear_console()
        self.compile_button.config(state='disabled') # Disable button during conversion
        self.clear_button.config(state='disabled')

        # Get current paths from entry widgets
        input_folder = self.input_folder_var.get()
        output_folder = self.output_folder_var.get()
        pre_extracted_textures_folder = self.pre_extracted_textures_folder_var.get()

        # Run conversion in a separate thread
        self.conversion_thread = threading.Thread(target=self.run_conversion, args=(input_folder, output_folder, pre_extracted_textures_folder))
        self.conversion_thread.start()
        self.master.after(100, self.check_conversion_thread) # Start checking thread status

    def run_conversion(self, input_folder, output_folder, pre_extracted_textures_folder):
        try:
            convert_folder(input_folder, output_folder, pre_extracted_textures_folder, self.console_text)
            messagebox.showinfo("Conversion Complete", "Map conversion process finished successfully!")
        except Exception as e:
            messagebox.showerror("Conversion Error", f"An error occurred during conversion: {e}")
            print(f"[ERROR] Critical error during conversion: {e}")
        finally:
            # Re-enable buttons in the main thread after conversion finishes
            self.master.after(0, self.enable_buttons)

    def check_conversion_thread(self):
        if self.conversion_thread.is_alive():
            self.master.after(100, self.check_conversion_thread) # Keep checking
        else:
            self.enable_buttons()

    def enable_buttons(self):
        self.compile_button.config(state='normal')
        self.clear_button.config(state='normal')

    def setup_dummy_files(self):
        """
        Ensures input folder and dummy textures exist for testing.
        Only creates files if the directories are empty.
        """
        # Ensure base directories exist
        os.makedirs(self.input_folder_var.get(), exist_ok=True)
        os.makedirs(self.pre_extracted_textures_folder_var.get(), exist_ok=True)

        # Create sample map only if the input folder is empty
        sample_map_path = os.path.join(self.input_folder_var.get(), "sample_map.map")
        if not os.listdir(self.input_folder_var.get()): # Check if folder is empty
            sample_map_content = """
// My Sample Quake Map
{
    "classname" "worldspawn"
    {
        ( -128 -128 0 ) ( 128 -128 0 ) ( -128 128 0 ) WALL_TEX [ 1 0 0 0 ] [ 0 1 0 0 ] 0 1 1
        ( -128 -128 128 ) ( -128 128 128 ) ( 128 -128 128 ) CEILING_TEX [ 1 0 0 0 ] [ 0 1 0 0 ] 0 1 1
        ( -128 -128 0 ) ( -128 -128 128 ) ( -128 128 0 ) FLOOR_TEX [ 1 0 0 0 ] [ 0 1 0 0 ] 0 1 1
        ( 128 -128 0 ) ( 128 128 0 ) ( 128 -128 128 ) BRICK_TEX [ 1 0 0 0 ] [ 0 1 0 0 ] 0 1 1
        ( -128 128 0 ) ( 128 128 0 ) ( -128 128 128 ) {CLIP [ 1 0 0 0 ] [ 0 1 0 0 ] 0 1 1
        ( -128 -128 0 ) ( -128 128 0 ) ( 128 -128 0 ) WATER_TEX [ 1 0 0 0 ] [ 0 1 0 0 ] 0 1 1
    }
    {
        "classname" "light"
        "origin" "0 0 64"
        "light" "300"
    }
}
"""
            with open(sample_map_path, "w") as f:
                f.write(sample_map_content)
            print(f"Created a sample map file: {sample_map_path}")
        else:
            print(f"Input folder '{self.input_folder_var.get()}' is not empty. Skipping sample map creation.")


        # --- Create dummy texture files for the sample map in the 'wad_extracted' folder ---
        # These are placeholder PNGs. In a real scenario, you would place your actual
        # extracted Quake textures (e.g., from a tool like Wally or TexMex) here.
        
        def create_dummy_png(filename, size=(64, 64), color=(128, 128, 128), text=None, transparent=False):
            if transparent:
                img = Image.new('RGBA', size, color + (0,)) # Add alpha channel for transparency
            else:
                img = Image.new('RGB', size, color)
            
            if text:
                d = ImageDraw.Draw(img)
                # A simple font for dummy text, adjust as needed
                try:
                    from PIL import ImageFont
                    font = ImageFont.truetype("arial.ttf", 10) # Try to load Arial
                except IOError:
                    font = ImageFont.load_default() # Fallback to default if Arial not found
                
                d.text((5, 5), text, fill=(0, 0, 0), font=font)
            img.save(filename)

        dummy_textures_to_create = [
            ("wall_tex.png", (128, 128, 128), "WALL_TEX", False),
            ("ceiling_tex.png", (100, 100, 100), "CEILING_TEX", False),
            ("floor_tex.png", (150, 150, 150), "FLOOR_TEX", False),
            ("brick_tex.png", (180, 80, 80), "BRICK_TEX", False),
            ("clip.png", (0, 0, 0), "CLIP", True), # Transparent
            ("water_tex.png", (50, 50, 200), "WATER_TEX", True) # Transparent
        ]

        # Only create dummy textures if the pre_extracted_textures_folder is empty
        if not os.listdir(self.pre_extracted_textures_folder_var.get()):
            for tex_name, color, text, transparent in dummy_textures_to_create:
                dummy_path = os.path.join(self.pre_extracted_textures_folder_var.get(), tex_name)
                if not os.path.exists(dummy_path):
                    create_dummy_png(dummy_path, color=color, text=text, transparent=transparent)
                    print(f"Created dummy texture: {dummy_path}")
            print("\nSetup of dummy textures complete.")
        else:
            print(f"Pre-extracted textures folder '{self.pre_extracted_textures_folder_var.get()}' is not empty. Skipping dummy texture creation.")


class TextRedirector:
    """A class to redirect stdout and stderr to a Tkinter Text widget."""
    def __init__(self, widget):
        self.widget = widget

    def write(self, s):
        # Schedule the update on the main Tkinter thread
        self.widget.after(0, self._write_to_widget, s)

    def _write_to_widget(self, s):
        self.widget.config(state='normal') # Enable editing
        self.widget.insert(tk.END, s, "console_output") # Apply tag for color
        self.widget.see(tk.END) # Auto-scroll to the end
        self.widget.config(state='disabled') # Disable editing

    def flush(self):
        pass # Required for file-like object


if __name__ == "__main__":
    root = tk.Tk()
    app = QuakeVmapConverterApp(root)
    root.mainloop()
