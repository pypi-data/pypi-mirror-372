import os
import asyncio
import logging

from dotenv import load_dotenv
from autogen_core import TRACE_LOGGER_NAME
from autogen_ext.models.azure import AzureAIChatCompletionClient
from azure.core.credentials import AzureKeyCredential

from KCw_WebSurferAgent import KCWMultimodalWebSurfer
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.ui import Console
from autogen_agentchat.conditions import TextMentionTermination

load_dotenv()
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
credential = AzureKeyCredential(os.getenv("AZURE_OPENAI_KEY"))
username = os.getenv("USER_NAME")
password = os.getenv("USER_PASSWORD")

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(TRACE_LOGGER_NAME)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

# Termination: stop when planner says "TASK COMPLETE" or after 10 messages
termination = TextMentionTermination("[]")  # | MaxMessageTermination(6)


async def main():
    model_client = AzureAIChatCompletionClient(
        model="gpt4o",
        endpoint=endpoint,
        credential=credential,
        model_info={
            "json_output": False,
            "function_calling": True,
            "vision": True,
            "family": "gpt-4o",
            "structured_output": False,
        },
    )
    # Planner agent: plans browser actions step by step
    planner = AssistantAgent(
        name="Planner",
        model_client=model_client,
        # tools=TOOL_REGISTRY,
        system_message=(
            "You are a planning agent for browser automation. Your job is to break down high-level user goals "
            "into specific, low-level browser actions. You must plan one step at a time and wait for feedback before planning the next.\n\n"
            "Available tools for the WebSurfer:\n"
            "- visit_url\n"
            "- click\n"
            "- input_text\n"
            "- scroll_down, scroll_up\n"
            "- hover\n"
            "- sleep\n"
            "- web_search\n"
            "- answer_question\n"
            "- summarize_page\n"
            "- menu_tab(tab_name)\n"
            "- stacked_windows\n"
            "- history_back\n\n"
            "- upload_files(to, files)\n\n"
            "- fill_upload_grid_cell(column, value)\n"
            "Always assume you only control the *Planner*. The WebSurfer is a separate agent that only executes concrete instructions.\n"
            "Use a numbered step-by-step format. **ONE STEP AT A TIME**. Use only the available tools. Whenever the user wants to open or expand a section named X, call the specialized tool `X`. "
            "If you think we don't need to plan any more and all the steps of the goal are complete, you will simply return an empty list []."
        ),
    )

    # WebSurfer agent: executes browser actions
    websurfer = KCWMultimodalWebSurfer(
        name="WebSurfer",
        model_client=model_client,
        headless=True,
        to_save_screenshots=True,
        use_ocr=False,
        # test omgeving
        # start_page="https://kpmgclara.ema.kpmg.com/Workbench/Web/2024v3/#/Project/93915b65-26e1-ee11-85fb-6045bd941f67?isNavigatedFrom=1",
        start_page="https://kcw2.stg.ema.kpmg.com//ClaraPortal/#/en-US/contents/workflowEngagementDashboard/g/1",
        # start_page="https://kpmgclara.ema.kpmg.com/ClaraPortal/#/en-US/contents/workflowEngagementDashboard/g/1",
        debug_dir="/Users/richtervanemmerik/Documents/dani-agent/websurfer_images",
        user_name=username,
        password=password,
    )

    # Selector prompt for orchestrator logic
    selector_prompt = """Select the correct agent to perform the next browser automation step.

    {roles}

    Current context:
    {history}

    Guidelines:
    - The **Planner** always goes first and breaks down the goal into individual browser actions.
    - The **WebSurfer** only executes commands exactly as instructed and reports the result.
    - The Planner analyzes the result and plans the next step.
    - Always alternate between Planner → WebSurfer → Planner → ...
    - Do not allow agents to skip or do each other's roles.
    Only select ONE agent from {participants} for the next step.
    """

    team = SelectorGroupChat(
        [planner, websurfer],
        model_client=model_client,
        selector_prompt=selector_prompt,
        termination_condition=termination,
        allow_repeated_speaker=False,
    )

    USER_TASK = """
        You are an intelligent browser automation agent. You are currently on a KPMG Engagements page.
        Click on "KCw Upload Test", then click on the stacked windows icon to navigate to Project Plan on the menu tab.
        Click on the Business processes caret, then click on the Financial Reporting caret, then click on the open in new window icon next to Period End Close.
        Click on the grey section indicator. Then fill the rich text box with the text "I am an agent, I saved this 5.0" and click on Save.
        """
    # USER_TASK = """
    #     You are an intelligent browser automation agent. You are currently on a KPMG Engagements page.
    #     Click on "KCw Upload Test", then click on the stacked windows icon to navigate to Project Plan on the menu tab.
    #     Click on the Business processes caret, then click on the Financial Reporting caret, then click on the open in new window icon next to Period End Close.
    #     press on the 0+ icon in the side bar. Then press on Upload, then Upload the following files using the 'Select file(s)' button:
    #     /Users/richtervanemmerik/Desktop/Screenshot 2025-08-05 at 10.14.37.png. Change the Ref No in the gridcell to 3.0046 and add a description in the Description gridcell of "I am an agent who uploaded this file". After upload, wait for the files to appear in the table of uploaded documents, then stop.
    #     """
    stream = team.run_stream(task=USER_TASK)
    await Console(stream)

    await websurfer.close()


if __name__ == "__main__":
    asyncio.run(main())
