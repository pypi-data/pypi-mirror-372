"""
MessagePack序列化工具模块
直接使用二进制，无 Base64 开销
"""
import msgpack


def dumps(obj):
    """序列化对象为字节"""
    return msgpack.packb(obj, use_bin_type=True)


def loads(data):
    """反序列化字节为对象"""
    return msgpack.unpackb(data, raw=False, strict_map_key=False)


# dumps_str 和 loads_str 直接使用二进制，不再使用 base64
def dumps_str(obj):
    """序列化对象为字节（直接二进制）"""
    return msgpack.packb(obj, use_bin_type=True)


def loads_str(data):
    """反序列化字节为对象"""
    return msgpack.unpackb(data, raw=False, strict_map_key=False)


# 导出使用的序列化器名称
SERIALIZER = "msgpack_binary"