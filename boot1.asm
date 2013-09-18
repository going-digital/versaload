        include "tokens.inc"
        include "globals.inc"
        include "romhooks.inc"
        include "sysvar.inc"

b_num   macro   n
        db      '0',$0e,0,0,low(n),high(n),0
        endm

        org     $5ccb           ; Base address for most Spectrum BASICs

; BASIC bootstrap to machine code
lineno  equ     0
basic:  db      high(lineno),low(lineno)        ; Line number is big endian!
        dw      lineend-linestart               ; Line length is little endian
linestart:
        db      T_CLS,':',T_RANDOMIZE,T_USR

        ; 0 CLS:RANDOMIZE USR (xx+PEEK 23635+256*PEEK 23636)
        ; although it appears as
        ; 0 CLS:RANDOMIZE USR (0+PEEK 0+0*PEEK 0)
        ; to keep the size small.

;        ; 28 bytes longer, but copes with different PROG bases
        db      '('
        b_num   code-basic
        db      '+',T_PEEK
        b_num   PROG
        db      '+'
        b_num   $100
        db      '*',T_PEEK
        b_num   PROG+1
        db      ')'

        ; 0 RANDOMIZE USR n
        ; This version is smaller, but assumes PROG = $5ccb
        ; which is true for most machines, but not Timex's or those
        ; expanded by peripherals like Interface 1 or disk drives.
;        b_num   code

        db      $0d

lineend:

; Machine code section
code:
        di
        ld      de,loadbase
        ld      hl,reloc_start - code   
        add     hl,bc           ; On entry, BC = code

        push    de              ; Set execution address of loader
        ld      bc,reloc_end - reloc_start
        ldir                    ; Relocate loader
        ret                     ; Jump to relocated loader

reloc_start:
        ; Pasmo can't assemble relocated code directly, so pre-assemble it and
        ; include as binary data.
        incbin  "boot2.bin"
reloc_end:
