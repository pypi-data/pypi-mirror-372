from setuptools import setup, find_packages

setup(
    name="bytedance_mcp_server_my_mr_analysis",
    version="0.0.1",
    packages=find_packages(),
    description="This is a reserved placeholder package to mitigate dependency confusion risks.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://code.byted.org/infra/bytedance_mcp_server_my_mr_analysis",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
        "Intended Audience :: Developers",
        "Development Status :: 7 - Inactive",
    ],
    python_requires='>=3.6',
)

