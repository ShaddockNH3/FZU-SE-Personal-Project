"""
测试 deal_json.py 模块
"""

import pytest
import json as json_module
import os
import sys
import tempfile
from collections import Counter

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import importlib.util
spec = importlib.util.spec_from_file_location("deal_json", os.path.join(os.path.dirname(__file__), '..', 'json', 'deal_json.py'))
deal_json_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(deal_json_module)

get_mode_name = deal_json_module.get_mode_name
process_danmaku_data = deal_json_module.process_danmaku_data
STOP_WORDS = deal_json_module.STOP_WORDS


class TestDealJson:
    """测试数据处理功能"""
    
    def test_get_mode_name(self):
        """测试弹幕类型名称映射"""
        assert get_mode_name('1') == '普通滚动'
        assert get_mode_name('4') == '底部弹幕'
        assert get_mode_name('5') == '顶部弹幕'
        assert get_mode_name('7') == '高级弹幕'
        assert get_mode_name('99') == '未知类型(99)'
    
    def test_stopwords_not_empty(self):
        """测试停用词表不为空"""
        assert len(STOP_WORDS) > 0
        assert '的' in STOP_WORDS
        assert '是' in STOP_WORDS
        assert '666' in STOP_WORDS
    
    def test_stopwords_filter(self):
        """测试停用词过滤"""
        import jieba
        
        test_text = "这个视频666很不错啊"
        words = jieba.lcut(test_text)
        filtered = [w.strip() for w in words if w.strip() and w.strip() not in STOP_WORDS]
        
        assert '666' not in filtered
        assert '这个' not in filtered
    
    def test_process_empty_file(self):
        """测试处理不存在的文件"""
        result = process_danmaku_data('nonexistent_file.json')
        assert result == (None, None, None)
    
    def test_process_valid_data(self):
        """测试处理有效数据"""
        test_data = {
            'BV1test': {
                'cid': '123456',
                'danmaku_list': [
                    {
                        'content': '测试弹幕',
                        'attributes': '0.0,1,25,16777215,1234567890,0,abc123,0'
                    },
                    {
                        'content': '另一条弹幕',
                        'attributes': '1.5,1,25,16777215,1234567891,0,def456,0'
                    }
                ]
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json_module.dump(test_data, f, ensure_ascii=False)
            temp_file = f.name
        
        try:
            totals, freq_sentence, freq_word = process_danmaku_data(temp_file)
            
            assert totals is not None
            assert isinstance(totals, Counter)
            assert totals['1'] == 2
            
            assert freq_sentence is not None
            assert isinstance(freq_sentence, dict)
            assert '测试弹幕' in freq_sentence['1']
            
            assert freq_word is not None
            assert isinstance(freq_word, dict)
            
        finally:
            os.unlink(temp_file)
    
    def test_process_invalid_json(self):
        """测试处理无效JSON"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            f.write('invalid json content')
            temp_file = f.name
        
        try:
            result = process_danmaku_data(temp_file)
            assert result == (None, None, None)
        finally:
            os.unlink(temp_file)


if __name__ == '__main__':
    pytest.main(['-v', __file__])
