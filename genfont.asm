; Generate bold font from Spectrum ROM font

        include "globals.inc"

        org     genfont

        ld      ix,$3d00    ; Address of ROM font
        ld      de,fontbase
        ld      bc,$300     ; Length of font in bytes
loop:   ld      a,(ix+0)
        ld      h,a
        srl     a
        or      h
        ld      (de),a
        inc     ix
        inc     de
        dec     bc
        ld      a,b
        or      c
        jp      nz,loop
        ret

GENFONT_ROUTINE equ genfont
FONTBASE        equ fontbase