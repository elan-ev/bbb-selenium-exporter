import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bbb-selenium-exporter",
    version="0.1.1",
    author="Markus Otto",
    author_email="markus.otto@infra.run",
    description="Export Prometheus metrics scraped from BigBlueButton servers using Selenium",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/infra.run/public/bbb-selenium-exporter",
    install_requires=[
        "mpipe",
        "pillow",
        "prometheus-client",
        "requests",
        "selenium",
    ],
    packages=setuptools.find_packages(),
    package_data={"": ["assets/*.pdf"]},
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "bbb-selenium-exporter=bbb_selenium_exporter.server:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3.6',
)
