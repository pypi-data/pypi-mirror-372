from setuptools import setup, find_packages

setup(
  name            = "pyotme",
  url             = "https://t.me/NexLangPy",
  description     = "library for python (2+3)",
  version         = "1.3",
  author          = "Devil",
  author_email    = "nasr2python@gmail.com",
  license         = "LGPLv3+",
  classifiers     = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Topic :: Software Development :: Libraries",
    "License :: OSI Approved :: GNU Lesser General Public License" +
      " v3 or later (LGPLv3+)",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: Implementation :: CPython",
    "Programming Language :: Python :: Implementation :: PyPy",
  ],
  keywords        = "functional development tools lazy immutable",
  packages        = find_packages(),
  extras_require  = { "test": ["coverage"] },
)
