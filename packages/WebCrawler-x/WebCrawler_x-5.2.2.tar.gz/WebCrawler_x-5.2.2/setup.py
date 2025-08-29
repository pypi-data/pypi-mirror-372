from setuptools import setup, find_packages


packages = ['WebCrawler_x']
setup(name='WebCrawler_x',
    version='5.2.2',
    author='jackson_tao',
    packages=packages,
    install_requires=[
        "requests",
        "retrying",
        "beautifulsoup4",
        "fake-useragent",
        "gne",
        "htmldate",
        "loguru",
        "lxml",
        "lxparse",
        "pybloom_live",
        "DrissionPage"
    ]
      )
