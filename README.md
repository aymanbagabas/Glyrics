# Glyrics
A GTK+ lyrics viewer that uses [glyr](https://github.com/sahib/glyr) and [playerctl](https://github.com/acrisci/playerctl) for its back-end.
<p align="center">
  <img alt="glyrics" src="glyrics.png"/>
</p>

## Install

### Flatpak
You can get flatpak builds from the releases page [here](https://github.com/aymanbagabas/Glyrics/releases).

### Build
Glyrics depends on the following:
* [meson](https://mesonbuild.com/) >= 0.46.0
* [ninja](https://ninja-build.org/)
* [playerctl](https://github.com/acrisci/playerctl)
* [glyr](https://github.com/sahib/glyr)
* [python-glyr](https://github.com/sahib/python-glyr)

**NOTE:** if you're installing these packages locally, make sure to specify `prefix` to `/usr` otherwise you will have trouble getting everything to work.

```
$ git clone https://github.com/aymanbagabas/Glyrics.git
$ cd Glyrics
$ meson build-meson
$ sudo ninja -C build-meson install
```

## Todo
See TODO.

## Credit
* [sahib](https://github.com/sahib) for [libglyr](https://github.com/sahib/glyr) and [plyr](https://github.com/sahib/python-glyr).
* [acrisci](https://github.com/acrisci) for [playerctl](https://github.com/acrisci/playerctl) library.

## License
See LICENSE.

Copyright © 2019, Ayman Bagabas
