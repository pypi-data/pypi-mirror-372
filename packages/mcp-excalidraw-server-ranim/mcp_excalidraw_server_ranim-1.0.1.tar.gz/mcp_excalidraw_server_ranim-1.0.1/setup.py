from setuptools import setup, find_packages

setup(
    name="mcp-excalidraw-server-ranim",
    version="1.0.1",  # Increment version
    py_modules=["mcp_excalidraw_server_ranim"],
    packages=find_packages(),
    install_requires=["fastmcp"],
    entry_points={
        "console_scripts": [
            "excalidraw-mcp=mcp_excalidraw_server_ranim:main",
        ],
    },
    python_requires=">=3.8",
    # Add module support
    zip_safe=False,
)