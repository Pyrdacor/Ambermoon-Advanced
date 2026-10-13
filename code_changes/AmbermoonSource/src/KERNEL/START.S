; Program start & main loop
; Reconstructed from the disassembly of AM2_CPU (Ambermoon 1.21).
; This part is missing in the original source code.

	SECTION	Program,code

;*****************************************************************************
; [ Program entry ]
; Jumps to [ Check_start ]. The two following longwords are filled with
; pointers to the version and date/language strings when the texts are loaded.
;*****************************************************************************
Start:
;---- Debug printing
	macro DebugPrint
	movem.l D7/D0,-(SP)
	move.l \+,D0
	IFNB \.
		move.l #\.,D7
	ELSE
		moveq #10,D7
	ENDIF
	jsr FUN_DebugPrint
	movem.l (SP)+,D0/D7
	endm
	jmp	Check_start

Version_string1_ptr:
	dc.l	0

Version_string2_ptr:
	dc.l	0

;*****************************************************************************
; [ Load texts and resources and reset the module stack ]
;*****************************************************************************
Init_texts_and_resources:
	jsr	Load_texts
	jsr	Load_resources
	jsr FUN_DetermineVBlankFreq
	jsr FUN_CloseAllWindows
	rts

;*****************************************************************************
; [ Initializations before the program starts (fast memory check etc.) ]
;*****************************************************************************
FUN_DetermineVBlankFreq:
	movem.l A6/D0,-(SP)
	lea     4.w,A6         ; ExecBase
    move.w  $1A4(A6),D0    ; VBlankFrequency (Offset $1A4)
	cmpi.w  #60,D0
	beq.b   .Set
	moveq   #50,D0
.Set:
	move.w  D0,DAT_VBlankFreq
	movem.l (SP)+,D0/A6
	rts
DAT_VBlankFreq:
	dc.w 50
Pre_start:
	jsr	Pre_start_initializations
	bra.s	Start_program

;*****************************************************************************
; [ Check the start parameters ]
;   IN : a0 - Pointer to start parameters from the loader (.l)
;        $00abacab (.l), intro menu choice (.w), external files flag (.b)
;  OUT : d0 - -10 if not started by the Ambermoon loader
;*****************************************************************************
Check_start:
	cmpi.l	#11250859,(a0)+
	beq.s	Pre_start
	moveq.l	#-10,d0
	rts

;*****************************************************************************
; [ Program start ]
;   IN : a0 - Pointer to start parameters (after the magic longword) (.l)
; NOTE :
;   - Initializes the system and the kernel, then enters the main loop.
;*****************************************************************************
Start_program:
	move.w	(a0)+,Intro_menu_choice
	move.b	(a0)+,Intro_menu_choice+2
	move.l	(sp)+,Return_address
	move.l	sp,Stack_pointer
	lea.l	Return_value,sp
	jsr	Allocate_chip_and_fast_memory
	bpl.s	.Skip
	jmp	Exit_to_loader
.Skip:
	jsr	Init_system
	IFD	DEBUG
	jsr	Install_AE_handler	; Debug build only
	ENDC
	jsr	Init_blitter
Restart_game:
	lea.l	Return_value,sp
	jsr	Init_sub_files
	jsr	Reset_PA_stack
	jsr	Reset_MA_stack
	jsr	Reset_Mptr_stack
	jsr	Reset_CA_stack
	jsr	Reset_tree_stack
	jsr	Reset_scroll_bar_stack
	jsr	Clear_all_HDOBs
	jsr	Init_texts_and_resources
	jsr	Show_mouse_pointer
	moveq.l	#0,d0
	jsr	Set_music
	move.l	Off_screen,a0
	jsr	Clear_screen
	jsr	Update_screen
	jsr	Fade_in_all
	jsr	Init_program
.Loop:
	jsr	Update_display
	jsr	Handle_input
	jsr	Switch_screens
	bra.s	.Loop

;*****************************************************************************
; [ Exit the program ]
; NOTE :
;   - This routine does not return.
;*****************************************************************************
Exit_program:
	moveq.l	#0,d0
	jsr	Set_music
	jsr	Exit_system
Exit_to_loader:
	jsr	Free_all_memory
	move.l	Stack_pointer,sp
	move.l	Return_value,d0
	move.l	Return_address,a0
	jmp	(a0)


	SECTION	Chip_DATA,data_c
	SECTION	Longword_BSS,bss
MysticBackupData:
	ds.w	99			; 33 per possible char
	SECTION	Chip_DATA,data_c
	dc.w	$ffff		; Copper commands
	dc.w	$fffe
