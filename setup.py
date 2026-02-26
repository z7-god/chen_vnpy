from setuptools import setup, find_packages

setup(
    name="chen_vnpy",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "vnpy",
        "vnpy_ctp",
        "vnpy_ctastrategy",
        "vnpy_ctabacktester",
    ],
    author="z7-god",
    description="A VnPy-based automated trading system with CTP connectivity.",
)
