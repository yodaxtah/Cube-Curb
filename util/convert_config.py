# https://www.perplexity.ai/search/can-you-create-a-python-script-NGJIlr0fR_SeE7Eipelljg

import os
import re
import pathlib
import shutil

def is_upscaled_texture_path(filename: str) -> bool:
    return "harry" in filename \
        and "upscale" in filename \
        and "_diffuse" in filename


def filter_quotes(string: str) -> str:
    if string.startswith('"'):
        string = string[1:]
    if string.endswith('"'):
        string = string[:-1]
    return string


def extract_texture_parameters(param_list: str) -> list[str]:
    parameters = param_list.strip().split()
    while len(parameters) < 3:  # Ensure ROT, X, Y, SCALE are present
        parameters.append('0')  # Default for missing ROT, X, Y
    if len(parameters) < 4:
        parameters.append('1.0')  # Default SCALE value
    return parameters


def format_texture_param_list(parameters) -> str:
    param_list = ""
    for parameter in parameters:
        if parameter[-2:] == ".0":
            parameter = parameter[:-2]
        if "." in parameter:
            parameter = str(float(parameter)) # why is this necessary?
        param_list += " " + parameter
    return param_list[1:]


def format_texture_code(line, upscale=True, rotation=None, x_offset=None, y_offset=None, scale=None, inverse_texcoordscale = 4.0):
    # Match the texture command
    if match := re.match(r"texture\s+(\w+)\s+(\S+)(.*)", line):
        texture_type, filename, param_list = match.groups()
    else:
        return line, False, None

    # Ensure filename is enclosed in double quotes
    filename = filter_quotes(filename)

    # Split remaining parameters and ensure defaults
    parameters = extract_texture_parameters(param_list)

    if upscale and texture_type in ['0', 'c'] and not is_upscaled_texture_path(filename):
        filename = modify_diffuse_texture(filename)
        parameters[1] = str(float(parameters[1]) * inverse_texcoordscale)
        parameters[2] = str(float(parameters[2]) * inverse_texcoordscale)
        parameters[3] = str(float(parameters[3]) / inverse_texcoordscale)

    upscaled = texture_type in ['0', 'c'] and is_upscaled_texture_path(filename)
    if rotation != None:
        parameters[0] = rotation
    if x_offset != None:
        parameters[1] = str(float(x_offset) * inverse_texcoordscale) if upscaled else str(float(x_offset))
    if y_offset != None:
        parameters[2] = str(float(y_offset) * inverse_texcoordscale) if upscaled else str(float(y_offset))
    if scale != None:
        parameters[3] = str(float(scale) / inverse_texcoordscale) if upscaled else str(float(scale))
    
    param_list = format_texture_param_list(parameters)

    # Reconstruct the line with updated values
    formatted = f"""texture {texture_type} "{filename}" {param_list}"""
    return formatted, texture_type in ['0', 'c'], is_upscaled_texture_path(filename)


def modify_diffuse_texture(filename):
    """
    Modifies the diffuse texture (texture type 0) by:
      - Prepending "harry/upscale/" to the filestem.
      - Appending "_diffuse" to the filestem.
      - Appending ".png" suffix to the filestem.
    """
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
    return prefix + new_path.as_posix()


def format_exec_code(line):
    if match := re.match(r"exec\s+(\S+)(.*)", line):
        filename, _ = match.groups()
    else:
        return line

    # Ensure filename is enclosed in double quotes
    filename = filter_quotes(filename)

    # Modify the diffuse texture if texture type is '0'
    if "harry/upscale/" not in filename and filename.startswith("packages/"):
        filename = "packages/harry/upscale/" + filename[len("packages/"):]

    # Reconstruct the line with updated values
    formatted = f"""exec "{filename}\""""
    return formatted


def format_texrotate_line(line):
    if match := re.match(r"texrotate\s+(\S+)(.*)", line):
        rotation, _ = match.groups()
    else:
        return line

    # Reconstruct the line with updated values
    formatted = f"""texrotate {rotation}"""
    return formatted, rotation


def format_texscale_line(line):
    if match := re.match(r"texscale\s+(\S+)(.*)", line):
        scale, _ = match.groups()
    else:
        return line

    # Reconstruct the line with updated values
    formatted = f"""texscale {scale}"""
    return formatted, scale


def format_texoffset_line(line):
    if match := re.match(r"texoffset\s+(\S+)\s+(\S+)(.*)", line):
        x_offset, y_offset, _ = match.groups()
    elif match := re.match(r"texoffset\s+(\S+)(.*)", line):
        x_offset, _ = match.groups()
        y_offset = "0"
    else:
        return line

    # Reconstruct the line with updated values
    formatted = f"""texoffset {x_offset} {y_offset}"""
    return formatted, x_offset, y_offset


def format_texcoordscale(scale):
    return f"""setshaderparam "texcoordscale" {scale}"""


def format_shader_code(line, texcoordscale):
    if match := re.match(r"setshader\s+(\S+)(.*)", line):
        shader_name, _ = match.groups()
    else:
        return line

    # Ensure shader_name is enclosed in double quotes
    shader_name = filter_quotes(shader_name)

    return f"""setshader "{shader_name}\""""


def modify_buffer(buffer, rotation=None, x_offset=None, y_offset=None, scale=None, inverse_texcoordscale=4.0):
    new_buffer = ""
    # print(rotation, x_offset, y_offset, scale, repr(buffer))
    for line in buffer.splitlines():
        indentation, code, comment = strip_line(line)
        formatted, _, _ = format_texture_code(code, False, rotation, x_offset, y_offset, scale)
        new_buffer += indentation + formatted + comment + "\n"
    return new_buffer


def strip_line(line):
    parts = line.split('//', 1)
    code = parts[0].strip()
    indentation = parts[0] if code == "" else parts[0][:parts[0].find(code)]
    comment = f" // {parts[1].strip()}" if len(parts) > 1 else ""
    if code == "":
        comment = comment[1:]
    if comment == "// ":
        comment = "//"
    return indentation, code, comment


def format_lines(lines, texcoordscale=4.0, upscale_factor = 4.0):
    inverse_texcoordscale = upscale_factor / texcoordscale
    buffer = ""
    output_lines = ""
    rotation = None
    x_offset = None
    y_offset = None
    scale = None
    current_texcoordscale = texcoordscale
    reset = False
    shader_set = False
    for line in lines:
        indentation, code, comment = strip_line(line)
        if code.startswith("texture "):
            formatted, new_texture, is_upscaled = format_texture_code(code, inverse_texcoordscale=inverse_texcoordscale)
            if new_texture:
                output_lines += modify_buffer(buffer, rotation, x_offset, y_offset, scale, inverse_texcoordscale=inverse_texcoordscale)
                rotation = None
                x_offset = None
                y_offset = None
                scale = None
                buffer = ""
                if not shader_set:
                    shader_set = True
                    buffer += indentation + format_shader_code("setshader stdworld", texcoordscale) + "\n"
                    buffer += indentation + format_texcoordscale(texcoordscale) + "\n"
                if is_upscaled and current_texcoordscale != texcoordscale:
                    current_texcoordscale = texcoordscale
                    buffer += indentation + format_texcoordscale(current_texcoordscale) + "\n"
                elif not is_upscaled and current_texcoordscale == texcoordscale:
                    current_texcoordscale = 1.0
                    buffer += indentation + format_texcoordscale(current_texcoordscale) + "\n"
            buffer += indentation + formatted + comment + "\n"
        elif code.startswith("texrotate "):
            formatted, rotation = format_texrotate_line(code)
            buffer += indentation + "// " + formatted + comment + "\n"
        elif code.startswith("texscale "):
            formatted, scale = format_texscale_line(code)
            buffer += indentation + "// " + formatted + comment + "\n"
        elif code.startswith("texoffset "):
            formatted, x_offset, y_offset = format_texoffset_line(code)
            buffer += indentation + "// " + formatted + comment + "\n"
        elif code.startswith("texcolor "):
            buffer += line
        elif code == "":
            buffer += line
        else:
            output_lines += modify_buffer(buffer, rotation, x_offset, y_offset, scale, inverse_texcoordscale=inverse_texcoordscale)
            rotation = None
            x_offset = None
            y_offset = None
            scale = None
            buffer = ""
            if code.startswith("setshader "):
                shader_set = True
                current_texcoordscale = texcoordscale
                formatted = format_shader_code(code, texcoordscale)
                output_lines += indentation + formatted + comment + "\n"
                output_lines += indentation + format_texcoordscale(texcoordscale) + "\n"
            elif code.startswith("texturereset"):
                reset = True
                shader_set = False
                output_lines += line
                output_lines += indentation + format_texcoordscale(texcoordscale) + "\n"
            elif code.startswith("exec "):
                current_texcoordscale = 1.0
                formatted = format_exec_code(code)
                output_lines += indentation + formatted + comment + "\n"
            else:
                output_lines += line # write to buffer until next texture is read: buffer += line + "\n"
    output_lines += modify_buffer(buffer, rotation, x_offset, y_offset, scale, inverse_texcoordscale=inverse_texcoordscale)
    output_lines += format_texcoordscale(1.0) + "\n"
    if not reset:
        output_lines = format_texcoordscale(texcoordscale) + "\n" + output_lines
    return output_lines


def split_lines(line):
    parts = line.split(";")
    return [parts[0]] + [part.lstrip() for part in parts[1:]]


def split_lines_with_comments(line):
    if (start_comment_index := line.find("//")) == -1:
        return split_lines(line)
    else:
        lines = split_lines(line[:start_comment_index])
        return lines[:-1] + [lines[-1] + line[start_comment_index:]]


def format_config_file(input_file_path: pathlib.Path|str, output_file_path: pathlib.Path|str):
    lines = []
    with open(input_file_path, "r") as file:
        # lines = file.readlines()
        while line := file.readline():
            lines += split_lines_with_comments(line)
    with open(output_file_path, 'w') as file:
        output = format_lines(lines)
        file.write(output)

# if __name__ == '__main__':
#     input_file = 'input.cfg'  # Replace with your input file name
#     output_file = 'output.cfg'  # Replace with your desired output file name
#     format_config_file(input_file, output_file)

def process_directory(directory: str|pathlib.Path = ".", recursive = True):
    for p in pathlib.Path(directory).iterdir():
        p = pathlib.Path(p)
        if p.is_dir() and recursive:
            process_directory(p, recursive)
        else:
            t = p.parent / pathlib.Path("temp.cfg")
            print(p.as_posix())
            format_config_file(p.as_posix(), t.as_posix())
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