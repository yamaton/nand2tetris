// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed.
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.


(NOKEY)
    @i
    M=0

    @SCREEN
    D=A

    @pos
    M=D

(WHITELOOP)
    @i
    D=M

    @8192
    D=D-A

    @KEYCHECK
    D;JGE

    @pos
    A=M
    M=0

    @pos
    M=M+1

    @i
    M=M+1

    @WHITELOOP
    0;JMP

(KEYCHECK)
    @KBD   // keyboard
    D=M

    @NOKEY
    D;JEQ

    @i
    M=0

    @SCREEN
    D=A

    @pos
    M=D

(BLACKLOOP)
    @i
    D=M

    @8192
    D=D-A

    @KEYCHECK
    D;JGE

    @pos
    A=M
    M=-1

    @pos
    M=M+1

    @i
    M=M+1

    @BLACKLOOP
    0;JMP

