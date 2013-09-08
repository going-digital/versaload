; BMC decoder
;
;   Measure speed
;   Synchronise to bit period (avoid strings of 1s)
;   Look for synchronisation bit header

;   baud    1bit    0.75bit 0.5bit
;   1500    2333T           1167
;   2100    1667T           833
;   3000    1167T           583
;   4200    833T            417
;   6000    583T            292

;   Synchronise:
;   1:  Wait for edge
;       Store state
;       Wait 0.75 bit periods
;       If state is different, jump to 1
;   2:  

;   Readbit:
;       Wait for edge
;       Store state
;       Wait 0.75 bit periods
;       Sample and compare
;       Different: return 0
;       Same: return 1


        ; Wait for positive edge, then sample at 0.75 bit periods
sync:   in      a,($fe)         ; 11T [edge+11]
        rlca                    ; 4T [edge+15]
sm1:    jp      m,sync          ; 10T [edge+25]
        ; Delay loop
        ; This also handles all the bit processing from the last bit

sm2:    scf                     ; 4T [edge+29] Self modified: set or clear carry
sm3:    jp      0               ; 10T [edge+40] Self modified: jump to bit processing step

stage1: ; Stage 1:
        ; Wait for '1' bit to be detected.
        ; If we don't do this, we risk synchronising on the middle-bit edge
        ; of the '0' symbol
        ld      b,??            ; 7T [edge+47]
        jp      nc,samestage    ; 10T [edge+57] '0' bit - stay here
        ld      b,??            ; 7T [edge+64]
        ld      hl,stage2       ; 10T [edge+74]
        ld      de,0            ; 10T [edge+84]
        jp      newstage        ; 10T [edge+94] '1' bit - advange to stage 2

stage2: ; Wait for synchronisation pattern ('00111111 11111101')
        ; which matches the EBU LTC pattern
        rl      e               ; 8T [edge+48]
        rl      d               ; 8T [edge+56]
        ld      a,$3f           ; 7T [edge+63]
        xor     d               ; 4T [edge+67]
        ld      b,??            ; 7T [edge+74]
        jp      nz,samestage    ; 10T [edge+84]
        ld      a,$fd           ; 7T [edge+91]
        xor     e               ; 4T [edge+95]
        ld      b,??            ; 7T [edge+102]
        jp      nz,samestage    ; 10T [edge+112]
        ld      hl,stage3       ; 10T [edge+122] Synchronisation pattern match
        ld      b,??            ; 7T [edge+129]
        jp      newstage        ; 10T [edge+139]

stage3: ; Read block header and verify

stage4: ; Read data and verify

newstage:
        ld      l,(sm3+1)
        ld      h,(sm3+2)
        ld      b,nn
samestage:

dellp:  djnz    dellp           ; Wait 0.75 bit periods
                                ; Need to put processing here
        in      a,($fe)         ; 11T
        rlca                    ; 4T
sm2:    jp      m,rx0           ; 10T
rx1:    ; Just received a 1 bit. Invert sense next time.
        ld      a,(sm1)
        xor     $08             ; Swap jp p and jp m instructions
        ld      (sm1),a         ;
        ld      (sm2),a         ;
        scf                     ; 4T
        ret                     ; 10T
rx0:    ; Just received a 0 bit. No need to invert.
        and     a               ; 4T Clear carry flag
        ret

sync:   in      a,($fe)         ; 11T
        rlca                    ; 4T
sm1:    jp      m,sync          ; 10T
        ;
        ; Bit processing
        ;


measure_half_symbol:
        ; Starts checking edge 68T after CALL (including CALL instr)
        ; If A < glitch_delay, ignore edges until glitch_delay complete

        ; This loop is 32T long, matching the sample loop below
        and     0               ; 7T
        nop                     ; 4T
        inc     a               ; 4T 
        cp      glitch_delay    ; 7T loop until a > sync_delay
        jp      nc,measure_half_symbol ; 10T
        ld      b,a             ; 4T
mslp:   inc     b               ; 4T Cycle time is 32T
        in      a,($fe)         ;11T [edge+11T]
        and     $40             ; 7T
ms_cmp: jp      z,mslp          ;10T Selfmodified between Z and NZ
        ld      a,(ms_cmp)      ;13T
        xor     $08             ; 7T Swap jp z and jp nz opcodes
        ld      (ms_cmp),a      ;13T
b_fl:   ld      a,border_blue   ; 7T
        out     ($fe),a         ;11T
b_m:    ld      a,border_white  ; 7T
        out     ($fe),a         ;11T
        ld      a,b             ; 4T
        ret                     ;10T [edge+111T]
