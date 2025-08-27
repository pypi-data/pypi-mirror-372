"""
Volcanic Checker Library

This package provides tools to fetch and handle volcanic activity alerts
from the Japan Meteorological Agency (JMA) website.
"""

from .checker import VolcanoAlertChecker

# デフォルトインスタンスを作成
_checker = VolcanoAlertChecker()

# モジュールレベルの関数を定義
def get_alert_level_by_name(name="富士山"):
    """
    Convenience function to fetch alert level using the default checker instance.
    """
    return _checker.get_alert_level_by_name(name)

# 必要なら他の関数も同様にラップ可能
__all__ = ["VolcanoAlertChecker", "get_alert_level_by_name"]
