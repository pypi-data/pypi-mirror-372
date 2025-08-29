#!/usr/bin/env python3
import json
import uuid
from typing import Optional
from fastmcp import FastMCP

# Create server instance  
mcp = FastMCP("Excalidraw Server")

# In-memory storage
diagrams_store = {}

def create_excalidraw_element(element_type: str, x: int, y: int, 
                            width: int = 100, height: int = 100, text: str = ""):
    return {
        "id": str(uuid.uuid4()),
        "type": element_type,
        "x": x, "y": y, "width": width, "height": height,
        "angle": 0, "strokeColor": "#000000", "backgroundColor": "transparent",
        "text": text, "fontSize": 20, "textAlign": "center"
    }

@mcp.tool()
def create_diagram(name: str) -> str:
    """Create a new Excalidraw diagram"""
    diagrams_store[name] = {
        "type": "excalidraw",
        "version": 2,
        "elements": [],
        "appState": {"viewBackgroundColor": "#ffffff"}
    }
    return f"Created diagram: {name}"

@mcp.tool()
def add_rectangle(diagram_name: str, x: int, y: int, 
                 width: int = 100, height: int = 100, text: str = "") -> str:
    """Add a rectangle to a diagram"""
    if diagram_name not in diagrams_store:
        return f"Diagram '{diagram_name}' not found"
    
    element = create_excalidraw_element("rectangle", x, y, width, height, text)
    diagrams_store[diagram_name]["elements"].append(element)
    return f"Added rectangle to {diagram_name} at ({x}, {y})"

@mcp.tool()
def add_circle(diagram_name: str, x: int, y: int, 
              radius: int = 50, text: str = "") -> str:
    """Add a circle to a diagram"""
    if diagram_name not in diagrams_store:
        return f"Diagram '{diagram_name}' not found"
    
    element = create_excalidraw_element("ellipse", x, y, radius * 2, radius * 2, text)
    diagrams_store[diagram_name]["elements"].append(element)
    return f"Added circle to {diagram_name} at ({x}, {y})"

@mcp.tool()
def export_diagram(diagram_name: str) -> str:
    """Export diagram as JSON"""
    if diagram_name not in diagrams_store:
        return f"Diagram '{diagram_name}' not found"
    
    diagram_json = json.dumps(diagrams_store[diagram_name], indent=2)
    return f"Diagram JSON:\n```json\n{diagram_json}\n```"

@mcp.tool()
def list_diagrams() -> str:
    """List all available diagrams"""
    if not diagrams_store:
        return "No diagrams available"
    
    diagram_list = "\n".join([f"- {name} ({len(data['elements'])} elements)" 
                             for name, data in diagrams_store.items()])
    return f"Available diagrams:\n{diagram_list}"

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()