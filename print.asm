        include "globals.inc"
        include "undoc_instr.inc"

        org printbase

        ; Print text on screen
        ;
        ; Parameters:
        ;   screen address
        ;   character base address (characters starting at $20)
        ;   null terminated ASCII string
        ld      ix,printparam+4
plp:    ld      a,(ix+0)            ; Read ASCII
        inc     ix
        sub     $20
        ret     c
        ld      h,0                 ; Calculate character base address
        ld      l,a
        add     hl,hl
        add     hl,hl
        add     hl,hl
        ld      de,(printparam)
        add     hl,de
        ld      de,(printparam+2)   ; Screen address
        ld      b,8
clp:    ld      a,(hl)
        ld      (de),a
        inc     hl
        inc     d
        djnz    clp
        ld      hl,$1-$800
        add     hl,de
        ld      (printparam+2),hl
        jr      plp

printparam:
        ;dw      $3d00   ; Character set address
        ;dw      $4000   ; Screen base address
        ;db      "Hello world",0

; Passed to Python payload builder
PRINT_ROUTINE   equ     printbase
PRINT_PARAM     equ     printparam
