        include "tokens.inc"
        include "globals.inc"


; BASIC bootstrap to machine code
;
; Sets SP to stackptr, copies boot2.bin to loadbase and executes it.
;
; Be careful modifying this file - the code is executed twice. Once as BASIC,
; and once as Z80. The code needs to make sense in both.
;
        org     $5ccb           ; Base address for all Spectrum BASICs
        ld      de,loadbase
        di
        db      T_OVER          ; In BASIC, this appears as:
        db      T_USR           ;   <line no> OVER USR 7<garbage>
        db      '7'             ; But it executes as:
        db      $0e             ;   OVER USR $5ccb
        db      $8f             ; In machine code, it does not crash and
        db      $39             ;   preserves DE.
        db      $96
        ld      sp,stackptr     ; Move stack to a better place
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
