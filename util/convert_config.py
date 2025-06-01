# https://www.perplexity.ai/search/can-you-create-a-python-script-NGJIlr0fR_SeE7Eipelljg

import re
import pathlib
import shutil
import fileinput
import dotenv
import os
import types


def reload_environment_variables():
    dotenv.load_dotenv(".env")
    return types.SimpleNamespace(
        REPLACED_TEXTURE_TYPES = ["0", "c"],
        APPENDED_TEXTURE_TYPES = ["n", "z"],
        SAUERBRATEN_CLIENT = os.environ.get("SAUERBRATEN_CLIENT") or "Sauerbraten",
        OVERRIDDEN_SYSTEM_INSTALLATION_PATH = os.environ.get("OVERRIDDEN_SYSTEM_INSTALLATION_PATH"),
        OVERRIDDEN_USER_MOD_PATH = os.environ.get("OVERRIDDEN_USER_MOD_PATH"),
        OVERRIDDEN_REPOSITORY_PATH = os.environ.get("OVERRIDDEN_REPOSITORY_PATH"),
        WINDOWS_USER_NAME = os.environ.get("WINDOWS_USER_NAME"),
        TESSERACT_ENGINE = bool(os.environ.get("TESSERACT_ENGINE"))
    )


env = reload_environment_variables()


def filter_quotes(string: str) -> str:
    if string.startswith('"'):
        string = string[1:]
    if string.endswith('"'):
        string = string[:-1]
    return string


def int_else_float(value: str|float) -> int|float:
    value = str(value)
    if value[-2:] == ".0" or "." not in value:
        return int(float(value))
    else:
        return float(value)


class TextureBind(CubeScriptCommand):

    __postfixes = set({'NRM', 'n', 'height', 'local', 'normal', 'norm', 'depth', 'nm', 'z', 's', 'd', 'light', 'h', 'DISP', 'hm'})

    def __init__(self,
            type_: str,
            filename: str,
            rotation: int|float = 0,
            x_offset: int|float = 0,
            y_offset: int|float = 0,
            scale: int|float = 1,
            upscale_coordscale_ratio: int|float = 4.0) -> None:
        super().__init__()
        self.type: str = type_
        self.filename_prexif: str
        self.filename: str
        self.filename_prexif, self.filename = TextureBind.split_filename_and_prefix(filename)
        self.parameters: tuple[int|float, int|float, int|float, int|float] = (
            rotation,
            x_offset,
            y_offset,
            scale,
        )
        self.upscale_coordscale_ratio = upscale_coordscale_ratio
        if self.type in env.REPLACED_TEXTURE_TYPES and not TextureBind.is_upscaled_path(self.filename):
            self.filename = self.upscaled_filenamed()
            self.parameters = self.upscale_parameters(self.parameters, self.upscale_coordscale_ratio)

    @classmethod
    def from_text(cls, text: str, upscale_coordscale_ratio = 4.0) -> None:
        if match := re.match(r"texture\s+(\w+)\s+(\S+)(.*)", text):
            texture_type, filename, param_list = match.groups()
            filename = filter_quotes(filename)
            parameters = TextureBind.extract_texture_parameters(param_list)
            return cls(texture_type, filename, *parameters, upscale_coordscale_ratio)
        else:
            return None

    @staticmethod
    def split_filename_and_prefix(filename: str) -> tuple[str, str]:
        prefix = ""
        if filename[:1] == "<":
            end = filename.find(">") + 1
            prefix = filename[0:end]
            filename = filename[end:]
        return prefix, filename

    @staticmethod
    def is_upscaled_path(filename: str) -> bool:
        return "harry" in filename \
            and "upscale" in filename \
            and "_diffuse" in filename

    @property
    def is_upscaled(self) -> bool:
        return TextureBind.is_upscaled_path(self.filename)

    @property
    def is_primary(self) -> bool:
        return self.type in {"c", "0"}

    @property
    def trimmed_filestems(self) -> list[str]:
        path = pathlib.Path(self.filename)
        stem = path.stem
        # if self.type not in ["0", "c"] and len(parts := stem.split("_")) > 1:
        #     __postfixes.add(parts[-1])
        if not self.is_primary:
            for postfix in __postfixes:
                postfix = "_" + postfix
                if stem[(end := -len(postfix)):] == postfix:
                    return stem[:end]
        return [path.stem, stem]

    def __parameters_to_text(self) -> str:
        param_list = ""
        for parameter in self.parameters:
            param = str(int_else_float(parameter)) # why is this necessary?
            param_list += " " + param
        return param_list[1:]

    def _to_text(self) -> str:
        return f"""texture {self.type} "{self.filename_prexif}{self.filename}" {self.__parameters_to_text()}"""

    def upscale_parameters(self, parameters: tuple, upscale_coordscale_ratio: float) -> tuple:
        return (
            None if (p := parameters[0]) == None else p,
            None if (p := parameters[1]) == None else p * upscale_coordscale_ratio,
            None if (p := parameters[2]) == None else p * upscale_coordscale_ratio,
            None if (p := parameters[3]) == None else p / upscale_coordscale_ratio,
        )

    @staticmethod
    def extract_texture_parameters(param_list: str) -> tuple[int|float, int|float, int|float, int|float]:
        parameters = param_list.strip().split()
        while len(parameters) < 3:  # Ensure ROT, X, Y, SCALE are present
            parameters.append(0.0)  # Default for missing ROT, X, Y
        if len(parameters) < 4:
            parameters.append(1.0)  # Default SCALE value
        return tuple(float(p) for p in parameters)

    def overwrite_parameters(self, rotation=None, x_offset=None, y_offset=None, scale=None) -> None:
        override_parameters = (rotation, x_offset, y_offset, scale)
        if self.type in env.REPLACED_TEXTURE_TYPES and TextureBind.is_upscaled_path(self.filename):
            override_parameters = self.upscale_parameters(override_parameters, self.upscale_coordscale_ratio)
        self.parameters = tuple(self.parameters[i] if (o := override_parameters[i]) == None else o for i in range(4))

    def to_type_postfix(texture_type: "0|c|u|d|n|g|s|z|e|lava|water"):
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

    def upscaled_filenamed(self):
        """
        Modifies the diffuse texture (texture type 0) by:
        - Prepending "harry/upscale/" to the filestem.
        - Appending "_diffuse" to the filestem.
        - Appending ".png" suffix to the filestem.
        """
        # Extract directory, filestem, and extension
        path = pathlib.Path(self.filename)
        postfix = TextureBind.to_type_postfix(self.type)
        stems = self.trimmed_filestems
        stems.append(stems[-1] + "_d")
        for stem in stems:
            new_path = "harry/upscale" / path.parent / f"{stem}_{postfix}.png"
            file_path = to_packages_path("user") / new_path
            if file_path.is_file():
                break
        if not file_path.is_file():
            new_path = path
        return new_path.as_posix()


class CubeScriptCommand():
    
    def __init__(self) -> None:
        # assert text != None
        # self.text = text
        pass

    def __bool__(self) -> bool:
        return True
        # return self._is_valid()

    def _is_valid(self) -> bool:
        raise Exception("Not implemented")
        # return self.text != None

    def _invalidate(self) -> None:
        raise Exception("Not implemented")
        # self.text = None

    @property
    def as_text(self) -> str:
        return self._to_text()

    def _to_text(self) -> str:
        return self.text


class TextureRotate(CubeScriptCommand):

    def __init__(self, rotation: int|float) -> None:
        super().__init__()
        self.rotation: int = rotation

    @classmethod
    def from_text(cls, text: str) -> None:
        if match := re.match(r"texrotate\s+(\S+)(.*)", text):
            rotation, _ = match.groups()
            return cls(int(rotation))
        else:
            return None

    def _to_text(self) -> str:
        return f"""texrotate {self.rotation}"""


class TextureScale(CubeScriptCommand):

    def __init__(self, scale: int|float) -> None:
        super().__init__()
        self.scale: int = scale

    @classmethod
    def from_text(cls, text: str) -> None:
        if match := re.match(r"texscale\s+(\S+)(.*)", text):
            scale, _ = match.groups()
            return cls(int_else_float(scale))
        else:
            return None

    def _to_text(self) -> str:
        return f"""texscale {self.scale}"""


class TextureOffset(CubeScriptCommand):

    def __init__(self, x_offset: int|float, y_offset: int|float) -> None:
        super().__init__()
        self.x_offset: int|float = x_offset
        self.y_offset: int|float = y_offset

    @classmethod
    def from_text(cls, text: str) -> None:
        if match := re.match(r"texoffset\s+(\S+)\s+(\S+)(.*)", text):
            x_offset, y_offset, _ = match.groups()
            return cls(int_else_float(x_offset), int_else_float(y_offset))
        elif match := re.match(r"texoffset\s+(\S+)(.*)", text):
            x_offset, _ = match.groups()
            return cls(int_else_float(x_offset), int_else_float("0"))
        else:
            return None

    def _to_text(self) -> str:
        return f"""texoffset {self.x_offset} {self.y_offset}"""


class TextureColor(CubeScriptCommand):

    def __init__(self, channel_R: int|float, channel_G: int|float, channel_B: int|float) -> None:
        super().__init__()
        self.channel_R: int|float = channel_R
        self.channel_G: int|float = channel_G
        self.channel_B: int|float = channel_B

    @classmethod
    def from_text(cls, text: str) -> None:
        if text.startswith("texcolor "):
            return cls(0, 0, 0) # TODO
        else:
            return None

    def _to_text(self) -> str:
        return self.text # TODO


class SetShader(CubeScriptCommand):

    def __init__(self, shader_name: str) -> None:
        super().__init__()
        self.shader_name: str = shader_name

    @classmethod
    def from_text(cls, text: str) -> None:
        if match := re.match(r"setshader\s+(\S+)(.*)", text):
            shader_name, _ = match.groups()
            return cls(filter_quotes(shader_name))
        else:
            return None

    def _to_text(self) -> str:
        return f"""setshader "{self.shader_name}\""""


class SetShaderParam(CubeScriptCommand):

    def __init__(self, scale: int|float):
        super().__init__()
        self.scale = scale

    def _to_text(self) -> str:
        return f"""setshaderparam "texcoordscale" {self.scale}"""


class TextureReset(CubeScriptCommand):

    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def from_text(cls, text: str) -> None:
        if text.startswith("texturereset"):
            return cls()
        else:
            return None

    def _to_text(self) -> str:
        return f"""texturereset"""


class Execute(CubeScriptCommand):

    def __init__(self, filename: str) -> None:
        super().__init__()
        self.filename: str = filename
        if "harry/upscale/" not in self.filename and self.filename.startswith("packages/"):
            self.filename = "packages/harry/upscale/" + self.filename[len("packages/"):]

    @classmethod
    def from_text(cls, text: str) -> None:
        if match := re.match(r"exec\s+(\S+)(.*)", text):
            filename, _ = match.groups()
            filename = filter_quotes(filename)
            # Modify the diffuse texture if texture type is '0'
            return cls(filename)
        else:
            return None

    def _to_text(self) -> str:
        return f"""exec "{self.filename}\""""


class TextLine():
    def __init__(self, indentation: str, command_text: str, comment: str, command: CubeScriptCommand|None = None, enabled: bool = True) -> None:
        self.indentation: str = indentation
        self.command_text: str = command_text
        self.comment: str = comment
        self.enabled: bool = enabled
        self.__command: CubeScriptCommand|None = command

    @classmethod
    def from_text(cls, text: str) -> "TextLine":
        indentation, command_text, comment = TextLine.__strip_line(text)
        return cls(indentation, command_text, comment)

    @classmethod
    def from_command(cls, indentation: str, command: CubeScriptCommand, enabled: bool = True) -> "TextLine":
        return cls(indentation, command.as_text, "", command, enabled)

    @property
    def as_text(self) -> str:
        return self.indentation \
            + ("" if self.enabled else "// ") \
            + (self.command.as_text if self.command else self.command_text) \
            + self.comment \
            + "\n"

    @property
    def as_disabled_text(self) -> str:
        self.enabled = not self.enabled
        text = self.as_text
        self.enabled = not self.enabled
        return text

    @property
    def no_text(self) -> bool:
        return self.command_text == ""

    @property
    def command(self) -> CubeScriptCommand:
        return self.__command

    @command.setter
    def command(self, command: CubeScriptCommand):
        self.__command = command    
        
    @command.setter
    def disabled_command(self, command: CubeScriptCommand):
        self.enabled = False
        self.__command = command

    @staticmethod
    def __strip_line(line):
        parts = line.split('//', 1)
        code = parts[0].strip()
        indentation = parts[0] if code == "" else parts[0][:parts[0].find(code)]
        comment = f" // {parts[1].strip()}" if len(parts) > 1 else ""
        if code == "":
            comment = comment[1:]
        if comment == "// ":
            comment = "//"
        return indentation, code, comment


def modify_buffer(buffer, rotation=None, x_offset=None, y_offset=None, scale=None, upscale_coordscale_ratio=4.0):
    new_buffer = ""
    for line in buffer.splitlines():
        text_line = TextLine.from_text(line)
        if command := TextureBind.from_text(text_line.command_text, upscale_coordscale_ratio):
            command.overwrite_parameters(rotation, x_offset, y_offset, scale)
            text_line.command = command
        new_buffer += text_line.as_text
    return new_buffer


def format_lines(lines: list[str], texcoordscale=4.0, upscale_factor = 4.0):
    upscale_coordscale_ratio = upscale_factor / texcoordscale
    buffer, rotation, x_offset, y_offset, scale = "", None, None, None, None
    output_lines = ""
    current_texcoordscale = texcoordscale
    reset = False
    shader_set = False
    for line in lines:
        text_line = TextLine.from_text(line)
        if command := TextureBind.from_text(text_line.command_text, upscale_coordscale_ratio):
            text_line.command = command
            if command.is_primary:
                output_lines += modify_buffer(buffer, rotation, x_offset, y_offset, scale, upscale_coordscale_ratio)
                buffer, rotation, x_offset, y_offset, scale = ("", None, None, None, None)
                if not shader_set:
                    shader_set = True
                    buffer += text_line.indentation + SetShader("stdworld").as_text + "\n"
                    buffer += text_line.indentation + SetShaderParam(texcoordscale).as_text + "\n"
                if command.is_upscaled and current_texcoordscale != texcoordscale:
                    current_texcoordscale = texcoordscale
                    buffer += text_line.indentation + SetShaderParam(current_texcoordscale).as_text + "\n"
                elif not command.is_upscaled and current_texcoordscale == texcoordscale:
                    current_texcoordscale = 1.0
                    buffer += text_line.indentation + SetShaderParam(current_texcoordscale).as_text + "\n"
            buffer += text_line.as_text
        elif command := TextureRotate.from_text(text_line.command_text):
            text_line.disabled_command, rotation = command, command.rotation
            buffer += text_line.as_text
        elif command := TextureScale.from_text(text_line.command_text):
            text_line.disabled_command, scale = command, command.scale
            buffer += text_line.as_text
        elif command := TextureOffset.from_text(text_line.command_text):
            text_line.disabled_command, x_offset, y_offset = command, command.x_offset, command.y_offset
            buffer += text_line.as_text
        elif command := TextureColor.from_text(text_line.command_text):
            buffer += text_line.as_text
        elif text_line.command_text == "":
            buffer += line
        else:
            output_lines += modify_buffer(buffer, rotation, x_offset, y_offset, scale, upscale_coordscale_ratio=upscale_coordscale_ratio)
            buffer, rotation, x_offset, y_offset, scale = ("", None, None, None, None)
            if command := SetShader.from_text(text_line.command_text):
                shader_set = True
                current_texcoordscale = texcoordscale
                text_line.command = command
                output_lines += text_line.as_text
                output_lines += text_line.indentation + SetShaderParam(texcoordscale).as_text + "\n"
            elif command := TextureReset.from_text(text_line.command_text):
                reset = True
                shader_set = False
                output_lines += line
                output_lines += text_line.indentation + SetShaderParam(texcoordscale).as_text + "\n"
            elif command := Execute.from_text(text_line.command_text):
                current_texcoordscale = 1.0
                text_line.command = command
                output_lines += text_line.as_text
            else:
                output_lines += line # write to buffer until next texture is read: buffer += line + "\n"
    output_lines += modify_buffer(buffer, rotation, x_offset, y_offset, scale, upscale_coordscale_ratio=upscale_coordscale_ratio)
    buffer, rotation, x_offset, y_offset, scale = ("", None, None, None, None)
    output_lines += SetShaderParam(1.0).as_text + "\n"
    if not reset:
        output_lines = SetShaderParam(texcoordscale).as_text + "\n" + output_lines
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

def is_tesseract_client():
    return env.SAUERBRATEN_CLIENT == "Sauerract" \
        or env.TESSERACT_ENGINE == True

def to_sauerbraten_path(t: "user|system|repo"):
    match t:
        case "user":
            if env.OVERRIDDEN_USER_MOD_PATH:
                return pathlib.Path(env.OVERRIDDEN_USER_MOD_PATH)
            elif env.WINDOWS_USER_NAME:
                return pathlib.Path(r'C:\Users') / env.WINDOWS_USER_NAME / r'Documents\My Games' / env.SAUERBRATEN_CLIENT
            else:
                raise Exception("Some environment variables are not set yet.")
        case "system":
            if env.OVERRIDDEN_SYSTEM_INSTALLATION_PATH:
                return pathlib.Path(env.OVERRIDDEN_SYSTEM_INSTALLATION_PATH)
            else:
                return pathlib.Path(r'C:\Program Files (x86)') / env.SAUERBRATEN_CLIENT
        case "repo":
            return pathlib.Path(env.OVERRIDDEN_REPOSITORY_PATH or r'.')
        case _:
            raise Exception("Unhandled case.")

def to_packages_path(t: "user|system|repo"):
    return to_sauerbraten_path(t) / "packages"

def to_packages_base_path(t: "user|system|repo"):
    base = "map" if is_tesseract_client() else "base"
    return to_sauerbraten_path(t) / "packages" / base

def to_data_path(t: "user|system|repo"):
    data = "config" if is_tesseract_client() else "data"
    return to_sauerbraten_path(t) / data

def to_glsl_config_path(t: "user|system|repo"):
    if is_tesseract_client():
        return to_data_path(t) / "glsl" / "world.cfg"
    else:
        return to_data_path(t) / "glsl.cfg"

def copyover(cfg: pathlib.Path|str, destination: pathlib.Path|str = to_packages_base_path("user")):
    cfg = pathlib.Path(cfg)
    destination = pathlib.Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if cfg.suffix != ".cfg":
        cfg = cfg.with_suffix(".cfg")
    if destination.is_dir():
        destination = destination / cfg.name
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
    if (p := (to_packages_path("repo") / "fonts" / "default.cfg")).is_file():
        p.unlink()

    # 3. remove models, interface, sound
    directories = ["models", "interface", "sound"]
    for config_directory in directories:
        if (path := to_packages_path("repo") / config_directory).is_dir():
            configs = list(to_packages_path("repo").glob(f"./{config_directory}/**/*.cfg"))
            for config in configs:
                config.unlink()
            shutil.rmtree(path)

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

    # 6. copy the repository files over to the mod directory
    copyover_directory(to_packages_path("repo"), to_packages_path("user"), True)

    # 7. copy the repo base to the user base
    # default_map_settings.cfg
    copyover(to_data_path("system") / "default_map_settings.cfg", to_data_path("repo") / "default_map_settings.cfg")
    format_config_file(to_data_path("repo") / "default_map_settings.cfg", to_data_path("repo") / "default_map_settings.cfg")
    copyover(to_data_path("repo") / "default_map_settings.cfg", to_data_path("user") / "default_map_settings.cfg")
    # takeback(to_data_path("user") / "default_map_settings.cfg")

    # 8. copy the repo glsl config mod to the user data
    copyover(to_glsl_config_path("repo"), to_glsl_config_path("user")) 

    # 9. test environments
    test_maps()

    # 10. install each map
    test_each_map(install=True, uninstall=False)

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


def test_each_map(install = True, uninstall = True):
    # maps = ["aastha", "bklyn"]
    print("testing packages/base:")
    for path in sorted(to_packages_base_path("system").glob("*.ogz")):
        if path.is_file():
            map_name = path.stem
            file_name = path.stem + ".cfg"
            if install and uninstall:
                print("- ", map_name, end="\t : ")
            else:
                print(map_name, end=" ")
            if install and (to_packages_base_path("repo") / file_name).is_file():
                copyover(to_packages_base_path("repo") / file_name, to_packages_base_path("user"))
            if install and uninstall:
                input("press any key to takeback the files...")
            if uninstall and (to_packages_base_path("repo") / file_name).is_file():
                takeback(map_name)
    print()




def cob(cfg): return copyover(cfg + "/base")
def tbb(cfg): return takeback(cfg + "/base")