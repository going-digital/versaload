        include "tokens.inc"
        include "globals.inc"
        include "romhooks.inc"

b_num   macro   n
        db      '0'
        db      $0e
        db      0
        db      0
        db      low(n)
        db      high(n)
        db      0
        endm


        org     $5ccb           ; Base address for all Spectrum BASICs

; BASIC bootstrap to machine code
lineno  equ     1
        db      high(lineno),low(lineno)        ; Line number is big endian!
        dw      lineend-linestart               ; Line length is little endian
linestart:
        db      T_RANDOMIZE     ; In BASIC, this appears as:
        db      T_USR           ;   <line no> OVER USR 7<garbage>
        b_num   code
        db      $0d
lineend:

; Machine code section
code:
        di
        ld      de,loadbase
        ld      hl,reloc_start
        push    de              ; Set execution address of loader
        ld      bc,reloc_end - reloc_start
        ldir                    ; Relocate loader
        ret                     ; Jump to relocated loader

reloc_start:
        ; Pasmo can't assemble relocated code directly, so pre-assemble it and
        ; include as binary data.
        incbin  "boot2.bin"
reloc_end:
