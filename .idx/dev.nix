{ pkgs, ... }: {
  # Which nixpkgs channel to use.
  channel = "stable-24.05";

  # A list of packages to have in the environment.
  packages = [
    pkgs.nodejs_20
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.yarn
  ];

  # An attribute set of environment variables.
  env = {
    REACT_APP_BACKEND_URL = "http://localhost:8000";
  };

  # The previews configuration.
  idx.previews = {
    enable = true;
    previews = {
      web = {
        command = [ "yarn" "start" ];
        cwd = "frontend";
        manager = "web";
      };
    };
  };

  # Workspace lifecycle hooks.
  idx.workspace = {
    onCreate = {
      install-backend-deps = "cd backend && python3 -m pip install -r requirements.txt";
    };
    onStart = {
      # Install frontend dependencies every time the workspace starts.
      install-frontend-deps = "cd frontend && yarn install";
      # Start the backend server as a background process.
      start-backend = "cd backend && python3 -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload &";
    };
  };
}
