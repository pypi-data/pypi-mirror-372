"""
CLI for Volcanic Checker

This script allows the user to check volcano alert levels from the command line.
"""
import volcanic_checker as checker

def main():
    """
    Prompts the user for a volcano name, retrieves its alert level using
    VolcanoAlertChecker, and prints the result.
    """

    input_volcano_name = input("火山名を入力してください: ")
    alert = checker.get_alert_level_by_name(input_volcano_name)

    # 結果表示
    print(f"{alert.name} の警戒レベル: {alert.level}")
    print(f"情報URL: {alert.url or 'なし'}")
    print(f"取得日時: {alert.retrieved_at}")

if __name__ == "__main__":
    main()
