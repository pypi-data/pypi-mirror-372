"""
This package contains command line utilities to build plugin images.

At the time of writing, this module consists of two utilities:

* utility to label a plugin OCI image that is an extraction plugin.
* (deprecated) utility to fully build a plugin from a python file and docker directory;
  the downside of this approach is that it needs the plugins full runtime environment,
  which can be very large (in case when big data models are used).

The utilities are includeded in setup.py.
"""
