LD_BYTES    equ     $0556   ; Load headerless block
                            ; Carry set for load, clear for verify
                            ; A=$00 for header, $FF for data
                            ; DE=length
                            ; IX=start
                            ;
                            ; On return, Carry set = error occurred

CLS         equ     $0d6b
CL_ALL      equ     $0daf