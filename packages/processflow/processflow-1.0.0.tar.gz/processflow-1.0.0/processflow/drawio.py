from dataclasses import dataclass, field
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
from .shape import Shape, Circle, Connection, Box, Terminator
from .event import (
    Start,
    End,
    Conditional,
    ConditionalIntermediate,
    Timer,
    Intermediate,
    Message,
    MessageIntermediate,
    MessageEnd,
    Signal,
    SignalIntermediate,
    SignalEnd,
    Link,
)
from .activity import Task, Subprocess, ServiceTask
from .gateway import Exclusive, Inclusive, Parallel
from .helper import Helper
from .version import __version__


class DrawIOXMLExporter:
    def create_root_element(self) -> ET.Element:
        return ET.Element("mxfile", host="app.diagrams.net")

    def write_to_file(self, root: ET.Element, filename: str) -> None:
        self._indent(root)
        tree = ET.ElementTree(root)
        tree.write(filename, encoding="utf-8", xml_declaration=True)

    def _indent(self, elem: ET.Element, level: int = 0) -> None:
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = f"{i}  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for child in elem:
                self._indent(child, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        elif level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


class DrawIOElementCreator:
    def __init__(self):
        self.cell_id = 2  # Start from 2 as 0 and 1 are reserved
        self.shapes = {}  # Maps object ID to actual shape object
        self.cell_map = {}  # Maps object ID to cell ID

    def create_diagram_structure(self, root: ET.Element) -> ET.Element:
        diagram = ET.SubElement(root, "diagram", id="diagram_1", name="Page-1")
        graph = ET.SubElement(diagram, "mxGraphModel", dx="1000", dy="1000", grid="1", gridSize="10")
        root_cell = ET.SubElement(graph, "root")

        # Base required cells
        ET.SubElement(root_cell, "mxCell", id="0")
        ET.SubElement(root_cell, "mxCell", id="1", parent="0")

        return root_cell

    def _get_shape_style(self, shape: Any) -> str:
        """Get draw.io style for different shape types"""
        if isinstance(shape, Start):
            return "ellipse;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;"
        elif isinstance(shape, End):
            return "ellipse;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;strokeWidth=3;"
        elif isinstance(shape, (Timer, Intermediate, Message, Signal, Conditional, Link)):
            return "ellipse;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;"
        elif isinstance(shape, (Task, Subprocess, ServiceTask)):
            return "rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;"
        elif isinstance(shape, Exclusive):
            return "rhombus;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;"
        elif isinstance(shape, (Inclusive, Parallel)):
            return "rhombus;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;"
        elif isinstance(shape, Terminator):
            return "shape=mxgraph.flowchart.terminator;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;"
        else:
            return "rounded=0;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;"

    def _get_pool_lane_style(self, is_pool: bool = False) -> str:
        """Get style for pools and lanes"""
        if is_pool:
            return "swimlane;horizontal=0;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1;"
        else:
            return "swimlane;horizontal=0;fillColor=#f8cecc;strokeColor=#b85450;"

    def _add_pool_or_lane(self, parent: ET.Element, element: Any, is_pool: bool = False) -> str:
        """Add pool or lane element"""
        style = self._get_pool_lane_style(is_pool)
        cell_id = self.cell_id
        self.cell_id += 1

        mxcell = ET.SubElement(parent, "mxCell",
                              id=str(cell_id),
                              value=element.name,
                              style=style,
                              vertex="1", parent="1")

        # Calculate geometry
        x = str(element.coord.x_pos)
        y = str(element.coord.y_pos)

        ET.SubElement(mxcell, "mxGeometry", {
            "x": x,
            "y": y,
            "width": str(element.width),
            "height": str(element.height),
            "as": "geometry"
        })

        # Store the mapping
        obj_id = id(element)
        self.shapes[obj_id] = element
        self.cell_map[obj_id] = str(cell_id)
        
        return str(cell_id)

    def _add_shape(self, parent: ET.Element, shape: Any) -> str:
        """Add shape element (event, task, gateway, etc.)"""
        style = self._get_shape_style(shape)
        cell_id = self.cell_id
        self.cell_id += 1

        mxcell = ET.SubElement(parent, "mxCell",
                              id=str(cell_id),
                              value=shape.name,
                              style=style,
                              vertex="1", parent="1")

        # Calculate geometry - for circles, adjust coordinates
        if isinstance(shape, Circle):
            x = str(shape.coord.x_pos - shape.radius)
            y = str(shape.coord.y_pos - shape.radius)
        else:
            x = str(shape.coord.x_pos)
            y = str(shape.coord.y_pos)

        ET.SubElement(mxcell, "mxGeometry", {
            "x": x,
            "y": y,
            "width": str(shape.width),
            "height": str(shape.height),
            "as": "geometry"
        })

        # Store the mapping
        obj_id = id(shape)
        self.shapes[obj_id] = shape
        self.cell_map[obj_id] = str(cell_id)

        # Add diamonds for Box shapes with attach attribute
        if isinstance(shape, Box) and hasattr(shape, 'attach') and shape.attach:
            self._add_diamond_attachments(parent, shape)

        return str(cell_id)

    def _add_diamond_attachments(self, parent: ET.Element, box_shape: Box) -> None:
        """Add diamond attachments to a box shape"""
        if not box_shape.attach:
            return
        
        diamond_size = 40  # Small diamond size
        diamond_spacing = 0  # No space between diamonds
        
        # Anchor position - bottom-right corner of the box
        anchor_x = box_shape.coord.x_pos + box_shape.width  # Right edge of box
        anchor_y = box_shape.coord.y_pos + box_shape.height  # Bottom edge of box

        total_diamonds = len(box_shape.attach)
        
        # Define positions based on number of diamonds
        positions = []
        
        if total_diamonds == 1:
            # Single diamond centered at bottom-right corner
            positions = [(anchor_x - (diamond_size // 2), anchor_y - (diamond_size // 2))]
        elif total_diamonds == 2:
            # Two diamonds side by side horizontally at bottom edge
            positions = [
                (anchor_x - diamond_size - (diamond_size // 2), anchor_y - (diamond_size // 2)),
                (anchor_x - (diamond_size // 2), anchor_y - (diamond_size // 2))
            ]
        elif total_diamonds == 3:
            # Triangle formation
            positions = [
                (anchor_x - (diamond_size // 2), anchor_y - (diamond_size // 2)),  # bottom right
                (anchor_x - (diamond_size // 2) - (diamond_size // 2), anchor_y - diamond_size),  # top center
                (anchor_x - diamond_size - (diamond_size // 2), anchor_y - (diamond_size // 2))  # bottom left
            ]
        elif total_diamonds == 4:
            # Diamond pattern (like playing card suit)
            positions = [
                (anchor_x - diamond_size, anchor_y - (diamond_size // 2)),  # left
                (anchor_x - (diamond_size // 2), anchor_y - diamond_size),  # top
                (anchor_x, anchor_y - (diamond_size // 2)),  # right
                (anchor_x - (diamond_size // 2), anchor_y)  # bottom
            ]
            
        # Add each diamond with its label
        for i, (label, (diamond_x, diamond_y)) in enumerate(zip(box_shape.attach, positions)):
            cell_id = self.cell_id
            self.cell_id += 1
            
            diamond_cell = ET.SubElement(parent, "mxCell",
                                      id=str(cell_id),
                                      value=str(label),
                                      style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;",
                                      vertex="1", parent="1")
            
            ET.SubElement(diamond_cell, "mxGeometry", {
                "x": str(diamond_x),
                "y": str(diamond_y),
                "width": str(diamond_size),
                "height": str(diamond_size),
                "as": "geometry"
            })

    def _add_connection(self, parent: ET.Element, connection: Connection) -> None:
        """Add connection/edge element"""
        # Get the cell IDs for source and target shapes
        source_id = self.cell_map.get(id(connection.source))
        target_id = self.cell_map.get(id(connection.target))

        if not source_id or not target_id:
            Helper.printc(f"Warning: Missing source or target for connection {connection.label}", 
                         show_level="export_to_drawio")
            return

        # Determine connection style (solid or dashed)
        style = "endArrow=block;html=1;strokeWidth=2;"
        if hasattr(connection.source, 'is_same_pool') and not connection.source.is_same_pool(connection.source, connection.target):
            style = "endArrow=block;html=1;strokeWidth=2;dashed=1;"

        cell_id = self.cell_id
        self.cell_id += 1

        mxcell = ET.SubElement(parent, "mxCell",
                              id=str(cell_id),
                              value=connection.label,
                              style=style,
                              edge="1", parent="1",
                              source=source_id,
                              target=target_id)

        mxgeo = ET.SubElement(mxcell, "mxGeometry", {"relative": "1", "as": "geometry"})

        # Add waypoints if they exist
        if hasattr(connection, 'connection_points') and len(connection.connection_points) > 2:
            mx_points = ET.SubElement(mxgeo, "Array", {"as": "points"})
            # Skip first and last points as they are source/target connection points
            for x_pos, y_pos in connection.connection_points[1:-1]:
                ET.SubElement(mx_points, "mxPoint", {
                    "x": str(x_pos),
                    "y": str(y_pos)
                })

    def create_diagram_elements(self, root_cell: ET.Element, pools: list[Any]) -> None:
        """Create all diagram elements from pools"""
        Helper.printc("Creating draw.io elements...", show_level="export_to_drawio")

        # First pass: Create pools and lanes
        for pool in pools:
            Helper.printc(f"Processing pool: {pool.name}", show_level="export_to_drawio")

            if hasattr(pool, 'has_pool') and pool.has_pool():
                self._add_pool_or_lane(root_cell, pool, is_pool=True)

            for lane in pool.lanes:
                Helper.printc(f"Processing lane: {lane.name}", show_level="export_to_drawio")
                self._add_pool_or_lane(root_cell, lane, is_pool=False)

        # Second pass: Create shapes
        for pool in pools:
            for lane in pool.lanes:
                for shape in lane.shapes:
                    Helper.printc(f"Processing shape: {shape.name}", show_level="export_to_drawio")
                    self._add_shape(root_cell, shape)

        # Third pass: Create connections
        for pool in pools:
            for lane in pool.lanes:
                for shape in lane.shapes:
                    if hasattr(shape, 'connection_to') and shape.connection_to is not None:
                        for connection in shape.connection_to:
                            if isinstance(connection, Connection):
                                Helper.printc(f"Processing connection: {connection.label}", 
                                           show_level="export_to_drawio")
                                self._add_connection(root_cell, connection)


@dataclass
class DrawIO:
    """Draw.io diagram exporter"""

    def __post_init__(self):
        self.xml_exporter = DrawIOXMLExporter()
        self.element_creator = DrawIOElementCreator()

    def export_to_xml(self, pools, filename):
        """Export the ProcessPiper diagram to draw.io XML format"""
        Helper.printc("Exporting diagram to .drawio format..", show_level="export_to_drawio")

        # Create root mxfile element
        root = self.xml_exporter.create_root_element()

        # Create diagram structure (diagram -> mxGraphModel -> root -> base cells)
        root_cell = self.element_creator.create_diagram_structure(root)

        # Create all diagram elements
        self.element_creator.create_diagram_elements(root_cell, pools)

        # Write to file
        self.xml_exporter.write_to_file(root, filename)
        Helper.printc(f"Draw.io diagram exported to: {filename}", show_level="export_to_drawio")


if __name__ == "__main__":
    drawio = DrawIO()
    drawio.export_to_xml([], "test.drawio")