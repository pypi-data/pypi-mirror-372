import tuxparse


def test_version():
    """Test that version is properly defined"""
    assert type(tuxparse.__version__) is str
    assert len(tuxparse.__version__) > 0


def test_module_imports():
    """Test that all main modules can be imported"""
    from tuxparse.boot_test_parser import BootTestParser
    from tuxparse.build_parser import BuildParser
    from tuxparse.lib.base_log_parser import BaseLogParser
    from tuxparse.test_parser import TestParser

    # Test that classes can be instantiated
    assert BootTestParser() is not None
    assert BuildParser() is not None
    assert BaseLogParser() is not None
    assert TestParser() is not None


def test_main_module_executable():
    """Test that main module can be imported"""
    from tuxparse.__main__ import main, parse_args

    # Test that functions exist
    assert callable(main)
    assert callable(parse_args)
