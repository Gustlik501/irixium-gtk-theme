{
  description = "Irixium GTK3 theme (GPL code, noncommercial CC-BY-NC-SA images)";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  outputs = { self, nixpkgs }:
    let
      systems = [ "x86_64-linux" ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
      # Upstream images are CC-BY-NC-SA-4.0. Permit only this package for
      # standalone builds; overlay consumers must opt in themselves.
      pkgsFor = system: import nixpkgs {
        inherit system;
        config.allowUnfreePredicate = pkg:
          nixpkgs.lib.getName pkg == "irixium-gtk-theme";
      };
    in {
      packages = forAllSystems (system:
        let pkgs = pkgsFor system;
        in rec {
          irixium-gtk-theme = pkgs.callPackage ./package.nix { };
          default = irixium-gtk-theme;
        });
      overlays.default = final: prev: {
        irixium-gtk-theme = final.callPackage ./package.nix { };
      };
      checks = forAllSystems (system: {
        inherit (self.packages.${system}) irixium-gtk-theme;
      });
      devShells = forAllSystems (system:
        let pkgs = pkgsFor system;
        in { default = pkgs.mkShell {
          packages = [ pkgs.xvfb-run pkgs.xorg.xwininfo pkgs.imagemagick
            pkgs.dbus pkgs.gtk3.dev pkgs.xfce.thunar pkgs.python3
            pkgs.adwaita-icon-theme pkgs.shared-mime-info ];
          IRIXIUM_TEST_DATA_DIRS = "${pkgs.adwaita-icon-theme}/share:${pkgs.shared-mime-info}/share";
        }; });
    };
}
