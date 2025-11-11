"""
测试 get_cid.py 模块
"""

import pytest
import responses
from bugs.get_cid import get_cid


class TestGetCid:
    """测试CID获取功能"""
    
    @responses.activate
    def test_get_cid_success(self):
        """测试成功获取CID"""
        test_url = 'https://www.bilibili.com/video/BV1xx411c7mD'
        responses.add(
            responses.GET,
            test_url,
            body='<!DOCTYPE html><html><head><script>window.__INITIAL_STATE__={"cid":123456}</script></head></html>',
            status=200
        )
        
        result = get_cid(test_url)
        assert result == '123456'
    
    @responses.activate
    def test_get_cid_404(self):
        """测试视频不存在"""
        test_url = 'https://www.bilibili.com/video/BV1invalid'
        responses.add(
            responses.GET,
            test_url,
            status=404
        )
        
        with pytest.raises(Exception, match="Failed to fetch"):
            get_cid(test_url)
    
    @responses.activate
    def test_get_cid_no_cid(self):
        """测试页面中没有CID"""
        test_url = 'https://www.bilibili.com/video/BV1xx411c7mD'
        responses.add(
            responses.GET,
            test_url,
            body='<!DOCTYPE html><html><body>No CID here</body></html>',
            status=200
        )
        
        with pytest.raises(Exception, match="Failed to find cid"):
            get_cid(test_url)
    
    def test_get_cid_invalid_url(self):
        """测试无效URL"""
        with pytest.raises(Exception):
            get_cid('not_a_url')


if __name__ == '__main__':
    pytest.main(['-v', __file__])
