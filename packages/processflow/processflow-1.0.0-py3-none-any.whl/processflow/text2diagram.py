import datetime
import re
import os
from PIL import Image
from rich.console import Console
# Removed unused tornado.options import as it's not needed


def _parse_and_generate_code(input_str, png_output_file, export_to_bpmn, export_to_drawio=False):
    """
    Parse input string and generate code to create a diagram
    """

    lines = [
        line.strip()
        for line in input_str.strip().split("\n")
        if not line.startswith("#") and line.strip()
    ]

    process_map_title = _parse_title(lines)
    process_map_width = int(_parse_width(lines))

    if not lines:
        raise ValueError(
            "No business process definition found. Please add pool(s), lane(s) and element(s)."
        )

    colour_theme = _parse_colour_theme(lines)

    colour_theme_code = f', colour_theme="{colour_theme}"'
    process_map_width_code = f", width={process_map_width}"
    file_extension = png_output_file.lower().split(".")[-1]

    if file_extension == "png":
        output_type_code = ", painter_type='PNG'"
    elif file_extension == "svg":
        output_type_code = ", painter_type='SVG'"
    else:
        # get png_output_file extension
        raise ValueError(f"Unsupported file type [{file_extension}]")

    code_lines = [
        "from processpiper import ProcessMap, EventType, ActivityType, GatewayType, TerminatorType",
        "from processpiper.coordinate import Side",
        f'with ProcessMap("{process_map_title}"{colour_theme_code if colour_theme is not None else ""}{output_type_code if output_type_code is not None else ""}{process_map_width_code if process_map_width > 0 else ""}) as my_process_map:',
    ]

    indent = ""
    pool_id = 1
    lane_id = 0
    pool_found = False
    defined_elements = set()
    while lines:
        line = lines.pop(0).strip()
        if line.startswith("pool:"):
            pool_found, pool_id = _parse_pool(code_lines, pool_id, line)

        elif line.startswith("lane:"):
            indent, lane_id = _parse_lane(
                code_lines, pool_id, lane_id, pool_found, line
            )
            # _parse_element(lines, code_lines, indent, lane_id)
            _parse_element(lines, code_lines, indent, lane_id, defined_elements)

    # _parse_connection(input_str, code_lines)
    _parse_connection(input_str, code_lines, defined_elements)

    footer = input_str.strip().split("\n")[-1].split("footer:")
    indent = " " * 4
    if len(footer) > 1:
        code_lines.append(f'{indent}my_process_map.set_footer("{footer[1]}")')

    code_lines.append(f"{indent}my_process_map.draw()")
    code_lines.append(f'{indent}my_process_map.save("{png_output_file}")')
    bpmn_output_file = png_output_file.replace(".png", ".bpmn").replace(".svg", ".bpmn")
    drawio_output_file = png_output_file.replace(".png", ".drawio").replace(".svg", ".drawio")
    if export_to_bpmn:
        code_lines.append(
            f'{indent}my_process_map.export_to_bpmn("{bpmn_output_file}")'
        )
    if export_to_drawio:
        code_lines.append(
            f'{indent}my_process_map.export_to_drawio("{drawio_output_file}")'
        )

    return "\n".join(code_lines)


# def _parse_element(lines, code_lines, indent, lane_id):
def _parse_element(lines, code_lines, indent, lane_id, defined_elements=None):
    """
    This function parses an element from a list of lines and adds it to a code block with the
    appropriate indentation.
    """
    if defined_elements is None:
        defined_elements = set()
    while (
        lines
        and not lines[0].strip().startswith("lane:")
        and not lines[0].strip().startswith("pool:")
        and not lines[0].strip().startswith("footer:")
        and not lines[0].strip().startswith("#")
        and lines[0].strip() != ""
    ):
        lane_element = lines.pop(0).strip()
        # check if lane_element contained '->' characters
        if lane_element.find("->") > 0:
            # push lane_element back to lines
            lines.insert(0, lane_element)
            break
        element_type, element_name, element_var = _parse_lane_element(lane_element)
        code_lines.append(
            f'{indent}{element_var} = lane{lane_id}.add_element("{element_name}", {element_type})'
        )
        
        # Check for diamond attachments
        # Format: [element] as element_var with diamonds: d1, d2, ...
        if " with diamonds: " in lane_element:
            diamonds_part = lane_element.split(" with diamonds: ")[1].strip()
            diamonds = [d.strip() for d in diamonds_part.split(",")]
            if diamonds:
                diamond_list = ", ".join([f'"{d}"' for d in diamonds])
                code_lines.append(f'{indent}{element_var}.attach = [{diamond_list}]')
        
        defined_elements.add(element_var)


def _parse_lane(code_lines, pool_id, lane_id, pool_found, line):
    """
    The function parses a lane from a code line and adds it to a process map.
    """
    lane_name = line.split(":")[1].strip()
    lane_id += 1
    if pool_found:
        indent = " " * 8
        code_lines.append(
            f'{indent}with pool{pool_id - 1}.add_lane("{lane_name}") as lane{lane_id}:'
        )
    else:
        indent = " " * 4
        code_lines.append(
            f'{indent}with my_process_map.add_lane("{lane_name}") as lane{lane_id}:'
        )

    indent += " " * 4
    return indent, lane_id


def _parse_pool(code_lines, pool_id, line):
    """
    This function parses a line of code to extract a pool name and adds it to a list of code lines with
    a specific format.
    """
    pool_name = line.split(":")[1].strip()
    indent = " " * 4
    code_lines.append(
        f'{indent}with my_process_map.add_pool("{pool_name}") as pool{pool_id}:'
    )
    pool_id += 1
    pool_found = True
    return pool_found, pool_id


# def _parse_connection(input_str, code_lines):
def _parse_connection(input_str, code_lines, defined_elements = None):
    """
    The function parses a string input containing connection information and generates code lines to
    establish those connections in Python.
    """
    if defined_elements is None:
        defined_elements = set()

    connections_list = [
        line.split("->") for line in input_str.strip().split("\n") if "->" in line
    ]

    for connection in connections_list:
        for i in range(len(connection) - 1):
            (
                element_name,
                label,
                source_source_side,
                source_target_side,
            ) = _get_element_name_and_label(connection[i].strip())
            (
                target_element_name,
                target_label,
                source_side,
                target_side,
            ) = _get_element_name_and_label(connection[i + 1].strip())

            # Skip connections that reference undefined elements
            if element_name not in defined_elements or target_element_name not in defined_elements:
                # Optional: Add debug logging for skipped connections
                import logging
                if element_name not in defined_elements:
                    logging.debug(f"Skipping connection: undefined source element '{element_name}'")
                if target_element_name not in defined_elements:
                    logging.debug(f"Skipping connection: undefined target element '{target_element_name}'")
                continue

            if target_label:
                if source_source_side is not None and source_target_side is not None:
                    code_lines.append(
                        " " * 8
                        + f"{element_name}.connect({target_element_name}, "
                        + f'"{target_label}", '
                        + f"source_connection_side=Side.{source_source_side.upper()}, "
                        + f"target_connection_side=Side.{source_target_side.upper()})"
                    )
                if source_source_side is not None and source_target_side is None:
                    code_lines.append(
                        " " * 8
                        + f"{element_name}.connect({target_element_name}, "
                        + f'"{target_label}", '
                        + f"source_connection_side=Side.{source_source_side.upper()})"
                    )
                if source_source_side is None and source_target_side is not None:
                    code_lines.append(
                        " " * 8
                        + f"{element_name}.connect({target_element_name}, "
                        + f'"{target_label}", '
                        + f"target_connection_side=Side.{source_target_side.upper()})"
                    )
                if source_source_side is None and source_target_side is None:
                    code_lines.append(
                        " " * 8
                        + f'{element_name}.connect({target_element_name}, "{target_label}")'
                    )
            else:
                if source_source_side is not None and source_target_side is not None:
                    code_lines.append(
                        " " * 8
                        + f"{element_name}.connect({target_element_name}, "
                        + f"source_connection_side=Side.{source_source_side.upper()}, "
                        + f"target_connection_side=Side.{source_target_side.upper()})"
                    )
                if source_source_side is not None and source_target_side is None:
                    code_lines.append(
                        " " * 8
                        + f"{element_name}.connect({target_element_name}, "
                        + f"source_connection_side=Side.{source_side.upper()})"
                    )
                if source_source_side is None and source_target_side is not None:
                    code_lines.append(
                        " " * 8
                        + f"{element_name}.connect({target_element_name}, "
                        + f"target_connection_side=Side.{source_target_side.upper()})"
                    )
                if source_source_side is None and source_target_side is None:
                    code_lines.append(
                        " " * 8 + f"{element_name}.connect({target_element_name})"
                    )


def _get_element_name_and_label(connection: str):
    """
    The function extracts the element name and label from a given connection string using regular
    expressions.
    """
    # -- Find the connection label
    pattern = r"(.*): (.*)"
    if result := re.search(pattern, connection):
        # -- Extract the element name and label
        return result[1], result[2], None, None

    # -- Find the connection source and target sides
    direction_pattern = r"(.*)-(?:\((.*?),(.*?)\))?"
    if direction_match := re.search(direction_pattern, connection):
        element_name = direction_match[1]
        source_side = direction_match[2]
        target_side = direction_match[3].strip()
        return element_name, None, source_side, target_side

    return connection.split(":")[0], None, None, None


def _parse_colour_theme(lines):
    """
    The function extracts the color theme from a list of lines if it exists.
    """
    return lines.pop(0).split(":")[1].strip() if "colourtheme" in lines[0] else None


def _parse_title(lines):
    """
    The function extracts the title from a list of lines if the first line contains the word "title".
    """
    if "title" in lines[0]:
        process_map_title = lines.pop(0).split(":")[1].strip()
    else:
        raise ValueError("The first line must contain the word 'title'.")
    return process_map_title


def _parse_width(lines):
    """
    The function extracts the title from a list of lines if the first line contains the word "title".
    """
    return lines.pop(0).split(":")[1].strip() if "width" in lines[0] else 0


def _parse_lane_element(element_str):
    """
    The function parses a string representing a BPMN element and returns its type, name, and variable
    name.
    """
    """Detect element type"""
    # Strip out any diamond attachments for parsing
    base_element_str = element_str
    if " with diamonds: " in element_str:
        base_element_str = element_str.split(" with diamonds: ")[0]
    
    # --EventType--
    if base_element_str.startswith("(start"):
        element_type = "EventType.START"
        element_name = base_element_str[1 : base_element_str.index(")")].strip()
    elif base_element_str.startswith("(end"):
        element_type = "EventType.END"
        element_name = base_element_str[1 : base_element_str.index(")")].strip()
    elif base_element_str.startswith("(@timer"):
        element_type = "EventType.TIMER"
        element_name = base_element_str[len("(@timer") : base_element_str.index(")")].strip()
    elif base_element_str.startswith("(@intermediate"):
        element_type = "EventType.INTERMEDIATE"
        element_name = base_element_str[
            len("(@intermediate") : base_element_str.index(")")
        ].strip()
    elif base_element_str.startswith("(@message"):
        element_type = "EventType.MESSAGE"
        element_name = base_element_str[len("(@message") : base_element_str.index(")")].strip()
    elif base_element_str.startswith("(@signal"):
        element_type = "EventType.SIGNAL"
        element_name = base_element_str[len("(@signal") : base_element_str.index(")")].strip()
    elif base_element_str.startswith("(@conditional"):
        element_type = "EventType.CONDITIONAL"
        element_name = base_element_str[
            len("(@conditional") : base_element_str.index(")")
        ].strip()
    elif base_element_str.startswith("(@link"):
        element_type = "EventType.LINK"
        element_name = base_element_str[len("(@link") : base_element_str.index(")")].strip()

    #  --ActivityType--
    elif base_element_str.startswith("[@subprocess"):
        element_type = "ActivityType.SUBPROCESS"
        element_name = base_element_str[len("[@subprocess") : base_element_str.index("]")].strip()
    elif base_element_str.startswith("["):
        element_type = "ActivityType.TASK"
        element_name = base_element_str[1 : base_element_str.index("]")].strip()

    #  --TerminatorType--
    elif base_element_str.startswith("{"):
        element_type = "TerminatorType.TERMINATOR"
        element_name = base_element_str[1: base_element_str.index("}")].strip()

    #  --GatewayType--
    elif base_element_str.startswith("<@parallel"):
        element_type = "GatewayType.PARALLEL"
        element_name = base_element_str[len("<@parallel") : base_element_str.index(">")].strip()
    elif base_element_str.startswith("<@inclusive"):
        element_type = "GatewayType.INCLUSIVE"
        element_name = base_element_str[len("<@exclusive") : base_element_str.index(">")].strip()
    elif base_element_str.startswith("<@exclusive"):
        element_type = "GatewayType.EXCLUSIVE"
        element_name = base_element_str[len("<@exclusive") : base_element_str.index(">")].strip()
    elif base_element_str.startswith("<"):
        element_type = "GatewayType.EXCLUSIVE"
        element_name = base_element_str[1 : base_element_str.index(">")].strip()
    elif base_element_str.startswith("(@event"):
        element_type = "GatewayType.EVENT"
        element_name = base_element_str[len("(@event") : base_element_str.index(")")].strip()

    else:
        raise ValueError(f"Invalid element string: {base_element_str}")

    print('>>>>>>:',base_element_str)
    element_var = base_element_str.split(" as ")[1].strip()

    return element_type, element_name, element_var


def _validate_generated_code(code: str):
    if "add_lane" not in code:
        raise ValueError("There is no lane defined. Please add lanes to process map.")

    # If a multiline code does not contain add_element, raise error
    if "add_element" not in code:
        raise ValueError("There is no element defined. Please add elements to lane.")


def _validate_connections(input_str: str, defined_elements: set):
    """Validate connections and report potential issues"""
    connections_list = [
        line.split("->") for line in input_str.strip().split("\n") if "->" in line
    ]


    issues = []
    for connection in connections_list:
        for i in range(len(connection) - 1):
            source_element = _get_element_name_and_label(connection[i].strip())[0]
            target_element = _get_element_name_and_label(connection[i + 1].strip())[0]


            if source_element not in defined_elements:
                issues.append(f"Source element '{source_element}' not defined")
            if target_element not in defined_elements:
                issues.append(f"Target element '{target_element}' not defined")


    return issues


def _analyze_connection_flow(input_str: str, defined_elements: set):
    """Analyze connection flow and suggest potential missing connections"""
    connections_list = [
        line.split("->") for line in input_str.strip().split("\n") if "->" in line
    ]


    connected_elements = set()
    connection_chains = []


    for connection in connections_list:
        chain = []
        for element in connection:
            element_name = _get_element_name_and_label(element.strip())[0]
            if element_name in defined_elements:
                chain.append(element_name)
                connected_elements.add(element_name)
        if chain:
            connection_chains.append(chain)


    # Find disconnected elements
    disconnected = defined_elements - connected_elements


    analysis = {
        'connection_chains': connection_chains,
        'connected_elements': connected_elements,
        'disconnected_elements': disconnected,
        'total_elements': len(defined_elements)
    }


    return analysis



def show_code_with_line_number(code: str):
    """
    The function takes a string of code and prints it with line numbers.
    """
    console = Console()
    console.print("Generated code: ")
    for i, line in enumerate(code.split("\n")):
        console.print(f"{i+1:3} {line}")


def render(
    text: str,
    output_file: str = "",
    show_code: bool = False,
    export_to_bpmn: bool = False,
    export_to_drawio: bool = False,
):
    """Render text to diagram"""
    output_file_provided = True
    if not output_file.strip():
        output_file_provided = False
        # Generate default output file name
        output_file = f"piper_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

    # check to make sure the output_file extension is either .png or .svg
    file_extension = output_file.lower().split(".")[-1]
    if output_file_provided and file_extension not in [
        "png",
        "svg",
    ]:
        raise ValueError("The output file extension must be either .png, .svg or .bpmn")

    generated_code = _parse_and_generate_code(text, output_file, export_to_bpmn, export_to_drawio)
    _validate_generated_code(generated_code)
    if show_code:
        show_code_with_line_number(generated_code)
    exec(generated_code)
    if file_extension == "svg":
        with open(output_file, "r") as f:
            generated_image = f.read()

    elif file_extension == "png":
        generated_image = Image.open(output_file)
        generated_image.load()

    # Clean up the generated image file
    if not output_file_provided:
        os.remove(output_file)

    return generated_code, generated_image
