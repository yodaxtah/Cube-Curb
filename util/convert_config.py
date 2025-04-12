# https://www.perplexity.ai/search/can-you-create-a-python-script-NGJIlr0fR_SeE7Eipelljg

import os
import re
import pathlib
import shutil

def process_texture_line(line, upscale=True, rotation=None, x_offset=None, y_offset=None, scale=None):
    # Split the line into main part and optional comment
    parts = line.split('//', 1)  # Split at the first occurrence of '//'
    main_part = parts[0].strip()  # Main part of the line (before the comment)
    comment = f" //{parts[1]}" if len(parts) > 1 else ""  # Preserve the comment if it exists

    # Match the texture command
    match = re.match(r'texture\s+(\w+)\s+(\S+)(.*)', main_part)
    if not match:
        return line, False  # Return the line unchanged if it's not a texture command

    texture_type, filename, params = match.groups()

    # Ensure filename is enclosed in double quotes
    if not filename.startswith('"') and not filename.endswith('"'):
        filename = f'"{filename}"'

    # Modify the diffuse texture if texture type is '0'

    # Split remaining parameters and ensure defaults
    param_list = params.strip().split()
    while len(param_list) < 3:  # Ensure ROT, X, Y, SCALE are present
        param_list.append('0')  # Default for missing ROT, X, Y
    if len(param_list) < 4:
        param_list.append('1.0')  # Default SCALE value

    if upscale and texture_type in ['0', 'c'] and "_diffuse" not in filename:
        filename = modify_diffuse_texture(filename)
        param_list[1] = str(float(param_list[1]) * 4)
        param_list[2] = str(float(param_list[2]) * 4)
        param_list[3] = str(float(param_list[3]) / 4)

    upscaled = texture_type in ['0', 'c'] and "_diffuse" in filename
    if rotation != None:
        param_list[0] = rotation
    if x_offset != None:
        param_list[1] = str(float(x_offset) * 4) if upscaled else x_offset
    if y_offset != None:
        param_list[2] = str(float(y_offset) * 4) if upscaled else y_offset
    if scale != None:
        param_list[3] = str(float(scale) / 4) if upscaled else scale
    
    for i in range(4):
        param_list[i] = p[:-2] if (p := param_list[i])[-2:] == ".0" else p

    # Reconstruct the line with updated values
    updated_line = f'texture {texture_type} {filename} {" ".join(param_list)}{comment}'
    return updated_line, (texture_type in ['0', 'c'])

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
    new_path = "harry/upscale" / path.parent / f"{path.stem}_diffuse.png"

    # Return the modified filename enclosed in quotes
    return f'"{new_path.as_posix()}"'

def process_exec_line(line):
    # Split the line into main part and optional comment
    parts = line.split('//', 1)  # Split at the first occurrence of '//'
    main_part = parts[0].strip()  # Main part of the line (before the comment)
    comment = f" //{parts[1]}" if len(parts) > 1 else ""  # Preserve the comment if it exists

    # Match the texture command
    match = re.match(r'exec\s+(\S+)(.*)', main_part)
    if not match:
        return line  # Return the line unchanged if it's not a texture command

    filename, _ = match.groups()

    # Ensure filename is enclosed in double quotes
    if not filename.startswith('"') and not filename.endswith('"'):
        filename = f'"{filename}"'

    # Modify the diffuse texture if texture type is '0'
    if "harry/upscale/" not in filename and filename.startswith("\"packages/"):
        filename = "\"packages/harry/upscale/" + filename[len("\"packages/"):]

    # Reconstruct the line with updated values
    updated_line = f'exec {filename}{comment}'
    return updated_line

def process_texrotate_line(line):
    # Split the line into main part and optional comment
    parts = line.split('//', 1)  # Split at the first occurrence of '//'
    main_part = parts[0].strip()  # Main part of the line (before the comment)
    comment = f" //{parts[1]}" if len(parts) > 1 else ""  # Preserve the comment if it exists

    # Match the texture command
    match = re.match(r'texrotate\s+(\S+)(.*)', main_part)
    if not match:
        return line  # Return the line unchanged if it's not a texture command

    rotation, _ = match.groups()

    # Reconstruct the line with updated values
    updated_line = f'texrotate {rotation}'
    return updated_line, rotation

def process_texscale_line(line):
    # Split the line into main part and optional comment
    parts = line.split('//', 1)  # Split at the first occurrence of '//'
    main_part = parts[0].strip()  # Main part of the line (before the comment)
    comment = f" //{parts[1]}" if len(parts) > 1 else ""  # Preserve the comment if it exists

    # Match the texture command
    match = re.match(r'texscale\s+(\S+)(.*)', main_part)
    if not match:
        return line  # Return the line unchanged if it's not a texture command

    scale, _ = match.groups()

    # Reconstruct the line with updated values
    updated_line = f'texscale {scale}'
    return updated_line, scale

def process_texoffset_line(line):
    # Split the line into main part and optional comment
    parts = line.split('//', 1)  # Split at the first occurrence of '//'
    main_part = parts[0].strip()  # Main part of the line (before the comment)
    comment = f" //{parts[1]}" if len(parts) > 1 else ""  # Preserve the comment if it exists

    # Match the texture command
    match = re.match(r'texoffset\s+(\S+)\s+(\S+)(.*)', main_part)
    if not match:
        match = re.match(r'texoffset\s+(\S+)(.*)', main_part)
        if not match:
            return line  # Return the line unchanged if it's not a texture command
        else:
            x_offset, _ = match.groups()
            y_offset = "0"
    else:
        x_offset, y_offset, _ = match.groups()

    # Reconstruct the line with updated values
    updated_line = f'texoffset {x_offset} {y_offset}'
    return updated_line, x_offset, y_offset


def modify_buffer(buffer, rotation=None, x_offset=None, y_offset=None, scale=None):
    new_buffer = ""
    print(rotation, x_offset, y_offset, scale, repr(buffer))
    for line in buffer.splitlines():
        modified_line, _ = process_texture_line(line, False, rotation, x_offset, y_offset, scale)
        new_buffer += modified_line + "\n"
    return new_buffer


def process_lines(lines):
    buffer = ""
    output_lines = ""
    rotation = None
    x_offset = None
    y_offset = None
    scale = None
    for line in lines:
        stripped_line = line.strip()
        if stripped_line.startswith('texture '):
            processed_line, new_texture = process_texture_line(stripped_line)
            processed_line += "\n"
            if new_texture:
                output_lines += modify_buffer(buffer, rotation, x_offset, y_offset, scale)
                rotation = None
                x_offset = None
                y_offset = None
                scale = None
                buffer = ""
            buffer += processed_line
        elif stripped_line.startswith("texrotate "):
            updated_line, rotation = process_texrotate_line(stripped_line)
            buffer += "// " + updated_line + "\n"
        elif stripped_line.startswith("texscale "):
            updated_line, scale = process_texscale_line(stripped_line)
            buffer += "// " + updated_line + "\n"
        elif stripped_line.startswith("texoffset "):
            updated_line, x_offset, y_offset = process_texoffset_line(stripped_line)
            buffer += "// " + updated_line + "\n"
        elif stripped_line == "":
            buffer += "\n"
        else:
            output_lines += modify_buffer(buffer, rotation, x_offset, y_offset, scale)
            rotation = None
            x_offset = None
            y_offset = None
            scale = None
            buffer = ""
            if stripped_line.startswith("exec "):
                processed_line = process_exec_line(stripped_line)
                output_lines += processed_line + "\n"
            else:
                output_lines += line + "\n" # write to buffer until next texture is read: buffer += line + "\n"
    output_lines += buffer
    return output_lines


def process_config_file(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        buffer = ""
        rotation = None
        x_offset = None
        y_offset = None
        scale = None
        for line in infile:
            stripped_line = line.strip()
            if stripped_line.startswith('texture '):
                processed_line, new_texture = process_texture_line(stripped_line)
                processed_line += "\n"
                if new_texture:
                    outfile.write(modify_buffer(buffer, rotation, x_offset, y_offset, scale))
                    rotation = None
                    x_offset = None
                    y_offset = None
                    scale = None
                    buffer = ""
                buffer += processed_line
            elif stripped_line.startswith("texrotate "):
                updated_line, rotation = process_texrotate_line(stripped_line)
                buffer += "// " + updated_line + "\n"
            elif stripped_line.startswith("texscale "):
                updated_line, scale = process_texscale_line(stripped_line)
                buffer += "// " + updated_line + "\n"
            elif stripped_line.startswith("texoffset "):
                updated_line, x_offset, y_offset = process_texoffset_line(stripped_line)
                buffer += "// " + updated_line + "\n"
            elif stripped_line == "":
                buffer += "\n"
            else:
                outfile.write(modify_buffer(buffer, rotation, x_offset, y_offset, scale))
                rotation = None
                x_offset = None
                y_offset = None
                scale = None
                buffer = ""
                if stripped_line.startswith("exec "):
                    processed_line = process_exec_line(stripped_line)
                    outfile.write(processed_line + "\n")
                else:
                    outfile.write(line) # write to buffer until next texture is read: buffer += line + "\n"
        outfile.write(buffer)

# if __name__ == '__main__':
#     input_file = 'input.cfg'  # Replace with your input file name
#     output_file = 'output.cfg'  # Replace with your desired output file name
#     process_config_file(input_file, output_file)

for p in pathlib.Path(".").iterdir():
    p = pathlib.Path(p)
    t = pathlib.Path("temp.cfg")
    print(p.name)
    process_config_file(p.name, t.name)
    p.unlink()
    t.rename(p.name)

User = "harry"
d = pathlib.Path(r'C:\Users') / User / r'Documents\My Games\Sauerbraten\packages\base'

def copyover(pkg: pathlib.Path|str):
    pkg = pathlib.Path(pkg)
    if pkg.suffix == ".cfg":
        shutil.copy(pathlib.Path(pkg).resolve(), d)
    else:
        shutil.copy(pathlib.Path(pkg + ".cfg").resolve(), d)

def takeback(pkg: pathlib.Path|str):
    pkg = pathlib.Path(pkg)
    if pkg.suffix == ".cfg":
        (d / pkg).unlink()
    else:
        (d / pkg + ".cfg").unlink()

def co(pkg): return copyover(pkg)
def tb(pkg): return takeback(pkg)