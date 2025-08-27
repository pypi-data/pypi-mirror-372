# Korg nanoKONTROL Studio™ config tool

While there exists MIDI protocol specification for other Korg nano* products
like nanoKONTROL™ or nanoKONTROL2™, we have nothing for the more modern
nanoKONTROL Studio™ (and thus no tools like [Nano-Basket](https://github.com/royvegard/Nano-Basket)
for the nanoKONTROL Studio™

This project provides a CLI tool for reading and writing configuration from and
to YAML based config files plus a basis for future nanoKONTROL Studio™ based
projects which need to talk to the device using the proprietary MIDI based
protocol.


## Install and use


You can either install `nanokontrol-config` via `pip`, simply run it via
`uvx` provided by the `uv` package or checkout the project and run the
entry-point via `uv run`:

```bash
[uvx|uv run] nanokontrol-config [<global-opts>] <CMD> [<command-opts>]
```

If you're running into problems installing `python-rtmidi`, try to provide
`pkg-config` and `libasound2-dev` (or similar) before installing
`nanokontrol-config`.


### Exporting the config

Read the current config from your attached nanoKONTROL Studio™ device and save
it to a YAML file.

```bash
nanokontrol-config e[xport] [-o|--output current-config.yaml]
```

### Sending the config

Read a YAML file and push it to your (attached) device:

```bash
nanokontrol-config s[et] [-i|--input modified-config.yaml]
```

### Patching the config

**NOT YET IMPLEMENTED**

Read just a sparse config (only implementing the modifications you need) and
apply it to the configuration currently stored on your device:

```bash
nanokontrol-config p[atch] [-i|--input sparse-config.yaml]
```


## Disclaimer

I'm not affiliated in any way with Korg and this project is solely based on
reverse engineering MIDI I/O.

Of course using this tool is fully your own risk - I hereby refuse any
responsibility for any damages.


## License

See [License.md].


## Contribution

```bash
git clone https://projects.om-office.de/frans/nanokontrol-config.git
cd nanokontrol-config
uv run pre-commit install
```

implement -> `uv run pytest` -> commit -> repeat

```bash
uv version --bump <patch|minor|major>
uv build
uv publish --token <TOKEN>
```

## Future

* Graphical UI
* Support for importing/exporting the Korg proprietary configuration file format
* Support for other Korg nano* products
* Support for other MIDI controllers
* Availability for MicroPython (i.e. no dependency to `pydandtic` or `mido`)


## External sources

* [Nano-Basket: config tool for nanoKONTROL](https://github.com/royvegard/Nano-Basket)

* [nanoKONTROL2 MIDI Implementation (v1.00 / 2010.12.14)](
https://cdn.korg.com/us/support/download/files/aeb2862daf0cb7db826d8c62f51ec28d.txt?response-content-disposition=attachment%3Bfilename%2A%3DUTF-8%27%27nanoKONTROL2_MIDIimp.txt)

* [uv: Building and publishing a package](https://docs.astral.sh/uv/guides/package/#preparing-your-project-for-packaging
)
