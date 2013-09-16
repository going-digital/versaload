; Memory map of loading environment
;
; $0000-$3FFF   BASIC ROM
; $4000-$7FFF   Page 0 (contended memory)
;   $4000-$4100 Post-load relocator
;   $5dbf       RAMTOP
;   $5dc0-$7fff Payload
; $8000-$BFFF   Page 5 (uncontended memory)
;   $8000-$bbff Payload
;   $bc00-$beff Loader
;   $bf00-$bfff System stack during load?
; $C000-$FFFF   Paged memory bank
;   $c000-$cfff Payload
;   $d000-$d3ff Payload to relocate to $bc00
;   $ef00-$efff Loader print routine
;   $f000-$f0ff Loader character set generator
;   $fd00-$ffff Loader print character set

loadbase        equ     $BC00
printbase       equ     $ef00
genfont         equ     $f000
fontbase        equ     $fd00

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