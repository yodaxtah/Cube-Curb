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
- Get the textures here, extract their contents and move the under `My Games/Sauerbraten/packages` as described for each:
    - Extract the textures from [here](https://de.skysend.ch/download/540c8c58e71fd808/#JusQGifEaoK_wnW7vqqzvQ) to the mod directory `.../packages/upscale`, such that you have new folders under `.../packages/harry/upscale`. One of the folder you should see under `upscale` is `aftas`.
    - Extract the textures from [here](https://de.skysend.ch/download/dcfbe8e8af88bed4/#ZirDy0ekxBnOPb4ag-OAfw) to the mod directory `.../packages/upscale`, such that you have new folders under `.../packages/harry/upscale`. One of the folder you should see under `upscale` is `trak5`.
    - Extract the textures from [here](https://de.skysend.ch/download/98f1e42b867cbe1d/#1sF0dpIA_AbD90wbgrWOqQ) to the mod directory `.../packages/upscale/textures`, such that you have new folders under `.../packages/harry/upscale/textures`. One of the folder you should see under `textures` is `nieb`.
    - Extract the textures from [here]() to the mod directory `.../packages/upscale/textures`, such that you have new folders under `.../packages/harry/upscale/textures`. One of the folder you should see under `textures` is `yves_allaire`.
- Place their contents in the mod directory `My Games/Sauerbraten/packages`, such that you have a new folder at `My Games/Sauerbraten/packages/harry/upscale`
- Download `packages`, `config` and `data` folders from this repository; they contain the prebuilt config files, generated using the `util/convert_config.py` script. The folder `data` is only needed for Sauerbraten, The folder `config` is only needed for Tesseract. NOTE: You need to run the script yourself if you are using a different client (Tesseract-Sauerbraten).
- If you have modifications in `packages`, `config` or `data`, make sure you backup your changes.
- Paste these folders in `My Games/Sauerbraten/` and override the contents if necessary. This will add the files to the potentially already existing folders and override files whenever it already existed.
- Start Sauerbraten, open any map and move towards a texture. It should look better.