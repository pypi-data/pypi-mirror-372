"""Basic test suite for qqgjyx core functionality."""

import pytest
from unittest.mock import patch, MagicMock


class TestQQClass:
    """Test the main QQ class interface."""
    
    def test_qq_import(self):
        """Test QQ class can be imported."""
        from qqgjyx import QQ
        assert QQ is not None
        assert hasattr(QQ, 'help')
        assert hasattr(QQ, 'env')
        assert hasattr(QQ, 'dev')
        assert hasattr(QQ, 'seed')
        assert hasattr(QQ, 'style')
        assert hasattr(QQ, 'split')
    
    def test_qq_help(self, capsys):
        """Test QQ.help() function."""
        from qqgjyx import QQ
        QQ.help()
        captured = capsys.readouterr()
        assert "QQ Utilities:" in captured.out
        assert "QQ.env()" in captured.out
        assert "QQ.dev()" in captured.out
        assert "QQ.seed(n)" in captured.out
        assert "QQ.style()" in captured.out
        assert "QQ.split(d)" in captured.out
        assert "QQ.help()" in captured.out
    
    def test_qq_methods_exist(self):
        """Test that all QQ methods exist and are callable."""
        from qqgjyx import QQ
        
        # Test that methods exist
        assert callable(QQ.env)
        assert callable(QQ.dev)
        assert callable(QQ.seed)
        assert callable(QQ.style)
        assert callable(QQ.split)
        assert callable(QQ.help)


class TestHelperModule:
    """Test helper module functions."""
    
    def test_backward_compatibility(self):
        """Test backward compatibility aliases."""
        from qqgjyx.helper import print_environment_info, get_device_info, set_all_seeds
        from qqgjyx.helper import env, dev, seed
        
        # Test that aliases point to new functions
        assert print_environment_info == env
        assert get_device_info == dev
        assert set_all_seeds == seed


class TestVisualModule:
    """Test visual module functions."""
    
    def test_backward_compatibility(self):
        """Test backward compatibility aliases."""
        from qqgjyx.visual import set_plt_style, style
        assert set_plt_style == style


class TestValidatorModule:
    """Test validator module functions."""
    
    def test_ensure_between_valid(self):
        """Test ensure_between with valid values."""
        from qqgjyx.validator import ensure_between
        
        assert ensure_between(5, 0, 10) == 5
        assert ensure_between(0, 0, 10) == 0
        assert ensure_between(10, 0, 10) == 10
        assert ensure_between(0.5, 0.0, 1.0) == 0.5
    
    def test_ensure_between_invalid(self):
        """Test ensure_between with invalid values."""
        from qqgjyx.validator import ensure_between
        
        with pytest.raises(ValueError):
            ensure_between(-1, 0, 10)
        
        with pytest.raises(ValueError):
            ensure_between(11, 0, 10)


class TestExceptorModule:
    """Test exceptor module."""
    
    def test_qqgjyx_error(self):
        """Test QQGJYXError exception."""
        from qqgjyx.exceptor import QQGJYXError
        
        with pytest.raises(QQGJYXError):
            raise QQGJYXError("Test error")
        
        error = QQGJYXError("Test message")
        assert str(error) == "Test message"


class TestPackageStructure:
    """Test package structure and imports."""
    
    def test_package_imports(self):
        """Test core package imports work."""
        import qqgjyx
        from qqgjyx import QQ
        from qqgjyx.helper import env, dev, seed
        from qqgjyx.validator import ensure_between
        from qqgjyx.exceptor import QQGJYXError
        
        assert qqgjyx.__version__ == "0.1.2"
        assert QQ is not None
    
    def test_subpackage_imports(self):
        """Test subpackage imports."""
        import qqgjyx.graph
        import qqgjyx.model
        
        # Test that subpackages exist
        assert hasattr(qqgjyx, 'graph')
        assert hasattr(qqgjyx, 'model')
    
    def test_version_consistency(self):
        """Test version consistency across modules."""
        import qqgjyx
        from qqgjyx import __version__
        
        assert qqgjyx.__version__ == __version__
        assert __version__ == "0.1.2"


class TestModuleStructure:
    """Test module structure and exports."""
    
    def test_helper_module_structure(self):
        """Test helper module structure."""
        from qqgjyx.helper import __all__
        
        expected_exports = ['env', 'dev', 'seed']
        for export in expected_exports:
            assert export in __all__
    
    def test_visual_module_structure(self):
        """Test visual module structure."""
        from qqgjyx.visual import __all__
        
        expected_exports = ['style']
        for export in expected_exports:
            assert export in __all__
    
    def test_validator_module_structure(self):
        """Test validator module structure."""
        from qqgjyx.validator import __all__
        
        expected_exports = ['ensure_between']
        for export in expected_exports:
            assert export in __all__
    
    def test_exceptor_module_structure(self):
        """Test exceptor module structure."""
        from qqgjyx.exceptor import __all__
        
        expected_exports = ['QQGJYXError']
        for export in expected_exports:
            assert export in __all__


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
