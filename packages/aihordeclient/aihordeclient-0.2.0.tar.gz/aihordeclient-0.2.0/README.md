# AIHordeclient

AIHordeclient is a lib to connect to https://aihorde.net/api/v2 and
ease plugin development.

There is an [official Python-SDK](https://pypi.org/project/aihorde/) from [AIHorde](https://aihorde.net).

## USAGE

```sh
pip install aihordeclient
```

<details>
<summary>In order to run a simple use and see the client in action, do:</summary>

```sh
git clone https://github.com/ikks/aihordeclient/
cd aihordeclient
uv venv -p 3.13
source .venv/bin/activate
uv pip install aihordeclient
AIHORDE_API_KEY=<yourapikey> python main.py
```

On success you will have a webp downloaded file in your temp directory.


This screenshot under [Debian](https://www.debian.org), [Sway](https://swaywm.org/) [Kitty terminal](https://sw-kovidgoyal-net.translate.goog/kitty/), [uv](https://docs.astral.sh/uv) and using [vv](https://github.com/wolfpld/moderncore/blob/master/doc/vv.md) to display the image.


</details>

Look at [https://github.com/ikks/aihordeclient/blob/main/main.py](main.py) for the simplest sample, for other real
use cases, see:

* [stablehorde-gimp3](https://github.com/ikks/gimp-stable-diffusion/)
* [libreoffice-stable-horde](https://github.com/ikks/libreoffice-stable-diffusion/)

Get an AIHORDE [free api_key](https://aihorde.net/register) to run
the sample code, once you have installed the package.

# AUTHORS

Most of the code descends from
[blueturtleai Gimp 2.10.X plugin](https://github.com/blueturtleai/gimp-stable-diffusion)
initial work.

# THANKS

* AIHorde
