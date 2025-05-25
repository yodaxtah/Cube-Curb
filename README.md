# Cube Curb

Sauerbraten is an old game, so are its textures. However, nowadays, many upscaling models are available, some of which are specialized on certain game textures. This repository contains the code for Cube Curb, a work in progress tool that tries to support the whole upscaling pipeline for Sauerbraten, modded clients and forks of Cube/Tesseract.

## Features

- [ ] CLI upscaling. Ideally, we include the upscale process in this tool such that is automated as much as possible and the same upscaling can be done by anyone for other/new textures or for forks of the game.
- [ ] CLI packaging, uploading and downloading and unpackaging. Currently, all this must be done manually.
- [x] Config file conversions to point to upscaled files without side effects. Currently, most conversions work, aside some formatting and lacking parsing for `lava`, `water` and other materials, as far as is known.
- [ ] Broad client support. Sauerbraten is a game with many clients and forks, but currently only Sauerbraten and Tesseract-Sauerbraten are supported. Ideally, the tool can generate config files for clients that have slightly different structures (as part of the changes in the fork).
- [ ] External texture repository. Ideally, the tool can automatically create links to an external texture repository (outside of the mod directory) such that all clients can use the same upscaled textures, rather than duplicating that (large) folder.
- [ ] Configuration of override policy: specify which types to include and when to override or add new textures (such as normal and height maps).

## Manual install (WIP)

- Optional: Go to a specific map, move close to the geometry, make sure you have a few (but not only 1) close textures in sight and take a screenshot.
- Go to `My Games/Sauerbraten/packages`, create `harry`, enter the folder, create `upscale`. You should now be at `My Games/Sauerbraten/packages/harry/upscale`.
- Get the Send content (see below). If you get a message "This browser might not be able to decrypt a file this big", just "Continue with this browser". The files are not encrypted. Extract the zip and you'll see two files: `README.md` and another zip containing textures. Extract the other zip which should be one of the following names. (You can back and forth to the next step as soon as you have a package.)
    - [upscale-subfolders-set-1.zip](https://de.skysend.ch/download/540c8c58e71fd808/#JusQGifEaoK_wnW7vqqzvQ): textures for packages `aard`, `aftas`, ..., `loopix`, `lunaran`.
    - [upscale-subfolders-set-2.zip](https://de.skysend.ch/download/dcfbe8e8af88bed4/#ZirDy0ekxBnOPb4ag-OAfw): textures for packages `makke`, `meister`, ..., `tomek`, `trak5`, excluding package `textures`.
    - [upscale-textures-subfolders-set-1.zip](https://de.skysend.ch/download/98f1e42b867cbe1d/#1sF0dpIA_AbD90wbgrWOqQ): textures for folders `fatum`, ..., `nieb` in package `textures`.
    - [upscale-textures-subfolders-set-1.zip](https://de.skysend.ch/download/7940609793ca7032/#ojThPmKHBAUoNk2k-Uf88w): textures for folders `ow`, ..., `yves_allaire` in package `textures`.
- Now, do the following:
    - Extract the textures from `upscale-subfolders-set-1.zip` to the folder `.../upscale`, such that you have new folders `.../upscale/aard`, `.../upscale/aftas`, ..., `.../upscale/loopix`, `.../upscale/lunaran`.
    - Extract the textures from `upscale-subfolders-set-2.zip` to the folder `.../upscale`, such that you have new folders `.../upscale/makke`, `.../upscale/meister`, ..., `.../upscale/tomek`, `.../upscale/trak5`.
    - Extract the textures from `upscale-textures-subfolders-set-1.zip` to the folder `.../upscale/textures`, such that you have new folders `.../upscale/textures/fatum`, ..., `.../upscale/textures/nieb`.
    - Extract the textures from `upscale-textures-subfolders-set-2.zip` to the folder `.../upscale/textures`, such that you have new folders `.../upscale/textures/ow`, ..., `.../upscale/textures/yves_allaire`.
- If you have modifications in `packages`, `config` or `data`, make sure you backup your changes.
- Download `packages`, and `data` (or `config`) folders from this repository; they contain the prebuilt config files, generated using the `util/convert_config.py` script. The folder `data` is only needed for Sauerbraten, the folder `config` is only needed for Tesseract. NOTE: You need to run a few `mklink`s for the Tesseract-Sauerbraten client; come back later for detailed instructions.
- Paste these folders in `My Games/Sauerbraten/` and override the contents if necessary. This will add the files to the potentially already existing folders and override files whenever it already existed.
- Start Sauerbraten, open any map and move towards a texture. It should look better.