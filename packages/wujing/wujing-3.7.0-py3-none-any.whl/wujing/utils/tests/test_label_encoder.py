"""测试 LabelEncoderWrapper 和 MultiLabelBinarizerWrapper 的功能"""

import pytest
from wujing.utils.label_encoder import LabelEncoderWrapper, MultiLabelBinarizerWrapper


class TestLabelEncoderWrapper:
    """测试 LabelEncoderWrapper 类"""

    def test_consistent_encoding_with_same_labels(self):
        """测试相同的标签列表是否产生相同的编码结果"""
        labels1 = ["apple", "banana", "cherry", "apple", "banana"]
        labels2 = ["banana", "apple", "cherry", "banana", "apple"]
        
        encoder1 = LabelEncoderWrapper(labels1)
        encoder2 = LabelEncoderWrapper(labels2)
        
        # 测试相同标签的编码结果应该一致
        assert encoder1.transform("apple") == encoder2.transform("apple")
        assert encoder1.transform("banana") == encoder2.transform("banana")
        assert encoder1.transform("cherry") == encoder2.transform("cherry")
        
        # 测试逆向转换也应该一致
        for i in range(3):  # 假设有3个不同的标签
            try:
                assert encoder1.inverse_transform(i) == encoder2.inverse_transform(i)
            except ValueError:
                # 如果某个索引不存在，两个编码器都应该抛出相同的异常
                with pytest.raises(ValueError):
                    encoder2.inverse_transform(i)

    def test_basic_functionality(self):
        """测试基本的编码和解码功能"""
        labels = ["cat", "dog", "bird"]
        encoder = LabelEncoderWrapper(labels)
        
        # 测试编码
        encoded = encoder.transform("cat")
        assert isinstance(encoded, int)
        assert 0 <= encoded < len(set(labels))
        
        # 测试解码
        decoded = encoder.inverse_transform(encoded)
        assert decoded == "cat"

    def test_duplicate_labels_handling(self):
        """测试重复标签的处理"""
        labels = ["a", "b", "a", "c", "b", "a"]
        encoder = LabelEncoderWrapper(labels)
        
        # 确保每个唯一标签都能正确编码和解码
        unique_labels = list(set(labels))
        for label in unique_labels:
            encoded = encoder.transform(label)
            decoded = encoder.inverse_transform(encoded)
            assert decoded == label

    def test_invalid_label_transform(self):
        """测试转换不存在的标签时的行为"""
        labels = ["x", "y", "z"]
        encoder = LabelEncoderWrapper(labels)
        
        with pytest.raises(ValueError):
            encoder.transform("unknown")

    def test_invalid_index_inverse_transform(self):
        """测试逆转换无效索引时的行为"""
        labels = ["x", "y", "z"]
        encoder = LabelEncoderWrapper(labels)
        
        with pytest.raises(ValueError):
            encoder.inverse_transform(999)


class TestMultiLabelBinarizerWrapper:
    """测试 MultiLabelBinarizerWrapper 类"""

    def test_consistent_encoding_with_same_labels(self):
        """测试相同的标签列表是否产生相同的编码结果"""
        labels1 = [["apple", "banana"], ["cherry"], ["apple", "cherry"]]
        labels2 = [["banana", "apple"], ["cherry"], ["cherry", "apple"]]
        
        encoder1 = MultiLabelBinarizerWrapper(labels1)
        encoder2 = MultiLabelBinarizerWrapper(labels2)
        
        # 测试相同标签组合的编码结果应该一致
        test_labels = ["apple", "banana"]
        result1 = encoder1.transform(test_labels)
        result2 = encoder2.transform(test_labels)
        assert result1 == result2
        
        # 测试逆向转换也应该一致
        decoded1 = encoder1.inverse_transform(result1)
        decoded2 = encoder2.inverse_transform(result2)
        assert set(decoded1) == set(decoded2)  # 使用集合比较，因为顺序可能不同

    def test_basic_functionality(self):
        """测试基本的编码和解码功能"""
        labels = [["cat", "mammal"], ["dog", "mammal"], ["bird", "oviparous"]]
        encoder = MultiLabelBinarizerWrapper(labels)
        
        # 测试编码
        test_labels = ["cat", "mammal"]
        encoded = encoder.transform(test_labels)
        assert isinstance(encoded, list)
        assert all(isinstance(x, int) for x in encoded)
        assert all(x in [0, 1] for x in encoded)
        
        # 测试解码
        decoded = encoder.inverse_transform(encoded)
        assert set(decoded) == set(test_labels)

    def test_empty_label_list(self):
        """测试空标签列表的处理"""
        labels = [["cat"], ["dog"], []]
        encoder = MultiLabelBinarizerWrapper(labels)
        
        # 测试空列表的编码
        encoded = encoder.transform([])
        decoded = encoder.inverse_transform(encoded)
        assert decoded == []

    def test_single_label(self):
        """测试单个标签的处理"""
        labels = [["cat"], ["dog"], ["bird"]]
        encoder = MultiLabelBinarizerWrapper(labels)
        
        encoded = encoder.transform(["cat"])
        decoded = encoder.inverse_transform(encoded)
        assert decoded == ["cat"]

    def test_multiple_labels(self):
        """测试多个标签的处理"""
        labels = [["cat", "pet"], ["dog", "pet"], ["bird", "wild"]]
        encoder = MultiLabelBinarizerWrapper(labels)
        
        test_labels = ["cat", "pet"]
        encoded = encoder.transform(test_labels)
        decoded = encoder.inverse_transform(encoded)
        assert set(decoded) == set(test_labels)


class TestInitReturnValue:
    """测试 __init__ 方法的返回值问题"""

    def test_label_encoder_init_return(self):
        """测试 LabelEncoderWrapper 的 __init__ 是否正确返回实例"""
        labels = ["a", "b", "c"]
        encoder = LabelEncoderWrapper(labels)
        
        # __init__ 不应该返回 Self，而是应该能够正常初始化对象
        assert encoder is not None
        assert hasattr(encoder, 'le')
        assert hasattr(encoder, 'labels')

    def test_multi_label_binarizer_init_return(self):
        """测试 MultiLabelBinarizerWrapper 的 __init__ 是否正确返回实例"""
        labels = [["a", "b"], ["c"]]
        encoder = MultiLabelBinarizerWrapper(labels)
        
        # __init__ 不应该返回 Self，而是应该能够正常初始化对象
        assert encoder is not None
        assert hasattr(encoder, 'mlb')


if __name__ == "__main__":
    pytest.main([__file__])
