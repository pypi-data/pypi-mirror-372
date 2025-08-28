from typing import Any, Dict

from autogen_core.tools._base import ParametersSchema, ToolSchema


def _load_tool(tooldef: Dict[str, Any]) -> ToolSchema:
    return ToolSchema(
        name=tooldef["function"]["name"],
        description=tooldef["function"]["description"],
        parameters=ParametersSchema(
            type="object",
            properties=tooldef["function"]["parameters"]["properties"],
            required=tooldef["function"]["parameters"]["required"],
        ),
    )


REASONING_TOOL_PROMPT = "A short description of the action to be performed and reason for doing so, do not mention the user."


# Base tools from the official agent, replicated here to keep KCW agent self-contained
TOOL_VISIT_URL: ToolSchema = _load_tool(
    {
        "type": "function",
        "function": {
            "name": "visit_url",
            "description": "Navigate directly to a provided URL using the browser's address bar. Prefer this tool over other navigation techniques in cases where the user provides a fully-qualified URL (e.g., choose it over clicking links, or inputing queries into search boxes).",
            "parameters": {
                "type": "object",
                "properties": {
                    "reasoning": {
                        "type": "string",
                        "description": REASONING_TOOL_PROMPT,
                    },
                    "url": {
                        "type": "string",
                        "description": "The URL to visit in the browser.",
                    },
                },
                "required": ["reasoning", "url"],
            },
        },
    }
)

TOOL_WEB_SEARCH: ToolSchema = _load_tool(
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Performs a web search on Bing.com with the given query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reasoning": {
                        "type": "string",
                        "description": REASONING_TOOL_PROMPT,
                    },
                    "query": {
                        "type": "string",
                        "description": "The web search query to use.",
                    },
                },
                "required": ["reasoning", "query"],
            },
        },
    }
)

TOOL_HISTORY_BACK: ToolSchema = _load_tool(
    {
        "type": "function",
        "function": {
            "name": "history_back",
            "description": "Navigates back one page in the browser's history. This is equivalent to clicking the browser back button.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reasoning": {
                        "type": "string",
                        "description": REASONING_TOOL_PROMPT,
                    }
                },
                "required": ["reasoning"],
            },
        },
    }
)

TOOL_SCROLL_UP: ToolSchema = _load_tool(
    {
        "type": "function",
        "function": {
            "name": "scroll_up",
            "description": "Scrolls the entire browser viewport one page UP towards the beginning.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reasoning": {
                        "type": "string",
                        "description": REASONING_TOOL_PROMPT,
                    }
                },
                "required": ["reasoning"],
            },
        },
    }
)

TOOL_SCROLL_DOWN: ToolSchema = _load_tool(
    {
        "type": "function",
        "function": {
            "name": "scroll_down",
            "description": "Scrolls the entire browser viewport one page DOWN towards the end.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reasoning": {
                        "type": "string",
                        "description": REASONING_TOOL_PROMPT,
                    }
                },
                "required": ["reasoning"],
            },
        },
    }
)

TOOL_CLICK: ToolSchema = _load_tool(
    {
        "type": "function",
        "function": {
            "name": "click",
            "description": "Clicks the mouse on the target with the given id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reasoning": {
                        "type": "string",
                        "description": REASONING_TOOL_PROMPT,
                    },
                    "target_id": {
                        "type": "integer",
                        "description": "The numeric id of the target to click.",
                    },
                },
                "required": ["reasoning", "target_id"],
            },
        },
    }
)

TOOL_TYPE: ToolSchema = _load_tool(
    {
        "type": "function",
        "function": {
            "name": "input_text",
            "description": "Types the given text value into the specified field.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reasoning": {
                        "type": "string",
                        "description": REASONING_TOOL_PROMPT,
                    },
                    "input_field_id": {
                        "type": "integer",
                        "description": "The numeric id of the input field to receive the text.",
                    },
                    "text_value": {
                        "type": "string",
                        "description": "The text to type into the input field.",
                    },
                },
                "required": ["reasoning", "input_field_id", "text_value"],
            },
        },
    }
)

TOOL_SCROLL_ELEMENT_DOWN: ToolSchema = _load_tool(
    {
        "type": "function",
        "function": {
            "name": "scroll_element_down",
            "description": "Scrolls a given html element (e.g., a div or a menu) DOWN.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reasoning": {
                        "type": "string",
                        "description": REASONING_TOOL_PROMPT,
                    },
                    "target_id": {
                        "type": "integer",
                        "description": "The numeric id of the target to scroll down.",
                    },
                },
                "required": ["reasoning", "target_id"],
            },
        },
    }
)

TOOL_SCROLL_ELEMENT_UP: ToolSchema = _load_tool(
    {
        "type": "function",
        "function": {
            "name": "scroll_element_up",
            "description": "Scrolls a given html element (e.g., a div or a menu) UP.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reasoning": {
                        "type": "string",
                        "description": REASONING_TOOL_PROMPT,
                    },
                    "target_id": {
                        "type": "integer",
                        "description": "The numeric id of the target to scroll UP.",
                    },
                },
                "required": ["reasoning", "target_id"],
            },
        },
    }
)

TOOL_HOVER: ToolSchema = _load_tool(
    {
        "type": "function",
        "function": {
            "name": "hover",
            "description": "Hovers the mouse over the target with the given id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reasoning": {
                        "type": "string",
                        "description": REASONING_TOOL_PROMPT,
                    },
                    "target_id": {
                        "type": "integer",
                        "description": "The numeric id of the target to hover over.",
                    },
                },
                "required": ["reasoning", "target_id"],
            },
        },
    }
)

TOOL_READ_PAGE_AND_ANSWER: ToolSchema = _load_tool(
    {
        "type": "function",
        "function": {
            "name": "answer_question",
            "description": "Uses AI to answer a question about the current webpage's content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reasoning": {
                        "type": "string",
                        "description": REASONING_TOOL_PROMPT,
                    },
                    "question": {
                        "type": "string",
                        "description": "The question to answer.",
                    },
                },
                "required": ["reasoning", "question"],
            },
        },
    }
)

TOOL_SUMMARIZE_PAGE: ToolSchema = _load_tool(
    {
        "type": "function",
        "function": {
            "name": "summarize_page",
            "description": "Uses AI to summarize the entire page.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reasoning": {
                        "type": "string",
                        "description": REASONING_TOOL_PROMPT,
                    }
                },
                "required": ["reasoning"],
            },
        },
    }
)

TOOL_SLEEP: ToolSchema = _load_tool(
    {
        "type": "function",
        "function": {
            "name": "sleep",
            "description": "Wait a short period of time. Call this function if the page has not yet fully loaded, or if it is determined that a small delay would increase the task's chances of success.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reasoning": {
                        "type": "string",
                        "description": REASONING_TOOL_PROMPT,
                    }
                },
                "required": ["reasoning"],
            },
        },
    }
)


# KCW-specific tools
TOOL_CLICK_MENU_TAB: ToolSchema = _load_tool(
    {
        "type": "function",
        "function": {
            "name": "menu_tab",
            "description": "Click the specified menu tab on the Engagement page. Use this tool when you need to open or interact with a specific menu tab on the Engagement page.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reasoning": {
                        "type": "string",
                        "description": REASONING_TOOL_PROMPT,
                    },
                    "tab_name": {
                        "type": "string",
                        "description": "The name of the menu tab to click.",
                    },
                },
                "required": ["reasoning", "tab_name"],
            },
        },
    }
)

TOOL_CLICK_STACKED_WINDOWS: ToolSchema = _load_tool(
    {
        "type": "function",
        "function": {
            "name": "stacked_windows",
            "description": "Open or expand the 'Stacked Windows' hamburger menu on the current page. Use this tool when you need to open or interact with the Stacked Windows section of an engagement.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reasoning": {
                        "type": "string",
                        "description": REASONING_TOOL_PROMPT,
                    }
                },
                "required": ["reasoning"],
            },
        },
    }
)

TOOL_UPLOAD_FILES: ToolSchema = _load_tool(
    {
        "type": "function",
        "function": {
            "name": "upload_files",
            "description": "Uploads one or more files by either clicking a control that opens the file chooser or by setting files directly on an input[type=file]. Provide absolute paths when possible.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reasoning": {
                        "type": "string",
                        "description": REASONING_TOOL_PROMPT,
                    },
                    "files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of file paths to upload.",
                    },
                },
                "required": ["reasoning", "files"],
            },
        },
    }
)

TOOL_FILL_UPLOAD_GRID_CELL: ToolSchema = _load_tool(
    {
        "type": "function",
        "function": {
            "name": "fill_upload_grid_cell",
            "description": "Edit a cell in the upload grid by specifying the column header and value. Prefer providing row_text when multiple rows exist.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reasoning": {
                        "type": "string",
                        "description": REASONING_TOOL_PROMPT,
                    },
                    "column": {
                        "type": "string",
                        "description": "Column header, e.g., 'Description' or 'Ref No'.",
                    },
                    "value": {"type": "string"},
                },
                "required": ["reasoning", "column", "value"],
            },
        },
    }
)


__all__ = [
    "TOOL_VISIT_URL",
    "TOOL_WEB_SEARCH",
    "TOOL_HISTORY_BACK",
    "TOOL_SCROLL_UP",
    "TOOL_SCROLL_DOWN",
    "TOOL_CLICK",
    "TOOL_TYPE",
    "TOOL_SCROLL_ELEMENT_DOWN",
    "TOOL_SCROLL_ELEMENT_UP",
    "TOOL_HOVER",
    "TOOL_READ_PAGE_AND_ANSWER",
    "TOOL_SUMMARIZE_PAGE",
    "TOOL_SLEEP",
    # KCW-specific
    "TOOL_CLICK_MENU_TAB",
    "TOOL_CLICK_STACKED_WINDOWS",
    "TOOL_UPLOAD_FILES",
    "TOOL_FILL_UPLOAD_GRID_CELL",
]
