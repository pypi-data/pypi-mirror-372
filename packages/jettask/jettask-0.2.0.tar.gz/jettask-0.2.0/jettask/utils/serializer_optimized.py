"""
优化的 MessagePack 序列化工具模块
直接使用二进制，避免 Base64 开销
"""
import msgpack


def dumps(obj):
    """序列化对象为字节"""
    return msgpack.packb(obj, use_bin_type=True)


def loads(data):
    """反序列化字节为对象"""
    if isinstance(data, str):
        # 兼容性：如果收到字符串，尝试作为 latin-1 解码
        data = data.encode('latin-1')
    return msgpack.unpackb(data, raw=False, strict_map_key=False)


# 为了兼容性，保留 dumps_str/loads_str 名称，但不再使用 base64
def dumps_str(obj):
    """序列化对象为字节（不再使用 base64）"""
    return msgpack.packb(obj, use_bin_type=True)


def loads_str(data):
    """反序列化字节为对象"""
    return msgpack.unpackb(data, raw=False, strict_map_key=False)


# 导出使用的序列化器名称
SERIALIZER = "msgpack_binary"