"""
代码质量检查脚本
运行多个代码质量分析工具，生成综合报告
"""

import subprocess
import sys
from datetime import datetime


def run_command(command, description):
    """运行命令并显示结果"""
    print(f"\n{'='*60}")
    print(f"正在运行: {description}")
    print(f"命令: {command}")
    print('='*60)
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(f"警告: {result.stderr}")
            
        return result.returncode == 0
    except Exception as e:
        print(f"执行失败: {e}")
        return False


def main():
    """主函数"""
    print(f"\n代码质量检查工具")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    checks = [
        {
            'command': 'pylint bugs/ cloud/ json/ --disable=R0915,W0703,C0301',
            'description': 'Pylint 静态代码分析',
            'required': False
        },
        {
            'command': 'flake8 bugs/ cloud/ json/ --max-line-length=120 --extend-ignore=E402',
            'description': 'Flake8 代码风格检查',
            'required': False
        },
        {
            'command': 'bandit -r bugs/ cloud/ json/ -ll',
            'description': 'Bandit 安全漏洞扫描',
            'required': False
        }
    ]
    
    results = []
    
    for check in checks:
        success = run_command(check['command'], check['description'])
        results.append({
            'description': check['description'],
            'success': success
        })
    
    print(f"\n{'='*60}")
    print("检查结果汇总")
    print('='*60)
    
    for result in results:
        status = "✓ 通过" if result['success'] else "⚠ 有警告"
        print(f"{result['description']}: {status}")
    
    print(f"\n结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_passed = all(r['success'] for r in results)
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
