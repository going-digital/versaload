; Add support for Z80 undocumented instructions that Pasmo doesn't know about
;


;       in      f,(c)       ; Reads IO port to F register
;
IN_F_C  MACRO
        db      $ed,$70
        ENDM
