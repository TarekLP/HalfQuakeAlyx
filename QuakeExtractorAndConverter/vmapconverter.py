import os
import re
import shutil
import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import threading
import sys
import subprocess
import struct
from PIL import Image

# --- Quake 1 Default Palette (RGB values 0-255) ---
QUAKE_PALETTE = [
    (0, 0, 0), (15, 15, 15), (31, 31, 31), (47, 47, 47), (63, 63, 63), (75, 75, 75), (91, 91, 91), (107, 107, 107),
    (123, 123, 123), (139, 139, 139), (155, 155, 155), (171, 171, 171), (187, 187, 187), (203, 203, 203), (219, 219, 219), (235, 235, 235),
    (15, 11, 7), (23, 15, 11), (31, 19, 15), (39, 23, 19), (47, 27, 23), (55, 31, 27), (63, 35, 31), (71, 39, 35),
    (79, 43, 39), (87, 47, 43), (95, 51, 47), (103, 55, 51), (111, 59, 55), (119, 63, 59), (127, 67, 63), (135, 71, 67),
    (15, 7, 3), (23, 11, 7), (31, 15, 11), (39, 19, 15), (47, 23, 19), (55, 27, 23), (63, 31, 27), (71, 35, 31),
    (79, 39, 35), (87, 43, 39), (95, 47, 43), (103, 51, 47), (111, 55, 51), (119, 59, 55), (127, 63, 59), (135, 67, 63),
    (15, 15, 3), (23, 23, 7), (31, 31, 11), (39, 39, 15), (47, 47, 19), (55, 55, 23), (63, 63, 27), (71, 71, 31),
    (79, 79, 35), (87, 87, 39), (95, 95, 43), (103, 103, 47), (111, 111, 51), (119, 119, 55), (127, 127, 59), (135, 135, 63),
    (7, 3, 15), (11, 7, 23), (15, 11, 31), (19, 15, 39), (23, 19, 47), (27, 23, 55), (31, 27, 63), (35, 31, 71),
    (39, 35, 79), (43, 39, 87), (47, 43, 95), (51, 47, 103), (55, 51, 111), (59, 55, 119), (63, 59, 127), (67, 63, 135),
    (3, 7, 15), (7, 11, 23), (11, 15, 31), (15, 19, 39), (19, 23, 47), (23, 27, 55), (27, 31, 63), (31, 35, 71),
    (35, 39, 79), (39, 43, 87), (43, 47, 95), (47, 51, 103), (51, 55, 111), (55, 59, 119), (59, 63, 127), (63, 67, 135),
    (3, 15, 15), (7, 23, 23), (11, 31, 31), (15, 39, 39), (19, 47, 47), (23, 55, 55), (27, 63, 63), (31, 71, 71),
    (35, 79, 79), (39, 87, 87), (43, 95, 95), (47, 103, 103), (51, 111, 111), (55, 119, 119), (59, 127, 127), (63, 135, 135),
    (15, 3, 7), (23, 7, 11), (31, 11, 15), (39, 15, 19), (47, 19, 23), (55, 23, 27), (63, 27, 31), (71, 31, 35),
    (79, 35, 39), (87, 39, 43), (95, 43, 47), (103, 47, 51), (111, 51, 55), (119, 55, 59), (127, 59, 63), (135, 63, 67),
    (7, 15, 3), (11, 23, 7), (15, 31, 11), (19, 39, 15), (23, 47, 19), (27, 55, 23), (31, 63, 27), (35, 71, 31),
    (39, 79, 35), (43, 87, 39), (47, 95, 43), (51, 103, 47), (55, 111, 51), (59, 119, 55), (63, 127, 59), (67, 135, 63),
    (15, 7, 7), (23, 11, 11), (31, 15, 15), (39, 19, 19), (47, 23, 23), (55, 27, 27), (63, 31, 31), (71, 35, 35),
    (79, 39, 39), (87, 43, 43), (95, 47, 47), (103, 51, 51), (111, 55, 55), (119, 59, 59), (127, 63, 63), (135, 67, 67),
    (7, 3, 3), (11, 7, 7), (15, 11, 11), (19, 15, 15), (23, 19, 19), (27, 23, 23), (31, 27, 27), (35, 31, 31),
    (39, 35, 35), (43, 39, 39), (47, 43, 43), (51, 47, 47), (55, 51, 51), (59, 55, 55), (63, 59, 59), (67, 63, 63),
    (3, 7, 3), (7, 11, 7), (11, 15, 11), (15, 19, 15), (19, 23, 19), (23, 27, 23), (27, 31, 27), (31, 35, 31),
    (35, 39, 35), (39, 43, 39), (43, 47, 43), (47, 51, 47), (51, 55, 51), (55, 59, 55), (59, 63, 59), (63, 67, 63),
    (7, 3, 7), (11, 7, 11), (15, 11, 15), (19, 15, 19), (23, 19, 23), (27, 23, 27), (31, 27, 31), (35, 31, 35),
    (39, 35, 39), (43, 39, 43), (47, 43, 47), (51, 47, 51), (55, 51, 55), (59, 55, 59), (63, 59, 63), (67, 63, 67),
    (3, 3, 7), (7, 7, 11), (11, 11, 15), (15, 15, 19), (19, 19, 23), (23, 23, 27), (27, 27, 31), (31, 31, 35),
    (35, 35, 39), (39, 39, 43), (43, 43, 47), (47, 47, 51), (51, 51, 55), (55, 55, 59), (59, 59, 63), (63, 63, 67),
    (15, 3, 3), (23, 7, 7), (31, 11, 11), (39, 15, 15), (47, 19, 19), (55, 23, 23), (63, 27, 27), (71, 31, 31),
    (79, 35, 35), (87, 39, 39), (95, 43, 43), (103, 47, 47), (111, 51, 51), (119, 55, 55), (127, 59, 59), (135, 63, 63),
    (63, 0, 0), (71, 0, 0), (79, 0, 0), (87, 0, 0), (95, 0, 0), (103, 0, 0), (111, 0, 0), (119, 0, 0),
    (127, 0, 0), (135, 0, 0), (143, 0, 0), (151, 0, 0), (159, 0, 0), (167, 0, 0), (175, 0, 0), (183, 0, 0),
    (63, 63, 0), (71, 71, 0), (79, 79, 0), (87, 87, 0), (95, 95, 0), (103, 103, 0), (111, 111, 0), (119, 119, 0),
    (127, 127, 0), (135, 135, 0), (143, 143, 0), (151, 151, 0), (159, 159, 0), (167, 167, 0), (175, 175, 0), (183, 183, 0),
    (0, 63, 0), (0, 71, 0), (0, 79, 0), (0, 87, 0), (0, 95, 0), (0, 103, 0), (0, 111, 0), (0, 119, 0),
    (0, 127, 0), (0, 135, 0), (0, 143, 0), (0, 151, 0), (0, 159, 0), (0, 167, 0), (0, 175, 0), (0, 183, 0),
    (0, 63, 63), (0, 71, 71), (0, 79, 79), (0, 87, 87), (0, 95, 95), (0, 103, 103), (0, 111, 111), (0, 119, 119),
    (0, 127, 127), (0, 135, 135), (0, 143, 143), (0, 151, 151), (0, 159, 159), (0, 167, 167), (0, 175, 175), (0, 183, 183),
    (0, 0, 63), (0, 0, 71), (0, 0, 79), (0, 0, 87), (0, 0, 95), (0, 0, 103), (0, 0, 111), (0, 0, 119),
    (0, 0, 127), (0, 0, 135), (0, 0, 143), (0, 0, 151), (0, 0, 159), (0, 0, 167), (0, 0, 175), (0, 0, 183),
    (63, 0, 63), (71, 0, 71), (79, 0, 79), (87, 0, 87), (95, 0, 95), (103, 0, 103), (111, 0, 111), (119, 0, 119),
    (127, 0, 127), (135, 0, 135), (143, 0, 143), (151, 0, 151), (159, 0, 159), (167, 0, 167), (175, 0, 175), (183, 0, 183),
    (31, 31, 0), (39, 39, 0), (47, 47, 0), (55, 55, 0), (63, 63, 0), (71, 71, 0), (79, 79, 0), (87, 87, 0),
    (95, 95, 0), (103, 103, 0), (111, 111, 0), (119, 119, 0), (127, 127, 0), (135, 135, 0), (143, 143, 0), (151, 151, 0),
    (0, 31, 31), (0, 39, 39), (0, 47, 47), (0, 55, 55), (0, 63, 63), (0, 71, 71), (0, 79, 79), (0, 87, 87),
    (0, 95, 95), (0, 103, 103), (0, 111, 111), (0, 119, 119), (0, 127, 127), (0, 135, 135), (0, 143, 143), (0, 151, 151),
    (31, 0, 31), (39, 0, 39), (47, 0, 47), (55, 0, 55), (63, 0, 63), (71, 0, 71), (79, 0, 79), (87, 0, 87),
    (95, 0, 95), (103, 0, 103), (111, 0, 111), (119, 0, 119), (127, 0, 127), (135, 0, 135), (143, 0, 143), (151, 0, 151),
    (47, 31, 15), (55, 39, 23), (63, 47, 31), (71, 55, 39), (79, 63, 47), (87, 71, 55), (95, 79, 63), (103, 87, 71),
    (111, 95, 79), (119, 103, 87), (127, 111, 95), (135, 119, 103), (143, 127, 111), (151, 135, 119), (159, 143, 127), (167, 151, 135),
    (183, 159, 127), (191, 167, 135), (199, 175, 143), (207, 183, 151), (215, 191, 159), (223, 199, 167), (231, 207, 175), (239, 215, 183),
    (247, 223, 191), (255, 231, 199), (255, 239, 207), (255, 247, 215), (255, 255, 223), (255, 255, 231), (255, 255, 239), (255, 255, 247)
]
# Flatten the palette list of tuples into a single list of integers
FLATTENED_PALETTE = [c for color_tuple in QUAKE_PALETTE for c in color_tuple]


def parse_quake_map(map_filepath):
    """
    Parses a Quake .map file to extract brush geometry (planes) and their original texture names.
    It identifies brush blocks within entities and accurately extracts all brush planes,
    ignoring other entity properties like key-value pairs.
    """
    brushes = []          # List to store all parsed brushes, each containing its planes
    unique_textures = set() # To collect all unique texture names
    current_brush_planes = [] # List to store planes for the current brush being parsed
    
    # State flags to correctly identify entity and brush blocks within the .map file
    in_entity_block = False
    
    try:
        with open(map_filepath, 'r') as f:
            print(f"  Attempting to parse map file: {map_filepath}")
            for line_num, line in enumerate(f, 1):
                stripped_line = line.strip()

                # Skip comments and empty lines for cleaner parsing
                if not stripped_line or stripped_line.startswith('//'):
                    continue

                if stripped_line == '{':
                    if not in_entity_block:
                        # This marks the beginning of a top-level entity (e.g., worldspawn)
                        in_entity_block = True
                        current_brush_planes = [] # Reset for potential new brush
                    else:
                        # This marks the beginning of a brush block within an entity
                        current_brush_planes = [] # Initialize list for planes of this new brush
                elif stripped_line == '}':
                    if current_brush_planes:
                        # If current_brush_planes has planes, it's a completed brush
                        brushes.append(current_brush_planes)
                        current_brush_planes = [] # Reset for next brush
                    elif in_entity_block:
                        # End of an entity block
                        in_entity_block = False
                else:
                    # If inside an entity block, attempt to parse a plane definition
                    if in_entity_block:
                        # Regex to extract three 3D points and the texture name.
                        # ( x1 y1 z1 ) ( x2 y2 z2 ) ( x3 y3 z3 ) TEXTURE_NAME [ ux uy uz offsetX ] [ vx vy vz offsetY ] rotation scaleX scaleY
                        plane_match = re.match(r'\(\s*([\d\.\-]+)\s+([\d\.\-]+)\s+([\d\.\-]+)\s*\)\s*\(\s*([\d\.\-]+)\s+([\d\.\-]+)\s+([\d\.\-]+)\s*\)\s*\(\s*([\d\.\-]+)\s+([\d\.\-]+)\s+([\d\.\-]+)\s*\)\s*([^\s]+).*', stripped_line)
                        if plane_match:
                            # Extract and convert points to floats
                            p1 = (float(plane_match.group(1)), float(plane_match.group(2)), float(plane_match.group(3)))
                            p2 = (float(plane_match.group(4)), float(plane_match.group(5)), float(plane_match.group(6)))
                            p3 = (float(plane_match.group(7)), float(plane_match.group(8)), float(plane_match.group(9)))
                            texture_name = plane_match.group(10).lower() # Get texture name and convert to lowercase

                            current_brush_planes.append({
                                'plane': (p1, p2, p3),
                                'texture': texture_name # Re-including texture name here
                            })
                            unique_textures.add(texture_name) # Add to unique textures set
                        # Lines not matching a plane within a brush block are ignored (e.g., UV/lightmap data or entity properties)
        
        # Add any remaining brush planes if the file ends abruptly without a closing brace
        if current_brush_planes:
            brushes.append(current_brush_planes)

        print(f"  Finished parsing {map_filepath}. Found {len(brushes)} brushes and {len(unique_textures)} unique textures.")
        return brushes, list(unique_textures)
    except FileNotFoundError:
        print(f"[ERROR] Map file not found: {map_filepath}")
        return [], []
    except Exception as e:
        print(f"[ERROR] An error occurred while parsing {map_filepath}: {e}")
        return [], []


def extract_and_save_texture_png(texture_name, output_dir, wad_files_paths=None):
    """
    Extracts the texture data from Quake .wad files and saves it as a PNG image.
    This implementation assumes Quake 1 (WAD2) format and uses a hardcoded palette.
    """
    if not wad_files_paths:
        print(f"  [ERROR] No WAD file paths provided. Cannot extract texture '{texture_name}'.")
        return False

    png_filepath = os.path.join(output_dir, f"{texture_name}.png")
    os.makedirs(os.path.dirname(png_filepath), exist_ok=True)

    if os.path.exists(png_filepath):
        print(f"  Texture '{texture_name}.png' already exists. Skipping extraction.")
        return True # Assume it's already extracted

    # Ensure wad_files_paths is always a list
    wad_files_to_check = []
    if isinstance(wad_files_paths, str):
        wad_files_to_check.append(wad_files_paths)
    elif isinstance(wad_files_paths, list):
        wad_files_to_check.extend(wad_files_paths)
    else:
        print(f"  [ERROR] Invalid wad_files_paths type: {type(wad_files_paths)}. Must be string or list of strings.")
        return False

    found_texture_data = False

    for wad_file_path in wad_files_to_check:
        if not os.path.exists(wad_file_path):
            print(f"  [WARNING] WAD file not found: {wad_file_path}")
            continue

        try:
            with open(wad_file_path, 'rb') as f:
                # Read WAD header
                header = f.read(12)
                magic, num_lumps, lump_offset = struct.unpack('<4sII', header) # Little-endian

                if magic != b'WAD2':
                    print(f"  [WARNING] '{wad_file_path}' is not a WAD2 file (magic: {magic}). Skipping.")
                    continue

                f.seek(lump_offset)

                # Read lump directory
                for _ in range(num_lumps):
                    lump_entry = f.read(32)
                    # Handle potential EOF if num_lumps is wrong or file is truncated
                    if len(lump_entry) < 32:
                        print(f"  [WARNING] Truncated WAD directory in {wad_file_path}.")
                        break
                    
                    lump_offset_data, lump_disk_size, lump_size, lump_type, lump_compression, lump_dummy, lump_name_raw = \
                        struct.unpack('<IIBBH16s', lump_entry)
                    
                    lump_name = lump_name_raw.decode('ascii').split('\0')[0].lower()

                    if lump_name == texture_name:
                        print(f"  Found texture '{texture_name}' in '{wad_file_path}'.")
                        current_pos = f.tell() # Save current position
                        f.seek(lump_offset_data)

                        # Read texture header (MIPTEX_HEADER)
                        tex_header = f.read(40)
                        if len(tex_header) < 40:
                            print(f"  [WARNING] Truncated MIPTEX header for '{texture_name}' in {wad_file_path}.")
                            f.seek(current_pos) # Restore position
                            continue
                        
                        tex_name_raw, tex_width, tex_height, mip_offset0, _, _, _ = \
                            struct.unpack('<16sIIII', tex_header)
                        
                        # We only need the first (largest) mipmap
                        f.seek(lump_offset_data + mip_offset0)
                        
                        # Read pixel data
                        pixel_data_size = tex_width * tex_height
                        pixel_data = f.read(pixel_data_size)

                        if len(pixel_data) < pixel_data_size:
                            print(f"  [WARNING] Truncated pixel data for '{texture_name}' in {wad_file_path}.")
                            f.seek(current_pos) # Restore position
                            continue
                        
                        img = Image.new('P', (tex_width, tex_height))
                        img.putpalette(FLATTENED_PALETTE)
                        img.putdata(pixel_data)

                        # If texture name starts with '{', make color 255 transparent
                        if texture_name.startswith('{'):
                            img.info['transparency'] = 255 # Set index 255 as transparent
                            print(f"  Marked '{texture_name}' (palette index 255) as transparent.")

                        img.save(png_filepath)
                        print(f"  Successfully extracted and saved '{png_filepath}'.")
                        found_texture_data = True # Indicate success
                        f.seek(current_pos) # Restore file position
                        break # Found texture in this WAD, move to next
                if found_texture_data:
                    break # Found texture in one WAD, no need to check others

        except Exception as e:
            print(f"  [ERROR] Could not read WAD file '{wad_file_path}' or extract texture '{texture_name}': {e}")
            # Continue to next WAD file if one fails
            continue

    if not found_texture_data:
        print(f"  [WARNING] Texture '{texture_name}' not found in any provided WAD files.")
        print(f"  Please ensure you manually provide '{texture_name}.png' at '{png_filepath}' if it's missing.")
        return False # Indicate texture not found

    return True # Indicate successful extraction


def convert_png_to_vtf(png_filepath, vtf_output_dir, vtex_path, s1_game_content_root, console_widget):
    """
    Converts a PNG image to a Source 1 VTF file using vtex.exe.
    """
    vtf_name = os.path.splitext(os.path.basename(png_filepath))[0]
    vtf_filepath = os.path.join(vtf_output_dir, f"{vtf_name}.vtf")

    # vtex.exe requires VPROJECT to be set to the game's content root (e.g., tf, hl2)
    # and often expects to be run from its own bin directory.
    
    # Ensure output directory exists for vtex
    os.makedirs(vtf_output_dir, exist_ok=True)

    # Command to run vtex.exe
    # -shader UnlitGeneric: A common simple shader for basic textures
    # -format DXT1: A common compressed format for diffuse textures
    # -alpha: Include alpha channel if present (for transparent textures)
    # -nocompress: If you want uncompressed textures (larger file size)
    # -file <input_png_path>
    
    command = [
        vtex_path,
        "-quiet", # Suppress most vtex output
        "-mkdir", # Create output directories if they don't exist
        "-shader", "UnlitGeneric", # Basic shader
        "-format", "DXT1", # Common compressed format for diffuse
        # "-alpha", # Only add if the image actually has transparency
        png_filepath
    ]

    # Check if the PNG has transparency to decide on -alpha flag
    try:
        with Image.open(png_filepath) as img:
            if img.mode == 'RGBA' or (img.mode == 'P' and 'transparency' in img.info):
                command.insert(2, "-alpha") # Insert -alpha flag after -quiet
                console_widget.insert(tk.END, f"  [VTEX] Detected transparency for '{vtf_name}', adding -alpha flag.\n")
    except Exception as e:
        console_widget.insert(tk.END, f"  [VTEX_WARNING] Could not check transparency for '{png_filepath}': {e}\n")

    env = os.environ.copy()
    env['VPROJECT'] = s1_game_content_root
    
    # vtex.exe usually expects its CWD to be its own bin directory
    vtex_bin_dir = os.path.dirname(vtex_path)

    console_widget.insert(tk.END, f"  [VTEX] Converting '{os.path.basename(png_filepath)}' to VTF...\n")
    console_widget.insert(tk.END, f"  [VTEX] VPROJECT set to: '{env['VPROJECT']}'\n")
    console_widget.insert(tk.END, f"  [VTEX] CWD for vtex.exe: '{vtex_bin_dir}'\n")
    console_widget.insert(tk.END, f"  [VTEX] Command: {' '.join(command)}\n")
    console_widget.see(tk.END)

    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace', env=env, cwd=vtex_bin_dir)
        stdout, stderr = process.communicate()

        if stdout:
            console_widget.insert(tk.END, f"  [VTEX_STDOUT] {stdout}\n")
        if stderr:
            console_widget.insert(tk.END, f"  [VTEX_STDERR] {stderr}\n")

        if process.returncode != 0:
            console_widget.insert(tk.END, f"  [ERROR] vtex.exe exited with code {process.returncode} for '{vtf_name}'.\n")
            return False
        else:
            # vtex outputs VTF to the VPROJECT's materials/ folder by default,
            # but we want it in our addon's materials folder.
            # We need to move it from the VPROJECT's materials folder to our output_dir.
            # vtex will output to <VPROJECT>/materials/<texture_name>.vtf
            # So we need to construct that path.
            expected_vtf_in_vproject = os.path.join(s1_game_content_root, "materials", f"{vtf_name}.vtf")
            
            if os.path.exists(expected_vtf_in_vproject):
                shutil.move(expected_vtf_in_vproject, vtf_filepath)
                console_widget.insert(tk.END, f"  Successfully converted and moved '{vtf_name}.vtf' to '{vtf_filepath}'.\n")
                return True
            else:
                console_widget.insert(tk.END, f"  [ERROR] vtex.exe did not produce VTF at expected location: '{expected_vtf_in_vproject}'.\n")
                return False

    except FileNotFoundError:
        console_widget.insert(tk.END, f"[ERROR] vtex.exe not found at '{vtex_path}'. Please check the path.\n")
        return False
    except Exception as e:
        console_widget.insert(tk.END, f"[ERROR] An unexpected error occurred while running vtex.exe for '{vtf_name}': {e}\n")
        return False


def generate_vmf_content(map_data):
    """
    Generates the content for a Source 1 .vmf file from the parsed Quake map data.
    Brush faces will be assigned their original Quake texture names (for VTF lookup).
    Includes a basic info_player_start and empty hidden block for VMF validity.
    """
    vmf_lines = []
    
    # VMF header information
    vmf_lines.append("versioninfo")
    vmf_lines.append("{")
    vmf_lines.append("    \"mapversion\" \"1\"")
    vmf_lines.append("    \"editorversion\" \"400\"")
    vmf_lines.append("    \"editorbuild\" \"8000\"")
    vmf_lines.append("    \"formatversion\" \"1\"")
    vmf_lines.append("    \"prefab\" \"0\"")
    vmf_lines.append("}")

    # Worldspawn entity block
    vmf_lines.append("world")
    vmf_lines.append("{")
    vmf_lines.append("    \"id\" \"1\"") # Worldspawn typically has ID 1
    vmf_lines.append("    \"mapversion\" \"1\"")
    vmf_lines.append("    \"classname\" \"worldspawn\"")

    # Define a scaling factor for Quake units to Source units.
    # The 0.75 scale is intended for the final Alyx map size.
    SCALE_FACTOR = 0.75 
    
    # Unique ID counter for solids (brushes) and sides, starting after worldspawn's ID 1
    current_id = 2 

    # Iterate through each brush parsed from the Quake map
    for brush_idx, brush_planes in enumerate(map_data):
        vmf_lines.append("    solid")
        vmf_lines.append("    {")
        vmf_lines.append(f"        \"id\" \"{current_id}\"")
        current_id += 1

        # Iterate through each plane (side) of the current brush
        for plane_data in brush_planes:
            vmf_lines.append("        side")
            vmf_lines.append("        {")
            vmf_lines.append(f"            \"id\" \"{current_id}\"")
            current_id += 1

            # Quake uses Z-up, Source (1 and 2) typically Y-up.
            # Conversion: (x_quake, y_quake, z_quake) -> (x_source, z_source, -y_source)
            # This is the standard conversion that usually works.
            p1 = plane_data['plane'][0]
            p2 = plane_data['plane'][1]
            p3 = plane_data['plane'][2]

            # Apply Z-up to Y-up conversion and scaling to each point
            p1_s = (p1[0] * SCALE_FACTOR, p1[2] * SCALE_FACTOR, -p1[1] * SCALE_FACTOR)
            p2_s = (p2[0] * SCALE_FACTOR, p2[2] * SCALE_FACTOR, -p2[1] * SCALE_FACTOR)
            p3_s = (p3[0] * SCALE_FACTOR, p3[2] * SCALE_FACTOR, -p3[1] * SCALE_FACTOR)

            # Format coordinates for VMF plane string: "(x1 y1 z1) (x2 y2 z2) (x3 y3 z3)"
            vmf_lines.append(f"            \"plane\" \"({p1_s[0]:.6f} {p1_s[1]:.6f} {p1_s[2]:.6f}) ({p2_s[0]:.6f} {p2_s[1]:.6f} {p2_s[2]:.6f}) ({p3_s[0]:.6f} {p3_s[1]:.6f} {p3_s[2]:.6f})\"")

            # Assign the original Quake texture name.
            # Source 1 VMFs typically reference materials without the 'materials/' prefix and without '.vtf' extension.
            # Hammer will look for 'materials/TEXTURE_NAME.vtf' in the game's content.
            vmf_lines.append(f"            \"material\" \"{plane_data['texture'].upper()}\"") 

            # Basic UVs for VMF. These are simplified and might require manual fine-tuning in Hammer.
            # A common scale for Quake-like textures might be 16 units per texture repeat (1/16 = 0.0625).
            vmf_lines.append("            \"uaxis\" \"[1 0 0 0] 0.0625\"") # X-axis projection, scale 0.0625
            vmf_lines.append("            \"vaxis\" \"[0 1 0 0] 0.0625\"") # Y-axis projection, scale 0.0625
            vmf_lines.append("            \"rotation\" \"0\"")
            vmf_lines.append("            \"lightmapscale\" \"16\"") # Default lightmap scale for lightmap grid
            vmf_lines.append("            \"smoothing_groups\" \"0\"")
            vmf_lines.append("        }") # End side
        
        # Editor block for solid (brush) in VMF
        vmf_lines.append("        \"editor\"")
        vmf_lines.append("        {")
        vmf_lines.append("            \"color\" \"255 0 0\"") # Default brush color in Hammer (Red)
        vmf_lines.append("            \"visgroupshown\" \"1\"") # Brush visible in Hammer
        vmf_lines.append("            \"visgroupautoshown\" \"1\"") # Brush auto-visible
        vmf_lines.append("        }")
        vmf_lines.append("    }") # End solid

    # Editor block for worldspawn in VMF
    vmf_lines.append("    \"editor\"")
    vmf_lines.append("    {")
    vmf_lines.append("        \"color\" \"255 0 0\"")
    vmf_lines.append("        \"visgroupshown\" \"1\"")
    vmf_lines.append("        \"visgroupautoshown\" \"1\"")
    vmf_lines.append("        \"logicalpos\" \"[0 0]\"")
    vmf_lines.append("    }")
    vmf_lines.append("}") # End world

    # Add a minimal info_player_start entity
    vmf_lines.append("entity")
    vmf_lines.append("{")
    vmf_lines.append(f"    \"id\" \"{current_id}\"")
    current_id += 1
    vmf_lines.append("    \"classname\" \"info_player_start\"")
    vmf_lines.append("    \"origin\" \"0 0 64\"") # Default spawn point
    vmf_lines.append("    \"angles\" \"0 0 0\"") # Default orientation
    vmf_lines.append("    \"editor\"")
    vmf_lines.append("    {")
    vmf_lines.append("        \"color\" \"255 255 0\"") # Yellow for player start
    vmf_lines.append("        \"visgroupshown\" \"1\"")
    vmf_lines.append("        \"visgroupautoshown\" \"1\"")
    vmf_lines.append("        \"logicalpos\" \"[0 0]\"")
    vmf_lines.append("    }")
    vmf_lines.append("}")

    # Add an empty hidden block (often present in VMFs)
    vmf_lines.append("hidden")
    vmf_lines.append("{")
    vmf_lines.append("}")

    return "\n".join(vmf_lines)


def convert_folder(input_folder, output_base_folder, wad_files_paths, vtex_path, s1_game_content_root, console_widget):
    """
    Orchestrates the conversion process:
    1. Parses Quake .map files.
    2. Extracts textures from WADs to PNG.
    3. Converts PNGs to Source 1 VTF files using vtex.exe.
    4. Generates Source 1 .vmf files (using original texture names).
    Output messages are redirected to the provided console_widget.
    """
    def print_to_console(s):
        """Helper function to print messages to the GUI console and auto-scroll."""
        console_widget.insert(tk.END, s + "\n")
        console_widget.see(tk.END) # Auto-scroll to the end
        console_widget.update_idletasks() # Force GUI update

    # --- Input Validation ---
    if not os.path.exists(input_folder):
        print_to_console(f"Error: Quake Maps Input folder '{input_folder}' does not exist. Please check the path.")
        return
    if not vtex_path or not os.path.exists(vtex_path):
        print_to_console(f"Error: vtex.exe not found at '{vtex_path}'. Please check the path.")
        return
    if not s1_game_content_root or not os.path.exists(s1_game_content_root):
        print_to_console(f"Error: Source 1 Game Content Root '{s1_game_content_root}' does not exist. Please check the path.")
        return
    if not wad_files_paths:
        print_to_console(f"Error: No Quake WAD files paths provided. Cannot extract textures.")
        return
    for wad_path in (wad_files_paths if isinstance(wad_files_paths, list) else [wad_files_paths]):
        if not os.path.exists(wad_path):
            print_to_console(f"Error: Quake WAD file '{wad_path}' not found. Please check the path(s).")
            return

    # Define the addon content structure: [output_base_folder]/quakeautomatedscriptport/[maps|materials]
    addon_content_dir = os.path.join(output_base_folder, "quakeautomatedscriptport")
    maps_output_dir = os.path.join(addon_content_dir, "maps")
    materials_output_dir = os.path.join(addon_content_dir, "materials") 

    # Create all necessary output directories, including the addon folder itself
    os.makedirs(addon_content_dir, exist_ok=True)
    os.makedirs(maps_output_dir, exist_ok=True)
    os.makedirs(materials_output_dir, exist_ok=True) # Create materials dir for VTF files

    map_files_found = False
    all_unique_textures = set()

    print_to_console(f"\n--- Starting Map Conversion Process ---")
    print_to_console(f"Scanning input folder: '{input_folder}' for .map files...")
    map_files_to_process = []
    # Walk through the input folder to find all .map files
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith(".map"):
                map_files_to_process.append(os.path.join(root, file))

    if not map_files_to_process:
        print_to_console(f"No .map files found in '{input_folder}' or its subdirectories. Nothing to convert.")
        return

    print_to_console(f"Found {len(map_files_to_process)} .map files to convert:")
    for map_filepath in map_files_to_process:
        print_to_console(f"- {map_filepath}")
        map_files_found = True
        map_name = os.path.splitext(os.path.basename(map_filepath))[0]
        # Construct the .vmf file path within the 'maps' subdirectory
        vmf_filepath = os.path.join(maps_output_dir, f"{map_name}.vmf")

        print_to_console(f"\nProcessing Quake map: {map_filepath}...")
        brushes, unique_textures_in_map = parse_quake_map(map_filepath) 
        all_unique_textures.update(unique_textures_in_map) # Collect all unique textures across all maps

        if brushes:
            vmf_content = generate_vmf_content(brushes)
            try:
                with open(vmf_filepath, 'w') as f:
                    f.write(vmf_content)
                print_to_console(f"Generated Source 1 .vmf file: {vmf_filepath}")
            except IOError as e:
                print_to_console(f"[ERROR] Could not write .vmf file '{vmf_filepath}': {e}")
            except Exception as e:
                print_to_console(f"[ERROR] An unexpected error occurred during VMF generation for {map_name}.vmf: {e}")
        else:
            print_to_console(f"No brushes found in {map_filepath}. Skipping .vmf generation.")

    if not map_files_found:
        print_to_console(f"No .map files were processed. Please ensure your input folder contains .map files.")
        return

    print_to_console("\n--- Extracting textures to PNG and converting to VTF ---")
    for texture in all_unique_textures:
        png_temp_filepath = os.path.join(materials_output_dir, f"{texture}.png")
        
        # 1. Extract to PNG
        if extract_and_save_texture_png(texture, materials_output_dir, wad_files_paths):
            # 2. Convert PNG to VTF
            convert_png_to_vtf(png_temp_filepath, materials_output_dir, vtex_path, s1_game_content_root, console_widget)
            # Optionally, remove the temporary PNG after VTF conversion
            try:
                os.remove(png_temp_filepath)
                print_to_console(f"  Removed temporary PNG: {os.path.basename(png_temp_filepath)}")
            except Exception as e:
                print_to_console(f"  [WARNING] Could not remove temporary PNG '{os.path.basename(png_temp_filepath)}': {e}")
        else:
            print_to_console(f"  Skipping VTF conversion for '{texture}' due to failed PNG extraction.")


    print_to_console("\n--- Conversion process completed. ---")
    print_to_console(f"Output files are located in: {addon_content_dir}")
    print_to_console("\nIMPORTANT NOTES FOR HALF-LIFE: ALYX:")
    print_to_console(f"1. Copy the entire '{os.path.basename(addon_content_dir)}' folder (located at '{addon_content_dir}')")
    print_to_console("   into your Half-Life: Alyx addon's 'content' directory.")
    print_to_console("   Example: `Half-Life Alyx/game/hlvr_addons/my_addon_name/content/`")
    print_to_console("2. This script provides a simplified conversion of Quake map geometry. Complex geometry (e.g., curved surfaces, precise UVs, advanced entities) are not fully handled.")
    print_to_console("3. Quake uses a Z-up coordinate system, while Source 2 typically uses Y-up. The script attempts to convert (X,Y,Z) to (X,Z,-Y). You might still need to adjust the map's orientation in Hammer after import.")
    print_to_console("4. **Material Assignment:** The generated VMFs will now include the original Quake texture names (e.g., 'WALL_TEX'). The script will generate corresponding Source 1 VTF files. Hammer will automatically look for these VTFs in the `materials/` folder.")
    print_to_console("5. For best results, you may need to manually adjust materials, brush geometry, and add entities in Half-Life: Alyx's Hammer editor.")


class QuakeVmapConverterApp:
    def __init__(self, master):
        self.master = master
        master.title("Quake .map to Alyx .vmap Converter")

        # Define dark theme colors for a modern look
        self.bg_dark_gray = "#2B2B2B"
        self.fg_light_gray = "#E0E0E0"
        self.button_bg = "#4A4A4A"
        self.button_fg = "#FFFFFF"
        self.console_bg = "#1E1E1E"
        self.console_text_color = "#BB86FC" # A shade of purple for console output

        master.config(bg=self.bg_dark_gray)

        # Use tk.StringVar for dynamic path updates in Entry widgets
        script_dir = os.path.dirname(__file__)
        self.input_folder_var = tk.StringVar(value=os.path.normpath(os.path.join(script_dir, "quake_maps_input")))
        self.output_folder_var = tk.StringVar(value=os.path.normpath(os.path.join(script_dir, "alyx_output")))
        
        # New: Quake WAD files path(s)
        # Pre-fill with common Quake paths for convenience, or leave empty.
        self.wad_files_var = tk.StringVar(value=os.path.normpath(r"F:\SteamLibrary\steamapps\common\Quake\id1\pak0.wad"))
        
        # New: vtex.exe path
        self.vtex_path_var = tk.StringVar(value=os.path.normpath(r"C:\Program Files (x86)\Steam\steamapps\common\Source SDK Base 2013 Singleplayer\bin\ep1\bin\vtex.exe"))
        
        # New: Source 1 Game Content Root (for VPROJECT)
        self.s1_game_content_root_var = tk.StringVar(value=os.path.normpath(r"C:\Program Files (x86)\Steam\steamapps\common\Source SDK Base 2013 Singleplayer\hl2"))


        self.create_widgets()
        self.setup_dummy_files() # Setup dummy files on app start for convenience

    def create_widgets(self):
        # Input Folder Selection
        tk.Label(self.master, text="Quake Maps Input Folder:", bg=self.bg_dark_gray, fg=self.fg_light_gray).pack(pady=(10, 0))
        input_frame = tk.Frame(self.master, bg=self.bg_dark_gray)
        input_frame.pack(fill=tk.X, padx=10)
        tk.Entry(input_frame, textvariable=self.input_folder_var, width=50, bg=self.button_bg, fg=self.button_fg, insertbackground=self.fg_light_gray).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(input_frame, text="Browse", command=lambda: self.browse_folder(self.input_folder_var), bg=self.button_bg, fg=self.button_fg, activebackground=self.fg_light_gray, activeforeground=self.button_bg).pack(side=tk.RIGHT)

        # Output Folder Selection
        tk.Label(self.master, text="Alyx Addon Content Base Folder (e.g., alyx_output):", bg=self.bg_dark_gray, fg=self.fg_light_gray).pack(pady=(10, 0))
        output_frame = tk.Frame(self.master, bg=self.bg_dark_gray)
        output_frame.pack(fill=tk.X, padx=10)
        tk.Entry(output_frame, textvariable=self.output_folder_var, width=50, bg=self.button_bg, fg=self.button_fg, insertbackground=self.fg_light_gray).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(output_frame, text="Browse", command=lambda: self.browse_folder(self.output_folder_var), bg=self.button_bg, fg=self.button_fg, activebackground=self.fg_light_gray, activeforeground=self.button_bg).pack(side=tk.RIGHT)

        # Quake WAD Files Path(s)
        tk.Label(self.master, text="Quake WAD Files Path(s) (e.g., pak0.wad):", bg=self.bg_dark_gray, fg=self.fg_light_gray).pack(pady=(10, 0))
        wad_frame = tk.Frame(self.master, bg=self.bg_dark_gray)
        wad_frame.pack(fill=tk.X, padx=10)
        tk.Entry(wad_frame, textvariable=self.wad_files_var, width=50, bg=self.button_bg, fg=self.button_fg, insertbackground=self.fg_light_gray).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(wad_frame, text="Browse", command=lambda: self.browse_file(self.wad_files_var, filetypes=[("WAD files", "*.wad")]), bg=self.button_bg, fg=self.button_fg, activebackground=self.fg_light_gray, activeforeground=self.button_bg).pack(side=tk.RIGHT)
        tk.Label(self.master, text="Separate multiple paths with ';'", bg=self.bg_dark_gray, fg=self.fg_light_gray, font=("Arial", 8)).pack(padx=10, anchor='w')

        # Source 1 VTF Converter (vtex.exe) Path
        tk.Label(self.master, text="Source 1 VTF Converter (vtex.exe) Path:", bg=self.bg_dark_gray, fg=self.fg_light_gray).pack(pady=(10, 0))
        vtex_frame = tk.Frame(self.master, bg=self.bg_dark_gray)
        vtex_frame.pack(fill=tk.X, padx=10)
        tk.Entry(vtex_frame, textvariable=self.vtex_path_var, width=50, bg=self.button_bg, fg=self.button_fg, insertbackground=self.fg_light_gray).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(vtex_frame, text="Browse", command=lambda: self.browse_file(self.vtex_path_var, filetypes=[("Executable files", "*.exe")]), bg=self.button_bg, fg=self.button_fg, activebackground=self.fg_light_gray, activeforeground=self.button_bg).pack(side=tk.RIGHT)

        # Source 1 Game Content Root
        tk.Label(self.master, text="Source 1 Game Content Root (for VPROJECT):", bg=self.bg_dark_gray, fg=self.fg_light_gray).pack(pady=(10, 0))
        s1_game_root_frame = tk.Frame(self.master, bg=self.bg_dark_gray)
        s1_game_root_frame.pack(fill=tk.X, padx=10)
        tk.Entry(s1_game_root_frame, textvariable=self.s1_game_content_root_var, width=50, bg=self.button_bg, fg=self.button_fg, insertbackground=self.fg_light_gray).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(s1_game_root_frame, text="Browse", command=lambda: self.browse_folder(self.s1_game_content_root_var), bg=self.button_bg, fg=self.button_fg, activebackground=self.fg_light_gray, activeforeground=self.button_bg).pack(side=tk.RIGHT)
        tk.Label(self.master, text="e.g., C:/Steam/steamapps/common/Team Fortress 2/tf", bg=self.bg_dark_gray, fg=self.fg_light_gray, font=("Arial", 8)).pack(padx=10, anchor='w')


        # Frame for buttons
        button_frame = tk.Frame(self.master, bg=self.bg_dark_gray)
        button_frame.pack(pady=10)

        self.compile_button = tk.Button(button_frame, text="Convert & Prepare", command=self.start_conversion_thread, bg=self.button_bg, fg=self.button_fg, activebackground=self.fg_light_gray, activeforeground=self.button_bg)
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

    def browse_file(self, path_var, filetypes=None):
        """Opens a file dialog to select a file and updates the StringVar."""
        file_selected = filedialog.askopenfilename(filetypes=filetypes)
        if file_selected:
            path_var.set(os.path.normpath(file_selected))

    def clear_console(self):
        """Clears the text in the console output area."""
        self.console_text.config(state='normal')
        self.console_text.delete(1.0, tk.END)
        self.console_text.config(state='disabled')

    def start_conversion_thread(self):
        """Starts the conversion process in a separate thread to keep the GUI responsive."""
        self.clear_console()
        self.compile_button.config(state='disabled') # Disable buttons during conversion
        self.clear_button.config(state='disabled')

        # Get current paths from entry widgets
        input_folder = self.input_folder_var.get()
        output_base_folder = self.output_folder_var.get()
        wad_files_paths_str = self.wad_files_var.get()
        vtex_path = self.vtex_path_var.get()
        s1_game_content_root = self.s1_game_content_root_var.get()

        # Split WAD paths string into a list
        wad_files_paths = [os.path.normpath(p.strip()) for p in wad_files_paths_str.split(';') if p.strip()]

        # Run conversion in a separate thread
        self.conversion_thread = threading.Thread(target=self.run_conversion, args=(input_folder, output_base_folder, wad_files_paths, vtex_path, s1_game_content_root))
        self.conversion_thread.start()
        # Start checking thread status periodically to re-enable buttons
        self.master.after(100, self.check_conversion_thread) 

    def run_conversion(self, input_folder, output_base_folder, wad_files_paths, vtex_path, s1_game_content_root):
        """Executes the map conversion logic."""
        try:
            convert_folder(input_folder, output_base_folder, wad_files_paths, vtex_path, s1_game_content_root, self.console_text)
            messagebox.showinfo("Conversion Complete", "Map conversion and texture preparation finished successfully!")
        except Exception as e:
            messagebox.showerror("Conversion Error", f"An unexpected error occurred during conversion: {e}")
            print(f"[ERROR] Critical error during conversion: {e}")
        finally:
            # Re-enable buttons in the main thread after conversion finishes
            self.master.after(0, self.enable_buttons)

    def check_conversion_thread(self):
        """Checks if the conversion thread is still alive and re-enables buttons when it finishes."""
        if self.conversion_thread.is_alive():
            self.master.after(100, self.check_conversion_thread) # Keep checking
        else:
            self.enable_buttons()

    def enable_buttons(self):
        """Re-enables the GUI buttons."""
        self.compile_button.config(state='normal')
        self.clear_button.config(state='normal')

    def setup_dummy_files(self):
        """
        Ensures input folder and dummy map exist for testing/initial setup.
        """
        # Ensure base directories exist
        os.makedirs(self.input_folder_var.get(), exist_ok=True)

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


class TextRedirector:
    """A class to redirect stdout and stderr to a Tkinter Text widget."""
    def __init__(self, widget):
        self.widget = widget

    def write(self, s):
        # Schedule the update on the main Tkinter thread to prevent threading issues with Tkinter
        self.widget.after(0, self._write_to_widget, s)

    def _write_to_widget(self, s):
        """Internal method to safely write text to the Tkinter Text widget."""
        self.widget.config(state='normal') # Enable editing
        self.widget.insert(tk.END, s, "console_output") # Apply tag for color
        self.widget.see(tk.END) # Auto-scroll to the end
        self.widget.config(state='disabled') # Disable editing
        self.widget.update_idletasks() # Force GUI update immediately

    def flush(self):
        """Required for file-like object compatibility."""
        pass 


if __name__ == "__main__":
    root = tk.Tk()
    app = QuakeVmapConverterApp(root)
    root.mainloop()
