# Hợp đồng module (chữ ký hàm đóng băng)

Quy ước kiểu: xem `docs/conventions.md`.

```python
from typing import Union
ByteData = Union[bytes, bytearray, memoryview]
State = bytearray            # đúng 16 byte, column-major: idx = 4*c + r
RoundKeys = list[bytes]      # 11 phần tử, mỗi phần tử 16 byte
```

## TV1 — `core/gf256.py`, `core/matrix_state.py`

```python
# gf256.py
POLY: int = 0x11B
def xtime(a: int) -> int: ...
def gmul(a: int, b: int) -> int: ...

# matrix_state.py
def idx(r: int, c: int) -> int: ...                 # 4*c + r
def get(state: State, r: int, c: int) -> int: ...
def bytes_to_state(data: bytes) -> State: ...       # ValueError nếu len != 16
def state_to_bytes(state: State) -> bytes: ...
```

## TV2 — `aes/sbox.py`, `aes/transforms.py`

```python
SBOX: tuple[int, ...]                               # 256 phần tử

def sub_bytes(state: State) -> State: ...
def shift_rows(state: State) -> State: ...
def mix_columns(state: State) -> State: ...
def add_round_key(state: State, round_key: bytes) -> State: ...
```

## TV3 — `aes/key_schedule.py`, `aes/standard_aes.py`

```python
def expand_key(key: bytes) -> RoundKeys: ...        # key 16 byte -> K0..K10

def encrypt_block(round_keys: RoundKeys, block: bytes) -> bytes: ...
# AES-128 chuẩn: ARK(K0), 9 vòng đầy đủ, vòng 10 không MixColumns.
# Chỉ dùng cho IV setup.
```

## TV4 — `lex/extractor.py`, `lex/round_engine.py`

```python
# Chỉ số byte (0..15) theo thứ tự ghi vào keystream (conventions.md, T3/T8)
LEAK_INDICES_ODD:  tuple[int, int, int, int] = (10, 2, 8, 0)    # vòng 1,3,5,7,9
LEAK_INDICES_EVEN: tuple[int, int, int, int] = (11, 3, 9, 1)    # vòng 2,4,6,8,10

def extract_leak(state: State, round_no: int) -> bytes: ...   # 4 byte, round_no 1..10

def lex_round(state: State, round_key: bytes, *, mix_columns: bool) -> State: ...

def lex_cycle(state: State, round_keys: RoundKeys) -> tuple[bytes, State]: ...
# Trả về (40 byte keystream, trạng thái đầu vào cho chu kỳ kế).
# Mọi vòng: SB→SR→MC→ARK(K_r), trích sau ARK; không K0; S10 là đầu vào chu kỳ sau.
```

## TV5 — `lex/validation.py`, `lex/context.py`, `lex/iv_setup.py`

```python
# validation.py
def validate_key(key: ByteData) -> bytes: ...       # TypeError / ValueError
def validate_iv(iv: ByteData) -> bytes: ...

# context.py
@dataclass(frozen=True)
class KeyContext:
    round_keys: RoundKeys

@dataclass
class StreamContext:
    state: State        # trạng thái đầu vào cho chu kỳ kế tiếp

# iv_setup.py
def make_key_context(key: bytes) -> KeyContext: ...
def compute_s0(key_ctx: KeyContext, iv: bytes) -> State: ...    # AES_K(IV'), IV' = IV đảo byte trong từng nhóm 4 byte (conventions.md, T7); không trích leak
```

## TV6 — `lex/keystream.py`, `lex/api.py`, `run_demo.py`

```python
# keystream.py
class KeystreamBuffer:
    def __init__(self, key_ctx: KeyContext, s0: State) -> None: ...
    def read(self, n_bytes: int) -> bytes: ...      # n_bytes >= 0, chunk tùy ý

# api.py
class LEX:
    def __init__(self, key: ByteData, iv: ByteData) -> None: ...
    def keystream(self, n_bytes: int) -> bytes: ...
    def process(self, data: ByteData) -> bytes: ...

def encrypt(key: ByteData, iv: ByteData, plaintext: ByteData) -> bytes: ...
def decrypt(key: ByteData, iv: ByteData, ciphertext: ByteData) -> bytes: ...
```

## Quy tắc thay đổi

Đổi chữ ký cần: sửa file này trong PR riêng, được ít nhất 1 thành viên dùng hàm đó phê duyệt, rồi mới sửa code.

## Ngoại lệ và ngữ nghĩa bắt buộc

| Hàm | Ném |
|---|---|
| `xtime`, `gmul` | `ValueError` nếu đối số ngoài `[0, 255]` |
| `bytes_to_state` | `ValueError` nếu `len != 16` |
| `add_round_key` | `ValueError` nếu `len(round_key) != 16` |
| `expand_key` | `ValueError` nếu `len(key) != 16` |
| `extract_leak` | `ValueError` nếu `round_no` ngoài `[1, 10]` |
| `validate_key`, `validate_iv` | `TypeError` nếu không phải bytes-like; `ValueError` nếu sai độ dài |
| `KeystreamBuffer.read`, `LEX.keystream` | `TypeError` nếu không phải `int`; `ValueError` nếu `n_bytes < 0`; `read(0)` trả `b""` |

- Mọi hàm biến đổi là hàm thuần (không sửa đối số).
- `LEX.process` tiêu thụ keystream đúng bằng `len(data)`; hai lần gọi liên tiếp tương đương một lần gọi trên dữ liệu nối.
- Gợi ý đổi tên gói `src/lex/lex/` thành `src/lex/stream/` để tránh import `lex.lex.*` (cần cả nhóm đồng ý trước khi tạo skeleton).
