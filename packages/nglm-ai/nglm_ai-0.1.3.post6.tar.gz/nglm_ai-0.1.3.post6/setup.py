from setuptools import setup, find_packages
import os

build_version = os.environ.get("NGLM_AI_VERSION", "0.1.1")
print("NGLM_AI_VERSION =", build_version)
setup(
        name='nglm-ai',
        version=build_version,
        description='nglm base build',
        author='Ra K',
        author_email='your.email@example.com',
        packages=find_packages(),
        install_requires=[
            'pandas',  # List any dependencies here, e.g., 'requests>=2.20.0',
            'Flask'
        ],
    )