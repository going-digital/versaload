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
        ld      a,-2                    ; 7T TODO: Timings in sync loop need adjusting for code change here
sync_2:
        inc     a                       ; 4T
        inc     a                       ; 4T
sync:
sync_loop:
        call    measure_half_symbol     ; 17T
        cp      sync_threshold          ; 7T carry set if time > threshold
        ccf                             ; 4T
        rl      e                       ; 8T
        rl      d                       ; 8T
        rl      l                       ; 8T
        rl      h                       ; 8T
        ld      a,sync_train_1          ; 7T
        cp      h                       ; 4T
        ld      a,+(69+16)/32           ; 7T
        jr      nz,sync_loop            ; 12T/7T exit: 69T
        ld      a,sync_train_2          ; 7T
        cp      l                       ; 4T
        ld      a,+(94+16)/32           ; 7T
        jr      nz,sync_loop            ; 12T/7T exit: 94T
        ld      a,sync_train_3          ; 7T
        cp      d                       ; 4T
        ld      a,+(119+16)/32          ; 7T
        jr      nz,sync_loop            ; 12T/7T exit: 119T
        ld      a,sync_train_4          ; 7T
        cp      e                       ; 4T
        ld      a,+(144+16)/32          ; 7T
        jr      nz,sync_loop            ; 12T/7T exit: 144T

        ; Sync has been received, 139T after edge so far
        ; Edge+139T
        ; Edge+157T

        ; Calibrate:
        ;
        ; Measure a test pattern.
        ; From this test, we calibrate the thresholds for pulse measurement
        ; later. This corrects for variation in record and playback motors
        ; as well as tape stretch, which gives much more accurate
        ; descrimination between symbols.
calibrate:
        ld      hl,+(179+19+19+19+16)/32; 10T
        ; HL incorporates corrections from all 4 calibration pulses
        ld      d,h                     ; 4T
        ld      e,l                     ; 4T
        xor     a                       ; 4T Edge+179T
        call    measure_symbol
        ld      e,a                     ; 4T
        add     hl,de                   ; 11T
        xor     a                       ; 4T Edge+19T
        call    measure_symbol
        ld      e,a                     ; 4T
        add     hl,de                   ; 11T
        xor     a                       ; 4T Edge+19T
        call    measure_symbol
        ld      e,a                     ; 4T
        add     hl,de                   ; 11T
        xor     a                       ; 4T Edge+19T
        call    measure_symbol
        ld      e,a                     ; 4T
        add     hl,de                   ; 11T Edge+15T

        ; HL now contains the duration of four 8 period delays.
        ; Multiply by 8:
        add     hl,hl                   ; 11T
        add     hl,hl                   ; 11T Edge+55T
        ; H contains 0.5 period delay
        ld      b,h                     ; 4T B: 0.5 periods
        add     hl,hl                   ; 11T Edge+70T
        ; H now contains the average measured 1 period time
        ld      c,h                     ; 4T C: 1 period
        add     hl,hl                   ; 11T
        ld      d,h                     ; 4T D: 2 periods
        add     hl,hl                   ; 11T
        ld      e,h                     ; 4T E: 4 periods
        add     hl,hl                   ; 4T H: 8 periods Edge+93T
        ; Now to calculate the thresholds
        ; Done in Gray code order for fastest calculation speed.

        ld      a,c                     ; 4T
        add     a,d                     ; 4T
        ld      (thres_3),a             ; 13T
        add     a,e                     ; 4T
        ld      (thres_7),a             ; 13T
        sub     d                       ; 4T
        ld      (thres_5),a             ; 13T Edge+148T

        ; Readdata:
        ;
        ; Read symbols, quantise to the correct period and pass to the
        ; decoding engine to extract real data.
        ;
        ; Tree Length Encoding
        ;  / 220us  00
        ; /\ 440us  01
        ; \/ 660us  10
        ;  \ 880us  11

        ; This part is unrolled for speed. The entire loop from edge to edge
        ; must complete within 700T otherwise the next pulse measurement may
        ; be compromised.

selfmodified    equ     0       ; Dummy value placeholder for selfmodified code

; TODO: Recalculate timings through this section

; Set up to load payload
        ; Edge + 148T
        ld      hl,payload_base         ; 10T
        ld      bc,payload_end_header   ; 10T
        ld      a,b                     ; 4T
        ld      (end_h),a               ; 13T
        ld      a,c                     ; 4T
        ld      (end_l),a               ; 13T

        ld      d,$01                   ; 7T
        xor     a                       ; 4T
        ld      (payload_data),a        ; 13T
        ld      a,+(230+16)/32-2        ; 7T Edge+230T
readdata_2:
        inc     a                       ; 4T
readdata_1:
        inc     a                       ; 4T
readdata:
        call    measure_symbol          ; 17T
smc01:  cp      selfmodified            ; 7T    thres_5 stored here
        ccf                             ; 4T
        jp      c,bits_1_               ; 10T Edge+21T
        call    addbit                  ; 61T
smc02:  cp      selfmodified            ; 7T    thres_3 stored here
        ccf                             ; 4T
        call    addbit                  ; 61T
        ld      a,+(171+16)/32          ; 7T
        jp      readdataend             ; 10T Edge+171T

        ; Called at Edge+21T
bits_1_:call    addbit                  ; 61T
smc03:  cp      selfmodified            ; 7T    thres_7 stored here
        ccf                             ; 4T
        call    addbit                  ; 61T
        ld      a,+(161+16)/32          ; 7T

thres_3         equ     smc02+1
thres_5         equ     smc01+1
thres_7         equ     smc03+1

readdataend:
        ; Up to 4 bits can be added for each symbol.
        ; Once BC=HL, the block is over.
        ld      e,a                     ; 4T
        ld      a,h                     ; 4T
smc10:  cp      selfmodified            ; 7T
        ld      a,e                     ; 4T
        jp      nz,readdata_1           ; 10T Edge+A+26T (add 32T)
        ld      a,l                     ; 4T
smc11:  cp      selfmodified            ; 7T
        ld      a,e                     ; 4T
        jp      nz,readdata_1           ; 10T Edge+A+48T (add 32T)
        ; Data is complete
        ld      a,(payload_data)        ; 13T
        and     a                       ; 4T
        ld      a,e                     ; 7T
        jp      nz,payload_complete     ; 10T Edge+A+82T (add 64T)

end_h   equ     smc10+1
end_l   equ     smc11+1

        ; Payload header loaded:
        ; Set up load and end address
        ; TODO: Handle block number
        ; TODO: Handle checksum

        ld      hl,(loadaddr)           ; 16T
        ld      bc,(endaddr)            ; 20T
        ld      a,b                     ; 4T
        ld      (end_h),a               ; 13T
        ld      a,c                     ; 4T
        ld      (end_l),a               ; 13T
        ld      a,$01                   ; 7T
        ld      (payload_data),a        ; 13T Edge+A+135T
        ld      a,$04                   ; 7T
        add     a,e                     ; 4T
        jp      readdata                ; Edge+A+142T (add 128T)

payload_complete:
        nop                             ; 4+4+4T          Loader can insert a CALL or JP here
        nop                             ; or 17T for CALL to execute external routines
        nop
        xor     a                       ; 4T  0 is opcode for NOP
        ld      (payload_complete),a    ; 13T
        ld      (payload_complete+1),a  ; 13T
        ld      (payload_complete+2),a  ; 13T
        jp      sync_2                  ; 10T
PAYLOAD_JUMP equ payload_complete

        ; For debugging
        jp      alert

        ; alert
        ;
        ; Distinctive effect for debugging use.
        ; Flashes border Wh/Ye/Gr/Bk/Bl/Re/Cy/Ma
        ;
        ; 7 bytes
alert:  ld      a,$17   ; De Bruijn sequence k=2 n=3
alertlp:out     ($fe),a
        rlca
        jr      alertlp

        ; addbit
        ;
        ; Adds the carry flag contents into the incoming data shift register
        ;
        ; On entry:
        ;       carry: Bit to add
        ; On exit:
        ;       DHL: updated
        ; Caller must preserve:
        ;       D: shift register
        ;       HL: memory pointer
        ; Execution time
        ;       CALL addbit takes either 
        ;               17+44 T states (7/8 times)
        ;               17+45 T states (1/8 times)
        ;       Assume CALL addbit takes 61T
        ;
addbit: rl      d               ; 8T
        jr      nc,delab        ; 7/12T
        ld      (hl),d          ; 7T
        ld      d,$01           ; 7T
        inc     hl              ; 6T
retab:  ret                     ; 10T (821+6+10 42)
delab:  nop                     ; 4T
        jp      retab           ; 10T

        ; measure_symbol and measure_half_symbol
        ;
        ; Measures duration of next half-symbol (time high or time low)
        ; or next full symbol (total of high and low period)
        ;
        ; On entry:
        ;       A: number of T states since last edge, in multiples of 32.
        ; On exit:
        ;       A: number of T states to edge, in multiples of 32.
        ; Corrupts:
        ;       B
        ;
measure_symbol:
        call    measure_half_symbol ; 17T

        ; Glitch ignore delay, because A already contains the half-symbol
        ; timing, and won't trigger the glitch delay in measure_half_symbol
        ld      b,glitch_delay-5        ; 7T    \ TODO: Investigate this '5'
        add     a,b                     ; 4T     |
mslp2:  jr      ms_jr                   ;12T     | 32T loop + 6T overhead
ms_jr:  and     0                       ; 7T     |
        djnz    mslp2                   ;13T/8T /

measure_half_symbol:
        ; Starts checking edge 68T after CALL (including CALL instr)
        ; If A < glitch_delay, ignore edges until glitch_delay complete
        ; Returns 100T after edge

        add     a,(100+16)/32     ; 7T Add compensation for return time after last measure_half_symbol call

        ; This loop is 32T long, matching the sample loop below
        and     0               ; 7T
        nop                     ; 4T
        inc     a               ; 4T 
        cp      glitch_delay    ; 7T loop until a > sync_delay
        jp      nc,measure_half_symbol ; 10T
        ld      b,a             ; 4T
mslp:   inc     b               ; 4T Cycle time is 32T
        in      a,($fe)         ;11T
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
        ret                     ;10T

BORDER_FLASH equ b_fl+1
BORDER_MAIN equ b_m+1

payload_data:   db      0
payload_base:
blocknum:       dw      0       ; Payload block number
loadaddr:       dw      0       ; Load address
endaddr:        dw      0       ; Last byte of payload + 1
checksum:       dw      0       ; Space allocated for future checksum
payload_end_header:
