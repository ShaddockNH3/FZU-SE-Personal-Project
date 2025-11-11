"""
性能分析脚本
使用cProfile分析程序性能瓶颈
"""

import cProfile
import pstats
import io
from datetime import datetime


def profile_function(func, *args, **kwargs):
    """
    分析函数性能
    
    Args:
        func: 要分析的函数
        *args: 函数参数
        **kwargs: 函数关键字参数
    """
    profiler = cProfile.Profile()
    profiler.enable()
    
    result = func(*args, **kwargs)
    
    profiler.disable()
    
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    ps.print_stats(30)
    
    print(s.getvalue())
    
    return result


def analyze_module(module_name, test_data=None):
    """分析指定模块的性能"""
    print(f"\n{'='*60}")
    print(f"性能分析: {module_name}")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print('='*60)
    
    if module_name == 'get_bv':
        from bugs.get_bv import get_bilibili_bvs
        print("\n分析 BV号爬取模块...")
        print("注意: 实际运行会启动浏览器，耗时较长")
        print("建议使用小规模测试数据")
        
    elif module_name == 'get_cid':
        from bugs.get_cid import get_cid
        print("\n分析 CID获取模块...")
        if test_data:
            profile_function(get_cid, test_data)
            
    elif module_name == 'deal_json':
        from json.deal_json import process_danmaku_data
        print("\n分析 数据统计模块...")
        profile_function(process_danmaku_data, 'json/LLM_danmaku_realtime_save.json')
        
    elif module_name == 'cloud':
        from cloud.cloud import create_word_cloud
        print("\n分析 词云生成模块...")
        profile_function(create_word_cloud, 
                        'json/LLM_danmaku_realtime_save.json',
                        'test_wordcloud.png',
                        'mask.png')


def main():
    """主函数"""
    print("性能分析工具")
    print("="*60)
    print("1. BV号爬取模块 (get_bv.py)")
    print("2. CID获取模块 (get_cid.py)")
    print("3. 弹幕爬取模块 (get_danmaku.py)")
    print("4. 数据统计模块 (deal_json.py)")
    print("5. 词云生成模块 (cloud.py)")
    print("="*60)
    
    print("\n提示: 实际性能分析需要运行完整流程")
    print("建议使用小规模测试数据进行分析")
    print("\n使用方法:")
    print("  python performance_profiler.py")
    print("\n或使用cProfile:")
    print("  python -m cProfile -o stats.prof bugs/get_bv.py")
    print("  python -c \"import pstats; p=pstats.Stats('stats.prof'); p.sort_stats('cumulative').print_stats(20)\"")


if __name__ == '__main__':
    main()
