from __future__ import annotations

from importlib import import_module

from botscore import __about__, config, constants, runtime


def test_package_metadata_is_available():
    assert __about__.__title__ == "botscore"
    assert __about__.__summary__
    assert __about__.__version__


def test_core_modules_import():
    for module_name in (
        "botscore.codecs",
        "botscore.config",
        "botscore.constants",
        "botscore.errors",
        "botscore.grammar",
        "botscore.imports",
        "botscore.inmessage",
        "botscore.message",
        "botscore.node",
        "botscore.outmessage",
        "botscore.runtime",
    ):
        assert import_module(module_name)


def test_config_defaults_and_runtime_directory_setup(tmp_path):
    ini = config.BotsConfig()
    runtime.ensure_runtime_defaults(ini)
    ini.set("directories", "botsenv", str(tmp_path))
    ini.set("directories", "botssys", "botssys")

    runtime.configure_botssys(ini)

    assert ini.get("settings", "botsreplacechar", None) == " "
    assert ini.get("directories", "botssys_org") == "botssys"
    assert ini.get("directories", "botssys") == str(tmp_path / "botssys")
    assert ini.get("directories", "data") == str(tmp_path / "botssys" / "data")
    assert ini.get("directories", "logging") == str(tmp_path / "botssys" / "logging")


def test_expected_constants_are_exposed():
    assert constants.DONE == 3
    assert constants.FILEOUT == 500
    assert constants.ID == 0
