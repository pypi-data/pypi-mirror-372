import argparse
import sys

from . import _core


def main():
    """
    License Server入口函数
    启动Seed许可证服务器
    """
    parser = argparse.ArgumentParser(
        description="SeedKey License Server - When no arguments are provided, the License Server will start by default"
    )

    args = parser.parse_args()

    try:
        # 在进入程序时，初始化数据库
        _core.init_db()
        # Default: start license server
        print("Starting SeedKey License Server...")
        if _core.start_license_server():
            return 0
        return -1
    except Exception as e:
        print(f"Error: {e}")
        return -1

    return 0


if __name__ == "__main__":
    sys.exit(main()) 