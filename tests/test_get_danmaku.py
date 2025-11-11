"""
测试 get_danmaku.py 模块
"""

import pytest
import responses
import zlib
from bugs.get_danmaku import fetch_danmaku_xml


class TestGetDanmaku:
    """测试弹幕获取功能"""
    
    @responses.activate
    def test_fetch_danmaku_success(self):
        """测试成功获取弹幕"""
        test_cid = '123456'
        xml_data = '<?xml version="1.0" encoding="UTF-8"?><i><d p="0,1,25,16777215,1234567890,0,abc,0">测试弹幕</d></i>'
        compressed = zlib.compress(xml_data.encode('utf-8'), -zlib.MAX_WBITS)
        
        responses.add(
            responses.GET,
            'https://api.bilibili.com/x/v1/dm/list.so',
            body=compressed,
            status=200
        )
        
        result = fetch_danmaku_xml(test_cid)
        assert result is not None
        assert isinstance(result, list)
        assert len(result) > 0
        assert result[0]['content'] == '测试弹幕'
    
    @responses.activate
    def test_fetch_danmaku_412(self):
        """测试触发风控"""
        test_cid = '123456'
        responses.add(
            responses.GET,
            'https://api.bilibili.com/x/v1/dm/list.so',
            status=412
        )
        
        result = fetch_danmaku_xml(test_cid)
        assert result == "RATE_LIMIT"
    
    @responses.activate
    def test_fetch_danmaku_timeout(self):
        """测试超时"""
        test_cid = '123456'
        responses.add(
            responses.GET,
            'https://api.bilibili.com/x/v1/dm/list.so',
            body=Exception('Timeout')
        )
        
        result = fetch_danmaku_xml(test_cid)
        assert result is None
    
    @responses.activate
    def test_fetch_danmaku_empty(self):
        """测试无弹幕"""
        test_cid = '123456'
        xml_data = '<?xml version="1.0" encoding="UTF-8"?><i></i>'
        compressed = zlib.compress(xml_data.encode('utf-8'), -zlib.MAX_WBITS)
        
        responses.add(
            responses.GET,
            'https://api.bilibili.com/x/v1/dm/list.so',
            body=compressed,
            status=200
        )
        
        result = fetch_danmaku_xml(test_cid)
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 0


if __name__ == '__main__':
    pytest.main(['-v', __file__])
