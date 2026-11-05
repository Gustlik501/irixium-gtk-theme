# irixium-gtk-theme

The SGI IRIX-inspired [Pyanyaleri/Irixium](https://github.com/Pyanyaleri/Irixium)
GTK3 theme, unmodified. Pinned to main commit
`ca46817bb2fe652ba73ba8e4c2b35a6827d9e091` (2022-05-22), verified as the
latest main commit when packaged. Installs:

- `$out/share/themes/Irixium/index.theme`
- `$out/share/themes/Irixium/gtk-3.0/gtk.css` and `assets/`
- `$out/share/doc/irixium-gtk-theme/{LICENSE,upstream-README.md}`

**GTK3 only:** there are no `gtk-2.0/` or `gtk-4.0/` directories, despite
upstream's README describing it as GTK3/4. No GTK4/libadwaita support is implied.

## Licence caveat

The code's `LICENSE` is **GPL-3.0**. The upstream README separately licenses
**images CC-BY-NC-SA-4.0**, which permits noncommercial redistribution with
attribution and share-alike, but is not a free-software licence. Both are
recorded in `meta.license`. Sources/assets are fetched with a pinned hash at
build time, not vendored here. Standalone flake packages explicitly allow
only this one unfree package; overlay users must opt in themselves.
**Do not assume the image assets are GPL or commercially redistributable.**

```sh
nix build
nix flake check
nix develop --command python verify.py
```

## NixOS / Home Manager

Add this flake as `inputs.irixium-gtk-theme` and make its nixpkgs input follow
yours. Direct package:
`inputs.irixium-gtk-theme.packages.x86_64-linux.irixium-gtk-theme`.
Alternatively add `inputs.irixium-gtk-theme.overlays.default` to
`nixpkgs.overlays`, exposing `pkgs.irixium-gtk-theme`, with:

```nix
nixpkgs.config.allowUnfreePredicate = pkg:
  builtins.elem (lib.getName pkg) [ "irixium-gtk-theme" ];
```

NixOS installation: `environment.systemPackages = [ pkgs.irixium-gtk-theme ];`.
Home Manager selection (for a future declarative activation):

```nix
gtk = {
  enable = true;
  theme = { package = pkgs.irixium-gtk-theme; name = "Irixium"; };
};
```

Or launch a GTK3 app with `XDG_DATA_DIRS=<package>/share:$XDG_DATA_DIRS
GTK_THEME=Irixium`. Theme name is case-sensitive.

## Isolated visual verification

`verify.py` launches its own Xvfb and private `dbus-run-session`, with private
HOME/XDG directories under `.work/`, in-memory settings, and no live Wayland
socket or system bus. It runs `gtk3-widget-factory` from `gtk3.dev`, then a
fresh Thunar browsing `/tmp`, and captures the virtual root with ImageMagick.
The virtual screen is 1600×900 so the factory's 1360px-wide window is not
clipped (initial 1280×800 captures are also retained with `-1280` suffixes).
No window manager is started; the black area is the unused virtual root.
All test processes, including activated helpers, are cleaned up by PID and
an invocation-specific environment token; the running desktop is untouched.

Inspected screenshots:
- `.work/irixium-widget-factory.png`
- `.work/irixium-thunar.png`

Both show the expected gray beveled controls, blue selections and red-tinted
entry fields. **Zero GTK CSS/theme warnings** in `widget-factory.log` and
`thunar.log`. Private D-Bus helper shutdown messages (xfconfd/tumbler losing
their private bus) are in `session.log`; these are not theme CSS errors.
Only GTK3/X11 was visually tested, not GTK3 on Wayland or any other toolkit.
