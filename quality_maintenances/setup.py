from setuptools import setup

setup(
    name="quality_maintenances",
    version="1.0",
    py_modules=["quality_maintenances"],
    include_package_data=True,
    install_requires=[
        "click==6.7",
        "prettytable==0.7.2",
        "redis==2.10.6",
    ],
    entry_points="""
        [console_scripts]
        quality_maintenances=quality_maintenances:cli
    """,
)
