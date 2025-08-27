.. image:: _static/yutipy_header.png
   :alt: Welcome to yutipy's documentation!
   :target: https://github.com/CheapNightbot/yutipy
   :align: center

**yutipy** is a Python package to interact and retrieving music information from various music platforms (see list of :doc:`available muisc platforms <available_platforms>`).
This documentation will help you get started with yutipy and provide detailed information about its features and usage.

   **Looking for an easy-to-use API or GUI to search for music, instead of using the CLI or building your own integration?**
   Check out `yutify <https://yutify.cheapnightbot.me>`_ — it’s powered by yutipy!

.. raw:: html

   <p align="center">
   <a href="https://github.com/CheapNightbot/yutipy/actions/workflows/tests.yml">
   <img alt="GitHub Actions Workflow Status" src="https://img.shields.io/github/actions/workflow/status/cheapnightbot/yutipy/pytest-unit-testing.yml?style=for-the-badge&label=Pytest">
   </a>
   <a href="https://yutipy.readthedocs.io/en/latest/">
   <img src="https://img.shields.io/readthedocs/yutipy?style=for-the-badge" alt="Documentation Status" />
   </a>
   <a href="https://pypi.org/project/yutipy/">
   <img src="https://img.shields.io/pypi/v/yutipy?style=for-the-badge" alt="PyPI" />
   </a>
   <a href="https://github.com/CheapNightbot/yutipy/blob/master/LICENSE">
   <img src="https://img.shields.io/github/license/CheapNightbot/yutipy?style=for-the-badge" alt="License" />
   </a>
   <a href="https://github.com/CheapNightbot/yutipy/stargazers">
   <img src="https://img.shields.io/github/stars/CheapNightbot/yutipy?style=for-the-badge" alt="Stars" />
   </a>
   <a href="https://github.com/CheapNightbot/yutipy/issues">
   <img src="https://img.shields.io/github/issues/CheapNightbot/yutipy?style=for-the-badge" alt="Issues" />
   </a>
   </p>

Features
=========

- Simple & Easy integration with popular music APIs.
- Search for music by artist and song title across multiple platforms.
- It uses ``RapidFuzz`` to compare & return the best match so that you can be sure you got what you asked for without having to worry and doing all that work by yourself.
- Retrieve detailed music information, including album art, release dates, lyrics, ISRC, and UPC codes.
- Authorize and access user resources easily.

Get Started
===========

.. toctree::
   :maxdepth: 2

   installation
   available_platforms
   usage_examples
   api_reference
   cli
   faq

.. toctree::
   :caption: Project Links
   :hidden:

   pypi <https://pypi.org/project/yutipy>
   source code <https://github.com/CheapNightbot/yutipy>
   issue tracker <https://github.com/CheapNightbot/yutipy/issues>
   support project <https://ko-fi.com/cheapnightbot>
