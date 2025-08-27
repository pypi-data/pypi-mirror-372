import os


class Config:
    """
    Configuration class for DIALS ML Deploy.
    """

    template_name = os.getenv("TEMPLATE_NAME", "template.yaml")
    dials_dev_cache_dir = os.getenv("DIALS_DEV_CACHE_DIR", ".cache-dev")
    build_path = os.getenv("BUILD_PATH", ".dism-artifacts/build")
    triton_config = os.getenv("TRITON_CONFIG", "config.pbtxt")
    mlserver_config = os.getenv("MLSERVER_CONFIG", "model-settings.json")
    kserve_tag = os.getenv("KSERVE_TAG", "v0.13.1")
    package_path = os.getenv("PACKAGE_PATH", ".dism-artifacts/package")
