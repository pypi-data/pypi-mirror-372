import argparse

from . import _core


def main():
    parser = argparse.ArgumentParser(
        description="SeedKey - the Activation Tool of SeedMath"
    )

    # 添加产品选择选项组
    product_group = parser.add_mutually_exclusive_group(required=False)
    product_group.add_argument(
        "--seedsat", action="store_true", help="Activate the SeedSAT solver(use with --cluster for cluster mode, use with --offline for offline activation mode), format: [cluster_type] [offline_mode] <activation_code>"
    )
    product_group.add_argument(
        "--seedsmt", action="store_true", help="Activate the SeedSMT solver(use with --cluster for cluster mode, use with --offline for offline activation mode), format: [cluster_type] [offline_mode] <activation_code>"
    )
    product_group.add_argument(
        "--seedkcompiler", action="store_true", help="Activate the SeedKCompiler solver (use with --cluster for cluster mode, use with --offline for offline activation mode), format: [cluster_type] [offline_mode] <activation_code>"
    )
    product_group.add_argument(
        "--seedmip", action="store_true", help="Activate the SeedMIP solver(use with --cluster for cluster mode, use with --offline for offline activation mode), format: [cluster_type] [offline_mode] <activation_code>"
    )
    product_group.add_argument(
        "--seedhypart", action="store_true", help="Activate the SeedHypart solver(use with --cluster for cluster mode, use with --offline for offline activation mode), format: [cluster_type] [offline_mode] <activation_code>"
    )
    product_group.add_argument(
        "--server",
        type=str,
        help="Set the license server hosts, e.g. http://127.0.0.1:15200,http://192.168.1.1:15200",
    )
    product_group.add_argument(
        "--check",
        action="store_true",
        help="Check if the product license is valid (use with --cluster for cluster mode)",
    )
    product_group.add_argument(
        "--server-health",
        action="store_true",
        help="Display the health status of license servers",
    )
    product_group.add_argument(
        "--hwid",
        action="store_true",
        help="Display hardware ID information",
    )

    # 添加激活码参数
    parser.add_argument("activation_code", type=str, nargs="?", help="Activation code")

    # 添加集群选项
    parser.add_argument(
        "--cluster", action="store_true", help="Additional option for activation and --check to enable cluster mode"
    )
    
    # 添加离线模式选项
    parser.add_argument(
        "--offline", action="store_true", help="Additional option for activation to activate the product in offline mode"
    )

    args = parser.parse_args()

    # 确定激活类型
    cluster_type = 1 if args.cluster else 0
    
    # 确保cluster_type有效，不为null
    if cluster_type != 0 and cluster_type != 1:
        cluster_type = 0  # 默认为单机版

    # 处理设置服务器的情况
    if args.server:
        _core.set_license_server(args.server)
        return 0
    # 处理检查许可证的情况
    if args.check:
        if not args.activation_code:
            print("Error: Product name is required for --check")
            parser.print_help()
            return -1
        valid, msg = _core.check(args.activation_code, cluster_type)
        print(msg)
        return 0
    # 处理显示服务器健康状态的情况
    if args.server_health:
        _core.display_server_health()
        return 0
    # 处理显示机器信息的情况
    if args.hwid:
        machine_info = _core.get_machine_info()
        print("Hardware ID:")
        print(machine_info)
        return 0

    # 确保有激活码
    if not args.activation_code:
        parser.print_help()
        return -1

    # 确定要激活的产品
    product = None
    if args.seedmip:
        product = "seedmip"
    elif args.seedsat:
        product = "seedsat"
    elif args.seedsmt:
        product = "seedsmt"
    elif args.seedkcompiler:
        product = "seedkcompiler"
    elif args.seedhypart:
        product = "seedhypart"
    if not product:
        parser.print_help()
        return -1

    # 判断是否为离线模式
    if args.offline:
        # 调用离线保存授权文件函数
        try:
            if _core.save_auth_file_offline(args.activation_code, product, cluster_type):
                return 0
        except Exception as e:
            print(e)
            return -1
    else:
        # 调用激活函数
        if _core.activate(product, args.activation_code, cluster_type):
            return 0
        return -1


if __name__ == "__main__":
    import sys

    sys.exit(main())