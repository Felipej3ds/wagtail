import pytest
from wagtail import hooks
from wagtail.admin import icons

@pytest.fixture(autouse=True)
def reset_hooks_and_cache():
    # Backup e limpeza dos hooks e cache antes e depois do teste
    original_hooks = hooks._hooks.get("register_icons", []).copy()
    hooks._hooks["register_icons"] = []
    icons.get_icons.cache_clear()
    icons.get_icon_sprite_hash.cache_clear()
    yield
    hooks._hooks["register_icons"] = original_hooks
    icons.get_icons.cache_clear()
    icons.get_icon_sprite_hash.cache_clear()

@hooks.register("register_icons")
def empty_icon_hook(icons_list):
    # Hook que não adiciona ícones
    return icons_list

def test_get_icons_raises_value_error_on_empty_icons():
    with pytest.raises(ValueError, match="no icons registered"):
        icons.get_icons()
