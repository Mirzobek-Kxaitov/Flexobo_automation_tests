from tests_mobile.screens.base_screen import BaseScreen


class LoadsScreen(BaseScreen):
    LOADS_TAB_RU = "Грузы"
    TRUCKS_TAB_RU = "Грузовики"
    FILTER_RU = "Фильтр"
    MAP_RU = "Карта"
    SORT_RU = "Сортировать"

    def expect_visible(self):
        self.wait_for_text(self.LOADS_TAB_RU, timeout=15)
        self.wait_for_text(self.TRUCKS_TAB_RU)
        self.wait_for_text(self.FILTER_RU)
        return self

    def expect_filter_controls_visible(self):
        self.expect_visible()
        self.wait_for_text(self.MAP_RU)
        self.wait_for_text(self.SORT_RU)
        return self

    def open_first_load_card(self) -> str:
        self.expect_visible()

        for node in self.device.all_nodes():
            content_desc = node.attrib.get("content-desc") or ""
            is_clickable = node.attrib.get("clickable") == "true"
            if is_clickable and "USD" in content_desc and "Км" in content_desc:
                self.device.tap_node(node)
                self.device.wait(seconds=2)
                return content_desc

        raise AssertionError("No clickable load card was found on the loads screen")
