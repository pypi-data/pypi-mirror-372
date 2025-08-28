import base64
import hashlib
import io
import json
import os
import re
import time
from typing import Dict, List, Optional

import aiofiles  # type: ignore[import-untyped]
import PIL.Image
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.utils import remove_images
from autogen_core import CancellationToken, FunctionCall
from autogen_core import Image as AGImage
from autogen_core.models import (
    ChatCompletionClient,
    LLMMessage,
    ModelFamily,
    UserMessage,
)
from playwright.async_api import BrowserContext, Playwright, async_playwright

# Import the official base agent
from autogen_ext.agents.web_surfer import MultimodalWebSurfer as BaseMultimodalWebSurfer

# Local helpers and extensions
from autogen_ext.agents.web_surfer._events import WebSurferEvent
from autogen_ext.agents.web_surfer._prompts import (
    WEB_SURFER_TOOL_PROMPT_MM,
    WEB_SURFER_TOOL_PROMPT_TEXT,
)
from autogen_ext.agents.web_surfer._set_of_mark import add_set_of_mark
from .kcw_tool_definitions import (
    TOOL_CLICK,
    TOOL_HISTORY_BACK,
    TOOL_HOVER,
    TOOL_READ_PAGE_AND_ANSWER,
    TOOL_SCROLL_DOWN,
    TOOL_SCROLL_UP,
    TOOL_SLEEP,
    TOOL_SUMMARIZE_PAGE,
    TOOL_TYPE,
    TOOL_VISIT_URL,
    TOOL_WEB_SEARCH,
    TOOL_CLICK_MENU_TAB,
    TOOL_CLICK_STACKED_WINDOWS,
    TOOL_UPLOAD_FILES,
    TOOL_FILL_UPLOAD_GRID_CELL,
)

from autogen_ext.agents.web_surfer._types import InteractiveRegion, UserContent
from .kcw_playwright_controller import KCWPlaywrightController
from typing import cast


DEFAULT_CONTEXT_SIZE = 128000


class KCWMultimodalWebSurfer(BaseMultimodalWebSurfer):
    """
    Specialized subclass of the official AutoGen MultimodalWebSurfer with
    KCW/KPMG Clara specific behaviors and tools.
    """

    # Override the default description with the KCW-focused one
    DEFAULT_DESCRIPTION = "\n".join(
        [
            "An intelligent browser automation agent specialized for the KPMG Clara Workflow Engagement site.",
            "This agent can navigate the engagement dashboard, interact with workflow elements, click buttons, fill in forms, and expand sections.",
            "It can perform targeted actions, summarize page content, answer questions based on the engagement data, and ensure accurate execution of complex workflows.",
            "Use this agent to automate and streamline engagement tasks within the KPMG Clara platform.",
            "RULES:",
            "1. If you are asked to click on a specific section, use the tool click.",
            "2. Whenever the user wants to open or expand a section named X, call the specialized tool `X`.",
        ]
    )

    # Keep image sizes consistent with the base class (fits GPT-4v constraints)
    MLM_HEIGHT = 765
    MLM_WIDTH = 1224

    SCREENSHOT_TOKENS = 1105

    def __init__(
        self,
        name: str,
        model_client: ChatCompletionClient,
        downloads_folder: str | None = None,
        description: str | None = None,
        debug_dir: str | None = None,
        headless: bool = True,
        start_page: str | None = None,
        animate_actions: bool = False,
        to_save_screenshots: bool = False,
        use_ocr: bool = False,
        browser_channel: str | None = None,
        browser_data_dir: str | None = None,
        to_resize_viewport: bool = True,
        playwright: Playwright | None = None,
        context: BrowserContext | None = None,
        user_name: str | None = None,
        password: str | None = None,
    ) -> None:
        super().__init__(
            name=name,
            model_client=model_client,
            downloads_folder=downloads_folder,
            description=description or self.DEFAULT_DESCRIPTION,
            debug_dir=debug_dir,
            headless=headless,
            start_page=start_page,
            animate_actions=animate_actions,
            to_save_screenshots=to_save_screenshots,
            use_ocr=use_ocr,
            browser_channel=browser_channel,
            browser_data_dir=browser_data_dir,
            to_resize_viewport=to_resize_viewport,
            playwright=playwright,
            context=context,
        )

        # KCW credentials; if provided we use deterministic login flow
        self.user_name = user_name
        self.password = password

        # Replace the Playwright controller with our extended version
        # Reuse the private download handler set up by the base class
        self._playwright_controller = KCWPlaywrightController(
            animate_actions=self.animate_actions,
            downloads_folder=self.downloads_folder,
            viewport_width=self.VIEWPORT_WIDTH,
            viewport_height=self.VIEWPORT_HEIGHT,
            _download_handler=self._download_handler,  # type: ignore[attr-defined]
            to_resize_viewport=self.to_resize_viewport,
        )

        # Extend the available tools
        self.default_tools = [
            TOOL_VISIT_URL,
            TOOL_WEB_SEARCH,
            TOOL_HISTORY_BACK,
            TOOL_CLICK,
            TOOL_TYPE,
            TOOL_READ_PAGE_AND_ANSWER,
            TOOL_SUMMARIZE_PAGE,
            TOOL_SLEEP,
            TOOL_HOVER,
            TOOL_CLICK_MENU_TAB,
            TOOL_CLICK_STACKED_WINDOWS,
            TOOL_UPLOAD_FILES,
            TOOL_FILL_UPLOAD_GRID_CELL,
        ]

    async def _kcw_init(self) -> None:
        """Deterministic browser setup and KPMG Clara login using provided credentials."""
        self._last_download = None
        self._prior_metadata_hash = None

        if self._playwright is None:
            self._playwright = await async_playwright().start()

        browser = await self._playwright.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0"
            )
        )
        await context.tracing.start(screenshots=True, snapshots=True, sources=True)
        self._page = await context.new_page()

        # Base init script, viewport and handlers
        self._page.on("download", self._download_handler)  # type: ignore[attr-defined]
        if self.to_resize_viewport:
            await self._page.set_viewport_size(
                {"width": self.VIEWPORT_WIDTH, "height": self.VIEWPORT_HEIGHT}
            )
        await self._page.add_init_script(
            path=os.path.join(
                os.path.abspath(os.path.dirname(__file__)), "page_script.js"
            )
        )

        # Login flow
        assert self.user_name and self.password, (
            "KCW login requires user_name and password"
        )
        await self._page.goto(
            self.start_page or self.DEFAULT_START_PAGE, wait_until="networkidle"
        )
        await self._page.get_by_placeholder("Sign in with your KPMG email").click()
        await self._page.get_by_placeholder("Sign in with your KPMG email").fill(
            self.user_name
        )
        await self._page.get_by_role("button", name="Next").click()

        # Redirect to ADFS login
        await self._page.wait_for_url(
            r"https:\/\/gfs2\.glb\.kworld\.kpmg\.com\/adfs\/ls\/wia\?**"
        )
        login_url = self._page.url.replace(
            "https://", f"https://{self.user_name}:{self.password}@"
        )
        await self._page.goto(login_url, wait_until="networkidle")
        await self._page.goto(
            self.start_page or self.DEFAULT_START_PAGE, wait_until="networkidle"
        )
        await self._page.wait_for_timeout(10_000)

        # Validate login success (not back at the starting login screen)
        login_field = self._page.get_by_placeholder("Sign in with your KPMG email")
        if (await login_field.count()) and (await login_field.first.is_visible()):
            raise RuntimeError("Login failed: back at login screen.")

        await self._set_debug_dir(self.debug_dir)  # type: ignore[arg-type]
        self.did_lazy_init = True

    async def _generate_reply(
        self, cancellation_token: CancellationToken
    ) -> UserContent:
        # Initialize on first call
        if not self.did_lazy_init:
            if self.user_name and self.password:
                await self._kcw_init()
            else:
                await self._lazy_init()

        assert self._page is not None

        # Clone the messages, removing old screenshots
        history: List[LLMMessage] = remove_images(self._chat_history)

        # Split the history, removing the last message
        user_request: LLMMessage
        if len(history):
            user_request = history.pop()
        else:
            user_request = UserMessage(content="Empty request.", source="user")

        # Truncate the history for smaller models
        if self._model_client.model_info["family"] not in [
            ModelFamily.GPT_4O,
            ModelFamily.O1,
            ModelFamily.O3,
            ModelFamily.GPT_4,
            ModelFamily.GPT_35,
        ]:
            history = []

        # Ask the page for interactive elements, then prepare the SOM screenshot
        rects: Dict[
            str, InteractiveRegion
        ] = await self._playwright_controller.get_all_interactive_elements(self._page)  # type: ignore[attr-defined]
        self._playwright_controller.interactive_elements = rects  # type: ignore[attr-defined]

        # Debug: write rects to a file
        try:
            with open(
                "/Users/richtervanemmerik/Documents/dani-agent/rects_debug.txt", "w"
            ) as f:
                f.write(json.dumps(rects, indent=2))
        except Exception as e:
            print(f"Error saving rects for debugging: {e}")

        viewport = await self._playwright_controller.get_visual_viewport(self._page)  # type: ignore[attr-defined]
        screenshot = await self._page.screenshot()
        som_screenshot, visible_rects, rects_above, rects_below = add_set_of_mark(
            screenshot, rects
        )

        if self.to_save_screenshots and self.debug_dir is not None:
            current_timestamp = "_" + int(time.time()).__str__()
            screenshot_png_name = "screenshot_som" + current_timestamp + ".png"
            som_screenshot.save(os.path.join(self.debug_dir, screenshot_png_name))
            self.logger.info(
                WebSurferEvent(
                    source=self.name,
                    url=self._page.url,
                    message="Screenshot: " + screenshot_png_name,
                )
            )

        # What tools are available?
        tools = self.default_tools.copy()
        if viewport["pageTop"] > 5:
            tools.append(TOOL_SCROLL_UP)
        if (viewport["pageTop"] + viewport["height"] + 5) < viewport["scrollHeight"]:
            tools.append(TOOL_SCROLL_DOWN)

        # Focus hint
        focused = await self._playwright_controller.get_focused_rect_id(self._page)  # type: ignore[attr-defined]
        focused_hint = ""
        if focused:
            name = self._target_name(focused, rects)  # type: ignore[attr-defined]
            if name:
                name = f"(and name '{name}') "
            else:
                name = ""
            role = "control"
            try:
                role = rects[focused]["role"]
            except KeyError:
                pass
            focused_hint = f"\nThe {role} with ID {focused} {name}currently has the input focus.\n\n"

        # Everything visible
        visible_targets = (
            "\n".join(self._format_target_list(visible_rects, rects)) + "\n\n"
        )  # type: ignore[attr-defined]

        # Everything else
        other_targets: List[str] = []
        other_targets.extend(self._format_target_list(rects_above, rects))  # type: ignore[attr-defined]
        other_targets.extend(self._format_target_list(rects_below, rects))  # type: ignore[attr-defined]

        if len(other_targets) > 0:
            if len(other_targets) > 30:
                other_targets = other_targets[0:30]
                other_targets.append("...")
            other_targets_str = (
                "Additional valid interaction targets include (but are not limited to):\n"
                + "\n".join(other_targets)
                + "\n\n"
            )
        else:
            other_targets_str = ""

        state_description = "Your " + await self._get_state_description()  # type: ignore[attr-defined]
        tool_names = "\n".join([t["name"] for t in tools])
        page_title = await self._page.title()

        prompt_message = None
        if self._model_client.model_info["vision"]:
            text_prompt = WEB_SURFER_TOOL_PROMPT_MM.format(
                state_description=state_description,
                visible_targets=visible_targets,
                other_targets_str=other_targets_str,
                focused_hint=focused_hint,
                tool_names=tool_names,
                title=page_title,
                url=self._page.url,
            ).strip()

            # Save the text prompt to a debug file
            try:
                with open(
                    "/Users/richtervanemmerik/Documents/dani-agent/text_prompt_debug.txt",
                    "w",
                ) as f:
                    f.write(text_prompt)
            except Exception as e:
                print(f"Error saving text prompt: {e}")

            # Scale the screenshot for the MLM, and close the original
            scaled_screenshot = som_screenshot.resize((self.MLM_WIDTH, self.MLM_HEIGHT))
            som_screenshot.close()
            if self.to_save_screenshots and self.debug_dir is not None:
                scaled_screenshot.save(
                    os.path.join(self.debug_dir, "screenshot_scaled.png")
                )

            prompt_message = UserMessage(
                content=[
                    re.sub(r"(\n\s*){3,}", "\n\n", text_prompt),
                    AGImage.from_pil(scaled_screenshot),
                ],
                source=self.name,
            )
        else:
            text_prompt = WEB_SURFER_TOOL_PROMPT_TEXT.format(
                state_description=state_description,
                visible_targets=visible_targets,
                other_targets_str=other_targets_str,
                focused_hint=focused_hint,
                tool_names=tool_names,
                title=page_title,
                url=self._page.url,
            ).strip()
            prompt_message = UserMessage(
                content=re.sub(r"(\n\s*){3,}", "\n\n", text_prompt), source=self.name
            )

        history.append(prompt_message)
        history.append(user_request)

        response = await self._model_client.create(
            history,
            tools=tools,
            extra_create_args={"tool_choice": "auto"},
            cancellation_token=cancellation_token,
        )

        self.model_usage.append(response.usage)  # type: ignore[attr-defined]
        message = response.content
        self._last_download = None
        if isinstance(message, str):
            self.inner_messages.append(TextMessage(content=message, source=self.name))  # type: ignore[attr-defined]
            return message
        elif isinstance(message, list):
            return await self._execute_tool(
                message, rects, tool_names, cancellation_token=cancellation_token
            )
        else:
            raise AssertionError(f"Unknown response format '{message}'")

    async def _execute_tool(
        self,
        message: List[FunctionCall],
        rects: Dict[str, InteractiveRegion],
        tool_names: str,
        cancellation_token: Optional[CancellationToken] = None,
    ) -> UserContent:
        # Execute the tool
        assert self._page is not None
        name = message[0].name
        args = json.loads(message[0].arguments)
        action_description = ""
        self.logger.info(
            WebSurferEvent(
                source=self.name,
                url=self._page.url,
                action=name,
                arguments=args,
                message=f"{name}( {json.dumps(args)} )",
            )
        )
        self.inner_messages.append(
            TextMessage(content=f"{name}( {json.dumps(args)} )", source=self.name)
        )  # type: ignore[attr-defined]
        print(message)
        if name == "visit_url":
            url = args.get("url")
            action_description = f"I typed '{url}' into the browser address bar."
            if url.startswith(("https://", "http://", "file://", "about:")):
                (
                    reset_prior_metadata,
                    reset_last_download,
                ) = await self._playwright_controller.visit_page(self._page, url)  # type: ignore[attr-defined]
            elif " " in url:
                from urllib.parse import quote_plus

                (
                    reset_prior_metadata,
                    reset_last_download,
                ) = await self._playwright_controller.visit_page(  # type: ignore[attr-defined]
                    self._page,
                    f"https://www.bing.com/search?q={quote_plus(url)}&FORM=QBLH",
                )
            else:
                (
                    reset_prior_metadata,
                    reset_last_download,
                ) = await self._playwright_controller.visit_page(
                    self._page, "https://" + url
                )  # type: ignore[attr-defined]
            if reset_last_download and self._last_download is not None:
                self._last_download = None
            if reset_prior_metadata and self._prior_metadata_hash is not None:
                self._prior_metadata_hash = None

        elif name == "history_back":
            action_description = "I clicked the browser back button."
            await self._playwright_controller.back(self._page)  # type: ignore[attr-defined]

        elif name == "web_search":
            query = args.get("query")
            action_description = f"I typed '{query}' into the browser search bar."
            from urllib.parse import quote_plus

            (
                reset_prior_metadata,
                reset_last_download,
            ) = await self._playwright_controller.visit_page(  # type: ignore[attr-defined]
                self._page,
                f"https://www.bing.com/search?q={quote_plus(query)}&FORM=QBLH",
            )
            if reset_last_download and self._last_download is not None:
                self._last_download = None
            if reset_prior_metadata and self._prior_metadata_hash is not None:
                self._prior_metadata_hash = None

        elif name == "scroll_up":
            action_description = "I scrolled up one page in the browser."
            await self._playwright_controller.page_up(self._page)  # type: ignore[attr-defined]

        elif name == "scroll_down":
            action_description = "I scrolled down one page in the browser."
            await self._playwright_controller.page_down(self._page)  # type: ignore[attr-defined]

        elif name == "click":
            target_id = str(args.get("target_id"))
            target_name = self._target_name(target_id, rects)  # type: ignore[attr-defined]
            if target_name:
                action_description = f"I clicked '{target_name}'."
            else:
                action_description = "I clicked the control."
            controller = cast(KCWPlaywrightController, self._playwright_controller)
            new_page_tentative = await controller.click_id(self._page, target_id, rects)
            if new_page_tentative is not None:
                self._page = new_page_tentative
                self._prior_metadata_hash = None
                self.logger.info(
                    WebSurferEvent(
                        source=self.name,
                        url=self._page.url,
                        message="New tab or window.",
                    )
                )

        elif name == "menu_tab":
            tab_name = args.get("tab_name")
            action_description = (
                f"I used a deterministic script to click the '{tab_name}' tab."
            )
            controller = cast(KCWPlaywrightController, self._playwright_controller)
            new_page_tentative = await controller.menu_tab(self._page, tab_name)
            if new_page_tentative is not None:
                self._page = new_page_tentative
                self._prior_metadata_hash = None
                self.logger.info(
                    WebSurferEvent(
                        source=self.name,
                        url=self._page.url,
                        message="Successfully navigated to 'Project Plan' (deterministic).",
                    )
                )

        elif name == "stacked_windows":
            action_description = (
                "I used a deterministic script to click the 'Stacked Windows' tab."
            )
            await self._playwright_controller.stacked_windows(self._page)  # type: ignore[attr-defined]
            self._prior_metadata_hash = None
            self.logger.info(
                WebSurferEvent(
                    source=self.name,
                    url=self._page.url,
                    message="Successfully navigated to 'Financial Reporting' (deterministic).",
                )
            )

        elif name == "input_text":
            input_field_id = str(args.get("input_field_id"))
            text_value = str(args.get("text_value"))
            input_field_name = self._target_name(input_field_id, rects)  # type: ignore[attr-defined]
            if input_field_name:
                action_description = (
                    f"I typed '{text_value}' into '{input_field_name}'."
                )
            else:
                action_description = f"I input '{text_value}'."
            await self._playwright_controller.fill_id(
                self._page, input_field_id, text_value
            )  # type: ignore[attr-defined]

        elif name == "scroll_element_up":
            target_id = str(args.get("target_id"))
            target_name = self._target_name(target_id, rects)  # type: ignore[attr-defined]
            if target_name:
                action_description = f"I scrolled '{target_name}' up."
            else:
                action_description = "I scrolled the control up."
            await self._playwright_controller.scroll_id(self._page, target_id, "up")  # type: ignore[attr-defined]

        elif name == "scroll_element_down":
            target_id = str(args.get("target_id"))
            target_name = self._target_name(target_id, rects)  # type: ignore[attr-defined]
            if target_name:
                action_description = f"I scrolled '{target_name}' down."
            else:
                action_description = "I scrolled the control down."
            await self._playwright_controller.scroll_id(self._page, target_id, "down")  # type: ignore[attr-defined]

        elif name == "answer_question":
            question = str(args.get("question"))
            action_description = (
                f"I answered the following question '{question}' based on the web page."
            )
            return await self._summarize_page(
                question=question, cancellation_token=cancellation_token
            )  # type: ignore[attr-defined]

        elif name == "summarize_page":
            action_description = "I summarized the current web page"
            return await self._summarize_page(cancellation_token=cancellation_token)  # type: ignore[attr-defined]

        elif name == "hover":
            target_id = str(args.get("target_id"))
            target_name = self._target_name(target_id, rects)  # type: ignore[attr-defined]
            if target_name:
                action_description = f"I hovered over '{target_name}'."
            else:
                action_description = "I hovered over the control."
            controller = cast(KCWPlaywrightController, self._playwright_controller)
            await controller.hover_id(self._page, target_id)

        elif name == "sleep":
            action_description = (
                "I am waiting a short period of time before taking further action."
            )
            controller = cast(KCWPlaywrightController, self._playwright_controller)
            await controller.sleep(self._page, 3)

        elif name == "upload_files":
            file_list = list(args.get("files", []))
            to = args.get("to")
            action_description = "I uploaded the specified file(s)."
            controller = cast(KCWPlaywrightController, self._playwright_controller)
            await controller.upload_files(self._page, file_list, to=to)

        elif name == "fill_upload_grid_cell":
            column = str(args.get("column"))
            value = str(args.get("value"))
            action_description = f"I set column '{column}' to '{value}'."
            controller = cast(KCWPlaywrightController, self._playwright_controller)
            await controller.fill_grid_cell_by_header(
                self._page, column=column, value=value
            )

        else:
            raise ValueError(
                f"Unknown tool '{name}'. Please choose from:\n\n{tool_names}"
            )

        await self._page.wait_for_load_state()
        controller = cast(KCWPlaywrightController, self._playwright_controller)
        await controller.sleep(self._page, 3)

        # Handle downloads
        if self._last_download is not None and self.downloads_folder is not None:
            fname = os.path.join(
                self.downloads_folder, self._last_download.suggested_filename
            )
            await self._last_download.save_as(fname)  # type: ignore
            page_body = (
                f'<html><head><title>Download Successful</title></head><body style="margin: 20px;">'
                f"<h1>Successfully downloaded '{self._last_download.suggested_filename}' to local path:<br><br>{fname}</h1>"
                f"</body></html>"
            )
            await self._page.goto(
                "data:text/html;base64,"
                + base64.b64encode(page_body.encode("utf-8")).decode("utf-8")
            )
            await self._page.wait_for_load_state()

        # Handle metadata
        page_metadata = json.dumps(
            await self._playwright_controller.get_page_metadata(self._page), indent=4
        )  # type: ignore[attr-defined]
        metadata_hash = hashlib.md5(page_metadata.encode("utf-8")).hexdigest()
        if metadata_hash != self._prior_metadata_hash:
            page_metadata = (
                "\n\nThe following metadata was extracted from the webpage:\n\n"
                + page_metadata.strip()
                + "\n"
            )
        else:
            page_metadata = ""
        self._prior_metadata_hash = metadata_hash

        new_screenshot = await self._page.screenshot()
        if self.to_save_screenshots and self.debug_dir is not None:
            current_timestamp = "_" + int(time.time()).__str__()
            screenshot_png_name = "screenshot" + current_timestamp + ".png"
            async with aiofiles.open(
                os.path.join(self.debug_dir, screenshot_png_name), "wb"
            ) as file:
                await file.write(new_screenshot)  # type: ignore
            self.logger.info(
                WebSurferEvent(
                    source=self.name,
                    url=self._page.url,
                    message="Screenshot: " + screenshot_png_name,
                )
            )

        state_description = "The " + await self._get_state_description()  # type: ignore[attr-defined]
        message_content = (
            f"{action_description}\n\n"
            + state_description
            + page_metadata
            + "\nHere is a screenshot of the page."
        )
        return [
            re.sub(r"(\n\s*){3,}", "\n\n", message_content),
            AGImage.from_pil(PIL.Image.open(io.BytesIO(new_screenshot))),
        ]
