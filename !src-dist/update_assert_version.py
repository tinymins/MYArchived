#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新Lua文件中的AssertVersion调用版本号

此模块提供命令行接口，实际功能通过 plib.assert_version 模块实现
"""

import argparse

import plib.utils as utils
from plib.semver import Semver
from plib.assert_version import update_assert_version


def main():
    """
    主函数 - 只负责命令行参数处理和调用核心函数
    """
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(
        description="更新Lua文件中的AssertVersion调用版本号"
    )
    parser.add_argument("new_version", help="新版本号")
    parser.add_argument(
        "--diff",
        type=str,
        help="指定对比版本，只更新从该版本到当前提交之间变更的子插件",
    )
    parser.add_argument(
        "--force-changed",
        action="store_true",
        help="对变更的子插件强制更新版本约束（忽略是否满足要求）",
    )

    args = parser.parse_args()

    # 验证新版本格式
    try:
        Semver(args.new_version)
    except Exception:
        utils.exit_with_message(f"Error: Invalid version format: {args.new_version}")

    # 调用核心函数
    update_assert_version(
        new_version=args.new_version,
        diff_ver=args.diff,
        force_changed=args.force_changed,
        scan_all_if_no_changes=True,
    )


if __name__ == "__main__":
    main()
