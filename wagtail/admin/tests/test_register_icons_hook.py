import pytest
from unittest.mock import patch
from wagtail.admin import icons
from wagtail import hooks

@patch("wagtail.admin.icons.render_to_string", return_value="<svg></svg>")
def test_register_icons_hook_raises_value_error(mock_render):
    def broken_hook(icons_list):
        icons_list.remove("wagtailadmin/icons/time.svg")
        return icons_list

    with hooks.register_temporarily("register_icons", broken_hook):
        try:
            icons.get_icons()
        except ValueError:
            pytest.fail("O teste falhou porque ocorreu um ValueError, que é o erro da issue.")
        except Exception:
            pass  