/* Minimal shim written for this project (NOT the official ECRYPT header). */
#ifndef ECRYPT_PORTABLE
#define ECRYPT_PORTABLE
#include <stdint.h>
typedef uint8_t u8; typedef uint16_t u16; typedef uint32_t u32; typedef uint64_t u64;
#define U8V(v)  ((u8)(v) & 0xFFU)
#define U32V(v) ((u32)(v) & 0xFFFFFFFFU)
#define U8TO32_LITTLE(p) (((u32)((p)[0])) | ((u32)((p)[1])<<8) | ((u32)((p)[2])<<16) | ((u32)((p)[3])<<24))
#define U32TO32_LITTLE(v) (v)
#define ROTL32(v,n) (U32V((v)<<(n)) | ((v)>>(32-(n))))
#endif
