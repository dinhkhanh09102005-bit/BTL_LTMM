"""TODO: TV1 GF256. No implementation yet."""
POLY = 0x1B # x^8 mod m(x) 
def xtime(a: int) -> int:
    """a * {02} = a * x."""
    carry = a & 0x80
    a = (a << 1) & 0xFF
    return a ^ POLY if carry else a 
  
def gmul(a: int, b: int) -> int:
    """a * b trong GF(2^8): a*b = sum b_i (a * x^i)."""
    p = 0
    while b:
        if b & 1:
            p ^= a
        a = xtime(a)
        b >>= 1
    return p
  
def gpow(a: int, n: int) -> int:
    """a^n, square-and-multiply."""
    r = 1
    while n:
        if n & 1:
            r = gmul(r, a)
        a = gmul(a, a)
        n >>= 1
    return r


def ginv(a: int) -> int:
    """a^-1 = a^254 (|GF(2^8)*| = 255); quy ước 0^-1 = 0."""
    return gpow(a, 254) if a else 0
