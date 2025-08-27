"""Comprehensive test suite for qqgjyx."""

import pytest
import sys
from unittest.mock import patch, MagicMock

# Try import torch; some tests will be skipped if unavailable
try:
    import torch  # type: ignore
    TORCH_AVAILABLE = True
except Exception:  # pragma: no cover - environment dependent
    TORCH_AVAILABLE = False
    torch = None  # type: ignore

from torch.utils.data import Dataset as TorchDataset if TORCH_AVAILABLE else (object)  # type: ignore


class MockDataset(torch.utils.data.Dataset if TORCH_AVAILABLE else object):  # type: ignore
    """Mock dataset for testing when torch is available."""
    def __init__(self, size=100):
        if not TORCH_AVAILABLE:
            pytest.skip("torch not available")
        self.data = torch.randn(size, 5)
        self.labels = torch.randint(0, 3, (size,))
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        return self.data[idx], self.labels[idx]


class TestQQClass:
    """Test the main QQ class interface."""
    
    def test_qq_import(self):
        from qqgjyx import QQ
        assert QQ is not None
        for name in ("help", "env", "dev", "seed", "style", "split"):
            assert hasattr(QQ, name)
    
    def test_qq_help(self, capsys):
        from qqgjyx import QQ
        QQ.help()
        out = capsys.readouterr().out
        assert "QQ Utilities:" in out
        assert "QQ.env()" in out and "QQ.dev()" in out
        assert "QQ.seed(" in out and "QQ.style()" in out and "QQ.split(" in out
    
    def test_qq_env(self):
        from qqgjyx import QQ
        with patch("qqgjyx.helper.env") as mock_env:
            QQ.env()
            mock_env.assert_called_once()
    
    def test_qq_dev(self):
        from qqgjyx import QQ
        with patch("qqgjyx.helper.dev") as mock_dev:
            mock_dev.return_value = "cpu"
            assert QQ.dev() == "cpu"
    
    def test_qq_seed(self):
        from qqgjyx import QQ
        with patch("qqgjyx.helper.seed") as mock_seed:
            mock_seed.return_value = 42
            assert QQ.seed(42) == 42
            mock_seed.assert_called_once_with(42)
    
    def test_qq_style(self):
        from qqgjyx import QQ
        with patch("qqgjyx.visual.style") as mock_style:
            QQ.style()
            mock_style.assert_called_once()
    
    @pytest.mark.skipif(not TORCH_AVAILABLE, reason="torch not available")
    def test_qq_split(self):
        from qqgjyx import QQ
        dataset = MockDataset(100)
        with patch("qqgjyx.data.split") as mock_split:
            mock_split.return_value = (dataset, dataset)
            train, val = QQ.split(dataset, val_ratio=0.2, seed=42)
            assert train is dataset and val is dataset


class TestHelperModule:
    """Test helper module functions."""
    
    def test_env_function(self, capsys):
        from qqgjyx import helper
        # Inject mocks for lazy imports
        helper.np = MagicMock()  # type: ignore
        helper.torch = MagicMock()  # type: ignore
        helper.env()
        out = capsys.readouterr().out
        assert "Environment Information" in out
        assert "Python version:" in out
    
    def test_dev_function(self, capsys):
        from qqgjyx import helper
        helper.torch = MagicMock()  # type: ignore
        helper.torch.cuda.is_available.return_value = False  # type: ignore
        helper.torch.device.return_value = "cpu"  # type: ignore
        result = helper.dev()
        assert result == "cpu"
        assert "Device Information" in capsys.readouterr().out
    
    def test_seed_function(self, capsys):
        from qqgjyx import helper
        helper.torch = MagicMock()  # type: ignore
        helper.np = MagicMock()  # type: ignore
        helper.pl = MagicMock()  # type: ignore
        assert helper.seed(42) == 42
        out = capsys.readouterr().out
        assert "Setting Random Seeds" in out
        helper.torch.manual_seed.assert_called()  # type: ignore
        helper.np.random.seed.assert_called()  # type: ignore
        helper.pl.seed_everything.assert_called()  # type: ignore
    
    def test_backward_compatibility(self):
        from qqgjyx.helper import print_environment_info, get_device_info, set_all_seeds, env, dev, seed
        assert print_environment_info == env
        assert get_device_info == dev
        assert set_all_seeds == seed


class TestVisualModule:
    def test_style_function(self):
        # Patch at the correct module path where plt exists
        with patch("qqgjyx.visual.plotting.plt") as mock_plt:
            from qqgjyx.visual import style
            style()
            mock_plt.style.use.assert_called_with("science")
            assert mock_plt.rcParams.update.called
    
    def test_backward_compatibility(self):
        from qqgjyx.visual import set_plt_style, style
        assert set_plt_style == style


@pytest.mark.skipif(not TORCH_AVAILABLE, reason="torch not available")
class TestDataModule:
    def test_split_function(self):
        from qqgjyx.data import split
        dataset = MockDataset(100)
        train_set, val_set = split(dataset, val_ratio=0.2, seed=42)
        assert len(train_set) == 80 and len(val_set) == 20
    
    def test_split_edge_cases(self):
        from qqgjyx.data import split
        dataset = MockDataset(10)
        train_set, val_set = split(dataset, val_ratio=0.0, seed=42)
        assert len(train_set) == 10 and len(val_set) == 0
        train_set, val_set = split(dataset, val_ratio=1.0, seed=42)
        assert len(train_set) == 0 and len(val_set) == 10
    
    def test_backward_compatibility(self):
        from qqgjyx.data import train_val_split, split
        assert train_val_split == split


class TestValidatorModule:
    def test_ensure_between_valid(self):
        from qqgjyx.validator import ensure_between
        assert ensure_between(5, 0, 10) == 5
        assert ensure_between(0.5, 0.0, 1.0) == 0.5
    
    def test_ensure_between_invalid(self):
        from qqgjyx.validator import ensure_between
        with pytest.raises(ValueError):
            ensure_between(-1, 0, 10)
        with pytest.raises(ValueError):
            ensure_between(11, 0, 10)
        with pytest.raises(ValueError, match="custom"):
            ensure_between(-5, 0, 10, "custom")


class TestExceptorModule:
    def test_qqgjyx_error(self):
        from qqgjyx.exceptor import QQGJYXError
        with pytest.raises(QQGJYXError):
            raise QQGJYXError("Test error")
        assert str(QQGJYXError("Test message")) == "Test message"


class TestPackageStructure:
    def test_package_imports(self):
        import qqgjyx
        from qqgjyx import QQ
        from qqgjyx.helper import env, dev, seed
        from qqgjyx.visual import style
        from qqgjyx.validator import ensure_between
        from qqgjyx.exceptor import QQGJYXError
        assert QQ is not None and qqgjyx.__version__ == qqgjyx.__version__
    
    def test_subpackage_imports(self):
        import qqgjyx.graph, qqgjyx.model, qqgjyx.visual, qqgjyx.data
        for name in ("graph", "model", "visual", "data"):
            assert hasattr(__import__("qqgjyx"), name)
    
    def test_version_consistency(self):
        import qqgjyx
        from qqgjyx import __version__
        assert qqgjyx.__version__ == __version__


class TestIntegration:
    @pytest.mark.skipif(not TORCH_AVAILABLE, reason="torch not available")
    def test_complete_workflow(self):
        from qqgjyx import QQ
        dataset = MockDataset(100)
        QQ.seed(42)
        train_set, val_set = QQ.split(dataset, val_ratio=0.2)
        assert len(train_set) == 80 and len(val_set) == 20
    
    @pytest.mark.skipif(not TORCH_AVAILABLE, reason="torch not available")
    def test_mixed_imports(self):
        from qqgjyx import QQ
        from qqgjyx.data import split
        dataset = MockDataset(50)
        QQ.seed(123)
        train, val = split(dataset, val_ratio=0.3)
        assert len(train) == 35 and len(val) == 15


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
