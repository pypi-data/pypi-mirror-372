import gzip
import base64
from io import BytesIO


def compress(data: bytes) -> bytes:
    try:
        memory_stream = BytesIO()
        with gzip.GzipFile(fileobj=memory_stream, mode="wb") as gzip_stream:
            gzip_stream.write(data)
        return memory_stream.getvalue()
    except Exception as ex:
        raise Exception(str(ex))


def decompress(data: bytes) -> bytes:
    try:
        memory_stream = BytesIO(data)
        with gzip.GzipFile(fileobj=memory_stream, mode="rb") as gzip_stream:
            return gzip_stream.read()
    except Exception as ex:
        raise Exception(str(ex))


def compress_string(string: str) -> str:
    compressed_data = compress(string.encode("utf-8"))
    return base64.b64encode(compressed_data).decode("utf-8")


def decompress_string(string: str) -> str:
    compressed_data = base64.b64decode(string)
    decompressed_data = decompress(compressed_data)
    return decompressed_data.decode("utf-8")
