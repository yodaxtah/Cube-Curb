# https://www.perplexity.ai/search/can-you-create-a-python-script-NGJIlr0fR_SeE7Eipelljg

import os
import re
import pathlib

def process_texture_line(line):
    # Split the line into main part and optional comment
    parts = line.split('//', 1)  # Split at the first occurrence of '//'
    main_part = parts[0].strip()  # Main part of the line (before the comment)
    comment = f" //{parts[1]}" if len(parts) > 1 else ""  # Preserve the comment if it exists

    # Match the texture command
    match = re.match(r'texture\s+(\w+)\s+(\S+)(.*)', main_part)
    if not match:
        return line  # Return the line unchanged if it's not a texture command

    texture_type, filename, params = match.groups()

    # Ensure filename is enclosed in double quotes
    if not filename.startswith('"') and not filename.endswith('"'):
        filename = f'"{filename}"'

    # Split remaining parameters and ensure defaults
    param_list = params.strip().split()
    while len(param_list) < 3:  # Ensure ROT, X, Y, SCALE are present
        param_list.append('0')  # Default for missing ROT, X, Y
    if len(param_list) < 4:
        param_list.append('1.0')  # Default SCALE value

    # Modify the diffuse texture if texture type is '0'
    if texture_type in ['0', 'c']:
        filename = modify_diffuse_texture(filename)
        param_list[-1] = str(float(param_list[-1]) / 4)

    # Reconstruct the line with updated values
    updated_line = f'texture {texture_type} {filename} {" ".join(param_list)}{comment}'
    return updated_line

def modify_diffuse_texture(filename):
    """
    Modifies the diffuse texture (texture type 0) by:
      - Prepending "harry/upscale/" to the filestem.
      - Appending "_diffuse" to the filestem.
      - Appending ".png" suffix to the filestem.
    """
    # Remove quotes for easier processing
    if filename.startswith('"') and filename.endswith('"'):
        filename = filename[1:-1]

    # Extract directory, filestem, and extension
    path = pathlib.Path(filename)
    new_path = "harry/upscale/" / path.parent / f"{path.stem}_diffuse.png"

    # Return the modified filename enclosed in quotes
    return f'"{new_path.as_posix()}"'

def process_config_file(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            stripped_line = line.strip()
            if stripped_line.startswith('texture'):
                processed_line = process_texture_line(stripped_line)
                outfile.write(processed_line + '\n')
            else:
                outfile.write(line)

if __name__ == '__main__':
    input_file = 'input.cfg'  # Replace with your input file name
    output_file = 'output.cfg'  # Replace with your desired output file name
    process_config_file(input_file, output_file)

for p in pathlib.Path(".").iterdir():
    p = pathlib.Path(p)
    t = pathlib.Path("temp.cfg")
    print(p.name)
    process_config_file(p.name, t.name)
    p.unlink()
    t.rename(p.name)

User = "harry"
d = pathlib.Path(r'C:\Users') / User / r'Documents\My Games\Sauerbraten\packages\base'
def copyover(pkg): shutil.copy(pathlib.Path(pkg + ".cfg").resolve(), d)