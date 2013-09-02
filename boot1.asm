        include "tokens.inc"
        include "globals.inc"
        include "romhooks.inc"

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

        ;
        ; Clear screen, leaving 'Loading' on-screen
        ;
        ld      hl,$4000        ; Clear top third of screen
        ld      de,$4001        ; (the Program: part)
        ld      bc,$0800
        ld      (hl),l
        ldir
        ld      h,$50           ; Clear bottom third of screen
        ld      d,h             ; (The Tape Loader bar on 128K Spectrum)
        ld      b,$08
        ld      (hl),l
        ldir
        ld      (hl),$38        ; Clear attributes to INK 0 PAPER 7
        ld      bc,$2ff         ; Blanking out the Tape Loader bar
        ldir
        ret                     ; Jump to relocated loader

reloc_start:
        ; Pasmo can't assemble relocated code directly, so pre-assemble it and
        ; include as binary data.
        incbin  "boot2.bin"
reloc_end:
