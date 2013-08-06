; This code _must_ execute in uncontended memory as it is time critical.

; TODO: Get this code complete and tested

        include "globals.inc"
        include "undoc_instr.inc"

        org loadbase

        ; Sync:
        ;
        ; Look for a specific 32 step data pattern
        ; This has multiple functions:
        ;   1) Take up the unknown slack before the next pattern
        ;   2) Handle any inversion in the audio system
        xor     a
sync:
sync_loop:
        call    measure_half_symbol
        sub     sync_threshold          ; 7T
        rl      e                       ; 8T
        rl      d                       ; 8T
        rl      l                       ; 8T
        rl      h                       ; 8T
        ld      a,sync_train_1          ; 7T
        cp      h                       ; 4T
        ld      a,+(69+15)/29           ; 7T
        jr      nz,sync_loop            ; 12T/7T exit: 69T
        ld      a,sync_train_2          ; 7T
        cp      l                       ; 4T
        ld      a,+(94+15)/29           ; 7T
        jr      nz,sync_loop            ; 12T/7T exit: 94T
        ld      a,sync_train_3          ; 7T
        cp      d                       ; 4T
        ld      a,+(119+15)/29          ; 7T
        jr      nz,sync_loop            ; 12T/7T exit: 119T
        ld      a,sync_train_4          ; 7T
        cp      e                       ; 4T
        ld      a,+(144+15)/29          ; 7T
        jr      nz,sync_loop            ; 12T/7T exit: 144T
        ; Sync has been received, 139T after edge so far

        ; Calibrate:
        ;
        ; Measure a test pattern.
        ; From this test, we calibrate the thresholds for pulse measurement
        ; later. This corrects for variation in record and playback motors
        ; as well as tape stretch, which gives much more accurate
        ; descrimination between symbols.
calibrate:
        ld      hl,+(161+19+19+19+15)/29; 10T
        ld      d,h                     ; 4T
        ld      e,l                     ; 4T
        xor     a                       ; 4T = 161T total
        call    measure_symbol
        ld      e,a                     ; 4T
        add     hl,de                   ; 11T
        xor     a                       ; 4T = 19T
        call    measure_symbol
        ld      e,a                     ; 4T
        add     hl,de                   ; 11T
        xor     a                       ; 4T = 19T
        call    measure_symbol
        ld      e,a                     ; 4T
        add     hl,de                   ; 11T
        xor     a                       ; 4T = 19T
        call    measure_symbol
        ld      e,a                     ; 4T
        add     hl,de                   ; 11T
        ; HL now contains the duration of four 8 period delays.
        ; Multiply by 8:
        add     hl,hl                   ; 11T
        add     hl,hl                   ; 11T
        ; H contains 0.5 period delay
        ld      b,h                     ; 4T B: 0.5 periods
        add     hl,hl                   ; 11T
        ; H now contains the average measured 1 period time
        ld      c,h                     ; 4T C: 1 period
        add     hl,hl                   ; 11T
        ld      d,h                     ; 4T D: 2 periods
        add     hl,hl                   ; 11T
        ld      e,h                     ; 4T E: 4 periods
        add     hl,hl                   ; 4T H: 8 periods
        ; Now to calculate the thresholds
        ; Done in Gray code order for fastest calculation speed.
        ld      a,b                     ; 4T
        add     a,c                     ; 4T
        ;ld      (thres_1_5),a           ; 13T
        add     a,d                     ; 4T
        ld      (thres_3_5),a           ; 13T
        sub     c                       ; 4T
        ld      (thres_2_5),a           ; 13T
        add     a,e                     ; 4T
        ld      (thres_6_5),a           ; 13T
        sub     d                       ; 4T
        ld      (thres_4_5),a           ; 13T
        add     a,c                     ; 4T
        ld      (thres_5_5),a           ; 13T
        add     a,d                     ; 4T
        ld      (thres_7_5),a           ; 13T
        ld      a,h                     ; 4T
        add     a,b                     ; 4T
        ld      (thres_8_5),a           ; 13T

        ; Readdata:
        ;
        ; Read symbols, quantise to the correct period and pass to the
        ; decoding engine to extract real data.
        ;
        ; Tree Length Encoding
        ;    / 220us  00
        ;   /\ 330us  01
        ;  / / 440us  100
        ; / /\ 550us  101
        ; \/ / 660us  1100
        ;  \/\ 770us  1101
        ;   \/ 880us  1110
        ;    \ 990us  1111

        ; This part is unrolled for speed. The entire loop from edge to edge
        ; must complete within 700T otherwise the next pulse measurement may
        ; be compromised.

thres_2_5 equ smc02+1
thres_3_5 equ smc01+1
thres_4_5 equ smc04+1
thres_5_5 equ smc03+1
thres_6_5 equ smc07+1
thres_7_5 equ smc06+1
thres_8_5 equ smc08+1

; TODO: Recalculate timings through this section

        ld      a,0             ; 7T
readdata:
        call    measure_symbol
smc01:  cp      0               ; 7T    thres_3_5 stored here
        jp      c,bits_1_       ; 10T
        call    addbit
smc02:  cp      0               ; 7T    thres_2_5 stored here
        call    addbit
        ld      a,+(108+15)/29  ; 7T
        jp      readdataend     ; 10T

bits_1_:call    addbit
smc03:  cp      0               ; 7T    thres_5_5 stored here
        jp      c,bits_11_      ; 10T        [10 + 54]
        call    addbit
smc04:  cp      0               ; 7T    thres_4_5 stored here
        call    addbit
        ld      a,+(159+15)/29  ; 7T
        jp      readdataend     ; 10T

bits_11_:
        call    addbit
smc06:  cp      0               ; 7T    thres_7_5 stored here
        jr      c,bits_111_     ; 12T/7T
        call    addbit
smc07:  cp      0               ; 7T    thres_6_5 stored here
        call    addbit
ret08:  ld      a,+(213+15)/29  ; 7T
        jp      readdataend     ; 10T

bits_111_:
        call    addbit
smc08:  cp      0               ; 7T    thres_8_5 stored here
        call    addbit
        ld      a,+(206+15)/29  ; 7T

readdataend:
        ;
        ; TODO: Handling of binary datastream goes here
        ;
        ; TODO: Count bytes, then jump to either readdata or sync
        ;
        ; TODO: Need to test for end-of-block condition
        ;
        ld      e,a
        ld      a,h
        cp      b
        ld      a,e
        jp      nz,readdata
        ld      a,l
        cp      c
        ld      a,e
        jp      nz,readdata
        ; HL = BC, end of block condition so resync
        jp      sync


        ; For debugging
        jp      alert

        ;
        ; Test code: flash border in distinctive pattern and make noise
        ;
alert:  ld      a,$17   ; De Bruijn sequence k=2 n=3
        ld      c,$fe
alertlp:out     (c),a
        rlca
        jr      alertlp

addbit: rl      d
        jr      nc,delab
        ld      (hl),d
        ld      d,$01
        inc     hl
retab:  ret
delab:  nop
        jp      retab

        ; measure_symbol and measure_half_symbol
        ;
        ; Measures duration of next half-symbol (time high or time low)
        ; or next full symbol (total of high and low period)
        ;
        ; On entry:
        ;       A: number of T states since last edge, in multiples of 29.
        ; On exit:
        ;       A: number of T states to edge, in multiples of 29.
        ; Corrupts:
        ;       B'C'
        ;
measure_symbol:
        call    measure_half_symbol
measure_half_symbol:
        exx
        ld      c,$FE           ; Mic port
        ex      af,af'
        ld      a,ms_0 - ms_1
        ld      (ms_link+1),a
        ex      af,af'
ms_link:jr      ms_1            ; * Selfmodifying code
ms_1:   
ms1lp:  inc     a               ;  7T
        IN_F_C                  ; 12T in f,(c) undocumented instruction
        jp      po,ms1lp        ; 10T
        ret
ms_0:   
ms0lp:  inc     a
        IN_F_C
        jp      pe,ms0lp
        exx
        ret
