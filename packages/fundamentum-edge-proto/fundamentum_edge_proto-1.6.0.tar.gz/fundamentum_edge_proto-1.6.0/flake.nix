{
  description = "A basic flake";
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = {
    nixpkgs,
    uv2nix,
    pyproject-nix,
    pyproject-build-systems,
    ...
  }: let
    forAllSystems = f:
      nixpkgs.lib.genAttrs [
        "aarch64-linux"
        "x86_64-linux"
        "aarch64-darwin"
        "x86_64-darwin"
      ] (
        system:
          f {
            pkgs = import nixpkgs {
              inherit system;
              config.allowUnfree = false;
            };
          }
      );
  in {
    devShells = forAllSystems ({pkgs}: let
      python = pkgs.python312;
      workspace = uv2nix.lib.workspace.loadWorkspace {workspaceRoot = ./.;};
      overlay = workspace.mkPyprojectOverlay {sourcePreference = "wheel";};
      baseSet = pkgs.callPackage pyproject-nix.build.packages {inherit python;};
      pythonSet = baseSet.overrideScope (
        pkgs.lib.composeManyExtensions [
          pyproject-build-systems.overlays.default
          overlay
        ]
      );
      venv = pythonSet.mkVirtualEnv "venv" workspace.deps.all;
    in {
      default = pkgs.mkShell {
        packages = [
          venv
          pkgs.uv
          pkgs.just
          pkgs.protobuf_25
          pkgs.git-subrepo
        ];

        env = {
          PYTHONPATH = "";
          VIRTUAL_ENV = "${venv}";
          UV_PROJECT_ENVIRONMENT = "${venv}";
          UV_PYTHON = "${venv}/bin/python";
          UV_NO_SYNC = "1";
          UV_PYTHON_DOWNLOADS = "never";
        };
      };
    });
  };
}
