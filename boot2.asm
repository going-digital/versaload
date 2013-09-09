; This code _must_ execute in uncontended memory as it is time critical.

; BMC decoder
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

        org     loadbase

bmc:    ld      de,$ffff        ; Inhibit sync pattern detection for at least 16 bits

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
        
        ; At this point, data is already corrupt. Shifted?



; E1 (blue paper) E0 (black paper)
; 11100001        11100000

; Should be blue paper white ink
; 0?001111        0?000111

;0x0011110x001111  0x0001110x000111

; Black area:
; 


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
sm4:    ld      a,9             ; 7T [edge+230] Blue flash
        ld      (sm9+1),a       ; 13T [edge+243]
sm5:    ld      a,8             ; 7T [edge+230] Black border
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
sm6:    ld      a,$b            ; 7T [edge+83] Magenta flash
        ld      (sm9+1),a       ; 13T [edge+96]
sm7:    ld      a,$a            ; 7T [edge+103] Red border
        ld      (smA+1),a       ; 13T [edge+116]
        ld      b,30-10         ; 7T [edge+123]
        jp      endstage        ; 10T [edge+133] -10 => 130T

endstage:
        ; Loop to balance alternate code path timings
        ; 13 cycles per unit
dellp:  djnz    dellp           ; Wait 0.75 bit periods
        ; [edge+390T]
        ; Baud rate adjustment
sm8:    ld      b,37            ; 3000 baud
del2lp: djnz    del2lp

sm9:    ld      a,$9            ; Default flash blue
        out     ($fe),a
smA:    ld      a,$f            ; Default border white
        out     ($fe),a

        ; Next bit sample point
        ; Baud 1b    0.75b Loops
        ; 1500 2333T 1750T 105
        ; 2000 1750T 1313T 71   Equiv to ROM
        ; 2500 1400T 1050T 51
        ; 3000 1167T 875T  37
        ; 3500 1000T 750T  28
        ; 4000 875T  656T  20   Equiv to Microsphere
        ; 4500 778T  583T  15
        ; 5000 700T  525T  10
        ; 5500 636T  477T  7
        ; 6000 583T  438T  4
        ; 6500 538T  404T  1
        ; 7000 500T  375T  n/a


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

nextblk dw      0

        ; Header block, 8 bytes long.
headerParam:
blknum  ds      2               ; Block number, incrementing from 0000
blkaddr ds      2               ; Block address.
blklen  ds      1               ; Data length, 1-256 bytes (0=256 bytes)
blktype ds      1               ; 0: Load data. 1: Call code
blksum  ds      1               ; Checksum of data block (so additive sum = 0)
blkhsum ds      1               ; Checksum of header block (so additive sum = 0)

; Exports
BORDER_FLASH            equ     sm4+1
BORDER_MAIN             equ     sm5+1
BORDER_ERROR_FLASH      equ     sm6+1
BORDER_ERROR_MAIN       equ     sm7+1
