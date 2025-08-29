{ inputs, pkgs, projectPath }:
let
  envars = pkgs.callPackage ./envars.nix { inherit projectPath; };
  venv = pkgs.callPackage ./venv.nix { inherit inputs projectPath; };

  dependencies = let osDependencies = [ pkgs.git pkgs.skopeo pkgs.uv ];
  in {
    default = pkgs.lib.flatten [ venv.default osDependencies ];
    editable = pkgs.lib.flatten [ venv.editable osDependencies ];
  };
in { inherit dependencies envars venv; }
