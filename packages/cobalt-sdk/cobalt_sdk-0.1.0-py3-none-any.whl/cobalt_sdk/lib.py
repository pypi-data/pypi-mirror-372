from websockets.asyncio.client import connect, ClientConnection
import json


def proto_connect() -> ClientConnection:
    """
    Connect to the protocol WebSocket server.

    プロトコルWebSocketサーバーに接続します。
    """
    return connect("ws://localhost:23787")


def data_connect() -> ClientConnection:
    """
    Connect to the data WebSocket server.

    データWebSocketサーバーに接続します。
    """
    return connect("ws://localhost:9030")


async def subscribe_objects(ws: ClientConnection):
    """
    Subscribe to object detection data on a WebSocket connection.

    WebSocket接続でオブジェクト検出データを購読します。
    """
    msg = json.dumps([{"token": "COBJ", "subscribed": True}])
    await ws.send(msg)


import ctypes


class Object(ctypes.LittleEndianStructure):
    """
    Single object data structure

    単一オブジェクトのデータ構造
    """

    _fields_ = [
        ("x", ctypes.c_float),
        ("y", ctypes.c_float),
        ("z", ctypes.c_float),
        ("length", ctypes.c_float),
        ("width", ctypes.c_float),
        ("height", ctypes.c_float),
        ("theta", ctypes.c_float),
        ("classification", ctypes.c_uint32),
        ("object_id", ctypes.c_uint32),
    ]


class ObjectsHeader(ctypes.LittleEndianStructure):
    """
    Header portion of the Objects frame

    Objectsフレームのヘッダー部分
    """

    _fields_ = [
        ("magic", ctypes.c_char * 4),  # "COBJ" - マジック番号
        ("num_objects", ctypes.c_uint32),  # オブジェクト数
        ("sequence_id", ctypes.c_uint32),  # シーケンスID
    ]


class Objects(ctypes.LittleEndianStructure):
    """
    Complete Objects frame structure

    完全なObjectsフレーム構造
    """

    _fields_ = [
        ("magic", ctypes.c_char * 4),  # "COBJ" - マジック番号
        ("num_objects", ctypes.c_uint32),  # オブジェクト数
        ("sequence_id", ctypes.c_uint32),  # シーケンスID
        # Note: objects array needs to be handled separately due to dynamic size
        # 注意: オブジェクト配列は動的サイズのため別途処理が必要
    ]

    def __init__(self, num_objects: int = 0):
        super().__init__()
        self.magic = b"COBJ"
        self.num_objects = num_objects
        self.sequence_id = 0

    @classmethod
    def from_bytes(cls, data: bytes):
        """
        Parse Objects frame from binary data

        バイナリデータからObjectsフレームをパースします
        """
        # Parse header first
        # 最初にヘッダーをパースします
        header = ObjectsHeader.from_buffer_copy(data[: ctypes.sizeof(ObjectsHeader)])

        if header.magic != b"COBJ":
            raise ValueError(f"Invalid magic: {header.magic}")

        # Create Objects instance
        # Objectsインスタンスを作成します
        objects_frame = cls(header.num_objects)
        objects_frame.sequence_id = header.sequence_id

        # Parse objects array
        # オブジェクト配列をパースします
        objects_start = ctypes.sizeof(ObjectsHeader)
        object_size = ctypes.sizeof(Object)
        objects_data = []

        for i in range(header.num_objects):
            offset = objects_start + (i * object_size)
            obj_bytes = data[offset : offset + object_size]
            obj = Object.from_buffer_copy(obj_bytes)
            objects_data.append(obj)

        objects_frame.objects = objects_data
        return objects_frame

    def to_bytes(self) -> bytes:
        """
        Serialize Objects frame to binary data

        Objectsフレームをバイナリデータにシリアライズします
        """
        # Create header
        # ヘッダーを作成します
        header_data = bytes(self)

        # Serialize objects
        # オブジェクトをシリアライズします
        objects_data = b""
        for obj in getattr(self, "objects", []):
            objects_data += bytes(obj)

        return header_data + objects_data
