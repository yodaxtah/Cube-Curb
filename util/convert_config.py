# https://www.perplexity.ai/search/can-you-create-a-python-script-NGJIlr0fR_SeE7Eipelljg

import os
import re
import pathlib
import shutil

def process_texture_line(line, upscale=True, rotation=None, x_offset=None, y_offset=None, scale=None, inverse_texcoordscale = 4.0):
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
        param_list[1] = str(float(param_list[1]) * inverse_texcoordscale)
        param_list[2] = str(float(param_list[2]) * inverse_texcoordscale)
        param_list[3] = str(float(param_list[3]) / inverse_texcoordscale)

    upscaled = texture_type in ['0', 'c'] and "_diffuse" in filename
    if rotation != None:
        param_list[0] = rotation
    if x_offset != None:
        param_list[1] = str(float(x_offset) * inverse_texcoordscale) if upscaled else str(float(x_offset))
    if y_offset != None:
        param_list[2] = str(float(y_offset) * inverse_texcoordscale) if upscaled else str(float(y_offset))
    if scale != None:
        param_list[3] = str(float(scale) / inverse_texcoordscale) if upscaled else str(float(scale))
    
    for i in range(4):
        param = param_list[i]
        if param[-2:] == ".0":
            param = param[:-2]
        if "." in param:
            param = str(float(param)) # why is this necessary?
        param_list[i] = param

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

    prefix = ""
    if len(filename) > 0 and filename[0] == "<":
        prefix = filename[0:filename.find(">")+1]
        filename = filename[filename.find(">")+1:]

    # Extract directory, filestem, and extension
    path = pathlib.Path(filename)
    new_path = "harry/upscale" / path.parent / f"{path.stem}_diffuse.png"

    file_path = to_packages_path("user") / new_path
    if not file_path.is_file():
        new_path = path
    return f'"{prefix + new_path.as_posix()}"'

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


def process_shader_line(line, texcoordscale):
    # Split the line into main part and optional comment
    parts = line.split('//', 1)  # Split at the first occurrence of '//'
    main_part = parts[0].strip()  # Main part of the line (before the comment)
    comment = f" //{parts[1]}" if len(parts) > 1 else ""  # Preserve the comment if it exists

    match = re.match(r'setshader\s+(\S+)(.*)', main_part)
    if not match:
        return line  # Return the line unchanged if it's not a texture command

    shader_name, _ = match.groups()

    # Ensure shader_name is enclosed in double quotes
    if shader_name.startswith('"'):
        shader_name = shader_name[1:]
    if shader_name.endswith('"'):
        shader_name = shader_name[:-1]

    next_line = ""
    if True: # shader_name in ["stdworld", "glowworld"]:
        next_line = f"\nsetshaderparam \"texcoordscale\" {texcoordscale}"
    
    shader_name = f'"{shader_name}"'

    return f"setshader {shader_name}{comment}{next_line}"


def modify_buffer(buffer, rotation=None, x_offset=None, y_offset=None, scale=None, inverse_texcoordscale=4.0):
    new_buffer = ""
    # print(rotation, x_offset, y_offset, scale, repr(buffer))
    for line in buffer.splitlines():
        modified_line, _ = process_texture_line(line, False, rotation, x_offset, y_offset, scale)
        new_buffer += modified_line + "\n"
    return new_buffer


def process_lines(lines, texcoordscale=4.0, upscale_factor = 4.0):
    inverse_texcoordscale = upscale_factor / texcoordscale
    buffer = ""
    output_lines = ""
    rotation = None
    x_offset = None
    y_offset = None
    scale = None
    for line in lines:
        stripped_line = line.strip()
        if stripped_line.startswith('texture '):
            processed_line, new_texture = process_texture_line(stripped_line, inverse_texcoordscale=inverse_texcoordscale)
            processed_line += "\n"
            if new_texture:
                output_lines += modify_buffer(buffer, rotation, x_offset, y_offset, scale, inverse_texcoordscale=inverse_texcoordscale)
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
        elif stripped_line.startswith("texcolor "):
            buffer += line
        elif stripped_line.startswith("setshader "):
            updated_line = process_shader_line(stripped_line, texcoordscale)
            buffer += updated_line + "\n"
        elif stripped_line == "":
            buffer += "\n"
        else:
            output_lines += modify_buffer(buffer, rotation, x_offset, y_offset, scale, inverse_texcoordscale=inverse_texcoordscale)
            rotation = None
            x_offset = None
            y_offset = None
            scale = None
            buffer = ""
            if stripped_line.startswith("exec "):
                processed_line = process_exec_line(stripped_line)
                output_lines += processed_line + "\n"
            else:
                output_lines += line # write to buffer until next texture is read: buffer += line + "\n"
    output_lines += modify_buffer(buffer, rotation, x_offset, y_offset, scale, inverse_texcoordscale=inverse_texcoordscale)
    return output_lines


def process_config_file(input_file_path: pathlib.Path|str, output_file_path: pathlib.Path|str):
    lines = []
    with open(input_file_path, "r") as file:
        # lines = file.readlines()
        while line := file.readline():
            parts = line.split(";")
            lines.append(parts[0])
            for part in parts[1:]:
                lines.append(part.lstrip())
    with open(output_file_path, 'w') as file:
        output = process_lines(lines)
        file.write(output)

# if __name__ == '__main__':
#     input_file = 'input.cfg'  # Replace with your input file name
#     output_file = 'output.cfg'  # Replace with your desired output file name
#     process_config_file(input_file, output_file)

def process_directory(directory: str|pathlib.Path = ".", recursive = True):
    for p in pathlib.Path(directory).iterdir():
        p = pathlib.Path(p)
        if p.is_dir() and recursive:
            process_directory(p, recursive)
        else:
            t = p.parent / pathlib.Path("temp.cfg")
            print(p.as_posix())
            process_config_file(p.as_posix(), t.as_posix())
            p.unlink()
            t.rename(p.as_posix())

User = "harry"

def to_sauerbraten_path(t: "user|system|repo"):
    match t:
        case "user":
            return pathlib.Path(r'C:\Users') / User / r'Documents\My Games\Sauerbraten'
        case "system":
            return pathlib.Path(r'C:\Program Files (x86)\Sauerbraten')
        case "repo":
            return pathlib.Path(r'.')

def to_packages_path(t: "user|system|repo"):
    return to_sauerbraten_path(t) / "packages"

def to_packages_base_path(t: "user|system|repo"):
    return to_sauerbraten_path(t) / "packages" / "base"

def to_data_path(t: "user|system|repo"):
    return to_sauerbraten_path(t) / "data"

def copyover(cfg: pathlib.Path|str, destination: pathlib.Path|str = to_packages_path("user")):
    cfg = pathlib.Path(cfg)
    destination = pathlib.Path(destination)
    assert cfg.is_file()
    if cfg.suffix == ".cfg":
        shutil.copy(pathlib.Path(cfg).resolve(), destination.resolve())
    else:
        print(cfg)
        shutil.copy(pathlib.Path(cfg + ".cfg").resolve(), destination.resolve())

def takeback(cfg: pathlib.Path|str, destination: pathlib.Path|str = to_packages_path("user")):
    cfg = pathlib.Path(cfg)
    destination = pathlib.Path(destination)
    if cfg.suffix == ".cfg":
        (destination / cfg).unlink()
    else:
        (destination / cfg + ".cfg").unlink()

def copyover_directory(source: str|pathlib.Path = to_packages_path("repo"), destination: pathlib.Path|str = to_packages_path("user"), recursive = True, directory = None):
    source = source.resolve()
    destination = destination.resolve()
    if directory == None:
        directory = source
    for p in pathlib.Path(source).iterdir():
        p = pathlib.Path(p)
        if p.is_dir() and recursive:
            copyover_directory(p, destination, recursive, directory)
        elif p.suffix == ".cfg":
            print(p.as_posix())
            d = (destination / p.relative_to(directory)).parent
            d.mkdir(parents=True, exist_ok=True)
            copyover(p, d)


def setup():
    copyover_directory(to_packages_path("system"), to_packages_path("repo"), True)
    # 2. remove fonts
    """
    >>> R = pathlib.Path("./fonts/default.cfg")
    >>> R.unlink()
    """
    # 3. replace divf 1 3 with 0.3333333333
    process_directory()
    # 5. remove models
    """
    >>> Q = list(pathlib.Path(".").glob("./models/**/*.cfg"))
    >>> for q in Q: q.unlink()
    """


def cob(cfg): return copyover(cfg + "/base")
def tbb(cfg): return takeback(cfg + "/base")