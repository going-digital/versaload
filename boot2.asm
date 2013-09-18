; This code _must_ execute in uncontended memory as it is time critical.

; TODO: Can we move some of this to a turboloaded block? BASIC loader is
; getting rather long.
;

; Selfmodifying code notes:
;       sm1     jp m or jp p: Wait for positive or negative edge
;       sm2     scf or xor a: Set or clear carry from last received bit
;       sm3     Jump address for bit state machine
;       sm4     Border flash when loading
;       sm5     Border main when loading
;       sm6     Border flash after loading error
;       sm7     Border main after loading error
;       sm8     Baud rate adjustment
;       sm9     Current border flash
;       smA     Current border main
;       smB     jp m or jp p: Bit decision

        include "globals.inc"
        include "setbaud.asm"   ; Baud rate settings
        include "sysvar.inc"
        include "romhooks.inc"

        org     loadbase

        ; CLEAR
        ;
        ; Reset RAMTOP etc
        ; See the Spectrum ROM disassembly $1EAC
        ;
        ld      bc,clearbase
        push    bc
        ld      de,(VARS)
        ld      hl,(E_LINE)
        dec     hl
        call    RECLAIM_1
        pop     hl
        ld      (RAMTOP),hl
        pop     de              ; Pop STMT-RET
        pop     bc              ; Pop error address
        ld      (hl),$3e
        dec     hl
        ld      sp,hl
        push    bc
        ld      (ERR_SP),sp
        push    de

        ; Now load from tape
        ;
        ld      de,$ffff        ; Inhibit sync pattern detection for at least 16 bits
        di                      ; Interrupts off - time critical from here on
        ; Wait for positive edge, then sample at 0.75 bit periods
waitEdge:
        in      a,($fe)         ; 11T [edge+11] Loop time 25T
        add     a,a             ; 4T [edge+15]
sm1:    jp      m,waitEdge      ; 10T [edge+25]

        ; Whilst waiting for the next sampling point, process the last received
        ; bit.
        ; This means we have 0.75 bit periods to work, rather than 0.25.

sm2:    scf                     ; 4T [edge+29] Self modified: set or clear carry
sm3:    jp      stage1          ; 10T [edge+40] Self modified: jump to bit processing step

stage1: ; Wait for synchronisation pattern ('00111111 11111101')
        ; which matches the EBU LTC pattern
        rl      e               ; 8T [edge+48]
        rl      d               ; 8T [edge+56]
        ld      a,$3f           ; 7T [edge+63]
        xor     d               ; 4T [edge+67]
        ld      b,30-6          ; 7T [edge+74]
        jp      nz,endstage     ; 10T [edge+84] -6 => -78T delay
        ld      a,$fd           ; 7T [edge+91]
        xor     e               ; 4T [edge+95]
        ld      b,30-9          ; 7T [edge+102]
        jp      nz,endstage     ; 10T [edge+112] -9 => -117T delay

        ld      hl,stage2       ; 10T [edge+122] Synchronisation pattern match
        ld      (sm3+1),hl      ; 16T [edge+138]
        ld      bc,+(30-14)*256+8; 10T [edge+148] Set block length, and delay compensation
        ld      de,$0100        ; 10T [edge+158]
        ld      ix,headerParam  ; 14T [edge+172]
        jp      endstage        ; 10T [edge+182] -14 => -138T delay

stage2: ; Read block header and verify
        ; c: byte count
        ; d: incoming shift register / bit counter
        ; e: checksum

        rl      d               ; 8T [edge+48]
        ld      b,30-5          ; 7T [edge+55]
        jp      nc,endstage     ; 10T [edge+65] -5 => -65T delay
        ; Complete byte received
        ld      a,e             ; 4T [edge+69]
        add     a,d             ; 4T [edge+73]
        ld      e,a             ; 4T [edge+77]
        ld      (ix+0),d        ; 19T [edge+96]
        ld      d,$01           ; 7T [edge+103] Reset byte counter
        inc     ix              ; 10T [edge+113]
        dec     c               ; 4T [edge+117]
        ld      b,30-10         ; 7T [edge+124]
        jp      nz,endstage     ; 10T [edge+134] -10 => -130T delay
        ; Complete header received
        ; Verify checksum
        rlc     e               ; 8T [edge+142] Is checksum zero?
        ld      hl,stageerr     ; 10T [edge+152]
        ld      (sm3+1),hl      ; 16T [edge+168]
        ld      b,30-14         ; 7T [edge+175]
        jp      nz,endstage     ; 10T [edge+185] -14 => -138T delay
        ; Verify block number
        ld      de,(nextblk)    ; 20T [edge+205]
        ld      hl,(blknum)     ; 16T [edge+221]
        and     a               ; 4T [edge+225] clear carry
        adc     hl,de           ; 15T [edge+240] add hl,de doesn't adjust carry flag
        ld      b,30-20         ; 7T [edge+247]
        jp      nz,stageerr    ; 10T [edge+257] -20 => 260T delay
        ; Handle block mode
        ld      ix,(blkaddr)    ; 20T [edge+277] Set load address
        ld      a,(blktype)     ; 13T [edge+290]
        and     a               ; 4T [edge+294]
        jp      z,blkData       ; 10T [edge+304]
        call    exec            ; 17T [edge+321] Handle execution block
        ld      hl,(nextblk)    ; 16T [edge+?] Advance block counter
        dec     hl              ; 6T [edge+?]
        ld      (nextblk),hl    ; 16T [edge+?]
        ld      hl,stage1       ; 10T [edge+?]
        ld      (sm3+1),hl      ; 16T [edge+?]
        ld      de,$ffff        ; 10T [edge+?]
        ld      b,1             ; 7T [edge+?]
        jp      endstage        ; 10T [edge+?] Delay unknown. Resync after exec block.

exec    jp      (ix)            ; 10T [edge+327]

blkData:; Set up for data load
        ld      a,(blklen)      ;13T [edge+313] Set block length
        ld      c,a             ;4T [edge+317]
        ld      a,(blksum)      ;13T [edge+330] Set checksum
        ld      e,a             ;4T [edge+334]
        ld      hl,stage3       ;10T [edge+344]
        ld      (sm3+1),hl      ;16T [edge+360]
        ld      d,$01
        ld      b,30-29         ;7T [edge+367]
        jp      endstage        ;10T [edge+377] -29 => 377T delay

stage3: ; Read data and verify
        rl      d               ; 8T [edge+48]
        ld      b,30-5          ; 7T [edge+55]
        jp      nc,endstage     ; 10T [edge+65] -5 => 65T delay
        ; Complete byte received
        ld      a,e             ; 4T [edge+69] Update checksum
        add     a,d             ; 4T [edge+73]
        ld      e,a             ; 4T [edge+77]
        ld      (ix+0),d        ; 19T [edge+96]
        ld      d,$01           ; 7T [edge+103] Reset bit counter
        inc     ix              ; 10T [edge+113]
        dec     c               ; 4T [edge+117] Count bytes
        ld      b,30-10         ; 7T [edge+124]
        jp      nz,endstage     ; 10T [edge+134] -10 => 130T delay
        ; Verify checksum
        rlc     e               ; 8T [edge+142] Is checksum zero?
        ld      hl,stageerr     ; 10T [edge+152]
        ld      (sm3+1),hl      ; 16T [edge+168]
        ld      b,30-14         ; 7T [edge+175]
        jp      nz,endstage     ; 10T [edge+185] -14 => 182T delay
        ; Advance block counter
        ld      hl,(nextblk)    ; 16T [edge+201]
        dec     hl              ; 6T [edge+207]
        ld      (nextblk),hl    ; 16T [edge+223]
        ; Clear loading error indication
sm4:    ld      a,$9            ; 7T [edge+230] Blue flash
        ld      (sm9+1),a       ; 13T [edge+243]
sm5:    ld      a,$f            ; 7T [edge+230] White border
        ld      (smA+1),a       ; 13T [edge+243]
        ; Synchronise for next block
        ld      hl,stage1       ; 10T [edge+253]
        ld      (sm3+1),hl      ; 16T [edge+269]
        ld      de,$ffff        ; 10T [edge+279]
        ld      b,30-23         ; 7T [edge+286]
        jp      endstage        ; 10T [edge+296] -23 => 299T

stageerr: ; Last block was corrupt
        ld      hl,stage1       ; 10T [edge+50T]
        ld      (sm3+1),hl      ; 16T [edge+66]
        ld      de,$ffff        ; 10T [edge+76]
        ; Set loading error indication
sm6:    ld      a,$8            ; 7T [edge+83] Black flash
        ld      (sm9+1),a       ; 13T [edge+96]
sm7:    ld      a,$a            ; 7T [edge+103] Red border
        ld      (smA+1),a       ; 13T [edge+116]
        ld      (c_act),a       ; 13T [edge+129] Pause countdown state
        ld      b,30-11         ; 7T [edge+136]
        jp      endstage        ; 10T [edge+146]

endstage:
        ; Loop to balance alternate code path timings
        ; 13 cycles per unit
dellp:  djnz    dellp           ; Wait 0.75 bit periods
        ; [edge+390T]

        ; Loading state machine
        ; Perform useful tasks eg. loading counter, games or animation
        ; Each state must take an identical execution time.
        ;
        exx
statem: jp      state0          ; 10T [10]
endstate:
        ld      (statem+1),hl   ; [332] 16T [348]
        exx
        ; [edge+390T+348T]
        ; [edge+738T]

sm8:    ld      b,BAUDLOOPS     ; Set by setbaud.py
del2lp: djnz    del2lp

sm9:    ld      a,$9            ; Default flash blue
        out     ($fe),a
smA:    ld      a,$f            ; Default border white
        out     ($fe),a
        in      a,($fe)         ; 11T
        add     a,a             ; 4T
smB:    jp      m,rx0           ; 10T
rx1:    ; Just received a 1 bit. Invert sense next time.
        ld      a,(sm1)
        xor     $08             ; Swap jp p and jp m instructions
        ld      (sm1),a         ;
        ld      (smB),a
        ld      a,SCF_OPCODE
        ld      (sm2),a
        jp      waitEdge

rx0:    ld      a,ANDA_OPCODE   ; Just received a 0 bit. No need to invert.
        ld      (sm2),a         ; 4T Clear carry flag
        jp      waitEdge

; State machine states
; All states take a fixed time of X T-states to execute.

NUMSTATES equ 5

; State 0: Update countdown state with any new data
state0:

        ; Is update available? if so use it.
        ld      a,(count_update); 13T [63]
        cp      $a5             ; 7T [70]
        jp      nz,s0_a         ; 10T [80]

        ; Atomic update to working count
        ld      hl,count_block  ; 10T [90]
        ld      de,c_min        ; 10T [100]
        ld      bc,6            ; 10T [110]
        ldir                    ; 121T [231] LDIR takes 21*BC-5 T
        xor     a               ; 4T [235]
        ld      (count_update),a; 13T [248]
        jp      s0_b            ; 10T [258]

        ; Compensating delay if update didn't happen
s0_a:   call    delay161        ; [80] 17+161 [258]

        ; Is count active? If so, move to state 1
s0_b:   ld      a,(c_act)       ; [258] 13T [271]
        cp      $a5             ; 7T [278]
        ld      hl,state0       ; 10T [288]
        jp      nz,s0_c         ; 10T [298]
        ld      hl,state1       ; 10T [308]
        jp      s0_d            ; 10T [318]

s0_c:   jp      s0_e            ; [298] 10T [308]
s0_e:   jp      s0_f            ; 10T [318]
s0_d:   and     a               ; [318] 4T [322]
s0_f:   jp      endstate        ; 10T [332]


; State 1: Decrement countdown counters in memory
state1: ld      hl,(c_bits)     ; 16T [16] Decrement bits counter
        dec     hl              ; 6T [22]
        bit     7,h             ; 8T [30]
        jp      z,c1            ; 10T [40]
        ld      hl,BAUD/NUMSTATES; 10T [50] xx=bits per second / NUMSTATES = 750 for 3000baud, 4 states
        ld      (c_bits),hl     ; 16T [66]
        ld      a,(c_sec)       ; 13T [79] Decrement seconds
        dec     a               ; 4T [83]
        ld      (c_sec),a       ; 13T [96]
        jp      p,c2            ; 10T [106]
        ld      a,9             ; 7T [113]
        ld      (c_sec),a       ; 13T [126]
        ld      a,(c_tens)      ; 13T [139] Decrement tens of seconds
        dec     a               ; 4T [143]
        ld      (c_tens),a      ; 13T [156]
        jp      p,c3            ; 10T [166]
        ld      a,5             ; 7T [173]
        ld      (c_tens),a      ; 13T [186]
        ld      a,(c_min)       ; 13T [199] Decrement minutes
        dec     a               ; 4T [203]
        ld      (c_min),a       ; 13T [216]
        jp      s1end           ; 10T [226]
c1:     ld      (c_bits),hl     ; 16T [56]
        call    delay143        ; 17+143T [216]
        jp      s1end           ; 10T [226]
c2:     ld      (c_sec),a       ; 13T [119]
        call    delay80         ; 17+80T [216]
        jp      s1end           ; 10T [226]
c3:     ld      (c_tens),a      ; 13T [179]
        call    delay20         ; 17+20T [216]
        jp      s1end           ; 10T [226]
        ; TODO: Recalculate timings below
s1end:  call    delay69         ; 17+69T [312]
        ld      hl,state2       ; 10T [322]
        jp      endstate        ; 10T [332]

; State 2: Display countdown minutes digit
state2: ld      a,(c_min)       ; 13T [23] Print minutes digit
cd1:    ld      hl,$50de        ; 10T [33]
        ld      (pdest+1),hl    ; 16T [49]
        call    printn          ; 17+246T [312]
        ld      hl,state3       ; 10T [322]
        jp      endstate        ; 10T [332]

; State 3: Display countdown minutes digit
state3: ld      a,(c_tens)      ; 13T [23] Print tens digit
cd2:    ld      hl,$50fe        ; 10T [33]
        ld      (pdest+1),hl    ; 16T [49]
        call    printn          ; 17+246T [312]
        ld      hl,state4       ; 10T [322]
        jp      endstate        ; 10T [332]

; State 4: Display countdown minutes digit
state4: ld      a,(c_sec)       ; 13T [23] Print seconds digit
cd3:    ld      hl,$50ff        ; 10T [33]
        ld      (pdest+1),hl    ; 16T [49]
        call    printn          ; 17+246T [312]
        ld      hl,state0       ; 10T [322]
        jp      endstate        ; 10T [332]

        ; Print number routine
        ; A = number to print, 0-9
        ; 
printn: ld      de,chrset       ; 10T [33] ; $3d80
        add     a,a             ; 4T [4]
        add     a,a             ; 4T [8]
        add     a,a             ; 4T [12]
        ld      h,0             ; 7T [19] Calculate character base address
        ld      l,a             ; 4T [23]
        add     hl,de           ; 11T [44] HL = source character
pdest:  ld      de,$4000        ; 10T [54] DE = screen address
        rept    7
        ld      a,(hl)          ; 7*7T [103]
        ld      (de),a          ; 7*7T [152]
        inc     hl              ; 7*6T [194]
        inc     d               ; 7*4T [222]
        endm
        ld      a,(hl)          ; 7T [229]
        ld      (de),a          ; 7T [236]
        ret                     ; 10T [246]

; General purpose delay routines

delay161:
        and     a               ; [-161] 4 [-157]
        and     a               ; 4 [-153]
        jp      delay143        ; 10 [-143]
delay143:
        call    delay20         ; [-143] 17+13 [-113]
        ld      a,(0)           ; [-113] 13 [-100]
        ld      a,(0)           ; [-100] 13 [-87]
        jp      delay77         ; [-87] 10 [-77]
delay77:ld      a,(0)           ; [-77] 13 [-64]
delay64:call    delay23         ; [-64] 17+23 [-24]
        and     a               ; [-24] 4 [-20]
delay20:jp      d10             ; [-20]
d10:    ret                     ; [-10] 10T

delay80:inc     hl              ; [-80] 6T [-74]
        jp      delay64         ; [-74] 10+64

delay69:call    delay20         ; [-69] 17+20 [-32]
        nop                     ; [-32] 4 [-28]
        nop                     ; [-28] 4 [-24]
        nop                     ; [-24] 4 [-20]
        jp      d10             ; [-20] 10+10

delay23:ld      a,(0)           ; [-23] 13T [-10]
        ret


c_min:  db      1
c_tens: db      3
c_sec:  db      7
c_bits: dw      $1
c_act:  db      $0              ; Set to $a5 to activate countdown

nextblk dw      0



count_block:
        db      1       ; Minutes
        db      3       ; Tens of seconds
        db      7       ; Seconds
        dw      1       ; Fractions of a second, in state loops
count_update:
        db      0       ; Last byte of block: set to $a5 to load new values

        ; Header block, 8 bytes long.
headerParam:
blknum  dw      0               ; Block number, incrementing from 0000
blkaddr dw      0               ; Block address.
blklen  db      0               ; Data length, 1-256 bytes (0=256 bytes)
blktype db      0               ; 0: Load data. 1: Call code
blksum  db      0               ; Checksum of data block (so additive sum = 0)
blkhsum db      0               ; Checksum of header block (so additive sum = 0)

        ; Countdown character set
chrset  db      $1e,$3b,$6b,$63,$63,$62,$3c,$00 ; 0
        db      $0c,$1c,$3c,$0c,$0c,$0d,$3f,$60 ; 1
        db      $3e,$63,$43,$1e,$3d,$63,$7f,$00 ; 2
        db      $7f,$63,$46,$0e,$03,$63,$3e,$00 ; 3
        db      $0e,$0c,$6c,$ed,$6f,$7f,$0c,$18 ; 4
        db      $7f,$63,$61,$7e,$03,$63,$be,$00 ; 5
        db      $3e,$63,$60,$6e,$7b,$63,$3e,$00 ; 6
        db      $7f,$63,$43,$16,$0c,$1a,$18,$00 ; 7
        db      $3e,$63,$63,$3e,$63,$63,$3e,$00 ; 8
        db      $3e,$63,$6f,$3b,$03,$63,$3e,$00 ; 9

; Exports
;
; These addresses are altered during loading to customise the loader
;
BORDER_FLASH            equ     sm4+1   ; Border flash, loading
BORDER_MAIN             equ     sm5+1   ; Border main, loading
BORDER_ERROR_FLASH      equ     sm6+1   ; Border flash, loading error
BORDER_ERROR_MAIN       equ     sm7+1   ; Border main, loading error
COUNT_MINS              equ     cd1+1   ; Screen address of minutes digit
COUNT_TENS              equ     cd2+1   ; Screen address of tens digit
COUNT_SECS              equ     cd3+1   ; Screen address of secs digit
COUNT_BLOCK             equ     count_block
COUNT_CHRSET            equ     chrset  ; Countdown character set
COUNT_DISABLE           equ     c_act
COUNT_STATES            equ     NUMSTATES
