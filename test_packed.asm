                ; Decompression memory map:
                ;       $5b00-$5b9c     decompression tables
                ;            -$5bff     CPU stack
                ;       $5c00-$5bff     Decompression/run code

exo_mapbasebits equ     $5b00 ;:defs    156             ;tables for bits, baseL, baseH

                org     $5c00
                ; Decompress data
                ld      sp,$5c00
                ld      hl,packed_data
                ld      de,$ffff
                call    deexo
                ; Patch out 'press any key' routine
                ld      hl,$800c
                xor     a
                ld      (hl),a
                inc     hl
                ld      (hl),a
                ; Execute game
                ld      sp,$5fff
                jp      $8000

;Exomizer 2 Z80 decoder
; by Metalbrain
;
; optimized by Antonio Villena and Urusergi (167 bytes)
;
; compression algorithm by Magnus Lind

;input:         hl=compressed data start
;               de=uncompressed destination start
;
;               you may change exo_mapbasebits to point to any free buffer
;

deexo:          ld      iy, exo_mapbasebits+11
                ld      a, (hl)
                dec     hl
                ld      b, 52
                push    de
                cp      a
exo_initbits:   ld      c, 16
                jr      nz, exo_get4bits
                ld      ixl, c
                ld      de, 1           ;DE=b2
exo_get4bits:   srl a
                call z,exo_getbit       ;get one bit
                rl      c
                jr      nc, exo_get4bits
                inc     c
                push    hl
                ld      hl, 1
                ld      (iy+41), c      ;bits[i]=b1 (and opcode 41 == add hl,hl)
exo_setbit:     dec     c
                jr      nz, exo_setbit-1 ;jump to add hl,hl instruction
                ld      (iy-11), e
                ld      (iy+93), d      ;base[i]=b2
                add     hl, de
                ex      de, hl
                inc     iy
                pop     hl
                dec     ixl
                djnz    exo_initbits
                pop     de
                jr      exo_mainloop
exo_literalrun: ld      e, c            ;DE=1
exo_getbits:    dec     b
                ret     z
exo_getbits1:   srl a
                call z,exo_getbit
                rl      e
                rl      d
                jr      nc, exo_getbits
                ld      b, d
                ld      c, e
                pop     de
exo_literalcopy:lddr
exo_mainloop:   inc     c
                srl a
                call z,exo_getbit      ;literal?
                jr      c, exo_literalcopy
                ld      c, 239
exo_getindex:   srl a
                call z,exo_getbit
                inc     c
                jr      nc,exo_getindex
                ret     z
                push    de
                ld      d, b
                jp      p, exo_literalrun
                ld      iy, exo_mapbasebits-229
                call    exo_getpair
                push    de
                rlc     d
                jr      nz, exo_dontgo
                dec     e
                ld      bc, 512+32      ;2 bits, 48 offset
                jr      z, exo_goforit
                dec     e               ;2?
exo_dontgo:     ld      bc, 1024+16     ;4 bits, 32 offset
                jr      z, exo_goforit
                ld      de, 0
                ld      c, d            ;16 offset
exo_goforit:    call    exo_getbits1
                ld      iy, exo_mapbasebits+27
                add     iy, de
                call    exo_getpair
                pop     bc
                ex      (sp), hl
                ex      de, hl
                add     hl,de
                lddr
                pop     hl
                jr      exo_mainloop    ;Next!

exo_getpair:    add     iy, bc
                ld      e, d
                ld      b, (iy+41)
                call    exo_getbits
                ex      de, hl
                ld      c, (iy-11)
                ld      b, (iy+93)
                add     hl, bc          ;Always clear C flag
                ex      de, hl
                ret

exo_getbit:     ld      a, (hl)
                dec     hl
                rra
                ret

                incbin  "test.raw.exo_b"
packed_data_plus_1:
packed_data     equ     packed_data_plus_1-1
