CHANGELOG
=========

PyPI pythonic-fp-sentinels project.

Semantic Versioning
-------------------

Strict 3 digit semantic versioning

- **MAJOR** version incremented for incompatible API changes
- **MINOR** version incremented for backward compatible added functionality
- **PATCH** version incremented for backward compatible bug fixes

See `Semantic Versioning 2.0.0 <https://semver.org>`_.

Releases and Important Milestones
---------------------------------

2.0.0 - TBD
~~~~~~~~~~~

First PyPI release as pythonic-fp-sentinels.

New Repo - 2025-08-14
~~~~~~~~~~~~~~~~~~~~~

GitHub repo renamed pythonic-fp-sentinels. The singletons package effort will be
continued as the sentinel package. PyPI pythonic-fp-singletons project deprecated
in favor of pythonic-fp-sentinels project.


1.0.0+ - 2025-08-14
~~~~~~~~~~~~~~~~~~~

Last development version as pythonic-fp-singletons.

- moved module pythonic_fp.singletons.sbool to pythonic_fp.booleans

  - module ``singletons.sbool`` refactored into modules ``subtypable_bool`` and ``flavored_bool``

- removed pythonic_fp.nada module

  - learned a lot about Python getting it to work
  - decided its use case was not worth the effort to maintain it

- extended class Singleton

  - from declaring multiple singletons with strings
  - to declaring multiple "flavors" of any hashable type


1.0.0 - 2025-08-02
~~~~~~~~~~~~~~~~~~

Moved singletons.py from fptools. Also incorporated bool.py into the
singleton's package.
