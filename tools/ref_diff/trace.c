/* Trace harness for the official LEX-v2 reference (lex.c).
 * Build: gcc -O0 -w -I<dir containing lex.c, ecrypt-sync.h> -I. -o trace trace.c
 * Usage: trace <key hex 32> <iv hex 32> <cycles>
 * Prints per-round states (standard AES byte order: idx = 4*c + r) using the
 * Te tables of lex.c, and asserts the result equals ECRYPT_keystream_bytes(). */
#include <stdio.h>
#include <string.h>
#include "lex.c"

static void hexw(const u32 *w) { for (int i = 0; i < 4; i++) printf("%08X", (unsigned)w[i]); }
static u32 leak_odd(const u32 *t)  { return (t[0] & 0xFF00FF00) ^ ((t[2] & 0xFF00FF00) >> 8); }
static u32 leak_even(const u32 *s) { return ((s[0] & 0xFF00FF) << 8) ^ (s[2] & 0xFF00FF); }

int main(int argc, char **argv) {
  u8 key[16], iv[16]; ECRYPT_ctx c, ref; int cycles = argc > 3 ? atoi(argv[3]) : 1;
  if (argc < 3) return 2;
  for (int i = 0; i < 16; i++) { unsigned v; sscanf(argv[1] + 2*i, "%2x", &v); key[i] = v; sscanf(argv[2] + 2*i, "%2x", &v); iv[i] = v; }
  ECRYPT_init();
  ECRYPT_keysetup(&c, key, 128, 128); ECRYPT_ivsetup(&c, iv);
  ref = c;
  printf("IVBLOCK="); for (int i = 0; i < 16; i++) printf("%02X", iv[(i/4)*4 + 3 - (i%4)]); printf("\n");
  printf("S0="); hexw(c.blockstate); printf("\n");
  u8 refks[40 * 8]; ECRYPT_keystream_bytes(&ref, refks, 40 * cycles);
  u32 s[4] = { c.blockstate[0], c.blockstate[1], c.blockstate[2], c.blockstate[3] };
  int match = 1;
  for (int cyc = 1; cyc <= cycles; cyc++) {
    u8 ks[40];
    for (int r = 1; r <= 10; r++) {
      u32 n[4], *rk = c.subkeys + 4 * r;
      for (int j = 0; j < 4; j++)
        n[j] = Te0[s[j] >> 24] ^ Te1[(s[(j+1)&3] >> 16) & 0xff] ^ Te2[(s[(j+2)&3] >> 8) & 0xff] ^ Te3[s[(j+3)&3] & 0xff] ^ rk[j];
      memcpy(s, n, 16);
      u32 l = (r & 1) ? leak_odd(s) : leak_even(s);
      for (int b = 0; b < 4; b++) ks[4*(r-1) + b] = (u8)(l >> (8*b));   /* little-endian, as in ECRYPT_keystream_bytes */
      printf("C%dR%d=", cyc, r); hexw(s); printf(" LEAK="); for (int b = 0; b < 4; b++) printf("%02X", ks[4*(r-1)+b]); printf("\n");
    }
    printf("C%dKS=", cyc); for (int b = 0; b < 40; b++) printf("%02X", ks[b]); printf("\n");
    if (memcmp(ks, refks + 40*(cyc-1), 40)) match = 0;
  }
  printf("MATCH_OFFICIAL=%d\n", match);
  return match ? 0 : 1;
}
