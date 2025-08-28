try:
    import setuptools
except ImportError:
    pass
setuptools # keep pyflakes happy
from distutils.core import setup
import sys

long_desc = '''\
Enhanced Library -- extras beyond Python's stdlib

'''

data = dict(
       name='enhlib',
       version='0.0.11',
       url='https://github.com/ethanfurman/enhlib',
       packages=['enhlib','enhlib.stdlib','enhlib.test'],
       package_data={
           'enhlib' : [
               'LICENSE',
               'README.md',
               ]
           },
       include_package_data=True,
       license='BSD License',
       description="Extra library features not yet, or no longer, in the stdlib.",
       long_description=long_desc,
       provides=['enhlib'],
       author='Ethan Furman',
       author_email='ethan@stoneleaf.us',
       classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Programming Language :: Python',
            'Topic :: Software Development',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
            'Programming Language :: Python :: 3.11',
            'Programming Language :: Python :: 3.12',
            'Programming Language :: Python :: 3.13',
            ],
    )

py2_only = ()
py3_only = ()
make = [ ]

if __name__ == '__main__':
    if 'install' in sys.argv:
        import os, sys
        if sys.version_info[0] != 2:
            for file in py2_only:
                try:
                    os.unlink(file)
                except OSError:
                    pass
        if sys.version_info[0] != 3:
            for file in py3_only:
                try:
                    os.unlink(file)
                except OSError:
                    pass
    setup(**data)
