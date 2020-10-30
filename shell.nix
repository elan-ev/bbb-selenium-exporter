{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    chromedriver

    (python3.withPackages (p: [p.pip]))
  ];
}
