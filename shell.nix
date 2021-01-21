{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    chromedriver
    chromium
    
    (python3.withPackages (p: [p.pip p.twine]))
  ];
}
