"""
测试运行脚本
运行所有单元测试并生成覆盖率报告
"""

import subprocess
import sys
import os
from datetime import datetime


def run_tests():
    """运行所有测试"""
    print("="*60)
    print("单元测试运行")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    commands = [
        {
            'desc': '运行所有测试',
            'cmd': 'pytest tests/ -v'
        },
        {
            'desc': '生成覆盖率报告',
            'cmd': 'pytest tests/ --cov=bugs --cov=cloud --cov=json --cov-report=term --cov-report=html'
        }
    ]
    
    for item in commands:
        print(f"\n{item['desc']}...")
        print(f"命令: {item['cmd']}")
        print("-"*60)
        
        result = subprocess.run(
            item['cmd'],
            shell=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        if result.returncode != 0:
            print(f"警告: {item['desc']} 返回非零退出码")
    
    print("\n" + "="*60)
    print("测试完成")
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    print("\n覆盖率报告已生成到 htmlcov/ 目录")
    print("使用浏览器打开 htmlcov/index.html 查看详细报告")


if __name__ == '__main__':
    run_tests()
