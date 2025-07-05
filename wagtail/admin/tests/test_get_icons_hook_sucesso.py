from wagtail import hooks
from wagtail.admin import icons

# Fixture para limpar hooks e cache
import pytest

@pytest.fixture(autouse=True)
def reset_hooks_and_cache():
    original_hooks = hooks._hooks.get("register_icons", []).copy()
    hooks._hooks["register_icons"] = []
    icons.get_icons.cache_clear()
    icons.get_icon_sprite_hash.cache_clear()
    yield
    hooks._hooks["register_icons"] = original_hooks
    icons.get_icons.cache_clear()
    icons.get_icon_sprite_hash.cache_clear()

@hooks.register("register_icons")
def valid_icon_hook(icons_list):
    icons_list.append("wagtailadmin/icons/test-icon.svg")
    return icons_list

def test_get_icons_sucesso():
    # Chama get_icons e só verifica que retorna string não vazia
    result = icons.get_icons()
    assert isinstance(result, str)
    assert len(result) > 0
