# MIT License

# Copyright (c) 2022 CS Goh

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from dataclasses import dataclass


DEFAULT_FONT = "Arial"
DEFAULT_TITLE_FONT_SIZE = 26
DEFAULT_POOL_FONT_SIZE = 18
DEFAULT_LANE_FONT_SIZE = 18
# DEFAULT_ELEMENT_FONT_SIZE = 14
DEFAULT_ELEMENT_FONT_SIZE = 15
# DEFAULT_CONNECTOR_FONT_SIZE = 14
DEFAULT_CONNECTOR_FONT_SIZE = 15
# DEFAULT_CONNECTOR_ARROW_SIZE = 15
DEFAULT_CONNECTOR_ARROW_SIZE = 13
DEFAULT_FOOTER_FONT_SIZE = 18
DEFAULT_OUTLINE_COLOUR = "black"
DEFAULT_OUTLINE_WIDTH = 1

default_colour_settings = {
    "theme": "DEFAULT",
    "settings": {
        "background": {
            "background_fill_colour": "white",
        },
        "title": {
            "title_font": DEFAULT_FONT,
            "title_font_size": DEFAULT_TITLE_FONT_SIZE,
            "title_font_colour": "black",
        },
        "pool": {
            "pool_font": DEFAULT_FONT,
            "pool_font_size": DEFAULT_POOL_FONT_SIZE,
            "pool_font_colour": "white",
            "pool_fill_colour": "#1F1F1F",
            "pool_text_alignment": "centre",
        },
        "lane": {
            "lane_font": DEFAULT_FONT,
            "lane_font_size": DEFAULT_LANE_FONT_SIZE,
            "lane_font_colour": "white",
            "lane_fill_colour": "#474747",
            "lane_text_alignment": "centre",
            "lane_background_fill_colour": "#D9D9D9",
        },
        "element": {
            "element_font": DEFAULT_FONT,
            "element_font_size": DEFAULT_ELEMENT_FONT_SIZE,
            "element_font_colour": "black",
            "element_fill_colour": "darkgrey",
            "element_outline_colour": DEFAULT_OUTLINE_COLOUR,
            "element_outline_width": DEFAULT_OUTLINE_WIDTH,
            "element_text_alignment": "centre",
        },
        "connector": {
            "connector_font": DEFAULT_FONT,
            "connector_font_size": DEFAULT_CONNECTOR_FONT_SIZE,
            "connector_font_colour": "#000000",
            "connector_line_width": 1,
            "connector_line_colour": "#000000",
            "connector_arrow_colour": "#000000",
            "connector_arrow_size": DEFAULT_CONNECTOR_ARROW_SIZE,
        },
        "footer": {
            "footer_font": DEFAULT_FONT,
            "footer_font_size": DEFAULT_FOOTER_FONT_SIZE,
            "footer_font_colour": "#000000",
        },
    },
}

greywoof_colour_settings = {
    "theme": "GREYWOOF",
    "settings": {
        "background": {
            "background_fill_colour": "white",
        },
        "title": {
            "title_font": DEFAULT_FONT,
            "title_font_size": DEFAULT_TITLE_FONT_SIZE,
            "title_font_colour": "#666666",
        },
        "pool": {
            "pool_font": DEFAULT_FONT,
            "pool_font_size": DEFAULT_POOL_FONT_SIZE,
            "pool_font_colour": "white",
            "pool_fill_colour": "#666666",
            "pool_text_alignment": "centre",
        },
        "lane": {
            "lane_font": DEFAULT_FONT,
            "lane_font_size": DEFAULT_LANE_FONT_SIZE,
            "lane_font_colour": "white",
            "lane_fill_colour": "#666666",
            "lane_text_alignment": "centre",
            "lane_background_fill_colour": "#D9D9D9",
        },
        "element": {
            "element_font": DEFAULT_FONT,
            "element_font_size": DEFAULT_ELEMENT_FONT_SIZE,
            "element_font_colour": "black",
            "element_fill_colour": "#A9A9A9",
            "element_outline_colour": DEFAULT_OUTLINE_COLOUR,
            "element_outline_width": DEFAULT_OUTLINE_WIDTH,
            "element_text_alignment": "centre",
        },
        "connector": {
            "connector_font": DEFAULT_FONT,
            "connector_font_size": DEFAULT_CONNECTOR_FONT_SIZE,
            "connector_font_colour": "#000000",
            "connector_line_width": 1,
            "connector_line_colour": "#000000",
            "connector_arrow_colour": "#000000",
            "connector_arrow_size": DEFAULT_CONNECTOR_ARROW_SIZE,
        },
        "footer": {
            "footer_font": DEFAULT_FONT,
            "footer_font_size": DEFAULT_FOOTER_FONT_SIZE,
            "footer_font_colour": "#666666",
        },
    },
}

bluemountain_colour_settings = {
    "theme": "BLUEMOUNTAIN",
    "settings": {
        "background": {
            "background_fill_colour": "white",
        },
        "title": {
            "title_font": DEFAULT_FONT,
            "title_font_size": DEFAULT_TITLE_FONT_SIZE,
            "title_font_colour": "#0B5394",
        },
        "pool": {
            "pool_font": DEFAULT_FONT,
            "pool_font_size": DEFAULT_POOL_FONT_SIZE,
            "pool_font_colour": "white",
            "pool_fill_colour": "#0B5394",
            "pool_text_alignment": "centre",
        },
        "lane": {
            "lane_font": DEFAULT_FONT,
            "lane_font_size": DEFAULT_LANE_FONT_SIZE,
            "lane_font_colour": "white",
            "lane_fill_colour": "#0B5394",
            "lane_text_alignment": "centre",
            "lane_background_fill_colour": "#D9D9D9",
        },
        "element": {
            "element_font": DEFAULT_FONT,
            "element_font_size": DEFAULT_ELEMENT_FONT_SIZE,
            "element_font_colour": "black",
            "element_fill_colour": "#9FC5E8",
            "element_outline_colour": DEFAULT_OUTLINE_COLOUR,
            "element_outline_width": DEFAULT_OUTLINE_WIDTH,
            "element_text_alignment": "centre",
        },
        "connector": {
            "connector_font": DEFAULT_FONT,
            "connector_font_size": DEFAULT_CONNECTOR_FONT_SIZE,
            "connector_font_colour": "#000000",
            "connector_line_width": 1,
            "connector_line_colour": "#000000",
            "connector_arrow_colour": "#000000",
            "connector_arrow_size": DEFAULT_CONNECTOR_ARROW_SIZE,
        },
        "footer": {
            "footer_font": DEFAULT_FONT,
            "footer_font_size": DEFAULT_FOOTER_FONT_SIZE,
            "footer_font_colour": "#0B5394",
        },
    },
}

orangepeel_colour_settings = {
    "theme": "ORANGEPEEL",
    "settings": {
        "background": {
            "background_fill_colour": "white",
        },
        "title": {
            "title_font": DEFAULT_FONT,
            "title_font_size": DEFAULT_TITLE_FONT_SIZE,
            "title_font_colour": "#B45F06",
        },
        "pool": {
            "pool_font": DEFAULT_FONT,
            "pool_font_size": DEFAULT_POOL_FONT_SIZE,
            "pool_font_colour": "white",
            "pool_fill_colour": "#B45F06",
            "pool_text_alignment": "centre",
        },
        "lane": {
            "lane_font": DEFAULT_FONT,
            "lane_font_size": DEFAULT_LANE_FONT_SIZE,
            "lane_font_colour": "white",
            "lane_fill_colour": "#B45F06",
            "lane_text_alignment": "centre",
            "lane_background_fill_colour": "#D9D9D9",
        },
        "element": {
            "element_font": DEFAULT_FONT,
            "element_font_size": DEFAULT_ELEMENT_FONT_SIZE,
            "element_font_colour": "black",
            "element_fill_colour": "#F6B26B",
            "element_outline_colour": DEFAULT_OUTLINE_COLOUR,
            "element_outline_width": DEFAULT_OUTLINE_WIDTH,
            "element_text_alignment": "centre",
        },
        "connector": {
            "connector_font": DEFAULT_FONT,
            "connector_font_size": DEFAULT_CONNECTOR_FONT_SIZE,
            "connector_font_colour": "#000000",
            "connector_line_width": 1,
            "connector_line_colour": "#000000",
            "connector_arrow_colour": "#000000",
            "connector_arrow_size": DEFAULT_CONNECTOR_ARROW_SIZE,
        },
        "footer": {
            "footer_font": DEFAULT_FONT,
            "footer_font_size": DEFAULT_FOOTER_FONT_SIZE,
            "footer_font_colour": "#B45F06",
        },
    },
}

greenturtle_colour_settings = {
    "theme": "GREENTURTLE",
    "settings": {
        "background": {
            "background_fill_colour": "white",
        },
        "title": {
            "title_font": DEFAULT_FONT,
            "title_font_size": DEFAULT_TITLE_FONT_SIZE,
            "title_font_colour": "#38761D",
        },
        "pool": {
            "pool_font": DEFAULT_FONT,
            "pool_font_size": DEFAULT_POOL_FONT_SIZE,
            "pool_font_colour": "white",
            "pool_fill_colour": "#38761D",
            "pool_text_alignment": "centre",
        },
        "lane": {
            "lane_font": DEFAULT_FONT,
            "lane_font_size": DEFAULT_LANE_FONT_SIZE,
            "lane_font_colour": "white",
            "lane_fill_colour": "#38761D",
            "lane_text_alignment": "centre",
            "lane_background_fill_colour": "#D9D9D9",
        },
        "element": {
            "element_font": DEFAULT_FONT,
            "element_font_size": DEFAULT_ELEMENT_FONT_SIZE,
            "element_font_colour": "black",
            "element_fill_colour": "#93C47D",
            "element_outline_colour": DEFAULT_OUTLINE_COLOUR,
            "element_outline_width": DEFAULT_OUTLINE_WIDTH,
            "element_text_alignment": "centre",
        },
        "connector": {
            "connector_font": DEFAULT_FONT,
            "connector_font_size": DEFAULT_CONNECTOR_FONT_SIZE,
            "connector_font_colour": "#000000",
            "connector_line_width": 1,
            "connector_line_colour": "#000000",
            "connector_arrow_colour": "#000000",
            "connector_arrow_size": DEFAULT_CONNECTOR_ARROW_SIZE,
        },
        "footer": {
            "footer_font": DEFAULT_FONT,
            "footer_font_size": DEFAULT_FOOTER_FONT_SIZE,
            "footer_font_colour": "#38761D",
        },
    },
}

sunflower_colour_settings = {
    "theme": "SUNFLOWER",
    "settings": {
        "background": {
            "background_fill_colour": "white",
        },
        "title": {
            "title_font": DEFAULT_FONT,
            "title_font_size": DEFAULT_TITLE_FONT_SIZE,
            "title_font_colour": "#FFC300",
        },
        "pool": {
            "pool_font": DEFAULT_FONT,
            "pool_font_size": DEFAULT_POOL_FONT_SIZE,
            "pool_font_colour": "black",
            "pool_fill_colour": "#FFC300",
            "pool_text_alignment": "centre",
        },
        "lane": {
            "lane_font": DEFAULT_FONT,
            "lane_font_size": DEFAULT_LANE_FONT_SIZE,
            "lane_font_colour": "white",
            "lane_fill_colour": "#38761D",
            "lane_text_alignment": "centre",
            "lane_background_fill_colour": "#D9D9D9",
        },
        "element": {
            "element_font": DEFAULT_FONT,
            "element_font_size": DEFAULT_ELEMENT_FONT_SIZE,
            "element_font_colour": "black",
            "element_fill_colour": "#FFF68F",
            "element_outline_colour": DEFAULT_OUTLINE_COLOUR,
            "element_outline_width": DEFAULT_OUTLINE_WIDTH,
            "element_text_alignment": "centre",
        },
        "connector": {
            "connector_font": DEFAULT_FONT,
            "connector_font_size": DEFAULT_CONNECTOR_FONT_SIZE,
            "connector_font_colour": "#000000",
            "connector_line_width": 1,
            "connector_line_colour": "#000000",
            "connector_arrow_colour": "#000000",
            "connector_arrow_size": DEFAULT_CONNECTOR_ARROW_SIZE,
        },
        "footer": {
            "footer_font": DEFAULT_FONT,
            "footer_font_size": DEFAULT_FOOTER_FONT_SIZE,
            "footer_font_colour": "#FFC300",
        },
    },
}

purplerain_colour_settings = {
    "theme": "PURPLERAIN",
    "settings": {
        "background": {
            "background_fill_colour": "white",
        },
        "title": {
            "title_font": DEFAULT_FONT,
            "title_font_size": DEFAULT_TITLE_FONT_SIZE,
            "title_font_colour": "#660099",
        },
        "pool": {
            "pool_font": DEFAULT_FONT,
            "pool_font_size": DEFAULT_POOL_FONT_SIZE,
            "pool_font_colour": "white",
            "pool_fill_colour": "#660099",
            "pool_text_alignment": "centre",
        },
        "lane": {
            "lane_font": DEFAULT_FONT,
            "lane_font_size": DEFAULT_LANE_FONT_SIZE,
            "lane_font_colour": "white",
            "lane_fill_colour": "#660099",
            "lane_text_alignment": "centre",
            "lane_background_fill_colour": "#D9D9D9",
        },
        "element": {
            "element_font": DEFAULT_FONT,
            "element_font_size": DEFAULT_ELEMENT_FONT_SIZE,
            "element_font_colour": "black",
            "element_fill_colour": "#B19CD9",
            "element_outline_colour": DEFAULT_OUTLINE_COLOUR,
            "element_outline_width": DEFAULT_OUTLINE_WIDTH,
            "element_text_alignment": "centre",
        },
        "connector": {
            "connector_font": DEFAULT_FONT,
            "connector_font_size": DEFAULT_CONNECTOR_FONT_SIZE,
            "connector_font_colour": "#000000",
            "connector_line_width": 1,
            "connector_line_colour": "#000000",
            "connector_arrow_colour": "#000000",
            "connector_arrow_size": DEFAULT_CONNECTOR_ARROW_SIZE,
        },
        "footer": {
            "footer_font": DEFAULT_FONT,
            "footer_font_size": DEFAULT_FOOTER_FONT_SIZE,
            "footer_font_colour": "#660099",
        },
    },
}

rubyred_colour_settings = {
    "theme": "RUBYRED",
    "settings": {
        "background": {
            "background_fill_colour": "white",
        },
        "title": {
            "title_font": DEFAULT_FONT,
            "title_font_size": DEFAULT_TITLE_FONT_SIZE,
            "title_font_colour": "#FF005F",
        },
        "pool": {
            "pool_font": DEFAULT_FONT,
            "pool_font_size": DEFAULT_POOL_FONT_SIZE,
            "pool_font_colour": "white",
            "pool_fill_colour": "#FF005F",
            "pool_text_alignment": "centre",
        },
        "lane": {
            "lane_font": DEFAULT_FONT,
            "lane_font_size": DEFAULT_LANE_FONT_SIZE,
            "lane_font_colour": "white",
            "lane_fill_colour": "#FF005F",
            "lane_text_alignment": "centre",
            "lane_background_fill_colour": "#D9D9D9",
        },
        "element": {
            "element_font": DEFAULT_FONT,
            "element_font_size": DEFAULT_ELEMENT_FONT_SIZE,
            "element_font_colour": "black",
            "element_fill_colour": "#FF869A",
            "element_outline_colour": DEFAULT_OUTLINE_COLOUR,
            "element_outline_width": DEFAULT_OUTLINE_WIDTH,
            "element_text_alignment": "centre",
        },
        "connector": {
            "connector_font": DEFAULT_FONT,
            "connector_font_size": DEFAULT_CONNECTOR_FONT_SIZE,
            "connector_font_colour": "#000000",
            "connector_line_width": 1,
            "connector_line_colour": "#000000",
            "connector_arrow_colour": "#000000",
            "connector_arrow_size": DEFAULT_CONNECTOR_ARROW_SIZE,
        },
        "footer": {
            "footer_font": DEFAULT_FONT,
            "footer_font_size": DEFAULT_FOOTER_FONT_SIZE,
            "footer_font_colour": "#FF005F",
        },
    },
}

teal_waters_colour_settings = {
    "theme": "TEALWATERS",
    "settings": {
        "background": {
            "background_fill_colour": "white",
        },
        "title": {
            "title_font": DEFAULT_FONT,
            "title_font_size": DEFAULT_TITLE_FONT_SIZE,
            "title_font_colour": "#008B8B",
        },
        "pool": {
            "pool_font": DEFAULT_FONT,
            "pool_font_size": DEFAULT_POOL_FONT_SIZE,
            "pool_font_colour": "white",
            "pool_fill_colour": "#008B8B",
            "pool_text_alignment": "centre",
        },
        "lane": {
            "lane_font": DEFAULT_FONT,
            "lane_font_size": DEFAULT_LANE_FONT_SIZE,
            "lane_font_colour": "white",
            "lane_fill_colour": "#008B8B",
            "lane_text_alignment": "centre",
            "lane_background_fill_colour": "#D9D9D9",
        },
        "element": {
            "element_font": DEFAULT_FONT,
            "element_font_size": DEFAULT_ELEMENT_FONT_SIZE,
            "element_font_colour": "black",
            "element_fill_colour": "#00CCCC",
            "element_outline_colour": DEFAULT_OUTLINE_COLOUR,
            "element_outline_width": DEFAULT_OUTLINE_WIDTH,
            "element_text_alignment": "centre",
        },
        "connector": {
            "connector_font": DEFAULT_FONT,
            "connector_font_size": DEFAULT_CONNECTOR_FONT_SIZE,
            "connector_font_colour": "#000000",
            "connector_line_width": 1,
            "connector_line_colour": "#000000",
            "connector_arrow_colour": "#000000",
            "connector_arrow_size": DEFAULT_CONNECTOR_ARROW_SIZE,
        },
        "footer": {
            "footer_font": DEFAULT_FONT,
            "footer_font_size": DEFAULT_FOOTER_FONT_SIZE,
            "footer_font_colour": "#008B8B",
        },
    },
}

seafoam_colour_settings = {
    "theme": "SEAFOAMS",
    "settings": {
        "background": {
            "background_fill_colour": "white",
        },
        "title": {
            "title_font": DEFAULT_FONT,
            "title_font_size": DEFAULT_TITLE_FONT_SIZE,
            "title_font_colour": "#3F889F",
        },
        "pool": {
            "pool_font": DEFAULT_FONT,
            "pool_font_size": DEFAULT_POOL_FONT_SIZE,
            "pool_font_colour": "white",
            "pool_fill_colour": "#3F889F",
            "pool_text_alignment": "centre",
        },
        "lane": {
            "lane_font": DEFAULT_FONT,
            "lane_font_size": DEFAULT_LANE_FONT_SIZE,
            "lane_font_colour": "white",
            "lane_fill_colour": "#3F889F",
            "lane_text_alignment": "centre",
            "lane_background_fill_colour": "#D9D9D9",
        },
        "element": {
            "element_font": DEFAULT_FONT,
            "element_font_size": DEFAULT_ELEMENT_FONT_SIZE,
            "element_font_colour": "black",
            "element_fill_colour": "#80CBC4",
            "element_outline_colour": DEFAULT_OUTLINE_COLOUR,
            "element_outline_width": DEFAULT_OUTLINE_WIDTH,
            "element_text_alignment": "centre",
        },
        "connector": {
            "connector_font": DEFAULT_FONT,
            "connector_font_size": DEFAULT_CONNECTOR_FONT_SIZE,
            "connector_font_colour": "#000000",
            "connector_line_width": 1,
            "connector_line_colour": "#000000",
            "connector_arrow_colour": "#000000",
            "connector_arrow_size": DEFAULT_CONNECTOR_ARROW_SIZE,
        },
        "footer": {
            "footer_font": DEFAULT_FONT,
            "footer_font_size": DEFAULT_FOOTER_FONT_SIZE,
            "footer_font_colour": "#3F889F",
        },
    },
}

ColourThemesSettings = [
    default_colour_settings,
    greywoof_colour_settings,
    bluemountain_colour_settings,
    orangepeel_colour_settings,
    greenturtle_colour_settings,
    sunflower_colour_settings,
    purplerain_colour_settings,
    rubyred_colour_settings,
    teal_waters_colour_settings,
    seafoam_colour_settings,
    ### Add more themes here
]


@dataclass
class ColourTheme:
    """Colour theme for the ProcessPiper."""

    def __init__(self, colour_theme_name: str) -> None:
        # sourcery skip: simplify-boolean-comparison, use-any
        """Initialise the colour theme."""

        found = False
        for theme in ColourThemesSettings:
            if theme["theme"] == colour_theme_name:
                found = True

        if found is False:
            raise ValueError(f"Colour theme {colour_theme_name} not recognised.")

        self._colour_theme_name = colour_theme_name

    def get_colour_theme_settings(self, processmap_component: str) -> tuple:
        """Get the colour theme settings for the specified roadmap component."""

        colour_settings = None

        for value in ColourThemesSettings:
            if value["theme"] == self._colour_theme_name:
                colour_settings = value["settings"]
                break

        ### get the colour scheme for the specified roadmap component
        ### values() returns a list of dictionaries, convert it to tuple. e.g. {1, 2} -> (1, 2)
        return tuple(colour_settings[processmap_component].values())
