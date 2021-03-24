"""Setup file
Tutorial:
  http://the-hitchhikers-guide-to-packaging.readthedocs.io/en/latest/quickstart.html
rm -rf dist/
python setup.py sdist bdist_wheel
cd ..
pip install -I Pipelineorchestration/dist/Pipelineorchestration-1.0-py3-none-any.whl  # Must be outside the project root
cd Pipelineorchestration
"""
import setuptools  # this is for bdist wheel

from distutils.core import setup

setuptools.setup(
    name="Pipelineorchestration",
    version=1.,
    author_email="yogitasn@yahoo.com",
    url="",
    packages=setuptools.find_packages(),
    package_dir={
        "Pipelineorchestration": "Pipelineorchestration",
        "Pipelineorchestration.analytical_processing": "Pipelineorchestration/analytical_processing",
        "Pipelineorchestration.eod_load": "Pipelineorchestration/eod_load",
        "Pipelineorchestration.preprocessing": "Pipelineorchestration/preprocessing",
        "Pipelineorchestration.job_tracker": "Pipelineorchestration/job_tracker",
    },
    python_requires=">=3.7",
    data_files=[('config', ['Pipelineorchestration/config.cfg'])],
    license=""
)
