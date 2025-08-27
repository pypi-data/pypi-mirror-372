"""Main QQ class providing unified interface to qqgjyx utilities."""


class QQ:
    """Main interface for qqgjyx utilities."""
    
    @staticmethod
    def env():
        """Show environment info."""
        from .helper import env
        return env()
    
    @staticmethod
    def dev():
        """Get device info."""
        from .helper import dev
        return dev()
    
    @staticmethod
    def seed(value=42):
        """Set all seeds."""
        from .helper import seed
        return seed(value)
    
    @staticmethod
    def style():
        """Set matplotlib style."""
        from .visual import style
        return style()
    
    @staticmethod
    def split(dataset, val_ratio=0.2, seed=42):
        """Split dataset."""
        from .data import split
        return split(dataset, val_ratio, seed)
    
    @staticmethod
    def help():
        """Show available functions."""
        print("QQ Utilities:")
        print("  QQ.env()     - Show environment info")
        print("  QQ.dev()     - Get device info")
        print("  QQ.seed(n)   - Set seeds (default: 42)")
        print("  QQ.style()   - Set matplotlib style")
        print("  QQ.split(d)  - Split dataset")
        print("  QQ.help()    - Show this help")
        print("\nUsage:")
        print("  from qqgjyx import QQ")
        print("  QQ.env()")
        print("  QQ.seed(123)")
        print("  QQ.style()")
        print("  train, val = QQ.split(dataset)")


__all__ = ["QQ"]
