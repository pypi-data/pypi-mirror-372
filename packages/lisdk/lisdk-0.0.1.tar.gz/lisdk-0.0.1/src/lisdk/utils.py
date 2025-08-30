from faker import Faker
import datetime
import secrets
import time


class ApiUtils:
    timef = "%Y-%m-%dT%H:%M:%S+08:00"
    fake = Faker("zh_CN")

    @classmethod
    def now(cls):
        return datetime.datetime.now().strftime(cls.timef)

    @classmethod
    def datetime(cls, weeks=0, days=0, hours=0, minutes=0, seconds=0, microseconds=0, milliseconds=0):
        tdt = datetime.timedelta(
            weeks=weeks,
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            microseconds=microseconds,
            milliseconds=milliseconds
        )
        return (datetime.datetime.now() + tdt).strftime(cls.timef)

    @classmethod
    def num_string(cls, l=23):
        timestamp = str(time.time_ns())
        v = timestamp + str(str(secrets.randbits(12)))
        start = len(v) - l
        if start < 0:
            start = 0
        return v[start:len(v)]

    @classmethod
    def mobiles(cls, l=10):
        num = [cls.fake.phone_number() for _ in range(l)]
        if l == 1:
            return num[0]
        return num
    
    @classmethod
    def deep_update(cls, source_dict, target_dict):
        """
        递归地将目标字典的内容更新到源字典中
        
        支持以下情况：
        1. 嵌套字典的合并
        2. 列表的合并（如果目标字典中的列表不为空，则替换源字典中的列表）
        3. 列表中包含字典的情况（如果列表长度相同，则递归合并对应位置的字典）
        
        Args:
            source_dict: 源字典，将被更新
            target_dict: 目标字典，提供更新内容
            
        Returns:
            更新后的源字典
        """
        for key, value in target_dict.items():
            if key in source_dict:
                if isinstance(source_dict[key], dict) and isinstance(value, dict):
                    # 如果两个都是字典，递归合并
                    cls.deep_update(source_dict[key], value)
                elif isinstance(source_dict[key], list) and isinstance(value, list):
                    # 如果两个都是列表
                    if len(value) > 0:  # 如果目标列表不为空
                        if len(source_dict[key]) == len(value) and all(isinstance(s, dict) and isinstance(t, dict) for s, t in zip(source_dict[key], value)):
                            # 如果列表长度相同且所有元素都是字典，则递归合并对应位置的字典
                            for i, (source_item, target_item) in enumerate(zip(source_dict[key], value)):
                                cls.deep_update(source_item, target_item)
                        else:
                            # 否则替换整个列表
                            source_dict[key] = value
                    else:
                        pass
                else:
                    # 其他情况直接更新
                    source_dict[key] = value
            else:
                # 如果键不存在，直接添加
                source_dict[key] = value
        
        return source_dict

    @classmethod
    def ini_config(cls, section, option):
        path = '/Users/lizhankang/workSpace/selfProject/pythonProject/gan-zhong-xue/pytest.ini'
        return cls._read_ini(path)

    @classmethod
    def _read_ini(cls, path):
        import configparser
        config = configparser.ConfigParser()
        config.read(path, encoding='utf-8')
        return config
    
def a():
    print('a')

if __name__ == '__main__':
    # data = ApiBox.num_string(25)
    # print(data)
    # print(len(data))
    # 示例：生成一个长度为10的随机字符串
    pass
    data = ApiUtils.mobiles(10)
    print(data)
    # help(a)
    help(ApiUtils.datetime)