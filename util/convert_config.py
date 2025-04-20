# https://www.perplexity.ai/search/can-you-create-a-python-script-NGJIlr0fR_SeE7Eipelljg

import os
import re
import pathlib
import shutil
import fileinput

REPLACED_TEXTURE_TYPES = ["0", "c", "n"]
APPENDED_TEXTURE_TYPES = ["0", "c", "n", "z"]

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
        parameters.append(0.0)  # Default for missing ROT, X, Y
    if len(parameters) < 4:
        parameters.append(1.0)  # Default SCALE value
    return tuple(float(p) for p in parameters)


def format_texture_param_list(parameters) -> str:
    param_list = ""
    for parameter in parameters:
        param = str(float(parameter))
        if param[-2:] == ".0":
            param = param[:-2] # why is this necessary?
        param_list += " " + param
    return param_list[1:]


def upscale_texture_parameters(parameters: tuple, inverse_texcoordscale: float) -> tuple:
    return (
        None if (p := parameters[0]) == None else p,
        None if (p := parameters[1]) == None else p * inverse_texcoordscale,
        None if (p := parameters[2]) == None else p * inverse_texcoordscale,
        None if (p := parameters[3]) == None else p / inverse_texcoordscale,
    )


def split_filename_and_prefix(filename: str) -> tuple[str, str]:
    prefix = ""
    if filename[:1] == "<":
        end = filename.find(">") + 1
        prefix = filename[0:end]
        filename = filename[end:]
    return prefix, filename


def format_texture_code(line, upscale=True, rotation=None, x_offset=None, y_offset=None, scale=None, inverse_texcoordscale = 4.0):
    # Match the texture command
    if match := re.match(r"texture\s+(\w+)\s+(\S+)(.*)", line):
        texture_type, filename, param_list = match.groups()
    else:
        return line, False, None

    # Ensure filename is enclosed in double quotes
    filename = filter_quotes(filename)
    filename_prexif, filename = split_filename_and_prefix(filename)

    # Split remaining parameters and ensure defaults
    parameters = extract_texture_parameters(param_list)

    if upscale and texture_type in REPLACED_TEXTURE_TYPES and not is_upscaled_texture_path(filename):
        filename = upscaled_filename_for(filename, texture_type)
        parameters = upscale_texture_parameters(parameters, inverse_texcoordscale)

    # Overwrite parameters
    override_parameters = (rotation, x_offset, y_offset, scale)
    if texture_type in REPLACED_TEXTURE_TYPES and is_upscaled_texture_path(filename):
        override_parameters = upscale_texture_parameters(override_parameters, inverse_texcoordscale)
    parameters = tuple(parameters[i] if (o := override_parameters[i]) == None else o for i in range(4))

    # Convert parameters to a string
    param_list = format_texture_param_list(parameters)

    # Reconstruct the line with updated values
    formatted = f"""texture {texture_type} "{filename_prexif}{filename}" {param_list}"""
    return formatted, texture_type in {"c", "0"}, is_upscaled_texture_path(filename)


def to_texture_type_postfix(texture_type: "0|c|u|d|n|g|s|z|e|lava|water"):
    """
    "c" or 0 for primary diffuse texture (RGB)
    "u" or 1 for generic secondary texture
    "d" for decals (RGBA), blended into the diffuse texture if running in fixed-function mode. To disable this combining, specify secondary textures as generic with 1 or "u"
    "n" for normal maps (XYZ)
    "g" for glow maps (RGB), blended into the diffuse texture if running in fixed-function mode. To disable this combining, specify secondary textures as generic with 1 or "u"
    "s" for specularity maps (grey-scale), put in alpha channel of diffuse ("c")
    "z" for depth maps (Z), put in alpha channel of normal ("n") maps
    "e" for environment maps (skybox), uses the same syntax as "loadsky", and set a custom environment map (overriding the "envmap" entities) to use in environment-mapped shaders ("bumpenv*world")
    """
    match texture_type:
        case "c" | "0":
            return "diffuse"
        case "u" | "1":
            return None
        case "d":
            return None
        case "n":
            return "normal_dx"
        case "g":
            return None
        case "s":
            return None
        case "z":
            return "height"
        case "e":
            return None
        case _:
            return None


# postfixes = set()
# postfixes = set({'NRM', 'n', 'height', 'local', 'normal', 'norm', '2', 'depth', '27', 'nm', 'z', 's', 'trnd', 'd', 'light', 'h', 'basic128', 'DISP', 'hm', '45'})
postfixes = set({'NRM', 'n', 'height', 'local', 'normal', 'norm', 'depth', 'nm', 'z', 's', 'd', 'light', 'h', 'DISP', 'hm'})
def trim_texture_stem(stem, texture_type):
    global postfixes
    # if texture_type not in ["0", "c"] and len(parts := stem.split("_")) > 1:
    #     postfixes.add(parts[-1])
    if texture_type not in ["0", "c"]:
        for postfix in postfixes:
            postfix = "_" + postfix
            if stem[(end := -len(postfix)):] == postfix:
                return stem[:end]
    return stem


def upscaled_filename_for(filename: str, texture_type: "0|c|u|d|n|g|s|z|e|lava|water"):
    """
    Modifies the diffuse texture (texture type 0) by:
      - Prepending "harry/upscale/" to the filestem.
      - Appending "_diffuse" to the filestem.
      - Appending ".png" suffix to the filestem.
    """
    # Extract directory, filestem, and extension
    path = pathlib.Path(filename)
    postfix = to_texture_type_postfix(texture_type)
    stems = [path.stem, trim_texture_stem(path.stem, texture_type)]
    stems.append(stems[-1] + "_d")
    for stem in stems:
        new_path = "harry/upscale" / path.parent / f"{stem}_{postfix}.png"
        file_path = to_packages_path("user") / new_path
        if file_path.is_file():
            break
    if not file_path.is_file():
        new_path = path
    return new_path.as_posix()


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
    return formatted, int(rotation)


def format_texscale_line(line):
    if match := re.match(r"texscale\s+(\S+)(.*)", line):
        scale, _ = match.groups()
    else:
        return line

    # Reconstruct the line with updated values
    formatted = f"""texscale {scale}"""
    return formatted, float(scale)


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
    return formatted, float(x_offset), float(y_offset)


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

def copyover(cfg: pathlib.Path|str, destination: pathlib.Path|str = to_packages_base_path("user")):
    cfg = pathlib.Path(cfg)
    destination = pathlib.Path(destination)
    if cfg.suffix != ".cfg":
        cfg = cfg.with_suffix(".cfg")
    assert cfg.is_file()
    shutil.copy(pathlib.Path(cfg).resolve(), destination.resolve())

def takeback(cfg: pathlib.Path|str, target: pathlib.Path|str = to_packages_base_path("user")):
    cfg = pathlib.Path(cfg)
    target = pathlib.Path(target)
    if cfg.suffix != ".cfg":
        cfg = cfg.with_suffix(".cfg")
    (target / cfg).unlink()

def copyover_directory(source_root: str|pathlib.Path = to_packages_path("repo"), destination_root: pathlib.Path|str = to_packages_path("user"), recursive = True, directory = None):
    if directory == None:
        source_root = pathlib.Path(source_root).resolve()
        destination_root = pathlib.Path(destination_root).resolve()
        directory = source_root
    for path in directory.iterdir():
        if path.is_dir() and recursive:
            copyover_directory(source_root, destination_root, recursive, path)
        elif path.suffix == ".cfg":
            print(path.as_posix())
            destination = (destination_root / path.relative_to(source_root)).parent
            destination.mkdir(parents=True, exist_ok=True)
            copyover(path, destination)

def setup():
    # 1. copy the system files over to the repository directory
    copyover_directory(to_packages_path("system"), to_packages_path("repo"), True)

    # 2. remove fonts
    (to_packages_path("repo") / "fonts" / "default.cfg").unlink()

    # 3. remove models
    models = list(to_packages_path("repo").glob("./models/**/*.cfg"))
    for model in models:
        model.unlink()
    shutil.rmtree(to_packages_path("repo") / "models")

    # 4. replace divf 1 3 with 0.3333333333
    gorge = to_packages_base_path("repo") / "gorge.cfg"
    with fileinput.FileInput(gorge, inplace=True) as file:
        for line in file:
            print(line.replace("(divf 1 3)", "0.3333333333"), end="")
    island = to_packages_base_path("repo") / "island.cfg"
    with fileinput.FileInput(island, inplace=True) as file:
        for line in file:
            print(line.replace("""texture 0 "dg/mad064.jpg""", """texture 0 "dg/mad064.jpg\""""), end="")
    paradigm = to_packages_base_path("repo") / "paradigm.cfg"
    with fileinput.FileInput(paradigm, inplace=True) as file:
        for line in file:
            print(line.replace("32s", "32"), end="")

    # 5. process the directory
    process_directory(to_packages_path("repo"))

    # 6. copy the repo base to the user base
    copyover(to_data_path("system") / "default_map_settings.cfg", to_data_path("repo") / "default_map_settings.cfg")
    format_config_file(to_data_path("repo") / "default_map_settings.cfg", to_data_path("repo") / "default_map_settings.cfg")
    copyover(to_data_path("repo") / "default_map_settings.cfg", to_data_path("user") / "default_map_settings.cfg")
    # takeback(to_data_path("user") / "default_map_settings.cfg")

    # 7. test environments
    test_maps()

maps = ["asgard", "aard3c", "aastha", "abbey", "abyss", "academy", "access", "akaritori", "akimiski", "akroseum", "albatross", "alithia", "alloy", "antel", "anubis", "aod", "aqueducts", "arabic", "arbana", "asenatra"]


def test_maps():
    # maps = ["aastha", "bklyn"]
    print("testing packages/base:")
    for map_name in maps:
        print("-", map_name)
        copyover(to_packages_base_path("repo") / map_name, to_packages_base_path("user"))
    # copyover(to_data_path("repo") / "default_map_settings.cfg", to_data_path("user") / "default_map_settings.cfg")

    input("press any key to takeback the files...")

    # reset to defaults
    for map_name in maps:
        takeback(map_name)
    # copyover("default_map_settings.cfg", to_data_path("user") / "default_map_settings.cfg")


def test_each_map():
    # maps = ["aastha", "bklyn"]
    print("testing packages/base:")
    for path in to_packages_base_path("system").glob("*.ogz"):
        if path.is_file():
            map_name = path.stem
            print("- ", map_name, end="\t : ")
            if (to_packages_base_path("repo") / (path.stem + ".cfg")).is_file():
                copyover(to_packages_base_path("repo") / map_name, to_packages_base_path("user"))
            input("press any key to takeback the files...")
            if (to_packages_base_path("repo") / (path.stem + ".cfg")).is_file():
                takeback(map_name)


def cob(cfg): return copyover(cfg + "/base")
def tbb(cfg): return takeback(cfg + "/base")


User = "harry"