{ inputs, pkgs, projectPath }:
let
  python = pkgs.python311;
  workspaceRoot = projectPath "/";

  pythonEnv = let
    commonOverlay = final: prev: {
      phpserialize = prev.phpserialize.overrideAttrs (old: {
        nativeBuildInputs = old.nativeBuildInputs
          ++ [ (final.resolveBuildSystem { setuptools = [ ]; }) ];
      });
      pydeps = prev.pydeps.overrideAttrs (old: {
        nativeBuildInputs = old.nativeBuildInputs
          ++ [ (final.resolveBuildSystem { setuptools = [ ]; }) ];
      });
    };
  in {
    default = inputs.python-env.lib.mkPythonEnv {
      inherit pkgs python workspaceRoot;
      extraOverlays = [ commonOverlay ];
    };

    editable = inputs.python-env.lib.mkPythonEnv {
      inherit pkgs python workspaceRoot;
      editableRoot = "$PWD";
      extraOverlays = [
        commonOverlay
        (_: prev: {
          labels = prev.labels.overrideAttrs (old: {
            src = pkgs.lib.fileset.toSource {
              root = old.src;
              fileset = pkgs.lib.fileset.unions [
                (old.src + "/labels")
                (old.src + "/pyproject.toml")
                (old.src + "/test")
                (old.src + "/uv.lock")
              ];
            };
            nativeBuildInputs = old.nativeBuildInputs
              ++ prev.resolveBuildSystem { editables = [ ]; };
          });
        })
      ];
    };
  };
in {
  default = pythonEnv.default.mkVirtualEnv "labels"
    pythonEnv.default.workspace.deps.default;
  editable = pythonEnv.editable.mkVirtualEnv "labels"
    pythonEnv.editable.workspace.deps.all;
}
