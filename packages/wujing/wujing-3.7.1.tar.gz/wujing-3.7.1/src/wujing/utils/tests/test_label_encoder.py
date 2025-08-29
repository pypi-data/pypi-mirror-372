"""测试 ConsistentLabelEncoder 和 ConsistentMultiLabelBinarizer 的功能"""

import pytest
from wujing.utils.label_encoder import ConsistentLabelEncoder, ConsistentMultiLabelBinarizer


class TestConsistentLabelEncoder:
    """测试 ConsistentLabelEncoder 类"""

    def test_consistent_encoding_with_same_labels(self):
        """测试相同的标签列表是否产生相同的编码结果"""
        labels1 = ["apple", "banana", "cherry", "apple", "banana"]
        labels2 = ["banana", "apple", "cherry", "banana", "apple"]
        
        encoder1 = ConsistentLabelEncoder(labels1)
        encoder2 = ConsistentLabelEncoder(labels2)
        
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
        encoder = ConsistentLabelEncoder(labels)
        
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
        encoder = ConsistentLabelEncoder(labels)
        
        # 确保每个唯一标签都能正确编码和解码
        unique_labels = list(set(labels))
        for label in unique_labels:
            encoded = encoder.transform(label)
            decoded = encoder.inverse_transform(encoded)
            assert decoded == label

    def test_invalid_label_transform(self):
        """测试转换不存在的标签时的行为"""
        labels = ["x", "y", "z"]
        encoder = ConsistentLabelEncoder(labels)
        
        with pytest.raises(ValueError):
            encoder.transform("unknown")

    def test_invalid_index_inverse_transform(self):
        """测试逆转换无效索引时的行为"""
        labels = ["x", "y", "z"]
        encoder = ConsistentLabelEncoder(labels)
        
        with pytest.raises(ValueError):
            encoder.inverse_transform(999)

    def test_get_mapping_default(self):
        """测试get_mapping方法的默认行为（label到id）"""
        labels = ["apple", "banana", "cherry", "apple"]
        encoder = ConsistentLabelEncoder(labels)
        
        # 获取映射关系
        mapping = encoder.get_mapping()
        
        # 验证返回的是字典类型
        assert isinstance(mapping, dict)
        
        # 验证映射关系的正确性
        unique_labels = sorted(list(set(labels)))
        assert len(mapping) == len(unique_labels)
        
        # 验证每个标签都在映射中，且映射结果与transform方法一致
        for label in unique_labels:
            assert label in mapping
            assert mapping[label] == encoder.transform(label)
        
        # 验证所有ID都是不同的
        ids = list(mapping.values())
        assert len(ids) == len(set(ids))
        
        # 验证ID的范围是合理的
        assert all(0 <= id_val < len(unique_labels) for id_val in ids)
        
        # 验证键值类型
        assert isinstance(list(mapping.keys())[0], str)  # 键应该是字符串
        assert isinstance(list(mapping.values())[0], int)  # 值应该是整数

    def test_get_mapping_empty(self):
        """测试空标签列表的映射关系"""
        labels = []
        encoder = ConsistentLabelEncoder(labels)
        
        assert encoder.get_mapping() == {}
        assert encoder.get_mapping(reverse=True) == {}

    def test_get_mapping_reverse(self):
        """测试get_mapping方法的反向映射（id到label）"""
        labels = ["apple", "banana", "cherry", "apple"]
        encoder = ConsistentLabelEncoder(labels)
        
        # 获取映射关系
        mapping = encoder.get_mapping(reverse=True)
        
        # 验证返回的是字典类型
        assert isinstance(mapping, dict)
        
        # 验证映射关系的正确性
        unique_labels = sorted(list(set(labels)))
        assert len(mapping) == len(unique_labels)
        
        # 验证每个ID都在映射中，且映射结果与inverse_transform方法一致
        for id_val in mapping.keys():
            assert isinstance(id_val, int)
            assert mapping[id_val] == encoder.inverse_transform(id_val)
        
        # 验证所有标签都是不同的
        labels_list = list(mapping.values())
        assert len(labels_list) == len(set(labels_list))
        
        # 验证与正向映射的对应关系
        forward_mapping = encoder.get_mapping()
        for label, id_val in forward_mapping.items():
            assert mapping[id_val] == label
            
        # 验证键值类型
        assert isinstance(list(mapping.keys())[0], int)  # 键应该是整数
        assert isinstance(list(mapping.values())[0], str)  # 值应该是字符串

    def test_get_mapping_consistency(self):
        """测试get_mapping方法两个方向的一致性"""
        labels = ["apple", "banana", "cherry", "apple"]
        encoder = ConsistentLabelEncoder(labels)
        
        forward_mapping = encoder.get_mapping(reverse=False)
        reverse_mapping = encoder.get_mapping(reverse=True)
        
        # 验证两个映射互为反向
        for label, id_val in forward_mapping.items():
            assert reverse_mapping[id_val] == label


class TestConsistentMultiLabelBinarizer:
    """测试 ConsistentMultiLabelBinarizer 类"""

    def test_consistent_encoding_with_same_labels(self):
        """测试相同的标签列表是否产生相同的编码结果"""
        labels1 = [["apple", "banana"], ["cherry"], ["apple", "cherry"]]
        labels2 = [["banana", "apple"], ["cherry"], ["cherry", "apple"]]
        
        encoder1 = ConsistentMultiLabelBinarizer(labels1)
        encoder2 = ConsistentMultiLabelBinarizer(labels2)
        
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
        encoder = ConsistentMultiLabelBinarizer(labels)
        
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
        encoder = ConsistentMultiLabelBinarizer(labels)
        
        # 测试空列表的编码
        encoded = encoder.transform([])
        decoded = encoder.inverse_transform(encoded)
        assert decoded == []

    def test_single_label(self):
        """测试单个标签的处理"""
        labels = [["cat"], ["dog"], ["bird"]]
        encoder = ConsistentMultiLabelBinarizer(labels)
        
        encoded = encoder.transform(["cat"])
        decoded = encoder.inverse_transform(encoded)
        assert decoded == ["cat"]

    def test_multiple_labels(self):
        """测试多个标签的处理"""
        labels = [["cat", "pet"], ["dog", "pet"], ["bird", "wild"]]
        encoder = ConsistentMultiLabelBinarizer(labels)
        
        test_labels = ["cat", "pet"]
        encoded = encoder.transform(test_labels)
        decoded = encoder.inverse_transform(encoded)
        assert set(decoded) == set(test_labels)

    def test_get_mapping_default(self):
        """测试get_mapping方法的默认行为（label到索引）"""
        labels = [["apple", "fruit"], ["banana", "fruit"], ["carrot", "vegetable"]]
        encoder = ConsistentMultiLabelBinarizer(labels)
        
        # 获取映射关系
        mapping = encoder.get_mapping()
        
        # 验证返回的是字典类型
        assert isinstance(mapping, dict)
        
        # 获取所有唯一标签
        all_labels = set()
        for label_list in labels:
            all_labels.update(label_list)
        unique_labels = sorted(list(all_labels))
        
        # 验证映射关系的正确性
        assert len(mapping) == len(unique_labels)
        
        # 验证每个标签都在映射中
        for label in unique_labels:
            assert label in mapping
            assert isinstance(mapping[label], int)
        
        # 验证所有索引都是不同的且在合理范围内
        indices = list(mapping.values())
        assert len(indices) == len(set(indices))
        assert all(0 <= idx < len(unique_labels) for idx in indices)
        
        # 验证索引与classes_的对应关系
        for label, idx in mapping.items():
            assert encoder.mlb.classes_[idx] == label
            
        # 默认情况下应该返回 label -> index 的映射
        if mapping:  # 只有在映射不为空时才检查类型
            assert isinstance(list(mapping.keys())[0], str)  # 键应该是字符串
            assert isinstance(list(mapping.values())[0], int)  # 值应该是整数

    def test_get_mapping_empty(self):
        """测试空标签列表的映射关系"""
        labels = [[]]
        encoder = ConsistentMultiLabelBinarizer(labels)
        
        assert encoder.get_mapping() == {}
        assert encoder.get_mapping(reverse=True) == {}

    def test_get_mapping_reverse(self):
        """测试get_mapping方法的反向映射（索引到label）"""
        labels = [["apple", "fruit"], ["banana", "fruit"], ["carrot", "vegetable"]]
        encoder = ConsistentMultiLabelBinarizer(labels)
        
        # 获取映射关系
        mapping = encoder.get_mapping(reverse=True)
        
        # 验证返回的是字典类型
        assert isinstance(mapping, dict)
        
        # 获取所有唯一标签
        all_labels = set()
        for label_list in labels:
            all_labels.update(label_list)
        unique_labels = sorted(list(all_labels))
        
        # 验证映射关系的正确性
        assert len(mapping) == len(unique_labels)
        
        # 验证每个索引都在映射中
        for idx in mapping.keys():
            assert isinstance(idx, int)
            assert 0 <= idx < len(unique_labels)
            assert mapping[idx] == encoder.mlb.classes_[idx]
        
        # 验证所有标签都是不同的且在合理范围内
        labels_list = list(mapping.values())
        assert len(labels_list) == len(set(labels_list))
        
        # 验证与正向映射的对应关系
        forward_mapping = encoder.get_mapping()
        for label, idx in forward_mapping.items():
            assert mapping[idx] == label
            
        # reverse=True 应该返回 index -> label 的映射
        if mapping:  # 只有在映射不为空时才检查类型
            assert isinstance(list(mapping.keys())[0], int)  # 键应该是整数
            assert isinstance(list(mapping.values())[0], str)  # 值应该是字符串

    def test_get_mapping_consistency(self):
        """测试get_mapping方法两个方向的一致性"""
        labels = [["apple", "fruit"], ["banana", "fruit"], ["carrot", "vegetable"]]
        encoder = ConsistentMultiLabelBinarizer(labels)
        
        forward_mapping = encoder.get_mapping(reverse=False)
        reverse_mapping = encoder.get_mapping(reverse=True)
        
        # 验证两个映射互为反向
        for label, idx in forward_mapping.items():
            assert reverse_mapping[idx] == label


class TestInitReturnValue:
    """测试 __init__ 方法的返回值问题"""

    def test_label_encoder_init_return(self):
        """测试 ConsistentLabelEncoder 的 __init__ 是否正确返回实例"""
        labels = ["a", "b", "c"]
        encoder = ConsistentLabelEncoder(labels)
        
        # __init__ 不应该返回 Self，而是应该能够正常初始化对象
        assert encoder is not None
        assert hasattr(encoder, 'le')
        assert hasattr(encoder, 'labels')

    def test_multi_label_binarizer_init_return(self):
        """测试 ConsistentMultiLabelBinarizer 的 __init__ 是否正确返回实例"""
        labels = [["a", "b"], ["c"]]
        encoder = ConsistentMultiLabelBinarizer(labels)
        
        # __init__ 不应该返回 Self，而是应该能够正常初始化对象
        assert encoder is not None
        assert hasattr(encoder, 'mlb')


if __name__ == "__main__":
    pytest.main([__file__])
