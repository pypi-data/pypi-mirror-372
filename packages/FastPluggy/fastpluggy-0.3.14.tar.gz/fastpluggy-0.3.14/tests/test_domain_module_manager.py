import pprint

import pytest
from fastapi import FastAPI


def test_module_with_name_different(app_with_db: FastAPI, setup_domain_module_manager):

    list_module = setup_domain_module_manager.modules

    pprint.pprint(list_module)
    entry_name_diff = list_module['not_same_name']
    assert entry_name_diff.plugin.module_name == "not_same_name"

    assert 'name_diff' not in list_module.keys()


def test_module_with_test_domain(app_with_db: FastAPI, setup_domain_module_manager):

    list_module = setup_domain_module_manager.modules

    pprint.pprint(list_module)
    assert len(list_module) == 3
    entry = list_module['fake_module']
    entry_broke = list_module['broken_module']

    assert entry.plugin.module_name == 'fake_module'
    assert entry.module_type == 'domain'
    #assert entry.package_name == 'domains.fake_module'
    assert entry.error == []

    assert entry.loaded == False
    assert entry.enabled == True
    assert entry.initialized == True
    assert entry.plugin.requirements_exists == True
    assert entry.requirements_installed is None
    assert entry.plugin.display_name == 'Fake test Module'
    assert entry.plugin.module_menu_icon == "fa-test"
    assert entry.url == '/domain/fake_module'
    assert entry.error == []
#    assert entry.models != [] # todo fix that

    assert entry_broke.loaded == False
    assert entry_broke.initialized == False

    setup_domain_module_manager.initialize_plugins_in_order()
    assert entry.loaded == True
    assert entry.initialized == True

    assert entry_broke.loaded == False
    assert entry_broke.initialized == False

    # assert entry_loaded.package_name == 'domains.fake_module'
    assert entry_broke.plugin.module_name == 'broken_module'
    assert entry_broke.loaded == False
    assert entry_broke.error != []
    assert entry_broke.error[0] ==  "Failed to load plugin 'broken_module': Broken module can't be loaded !"
    assert entry_broke.status_html == """<span class="badge bg-danger" title="Failed to load plugin 'broken_module': Broken module can't be loaded !">Failed</span>"""



def test_module_extra_files(app_with_db: FastAPI, setup_domain_module_manager):

    result = setup_domain_module_manager.initialize_plugins_in_order()

    assert result['computed_order'] == ['fake_module','not_same_name']
    assert list(setup_domain_module_manager.modules.keys()) == result['computed_order'] + ['broken_module']

    extra_js = setup_domain_module_manager.get_extra_js_files()
    extra_css = setup_domain_module_manager.get_extra_css_files()


    assert extra_js == ['fake_module.js']
    assert extra_css == ['fake_module.css', 'name_diff.css']




if __name__ == "__main__":
    pytest.main()
