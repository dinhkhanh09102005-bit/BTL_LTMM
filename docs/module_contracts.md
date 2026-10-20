# Hop dong module - phan cong 5 thanh vien

Quy uoc:
- State la 16 bytearray theo column-major: index=4*column+row.
- RoundKeys la 11 khoa vong, moi khoa 16 bytes.
- ByteData = bytes | bytearray | memoryview.

## TV1
core/gf256.py: xtime(a:int)->int; gmul(a:int,b:int)->int.
core/matrix_state.py: idx(r,c)->int; bytes_to_state(data:bytes)->State; state_to_bytes(state)->bytes.
aes/sbox.py: SBOX (256 elements).
aes/transforms.py: sub_bytes(state)->State; shift_rows(state)->State;
mix_columns(state)->State; add_round_key(state,round_key:bytes)->State.

## TV2
aes/key_schedule.py: expand_key(key:bytes)->RoundKeys.
aes/standard_aes.py: encrypt_block(round_keys, block:bytes)->bytes.

## TV3
lex/extractor.py: extract_leak(state, round_no:int)->bytes (4 bytes).
lex/round_engine.py: lex_round(state,round_key,*,mix_columns:bool)->State;
lex_cycle(state,round_keys)->tuple[bytes,State].
lex_cycle produces 40 keystream bytes and next 16-byte state.

## TV4
lex/validation.py: validate_key(key)->bytes; validate_iv(iv)->bytes; validate_data(data)->bytes.
lex/context.py: frozen KeyContext(round_keys), StreamContext(state).
lex/iv_setup.py: make_key_context(key)->KeyContext; compute_s0(key_ctx,iv)->State.

## TV5
lex/keystream.py: KeystreamBuffer(key_ctx, s0); read(n_bytes:int)->bytes.
lex/api.py: LEX(key,iv); keystream(n_bytes:int)->bytes; process(data)->bytes;
encrypt(key,iv,plaintext)->bytes; decrypt(key,iv,ciphertext)->bytes.
run_demo.py: demo TV5.

Test: read(0) returns b-empty; read(-1) ValueError; non-int TypeError.
Split reads must equal one contiguous read. No repeated/dropped keystream bytes.
Change public signatures only after agreement with downstream team members.
