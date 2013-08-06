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
; LLSSLLSSSLLSSLLSSLLSSLLSLLSSLLSS
; This should never occur in the data stream, as high/low pairs are not
; matched.
;
sync_train_1    equ     $CC
sync_train_2    equ     $66
sync_train_3    equ     $66
sync_train_4    equ     $CC
