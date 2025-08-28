import asyncio
import re
import random
from pathlib import Path
from typing import Callable, Dict, Optional, Union, cast

from playwright._impl._errors import Error as PlaywrightError
from playwright._impl._errors import TimeoutError
from playwright.async_api import Download, Locator, Page

from autogen_ext.agents.web_surfer._types import (
    InteractiveRegion,
    DOMRectangle,
)


class KCWInteractiveRegion(InteractiveRegion, total=False):
    base_selector: str
    selector_index: int
    inner_selector: str


# Import the official base controller from AutoGen ext
try:
    from autogen_ext.agents.web_surfer.playwright_controller import (
        PlaywrightController as BasePlaywrightController,
    )
except Exception:  # pragma: no cover - fallback if path changes upstream
    from autogen_ext.agents.web_surfer import (
        PlaywrightController as BasePlaywrightController,
    )  # type: ignore


def _rects_are_overlapping(rect1: Dict, rect2: Dict, tolerance: int = 2) -> bool:
    return (
        abs(rect1["x"] - rect2["x"]) < tolerance
        and abs(rect1["y"] - rect2["y"]) < tolerance
        and abs(rect1["width"] - rect2["width"]) < tolerance
        and abs(rect1["height"] - rect2["height"]) < tolerance
    )


class KCWPlaywrightController(BasePlaywrightController):
    """Extension of the base controller with KCW-specific helpers and overrides."""

    def __init__(
        self,
        downloads_folder: str | None = None,
        animate_actions: bool = False,
        viewport_width: int = 1440,
        viewport_height: int = 900,
        _download_handler: Optional[Callable[[Download], None]] = None,
        to_resize_viewport: bool = True,
    ) -> None:
        super().__init__(
            downloads_folder=downloads_folder,
            animate_actions=animate_actions,
            viewport_width=viewport_width,
            viewport_height=viewport_height,
            _download_handler=_download_handler,
            to_resize_viewport=to_resize_viewport,
        )
        self.interactive_elements: Dict[str, KCWInteractiveRegion] = {}

    async def get_all_interactive_elements(
        self, page: Page
    ) -> Dict[str, InteractiveRegion]:
        base_elements = await self.get_interactive_rects(page)
        all_elements: Dict[str, KCWInteractiveRegion] = {
            k: cast(KCWInteractiveRegion, v) for k, v in base_elements.items()
        }
        all_elements = await self._enrich_elements_by_inspection(page, all_elements)
        custom_element_counter = 1000

        custom_interactive_patterns = {
            "iframe.tox-edit-area__iframe": "text_editor",
            "kendo-svgicon.k-treelist-toggle": "caret_toggle",
            "div.k-icon.k-i-hyperlink-open-sm": "open_in_new_window_icon",
        }
        for selector, custom_role in custom_interactive_patterns.items():
            try:
                elements = await page.locator(selector).all()
                for i, element in enumerate(elements):
                    if not await element.is_visible():
                        continue

                    text_clean = ""

                    if custom_role == "text_editor":
                        text_clean = "Text Box"
                    else:
                        parent_row = element.locator("xpath=ancestor::tr[1]")
                        if await parent_row.count() == 0:
                            parent_row = element.locator(
                                "xpath=ancestor::*[normalize-space(.)][1]"
                            )
                        if await parent_row.count() > 0:
                            parent_text = await parent_row.inner_text()
                            parts = parent_text.split("\t")
                            meaningful_parts = [
                                part.strip() for part in parts if part.strip()
                            ]
                            if meaningful_parts:
                                text_clean = " ".join(
                                    meaningful_parts[0].splitlines()
                                ).strip()
                        # default tag for custom non-iframe elements

                    if not text_clean:
                        continue

                    element_id = str(custom_element_counter)
                    custom_element_counter += 1
                    box = await element.bounding_box()
                    if not box:
                        continue

                    rect_data: DOMRectangle = {
                        "left": box["x"],
                        "top": box["y"],
                        "right": box["x"] + box["width"],
                        "bottom": box["y"] + box["height"],
                        "width": box["width"],
                        "height": box["height"],
                        "x": box["x"],
                        "y": box["y"],
                    }

                    entry_dict = {
                        "x": box["x"],
                        "y": box["y"],
                        "width": box["width"],
                        "height": box["height"],
                        "role": custom_role,
                        "aria_name": text_clean,
                        "rects": [rect_data],
                        "v_scrollable": False,
                        "base_selector": selector,
                        "selector_index": i,
                        "tag_name": "CUSTOM",
                    }
                    if custom_role == "text_editor":
                        entry_dict["tag_name"] = "CUSTOM_IFRAME"
                        entry_dict["inner_selector"] = "body#tinymce.mce-content-body"

                    all_elements[element_id] = cast(KCWInteractiveRegion, entry_dict)
            except Exception as e:  # pragma: no cover - best-effort enrichment
                print(f"Error finding custom pattern '{selector}': {e}")
                continue

        return cast(Dict[str, InteractiveRegion], all_elements)

    async def _enrich_elements_by_inspection(
        self, page: Page, all_elements: Dict[str, KCWInteractiveRegion]
    ) -> Dict[str, KCWInteractiveRegion]:
        enriched_elements: Dict[str, KCWInteractiveRegion] = dict(all_elements)
        custom_element_counter = 2000

        inspection_patterns = {
            "section_indicator": lambda html: "section-indicator-buildingblock" in html
            or "section_indicator_bb" in html
        }

        try:
            base_elements_locator = page.locator("[__elementId]")
            for i in range(await base_elements_locator.count()):
                live_element = base_elements_locator.nth(i)
                outer_html = await live_element.evaluate("(el) => el.outerHTML")

                for role, check_function in inspection_patterns.items():
                    if check_function(outer_html):
                        box = await live_element.bounding_box()
                        if not box:
                            continue

                        original_id = await live_element.get_attribute("__elementId")
                        if original_id in enriched_elements:
                            del enriched_elements[original_id]

                        parent_with_text = live_element.locator(
                            "xpath=ancestor::*[normalize-space(.)][1]"
                        )
                        text_clean = ""
                        if await parent_with_text.count() > 0:
                            parent_text = await parent_with_text.first.inner_text()
                            text_clean = re.sub(r"\s+", " ", parent_text).strip()

                        is_active = await live_element.evaluate(
                            "(el) => el.classList.contains('active')"
                        )
                        if is_active:
                            text_clean += " (Blue)"
                        else:
                            text_clean += " (Grey)"

                        new_id = str(custom_element_counter)
                        custom_element_counter += 1
                        rect_data: DOMRectangle = {
                            "left": box["x"],
                            "top": box["y"],
                            "right": box["x"] + box["width"],
                            "bottom": box["y"] + box["height"],
                            "width": box["width"],
                            "height": box["height"],
                            "x": box["x"],
                            "y": box["y"],
                        }

                        enriched_entry = {
                            "x": box["x"],
                            "y": box["y"],
                            "width": box["width"],
                            "height": box["height"],
                            "role": role,
                            "aria_name": text_clean or role.replace("_", " "),
                            "rects": [rect_data],
                            "v_scrollable": False,
                            "base_selector": f"[__elementId='{original_id}']",
                            "selector_index": 0,
                            "tag_name": "CUSTOM",
                        }

                        enriched_elements[new_id] = cast(
                            KCWInteractiveRegion, enriched_entry
                        )
                        break
        except Exception as e:  # pragma: no cover - best-effort enrichment
            print(f"Error during element enrichment by inspection: {e}")

        return enriched_elements

    async def click_id(
        self,
        page: Page,
        identifier: str,
        all_elements: Optional[Dict[str, InteractiveRegion]] = None,
    ) -> Page | None:
        new_page: Page | None = None
        assert page is not None
        element_data: Optional[KCWInteractiveRegion] = None
        if all_elements is not None:
            element_data = cast(
                Optional[KCWInteractiveRegion], all_elements.get(identifier)
            )
        if element_data is None:
            element_data = self.interactive_elements.get(identifier)

        if element_data and "base_selector" in element_data:
            base_selector = element_data["base_selector"]
            index = (
                element_data["selector_index"]
                if "selector_index" in element_data
                else 0
            )
            target = page.locator(base_selector).nth(index)
        else:
            target = page.locator(f"[__elementId='{identifier}']")

        try:
            await target.wait_for(timeout=5000)
        except TimeoutError:
            raise ValueError("No such element.") from None

        await target.scroll_into_view_if_needed()
        await asyncio.sleep(0.3)
        box = cast(Dict[str, Union[int, float]], await target.bounding_box())

        if self.animate_actions:
            await self.add_cursor_box(page, identifier)
            start_x, start_y = self.last_cursor_position
            end_x, end_y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
            await self.gradual_cursor_animation(page, start_x, start_y, end_x, end_y)
            await asyncio.sleep(0.1)
            try:
                async with page.expect_event("popup", timeout=1000) as page_info:  # type: ignore
                    await page.mouse.click(end_x, end_y, delay=10)
                    new_page = await page_info.value  # type: ignore
                    assert isinstance(new_page, Page)
                    await self.on_new_page(new_page)
            except TimeoutError:
                pass
            await self.remove_cursor_box(page, identifier)
        else:
            try:
                async with page.expect_event("popup", timeout=1000) as page_info:  # type: ignore
                    await page.mouse.click(
                        box["x"] + box["width"] / 2,
                        box["y"] + box["height"] / 2,
                        delay=10,
                    )
                    new_page = await page_info.value  # type: ignore
                    assert isinstance(new_page, Page)
                    await self.on_new_page(new_page)
            except TimeoutError:
                pass
        return new_page

    async def fill_id(
        self, page: Page, identifier: str, value: str, press_enter: bool = True
    ) -> None:
        assert page is not None
        element_data = self.interactive_elements.get(identifier)
        target = None
        if (
            element_data
            and "tag_name" in element_data
            and element_data["tag_name"] == "CUSTOM_IFRAME"
        ):
            iframe_selector = (
                element_data["base_selector"]
                if "base_selector" in element_data
                else None
            )
            inner_selector = (
                element_data["inner_selector"]
                if "inner_selector" in element_data
                else None
            )
            selector_index = (
                element_data["selector_index"]
                if "selector_index" in element_data
                else 0
            )
            if not iframe_selector or not inner_selector:
                raise ValueError(
                    "Iframe element data is missing 'base_selector' or 'inner_selector'."
                )
            frame = page.frame_locator(iframe_selector).nth(selector_index)
            target = frame.locator(inner_selector)
        else:
            target = page.locator(f"[__elementId='{identifier}']")

        try:
            await target.wait_for(timeout=5000)
        except TimeoutError:
            raise ValueError("No such element.") from None

        await target.scroll_into_view_if_needed()
        box = cast(Dict[str, Union[int, float]], await target.bounding_box())

        if self.animate_actions:
            await self.add_cursor_box(page, identifier)
            start_x, start_y = self.last_cursor_position
            end_x, end_y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
            await self.gradual_cursor_animation(page, start_x, start_y, end_x, end_y)
            await asyncio.sleep(0.1)

        await target.focus()
        if self.animate_actions:
            if len(value) < 100:
                delay_typing_speed = 50 + 100 * random.random()
            else:
                delay_typing_speed = 10
            await target.press_sequentially(value, delay=delay_typing_speed)
        else:
            try:
                await target.fill(value)
            except PlaywrightError:
                await target.press_sequentially(value)

        if press_enter and not (
            element_data and element_data.get("tag_name") == "CUSTOM_IFRAME"
        ):
            await target.press("Enter")

        if self.animate_actions:
            await self.remove_cursor_box(page, identifier)

    async def menu_tab(self, page: Page, tab_name: str) -> Page | None:
        assert page is not None
        tab_locator = page.locator(f'"{tab_name}"')
        try:
            await tab_locator.wait_for(state="visible", timeout=2000)
        except TimeoutError:
            raise ValueError(f"'{tab_name}' tab not found or not visible.")

        await tab_locator.scroll_into_view_if_needed()
        await asyncio.sleep(0.2)
        box = await tab_locator.bounding_box()
        new_page: Page | None = None
        if box is not None:
            try:
                async with page.expect_event("popup", timeout=1000) as page_info:
                    await page.mouse.click(
                        box["x"] + box["width"] / 2,
                        box["y"] + box["height"] / 2,
                        delay=10,
                    )
                    new_page = await page_info.value
                    assert isinstance(new_page, Page)
            except TimeoutError:
                await page.mouse.click(
                    box["x"] + box["width"] / 2, box["y"] + box["height"] / 2, delay=10
                )
        else:
            try:
                async with page.expect_event("popup", timeout=1000) as page_info:
                    await tab_locator.click()
                    new_page = await page_info.value
                    assert isinstance(new_page, Page)
            except TimeoutError:
                await tab_locator.click()
        return new_page

    async def period_end_close(self, page: Page) -> Page | None:
        row = page.locator("tr:has-text('3.Period-end close')")
        icon = row.locator("div.k-icon.k-i-hyperlink-open-sm").nth(0)
        popup_promise = page.wait_for_event("popup")
        await icon.click(force=True)
        new_page = await popup_promise
        await new_page.wait_for_load_state("networkidle")
        return new_page

    async def stacked_windows(self, page: Page) -> None:
        icon = page.locator("div#hamburgerToggle.app-icon_one")
        try:
            await icon.wait_for(state="visible", timeout=5_000)
        except TimeoutError:
            raise RuntimeError("Hamburger icon not found or not visible on page.")
        await icon.scroll_into_view_if_needed()
        await asyncio.sleep(0.1)
        await icon.click()
        menu = page.locator("ul.fwk--menu-content")
        try:
            await menu.wait_for(state="visible", timeout=5_000)
        except TimeoutError:
            raise RuntimeError("Menu did not appear after clicking the hamburger icon.")

    async def upload_files(
        self,
        page: Page,
        files: list[str],
        to: Optional[str] = "div[name='Select file(s)']",
    ) -> None:
        assert page is not None
        paths = [str(Path(p).expanduser().resolve()) for p in files]
        if to:
            try:
                async with page.expect_file_chooser(timeout=10_000) as fc_info:
                    await page.locator(to).first.click()
                chooser = await fc_info.value
                await chooser.set_files(paths)
            except TimeoutError:
                await page.locator("input[type=file]").first.set_input_files(paths)
        else:
            await page.locator("input[type=file]").first.set_input_files(paths)

    async def fill_grid_cell_by_header(
        self, page: Page, column: str, value: str
    ) -> None:
        assert page is not None

        def _normalize(s: Optional[str]) -> str:
            if not s:
                return ""
            s2 = re.sub(r"[^\w]+", " ", s, flags=re.UNICODE)
            s2 = re.sub(r"\s+", " ", s2).strip().lower()
            return s2

        expected_norm = _normalize(column)
        matched_header: Optional[Locator] = None
        all_headers = page.locator("[role='columnheader']")

        for i in range(await all_headers.count()):
            header = all_headers.nth(i)
            try:
                if not await header.is_visible():
                    continue
            except Exception:
                continue
            text_raw = await header.inner_text() or ""
            text = text_raw.strip()
            if not text:
                text = (
                    (await header.get_attribute("aria-label"))
                    or (await header.get_attribute("title"))
                    or ""
                )
            if expected_norm in _normalize(text):
                matched_header = header
                break

        if not matched_header:
            raise ValueError(f"Could not find a visible column header for '{column}'")

        col_idx_str = await matched_header.get_attribute("aria-colindex")
        if col_idx_str and col_idx_str.isdigit():
            col_idx = int(col_idx_str)
        else:
            col_idx = (
                await matched_header.locator("xpath=./preceding-sibling::*").count()
            ) + 1

        grid = matched_header.locator("xpath=ancestor::*[@role='grid']")
        if await grid.count() == 0:
            raise ValueError(
                "Could not find parent [role='grid'] for the matched header."
            )
        grid = grid.first

        first_data_row = grid.locator("[role='row']:has([role='gridcell'])").first
        cell = first_data_row.locator(
            f"[role='gridcell'][aria-colindex='{col_idx}'], "
            f"[role='gridcell']:nth-child({col_idx})",
        ).first

        try:
            await cell.wait_for(timeout=5000)
        except TimeoutError:
            raise TimeoutError(
                f"Found header '{column}' but could not find a corresponding data cell in the first row."
            )

        await cell.scroll_into_view_if_needed()
        await cell.dblclick()
        editor = cell.locator("input, textarea, [contenteditable='true']").first
        try:
            await editor.wait_for(timeout=2000)
        except TimeoutError:
            await cell.click()
            try:
                await editor.wait_for(timeout=2000)
            except TimeoutError:
                raise TimeoutError("Could not activate the editor for the cell.")

        await editor.fill(value)
        await editor.press("Enter")
        await page.wait_for_timeout(100)


__all__ = ["KCWPlaywrightController"]
