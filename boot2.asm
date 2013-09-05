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
        xor     a                    ; 4T
sync:
sync_loop:
        call    measure_half_symbol     ; 17T [edge+111T]
        cp      sync_threshold          ; 7T  [edge+118T] carry set if time > threshold
        ccf                             ; 4T [edge+122T]
        rl      e                       ; 8T [edge+130T]
        rl      d                       ; 8T [edge+138T]
        rl      l                       ; 8T [edge+146T]
        rl      h                       ; 8T [edge+154T]
        ld      a,sync_train_1          ; 7T [edge+161T]
        cp      h                       ; 4T [edge+165T]
        ld      a,+(69+16)/32           ; 7T [edge+172T]
        jr      nz,sync_loop            ; 12T/7T [edge+179/184T]
        ld      a,sync_train_2          ; 7T [edge+186T]
        cp      l                       ; 4T [edge+190T]
        ld      a,+(94+16)/32           ; 7T [edge+197T]
        jr      nz,sync_loop            ; 12T/7T [edge+204/209T]
        ld      a,sync_train_3          ; 7T [edge+211T]
        cp      d                       ; 4T [edge+215T]
        ld      a,+(119+16)/32          ; 7T [edge+222T]
        jr      nz,sync_loop            ; 12T/7T [edge+229/234T]
        ld      a,sync_train_4          ; 7T [edge+236T]
        cp      e                       ; 4T [edge+240T]
        ld      a,+(144+16)/32          ; 7T [edge+247T]
        jr      nz,sync_loop            ; 12T/7T [edge+254/259T]

        ; Calibrate:
        ;
        ; Measure a test pattern.
        ; From this test, we calibrate the thresholds for pulse measurement
        ; later. This corrects for variation in record and playback motors
        ; as well as tape stretch, which gives much more accurate
        ; descrimination between symbols.
calibrate:
        ld      hl,0                    ; 10T [edge+264T]
        ld      d,h                     ; 4T [edge+268T]
        ld      e,l                     ; 4T [edge+272T]
        ld      a,+(279+16)/32          ; 7T [edge+279T]
        call    measure_symbol          ;[edge+296T] 17T [edge+111T]
        ld      l,a                     ; 4T [edge+115T]
        ld      a,+(139+16)/32          ; 7T [edge+122T]
        call    measure_symbol          ;[edge+139T] 17T [edge+111T]
        ld      e,a                     ; 4T [edge+115T]
        add     hl,de                   ; 11T [edge+126T]
        ld      a,+(150+16)/32          ; 7T [edge+133T]
        call    measure_symbol          ;[edge+150T] 17T [edge+111T]
        ld      e,a                     ; 4T [edge+115T]
        add     hl,de                   ; 11T [edge+126T]
        ld      a,+(150+16)/32          ; 7T [edge+133T]
        call    measure_symbol          ;[edge+150T] 17T [edge+111T]
        ld      e,a                     ; 4T [edge+115T]
        add     hl,de                   ; 11T [edge+126T]

        ; HL now contains the duration of four 8 period delays.
        ; Multiply by 8:
        add     hl,hl                   ; 11T [edge+137T]
        add     hl,hl                   ; 11T [edge+148T]
        ; H contains 0.5 period delay
        ld      b,h                     ; 4T B: 0.5 periods [edge+154T]
        add     hl,hl                   ; 11T [edge+165T]
        ; H now contains the average measured 1 period time
        ld      c,h                     ; 4T C: 1 period [edge+169T]
        add     hl,hl                   ; 11T [edge+180T]
        ld      d,h                     ; 4T D: 2 periods [edge+184T]
        add     hl,hl                   ; 11T [edge+195T]
        ld      e,h                     ; 4T E: 4 periods [edge+199T]
        add     hl,hl                   ; 4T H: 8 periods [edge+203T]
        ; Now to calculate the thresholds
        ; Done in Gray code order for fastest calculation speed.
        ld      a,c                     ; 4T [edge+207T]
        add     a,d                     ; 4T [edge+211T]
        ld      (thres_3),a             ; 13T [edge+224T]
        add     a,e                     ; 4T [edge+228T]
        ld      (thres_7),a             ; 13T [edge+241T]
        sub     d                       ; 4T [edge+244T]
        ld      (thres_5),a             ; 13T [edge+257T]

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

; Set up to load payload
        ; [edge+257T]
        ld      hl,payload_base         ; 10T [edge+267T]
        ld      bc,payload_end_header   ; 10T [edge+277T]
        ld      a,b                     ; 4T [edge+281T]
        ld      (end_h),a               ; 13T [edge+294T]
        ld      a,c                     ; 4T [edge+298T]
        ld      (end_l),a               ; 13T [edge+311T]

        ld      d,$01                   ; 7T [edge+318T]
        xor     a                       ; 4T [edge+322T]
        ld      (payload_data),a        ; 13T [edge+335T]
        ld      a,+(342+16)/32          ; 7T [edge+342T]
readdata:
        call    measure_symbol          ; 17T [edge+111T]
smc01:  cp      selfmodified            ; 7T    thres_5 stored here [edge+119T]
        ccf                             ; 4T [edge+123T]
        jp      c,bits_1_               ; 10T [edge+133T]
        call    addbit                  ; 61T [edge+194T]
smc02:  cp      selfmodified            ; 7T    thres_3 stored here [edge+201T]
        ccf                             ; 4T [edge+205T]
        call    addbit                  ; 61T [edge+266T]
        jp      readdataend             ; 10T [edge+276T]

bits_1_:call    addbit                  ; 61T [edge+194T]
smc03:  cp      selfmodified            ; 7T    thres_7 stored here [edge+201T]
        ccf                             ; 4T [edge+205T]
        call    addbit                  ; 61T [edge+266T]
        jp      readdataend             ; 10T [edge+276T] This balances timings

thres_3         equ     smc02+1
thres_5         equ     smc01+1
thres_7         equ     smc03+1

readdataend:
        ; [edge+276T]
        ; Up to 4 bits can be added for each symbol.
        ; Once BC=HL, the block is over.
        ld      a,h                     ; 4T [edge+280T]
smc10:  cp      selfmodified            ; 7T [edge+287T]
        ld      a,+(404+16)/32          ; 7T [edge+394T]
        jp      nz,readdata             ; 10T [edge+404T]
        ld      a,l                     ; 4T [edge+414T]
smc11:  cp      selfmodified            ; 7T [edge+421T]
        ld      a,+(438+16)/32          ; 7T [edge+428T]
        jp      nz,readdata             ; 10T [edge+438T]
        ; Payload section is complete.
        ld      a,(payload_data)        ; 13T [edge+451T]
        and     a                       ; 4T [edge+455T]
        jp      nz,payload_complete     ; 10T [edge+465T]

end_h   equ     smc10+1
end_l   equ     smc11+1

        ; Payload header loaded:
        ; Set up load and end address
        ; TODO: Handle block number
        ; TODO: Handle checksum

        ld      hl,(loadaddr)           ; 16T [edge+481T]
        ld      bc,(endaddr)            ; 20T [edge+501T]
        ld      a,b                     ; 4T [edge+505T]
        ld      (end_h),a               ; 13T [edge+518T]
        ld      a,c                     ; 4T [edge+524T]
        ld      (end_l),a               ; 13T [edge+537T]
        ld      a,$01                   ; 7T [edge+544T]
        ld      (payload_data),a        ; 13T [edge+557T]
        ld      a,+(574+16)/32          ; 7T [edge+564T]
        jp      readdata                ; 10T [edge+574T] 574T = 164µs

payload_complete:
        ; No concern about counts past edge now, as next stage will be to resynchronise
        nop                             ; Loader can insert a CALL or JP here
        nop                             ; to execute external routines
        nop                             ;
        xor     a                       ; 0 is opcode for NOP
        ld      (payload_complete),a    ; 13T
        ld      (payload_complete+1),a  ; 13T
        ld      (payload_complete+2),a  ; 13T
        jp      sync                    ; 10T

PAYLOAD_JUMP equ payload_complete

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
addbit: rl      d               ; 8T [call+25T]
        jr      nc,delab        ; 7/12T [call+32/37T]
        ld      (hl),d          ; 7T [call+39T]
        ld      d,$01           ; 7T [call+46T]
        inc     hl              ; 6T [call+52T]
retab:  ret                     ; 10T [call+61/62T]
delab:  nop                     ; 4T [call+41T]
        jp      retab           ; 10T [call+51T]

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
        call    measure_half_symbol ; 17T [edge+111T]

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

BORDER_FLASH equ b_fl+1
BORDER_MAIN equ b_m+1

payload_data:   db      0
payload_base:
blocknum:       dw      0       ; Payload block number
loadaddr:       dw      0       ; Load address
endaddr:        dw      0       ; Last byte of payload + 1
checksum:       dw      0       ; Space allocated for future checksum
payload_end_header:
