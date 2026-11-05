{ lib, stdenvNoCC, fetchFromGitHub }:

stdenvNoCC.mkDerivation {
  pname = "irixium-gtk-theme";
  version = "0-unstable-2022-05-22";

  src = fetchFromGitHub {
    owner = "Pyanyaleri";
    repo = "Irixium";
    rev = "ca46817bb2fe652ba73ba8e4c2b35a6827d9e091";
    hash = "sha256-wuUxP6myjK/WV2rSJzF9n8H8GpoEKjAQPG2qkj5TmSk=";
  };

  dontBuild = true;
  installPhase = ''
    runHook preInstall
    mkdir -p "$out/share/themes/Irixium"
    cp -a index.theme gtk-3.0 "$out/share/themes/Irixium/"
    install -Dm644 LICENSE "$out/share/doc/irixium-gtk-theme/LICENSE"
    install -Dm644 README.md "$out/share/doc/irixium-gtk-theme/upstream-README.md"
    test -s "$out/share/themes/Irixium/gtk-3.0/gtk.css"
    runHook postInstall
  '';

  meta = {
    description = "SGI IRIX-inspired GTK3 theme, with noncommercial-licensed image assets";
    homepage = "https://github.com/Pyanyaleri/Irixium";
    # LICENSE covers code; README separately licenses the images.
    license = [ lib.licenses.gpl3Only lib.licenses.cc-by-nc-sa-40 ];
    platforms = lib.platforms.linux;
  };
}
