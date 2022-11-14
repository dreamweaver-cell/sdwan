from setuptools import setup

if __name__ == "__main__":
    try:
        setup(use_scm_version={"version_scheme": "no-guess-dev"})
    except:  # noqa
        print("\n\nUnexpected error. Please ensure you have the most updated version "
              "of setuptools, setuptools_scm and wheel.\n\n")
        raise
