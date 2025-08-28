#!/usr/bin/env python3
import argparse
import sys
import json
from .executor import SocExecutor


def main():
    """命令行入口函数"""
    parser = argparse.ArgumentParser(
        description='SOC工具执行器 - 执行本地Python文件并通过HTTP API提交',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  soc-executor script.py
  soc-executor script.py --params '{"key": "value"}'
  soc-executor /path/to/script.py
  soc-executor script.py --raise-on-error  # 抛出异常模式
        """
    )
    
    parser.add_argument(
        'file',
        help='要执行的Python文件路径'
    )
    
    parser.add_argument(
        '--params', '-p',
        type=str,
        default='{}',
        help='传递给脚本的参数(JSON格式), 默认为空对象'
    )
    
    parser.add_argument(
        '--raise-on-error',
        action='store_true',
        help='遇到错误时抛出异常而不是打印错误信息'
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='soc-executor 0.1.0'
    )
    
    args = parser.parse_args()
    
    # 获取文件路径
    file_path = args.file
    
    # 解析参数
    try:
        params = json.loads(args.params)
    except json.JSONDecodeError as e:
        print(f"参数解析错误: {e}", file=sys.stderr)
        sys.exit(1)
    
    # 执行工具
    executor = SocExecutor()
    
    if params:
        print(f"传入参数: {json.dumps(params, ensure_ascii=False)}")
        print()
    
    try:
        result = executor.execute_python_file(file_path, params, raise_on_error=args.raise_on_error)
        
        # 根据结果设置退出码
        if 'error' in result or result.get('code', 0) != 0:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except Exception as e:
        # 如果启用了raise_on_error，异常会被抛出并显示完整的堆栈信息
        if args.raise_on_error:
            raise
        else:
            # 否则正常处理
            sys.exit(1)


if __name__ == '__main__':
    main()