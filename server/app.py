"""Root-level server app for OpenEnv validation compatibility."""

from git_merge_conflict_env.server.app import app  # noqa: F401


def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()
