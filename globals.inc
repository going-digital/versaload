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

; Sync train is:
; LLSSLLSS SLLSSLLS SLLSSLLS LLSSLLSS
;  ___     _
; |   |___| |_|
;  _     ___
; | |___|   |_|
;
; This should never occur in the data stream, as high/low pairs are not
; matched.
;
sync_train_1    equ     $CC
sync_train_2    equ     $66
sync_train_3    equ     $66
sync_train_4    equ     $CC

; Symbols are 220 and 440µs long, so set threshold at geometric mean, 311µs
sync_threshold  equ     +(544+16)/32   ; 544T = 156us = sqrt(110 * 220)

;
border_black    equ     $08
border_blue     equ     $09
border_red      equ     $0a
border_magenta  equ     $0b
border_green    equ     $0c
border_cyan     equ     $0d
border_yellow   equ     $0e
border_white    equ     $0f
