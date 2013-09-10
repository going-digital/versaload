; Memory map of loading environment
;
; $0000-$3FFF   BASIC ROM
; $4000-$7FFF   Page 0 (contended memory)
; $8000-$BFFF   Page 5 (uncontended memory)
;   $BC00-$BEFF Loader
;   $BF00-$BFFF System stack during load
; $C000-$FFFF   Paged memory bank

loadbase        equ     $BC00
stackptr        equ     $C000
printbase       equ     $be00
genfont         equ     $f000
fontbase        equ     $fd00

; Sync train
;
sync_train_1    equ     $c3
sync_train_2    equ     $3c
sync_train_3    equ     $00
sync_train_4    equ     $ff

; Symbols are 110 and 440µs long, so set threshold at geometric mean, 220µs
sync_threshold  equ     +(770+16)/32   ; 770T = 220us = sqrt(110 * 440)
glitch_delay    equ     +(308+16)/32   ; 308T = 88us = 110us - 20%

; Symbols are 110 and 440µs long, so set threshold at geometric mean, 220µs
;sync_threshold  equ     +(1089+16)/32   ; 1089T = 311us = sqrt(156 * 622)
;glitch_delay    equ     +(436+16)/32   ; 436T = 124us = 110us - 20%

; Symbols are 220 and 880µs long, so set threshold at geometric mean, 220µs
;sync_threshold  equ     +(770+16)/32   ; 770T = 220us = sqrt(110 * 440)
;glitch_delay    equ     +(308+16)/32   ; 308T = 88us = 110us - 20%

; Border values for OUT($fe)
border_black    equ     $08
border_blue     equ     $09
border_red      equ     $0a
border_magenta  equ     $0b
border_green    equ     $0c
border_cyan     equ     $0d
border_yellow   equ     $0e
border_white    equ     $0f

; Opcode literals
SCF_OPCODE      equ     $37     ; Sets carry flag
ANDA_OPCODE     equ     $a7     ; Clears carry flag