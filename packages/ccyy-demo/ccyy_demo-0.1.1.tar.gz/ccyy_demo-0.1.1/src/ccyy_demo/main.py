import argparse

def main():
    """CLI 工具的主入口函数"""
    parser = argparse.ArgumentParser(
        description="一个由 ccyy-demo 创建的、使用 uv 构建的简单 CLI 工具。"
    )
    parser.add_argument(
        "--name",
        default="World",
        help="The name to greet."
    )
    args = parser.parse_args()
    print(f"Hello, {args.name}! This is ccyy-demo speaking.")

if __name__ == "__main__":
    main()
