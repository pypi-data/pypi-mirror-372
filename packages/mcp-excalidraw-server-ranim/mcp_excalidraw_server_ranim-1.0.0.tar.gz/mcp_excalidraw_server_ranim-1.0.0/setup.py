from setuptools import setup

setup(
    name="mcp-excalidraw-server-ranim",
    version="1.0.0",
    py_modules=["mcp_excalidraw_server_ranim"],
    install_requires=["fastmcp"],
    entry_points={
        "console_scripts": [
            "excalidraw-mcp=mcp_excalidraw_server_ranim:main",
        ],
    },
)