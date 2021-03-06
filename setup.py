#Adapted from scikit-learn

import sys
import os
import shutil
from distutils.core import Command

DISTNAME = 'Pawlabeling'
DESCRIPTION = 'A tool to process veterinary pressure measurements.'
LONG_DESCRIPTION = open('readme.md').read()
MAINTAINER = 'Ivo Flipse'
MAINTAINER_EMAIL = 'ivoflipse@gmail.com'
URL = 'https://github.com/ivoflipse/Pawlabeling'
LICENSE = 'new BSD'

import pawlabeling
VERSION = pawlabeling.__version__

###############################################################################
# Optional setuptools features
# We need to import setuptools early, if we want setuptools features,
# as it monkey-patches the 'setup' function

# For some commands, use setuptools
if len({'develop', 'release', 'bdist_egg', 'bdist_rpm', 'bdist_wininst', 'install_egg_info', 'build_sphinx', 'egg_info',
        'easy_install', 'upload', '--single-version-externally-managed'}.intersection(sys.argv)) > 0:
    extra_setuptools_args = dict(
        zip_safe=False,  # the package can run out of an .egg file
        include_package_data=True,
        )
else:
    extra_setuptools_args = dict()

###############################################################################
def configuration(parent_package='', top_path=None):
    if os.path.exists('MANIFEST'):
        os.remove('MANIFEST')

    from numpy.distutils.misc_util import Configuration
    config = Configuration(None, parent_package, top_path)

    # Avoid non-useful msg:
    # "Ignoring attempt to set 'name' (from ... "
    config.set_options(ignore_setup_xxx_py=True,
                       assume_default_configuration=True,
                       delegate_options_to_subpackages=True,
                       quiet=True)

    config.add_subpackage('pawlabeling')

    return config

def setup_package():
    metadata = dict(name=DISTNAME,
                    maintainer=MAINTAINER,
                    maintainer_email=MAINTAINER_EMAIL,
                    description=DESCRIPTION,
                    license=LICENSE,
                    url=URL,
                    install_require=["numpy",
                                     "scipy",
                                     "PySide",
                                     "matplotlib",
                                     "opencv",
                                     "pytables",
                                     "pypubsub"
                    ],
                    version=VERSION,
                    long_description=LONG_DESCRIPTION,
                    classifiers=['Intended Audience :: Science/Research',
                                 'Intended Audience :: Developers',
                                 'License :: OSI Approved',
                                 'Programming Language :: Python',
                                 'Topic :: Software Development',
                                 'Topic :: Scientific/Engineering',
                                 'Operating System :: Microsoft :: Windows',
                                 'Programming Language :: Python :: 2',
                                 'Programming Language :: Python :: 2.7',
                                 ],
                    **extra_setuptools_args)

    if (len(sys.argv) >= 2
        and ('--help' in sys.argv[1:] or sys.argv[1]
        in ('--help-commands', 'egg_info', '--version', 'clean'))):

        # For these actions, NumPy is not required.
        #
        # They are required to succeed without Numpy for example when
        # pip is used to install Scikit when Numpy is not yet present in
        # the system.
        try:
            from setuptools import setup
        except ImportError:
            from distutils.core import setup

        metadata['version'] = VERSION
    else:
        from numpy.distutils.core import setup

        metadata['settings'] = configuration

    setup(**metadata)


if __name__ == "__main__":
    setup_package()