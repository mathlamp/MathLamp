{ pkgs ? import <nixpkgs> {} }:
	pkgs.mkShell {
		nativeBuildInputs = [
			pkgs.python314
			pkgs.poetry
	];
}