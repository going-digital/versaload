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

; Sync train
;
sync_train_1    equ     $c3
sync_train_2    equ     $3c
sync_train_3    equ     $00
sync_train_4    equ     $ff

; Symbols are 110 and 440µs long, so set threshold at geometric mean, 220µs
sync_threshold  equ     +(770+16)/32   ; 770T = 220us = sqrt(110 * 440)
glitch_delay    equ     +(308+16)/32   ; 308T = 88us = 110us - 20%

; Border values for OUT($fe)
border_black    equ     $08
border_blue     equ     $09
border_red      equ     $0a
border_magenta  equ     $0b
border_green    equ     $0c
border_cyan     equ     $0d
border_yellow   equ     $0e
border_white    equ     $0f
