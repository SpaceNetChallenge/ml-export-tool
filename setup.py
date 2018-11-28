
import os

from setuptools import setup, find_packages

with open('ml_export/__init__.py') as f:
    for line in f:
        if line.find("__version__") >= 0:
            version = line.split("=")[1].strip()
            version = version.strip('"')
            version = version.strip("'")
            continue


with open('README.MD') as f:
    readme = f.read()

# Runtime requirements.
inst_reqs = ["rio-tiler~=1.0rc2", "rasterio[s3]~=1.0.0", "shapely", "mercantile",
             "numpy", "requests", "affine", "tqdm", "torchvision", "boto3",
             "sat-stac"]

extra_reqs = {
    'test': ['mock', 'pytest', 'pytest-cov', 'codecov']}

setup(name='ml-export',
      version=version,
      description=u"""Export Tools for Transforming ML Models into Maps""",
      long_description=readme,
      classifiers=[
          'Intended Audience :: Information Technology',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 3.6',
          'Topic :: Scientific/Engineering :: GIS'],
      keywords='raster aws tiler gdal rasterio spacenet machinelearning hotosm cog',
      author=u"David Lindenbaum",
      author_email='dlindenbaum@iqt.org',
      url='https://github.com/SpaceNetChallenge/ml-export-tool',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      zip_safe=False,
      install_requires=inst_reqs,
      extras_require=extra_reqs)
