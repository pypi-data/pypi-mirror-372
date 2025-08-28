# tests/test_page_object.py
import logging
from pathlib import Path

from shadowstep.page_object.page_object_element_node import UiElementNode
from shadowstep.page_object.page_object_generator import PageObjectGenerator
from shadowstep.page_object.page_object_parser import PageObjectParser
from shadowstep.page_object.page_object_recycler_explorer import PageObjectRecyclerExplorer
from shadowstep.shadowstep import Shadowstep
from shadowstep.utils.translator import YandexTranslate

parser = PageObjectParser()
POG = PageObjectGenerator()
logger = logging.getLogger(__name__)


class TestPageObjectextractor:

    def test_poe(self, app: Shadowstep, android_settings_open_close: None):
        source = app.driver.page_source
        ui_element_tree = parser.parse(source)
        assert isinstance(ui_element_tree, UiElementNode)

    def test_pog(self, app: Shadowstep, android_settings_open_close: None, cleanup_pages: None):
        parser = PageObjectParser()
        translator = YandexTranslate(folder_id="b1ghf7n3imfg7foodstv")
        generator = PageObjectGenerator(translator)

        tree = parser.parse(app.driver.page_source)
        page_path, page_class_name = generator.generate(tree, output_dir="pages")

        assert page_path == 'pages\page_settings.py'    # type: ignore  # noqa: W605
        assert page_class_name == 'PageSettings'
        file_path = Path(page_path)
        assert file_path.exists(), f"Файл {file_path} не найден"

    def test_explorer(self, app: Shadowstep, android_settings_open_close: None, cleanup_pages: None):
        translator = YandexTranslate(folder_id="b1ghf7n3imfg7foodstv")
        recycler_explorer = PageObjectRecyclerExplorer(app, translator)
        page_path = recycler_explorer.explore('pages')
        
        assert page_path == 'mergedpages\page_settings.py'    # type: ignore  # noqa: W605

        file_path = Path(page_path)
        assert file_path.exists(), f"Файл {file_path} не найден"
