; Combat magic
; Written by J.Horneman (In Tune With The Universe)
; Start : 4-5-1993
;
; *** Merged with Ambermoon 1.21 (based on the disassembly of AM2_CPU) ***
;   - Bugfixes are marked with "FIX:" comments.
;   - Texts and the item data are no longer part of the executable, they are
;     loaded from files. They are accessed via pointers ("..._ptr", see
;     KERNEL/TEXTS.S) instead of "lea.l <text>,an".
;

	SECTION	Program,code
;*****************************************************************************
; [ Combat screen - Use magic ]
;*****************************************************************************
Magic_combat:
	jsr	Destroy_ghosts		; Destroy !
	Get	Active_handle,a0		; Get spell classes
	move.b	Spell_class_counter(a0),d0
	Free	Active_handle
	moveq.l	#4-1,d7			; Find spell class
.Loop:	btst	d7,d0			; Got it ?
	beq.s	.Next
	move.w	d7,Selected_class		; Yes -> Store
	bra.s	.Found
.Next:	dbra	d7,.Loop			; No -> Next spell class
	bra.s	.Exit
.Found:	jsr	Set_layout_colours		; Select spell
	Push	Module,SpSelW_Mod
	jsr	Restore_combat_colours
	tst.w	Selected_spell		; Any selected ?
	beq.s	.Exit
	move.l	Active_participant,a0	; Yes -> Set caster's variables
	move.l	a0,Casting_participant
	moveq.l	#0,d0
	move.b	Part_nr(a0),d0
	move.w	d0,Casting_member
	move.b	Part_handle(a0),Casting_handle
 	move.b	#Cast_spell_action,Part_action(a0)
	jsr	Combat_spell_entry		; Select target
.Exit:	rts

;*****************************************************************************
; [ Combat - Select spell target & enter in participant data ]
; No registers are restored
;*****************************************************************************
Combat_spell_entry:
	lea.l	Spell_data,a0		; Get pointer to spell data
	move.w	Selected_class,d0
	mulu.w	#Max_spells,d0
	add.w	Selected_spell,d0
	subq.w	#1,d0
	mulu.w	#Spell_data_size,d0
	adda.w	d0,a0
	moveq.l	#0,d0			; Get target bits
	move.b	Spell_target_bits(a0),d0
	move.l	Casting_participant,a0	; Select target
	clr.b	Part_target+5(a0)
	tst.b	d0			; Any target ?
	beq.s	.None
	btst	#Special_target_bit,d0	; Special spell ?
	beq.s	.Target
.Special:	lea.l	Spell_exception_table,a1	; Yes -> Seek
	move.w	Selected_class,d0
	move.w	Selected_spell,d1
.Again:	cmp.l	#-1,(a1)			; End of table ?
	beq.s	.None
	cmp.w	Xspell_class(a1),d0		; Right class ?
	bne.s	.Next1
	cmp.w	Xspell_number(a1),d1	; Right spell ?
	bne.s	.Next1
	move.l	Xspell_target_entry(a1),a1	; Yes -> Do exception
	jsr	(a1)
	bra	.Exit
.Next1:	lea.l	Xspell_data_size(a1),a1	; Next exception
	bra.s	.Again
.None:	move.b	#No_targmode,Part_target+6(a0)	; No -> No target
	jsr	Enter_action
	bra.s	.Exit
.Target:	btst	#Item_target_bit,d0		; Item target ?
	beq.s	.Not_item
	move.b	#Item_targmode,Part_target+6(a0)	; Enter data
	clr.l	Part_target(a0)
	jsr	Enter_action
	bra.s	.Exit
.Not_item:	lea.l	Member_spell_target_table,a1	; Which target ?
	lea.l	Member_spell_target_vectors,a2
	moveq.l	#9-1,d7
.Loop2:	cmp.b	(a1)+,d0			; This one ?
	bne.s	.Next2
	move.l	(a2),a2			; Yes -> Select
	jsr	(a2)
	bra.s	.Exit
.Next2:	addq.l	#4,a2			; No
	dbra	d7,.Loop2
.Exit:	move.l	Casting_participant,a0	; Target selected ?
	tst.b	Part_target+5(a0)
	bne.s	.Yes
	clr.b	Part_action(a0)		; No -> Reset action
	move.w	#-1,Part_target(a0)
.Yes:	rts

;*****************************************************************************
; [ Combat action - Cast spell ]
;   IN : a0 - Pointer to caster participant data (.l)
; No registers are restored
;*****************************************************************************
Do_cast_spell:
;	move.l	a0,a1
;	lea.l	Combat_monsters,a0
;	moveq.l	#0,d0
;	move.w	Part_Y(a1),d1
;	mulu.w	#6,d1
;	add.w	Part_X(a1),d1
;	bset	d1,d0
;	move.l	d0,Part_target(a0)
;	move.l	Part_target+4(a1),Part_target+4(a0)
;	move.b	#Enemy_targmode,Part_target+6(a0)
;	not.b	Party_or_monster

	tst.b Party_or_monster
	beq.s	.Party1
	Set_anim	Magic_anim,a0		; Yes -> Animate
.Party1:	move.l	a0,Casting_participant	; Set caster's variables
	moveq.l	#0,d0
	move.b	Part_nr(a0),d0
	move.w	d0,Casting_member
	move.b	Part_handle(a0),Casting_handle
	moveq.l	#0,d0			; Set spell variables
	move.b	Part_target+4(a0),d0
	move.w	d0,Selected_class
	move.b	Part_target+5(a0),d0
	move.w	d0,Selected_spell
	jsr	Set_magic_target_mask
	jsr	Print_magic_action		; Tell 'em
	clr.b	Part_action(a0)		; Reset action
	tst.b Party_or_monster
	bne.s	.Monster
	lea.l	Party_comma_class_ptrs,a1	; Party
	bra.s	.Go_on
.Monster:	lea.l	Monster_comma_class_ptrs,a1	; Monster
.Go_on:	move.w	Selected_class,d0		; Get spell list address
	lsl.w	#2,d0
	move.l	0(a1,d0.w),d0
	beq	.Exit
	move.l	d0,a1
	move.w	Selected_spell,d0		; Get spell handler address
	lsl.w	#2,d0
	move.l	-4(a1,d0.w),d0
	beq	.Exit
	move.l	d0,a1
	jsr	(a1)			; Execute
.Exit:
	tst.b Party_or_monster
	beq.s	.Party2
	jsr	Wait_4_animation		; Yes -> Wait
.Party2:	rts

;*****************************************************************************
; [ Set normal magic target mask in combat ]
;   IN : a0 - Pointer to caster participant data (.l)
; All registers are restored
;*****************************************************************************
Set_magic_target_mask:
	movem.l	d0-d2/d6/d7/a1/a2,-(sp)
	moveq.l	#0,d1			; Clear
	move.b	Part_target+6(a0),d0	; Get target mode
	cmp.b	#Item_targmode,d0
	bpl	.Exit
	move.b	Part_type(a0),d2		; Friends or enemies ?
	btst	d0,#Targmode_invert
	beq.s	.Ok
	eor.b	#3,d2			; 1 <-> 2
.Ok:	cmp.b	#1,d2			; Friends ?
	bne	.Exit
	lea.l	Combat_matrix+29*4,a1	; Search two rows of matrix
	move.l	Part_target(a0),d0
	moveq.l	#30-1,d6
	moveq.l	#12-1,d7
.Loop:	btst	d6,d0			; Targeted ?
	beq.s	.Next
	tst.l	(a1)			; Yes -> Anyone there ?
	beq.s	.Next
	move.l	(a1),a2			; Yes -> Right type ?
	cmp.b	#1,Part_type(a2)
	bne.s	.Next
	move.b	Part_nr(a2),d2		; Yes -> Set
	bset	d2,d1
.Next:	subq.w	#1,d6			; Next matrix entry
	subq.l	#4,a1
	dbra	d7,.Loop
.Exit:	move.w	d1,Magic_target_mask	; Store
	movem.l	(sp)+,d0-d2/d6/d7/a1/a2
	rts

;*****************************************************************************
; [ Print "Casts!" text ]
;   IN : a0 - Pointer to attacker's participant data (.l)
; All registers are restored
;*****************************************************************************
Print_magic_action:
	movem.l	d0/a1,-(sp)
	move.l	a0,-(sp)
	lea.l	Magic_action_text,a1
	Get	Part_handle(a0),a0		; Insert caster's name
	lea.l	Char_name(a0),a0
	move.l	a0,(a1)
	move.l	Spell_names_ptr,a0		; Get spell name
	move.w	Selected_class,d0
	mulu.w	#Max_spells,d0
	add.w	Selected_spell,d0
	subq.w	#1,d0
	jsr	Find_small_text
	move.l	a0,8(a1)
	move.l	a1,a0			; Print text
	moveq.l	#0,d0
	jsr	Display_combat_text
	move.l	(sp)+,a0
	Free	Part_handle(a0)
	movem.l	(sp)+,d0/a1
	rts

;*****************************************************************************
; [ Combat action - Use magic object ]
;   IN : a0 - Pointer to participant data (.l)
; No registers are restored
;*****************************************************************************
Do_use_magic_object:
	move.l	a0,Casting_participant	; Set caster's variables
	moveq.l	#0,d0
	move.b	Part_nr(a0),d0
	move.w	d0,Casting_member
	move.b	Part_handle(a0),Casting_handle
	moveq.l	#0,d0			; Set spell variables
	move.b	Part_target+4(a0),d0
	move.w	d0,Selected_class
	move.b	Part_target+5(a0),d0
	move.w	d0,Selected_spell
	jsr	Set_magic_target_mask
	jsr	Print_magic_obj_action	; Tell 'em
	st	Magic_object_flag		; From object !
	clr.b	Part_action(a0)		; Reset action
	tst.b Party_or_monster
	bne.s	.Monster
	lea.l	Party_comma_class_ptrs,a1	; Party
	bra.s	.Go_on
.Monster:	lea.l	Monster_comma_class_ptrs,a1	; Monster
.Go_on:	move.w	Selected_class,d0		; Get spell list address
	lsl.w	#2,d0
	move.l	0(a1,d0.w),d0
	beq	.Exit
	move.l	d0,a1
	move.w	Selected_spell,d0		; Get spell handler address
	lsl.w	#2,d0
	move.l	-4(a1,d0.w),d0
	beq	.Exit
	move.l	d0,a1
	jsr	(a1)			; Execute
.Exit:	sf	Magic_object_flag
	rts

;*****************************************************************************
; [ Print "Uses object!" text ]
;   IN : a0 - Pointer to caster's participant data (.l)
; All registers are restored
;*****************************************************************************
Print_magic_obj_action:
	movem.l	d0/a0-a3,-(sp)
	lea.l	Magic_object_text,a3
	Get	Part_handle(a0),a1		; Insert caster's name
	lea.l	Char_name(a1),a2
	move.l	a2,(a3)
	moveq.l	#0,d0			; Get item slot
	move.b	Part_target+7(a0),d0
	lea.l	Char_inventory(a1),a2	; Get object packet
	subq.w	#1,d0
	mulu.w	#Object_packet_size,d0
	add.w	d0,a2
	move.w	Object_index(a2),d0		; Get object index
	move.l	Object_data_ptr,a2		; Get object data
	subq.w	#1,d0
	mulu.w	#Item_data_size,d0
	add.w	d0,a2
	cmp.b	#Spellscroll_itemtype,Item_type(a2)	; Is spell scroll ?
	bne.s	.No
	jsr	Print_magic_action		; Yes -> Normal text
	bra	.Exit
.No:	lea.l	Item_name(a2),a2		; Get item name
	move.l	a2,16(a3)			; Insert
	move.l	Spell_names_ptr,a0		; Get spell name
	move.w	Selected_class,d0
	mulu.w	#Max_spells,d0
	add.w	Selected_spell,d0
	subq.w	#1,d0
	jsr	Find_small_text
	move.l	a0,8(a3)			; Insert
	move.l	a3,a0			; Print text
	moveq.l	#0,d0
	jsr	Display_combat_text
.Exit:	movem.l	(sp)+,d0/a0-a3
	Free	Part_handle(a0)
	rts

;*****************************************************************************
; [ Do all combat targets ]
;   IN : a0 - Pointer to casting participant data (.l)
;        a2 - Pointer to routine (.l)
; All registers are restored
; Notes :
;   - The targets are handled backwards so the effects may be seen better,
;     or at least sooner.
;*****************************************************************************
Do_all_combat_targets:
	movem.l	d0-d7/a0-a6,-(sp)
	move.b	Part_target+6(a0),d0	; Get target mode
	cmp.b	#Item_targmode,d0
	bpl.s	.Exit
	move.l	a0,a1
	move.b	Part_type(a1),d2		; Friends or enemies ?
	btst	d0,#Targmode_invert
	beq.s	.Ok
	eor.b	#3,d2			; 1 <-> 2
.Ok:	lea.l	Combat_matrix+29*4,a3	; Search matrix
	move.l	Part_target(a1),d0
	moveq.l	#0,d6
	moveq.l	#30-1,d7
.Loop:	btst	d7,d0			; Targeted ?
	beq.s	.Next
	tst.l	(a3)			; Yes -> Anyone there ?
	beq.s	.Next
	move.l	(a3),a0			; Yes -> Right type ?
	cmp.b	Part_type(a0),d2
	bne.s	.Next
	addq.w	#1,d6			; Yes -> Count
	movem.l	d0/d2/d6/d7/a1-a3,-(sp)	; Do
	jsr	(a2)
	movem.l	(sp)+,d0/d2/d6/d7/a1-a3
.Next:	subq.l	#4,a3			; Next matrix entry
	dbra	d7,.Loop
	tst.w	d6			; Hit anything ?
	bne.s	.Exit
	cmp.b	#1,Part_type(a0)		; No -> Party ?
	bne.s	.Exit
	move.w	#211,d0			; Yes -> "Missed !"
	jsr	Do_part_prompt
.Exit:	movem.l	(sp)+,d0-d7/a0-a6
	rts

;*****************************************************************************
; [ Get target row number ]
;   IN : d0 - Target bitlist (.l)
;  OUT : d0 - Row number (.w)
; All registers are restored
;*****************************************************************************
Get_target_row_number:
	movem.l	d1-d3/d7,-(sp)
	move.l	d0,d2			; Save
	moveq.l	#0,d0			; Row number
	moveq.l	#%111111,d1		; One row bitmask
	moveq.l	#5-1,d7
.Loop:	move.l	d2,d3			; This row ?
	and.l	d1,d3
	bne.s	.Exit
	addq.w	#1,d0			; No -> Next
	rol.l	#6,d1
	dbra	d7,.Loop
.Exit:	movem.l	(sp)+,d1-d3/d7
	rts

;*****************************************************************************
; [ Handle magical defense ]
;   IN : a0 - Pointer to defender's participant data (.l)
;  OUT : eq - No defense
;        ne - Defended successfully
; All registers are restored
;*****************************************************************************
Handle_magical_defense:
	movem.l	d0-d2/d7/a1,-(sp)
	moveq.l	#-1,d7			; Default is OK
	Get	Part_handle(a0),a1
	move.w	AAnti_magic(a1),d0		; Get anti-magic attribute
	add.w	AAnti_magic+Magic(a1),d0
	jsr FUN_IsPartyMemberProtected
	beq .Proceed
	move.w #100,D0 ; 100% anti magic if protected
.Proceed:
	move.b	Spell_class_immunity(a1),d1	; Get immunities
	move.b	Spell_type_immunity(a1),d2
	Free	Part_handle(a0)
	cmp.b	#1,Part_type(a0)		; Party member ?
	bne.s	.Monster
	add.w	Spell_4_data,d0		; Yes -> Add spell's effect
.Monster:	jsr	Probe_100			; Probe anti-magic
	bmi.s	.Fail
	move.w	#246,d0			; "Deflected !"
	jsr	Do_part_prompt
	jsr	Show_deflecting		; Show
	bra	.Exit
.Fail:	move.w	Selected_class,d0		; Immune to spell class ?
	btst	d0,d1
	beq.s	.Not
.Immune:	move.w	#247,d0			; "Immune !"
	jsr	Do_part_prompt
	bra	.Exit
.Not:	lea.l	Spell_data,a1		; Get pointer to spell data
	mulu.w	#Max_spells,d0
	add.w	Selected_spell,d0
	subq.w	#1,d0
	mulu.w	#Spell_data_size,d0
	adda.w	d0,a1
	move.b	Spell_type_bits(a1),d0	; Get spell type
	btst	d0,d2			; Immune to spell type ?
	bne.s	.Immune
	moveq.l	#0,d7			; No -> No defense !
.Exit:	tst.w	d7			; Any luck ?
	movem.l	(sp)+,d0-d2/d7/a1
	rts

;*****************************************************************************
; [ Show deflecting ]
;   IN : a0 - Pointer to defender's participant data (.l)
; All registers are restored
;*****************************************************************************
Show_deflecting:
	movem.l	d0-d2/a0,-(sp)
	jsr	Get_3D_part_coordinates	; Create deflect shape
	jsr	Add_COMOB
	move.w	d0,COMOB_3D_X(a0)
	move.w	d1,COMOB_3D_Y(a0)
	move.w	d2,COMOB_3D_Z(a0)
	move.w	#48,COMOB_Display_width(a0)	; Set data
	move.w	#48,COMOB_Display_height(a0)
	move.w	#32,COMOB_Source_width(a0)
	move.w	#32,COMOB_Source_height(a0)
	move.b	FXGFX_handle,COMOB_Gfx_handle(a0)
	move.l	#Deflect_FXGFX,COMOB_Gfx_base(a0)
	moveq.l	#4,d0			; Show
	moveq.l	#4-1,d1
.Loop:	jsr	Update_combat_screen
	jsr	Circle_COMOB
	dbra	d1,.Loop
	jsr	Delete_COMOB		; Delete
	movem.l	(sp)+,d0-d2/a0
	rts

;*****************************************************************************
; [ Spell handlers - COMBAT / PARTY ]
;   IN : a0 - Pointer to casting participant data (.l)
; No registers are restored
;*****************************************************************************

; ********** Class 0 spells ***********************
; *** Destroy undead ***
CDestroy_undead:
	jsr	Handle_spell		; Handle spell
	bne	.Exit
	lea.l	.Destroy_undead_monster,a2	; Do all targets
	jsr	Do_all_combat_targets
.Exit:	rts

; [ Destroy undead monster ]
;   IN : a0 - Pointer to monster's participant data (.l)
;        a1 - Pointer to caster's participant data (.l)
; No registers are restored
.Destroy_undead_monster:
	Get	Part_handle(a0),a2		; Is undead ?
	move.b	Monster_type_status(a2),d0
	Free	Part_handle(a0)
	btst	#Undead_type,d0
	beq.s	.Exit			; (!)
	btst	#End_monster_type,d0	; Yes -> But end monster ?
	beq.s	.No
	move.w	#263,d0			; Yes -> "Immune !"
	jsr	Do_part_prompt
	bra.s	.Exit			; (!)
.No:	move.l	a0,a2			; No -> Do
	move.l	Part_COMOB_ptr(a2),a3
; ---------- Beam comes down ----------------------
	jsr	Add_COMOB			; Initialize beam
	move.w	COMOB_3D_X(a3),COMOB_3D_X(a0)	; Behind monster
	move.w	#200,COMOB_3D_Y(a0)
	move.w	COMOB_3D_Z(a3),d0
	addq.w	#1,d0
	move.w	d0,COMOB_3D_Z(a0)
	move.w	#20,COMOB_Display_width(a0)
	move.w	#10,COMOB_Display_height(a0)
	move.w	#16,COMOB_Source_width(a0)
	move.w	#1,COMOB_Source_height(a0)
	move.b	FXGFX_handle,COMOB_Gfx_handle(a0)
	move.l	#Beam_FXGFX,COMOB_Gfx_base(a0)
	move.w	#-10,COMOB_3D_vector_Y(a0)	; Moving down
	moveq.l	#200/10-2,d7
.Again:	jsr	Update_combat_screen	; Show
	move.w	COMOB_Display_width(a0),d0	; Make wider
	addq.w	#2,d0
	cmp.w	COMOB_Display_width(a3),d0
	bpl.s	.Skip
	move.w	d0,COMOB_Display_width(a0)
.Skip:	add.w	#10,COMOB_Display_height(a0)	; Make taller
	dbra	d7,.Again
	jsr	Update_combat_screen	; Show
	LOCAL
; ---------- Suck away beam + monster -------------
	exg	a2,a0			; Defend ?
	jsr	Handle_magical_defense
	beq.s	.Ok
	move.l	a2,a0			; Yes -> Delete beam
	jsr	Delete_COMOB
	bra	.Exit
.Ok:	exg	a2,a0
	move.w	#3,COMOB_3D_vector_Y(a0)	; Move up
	move.w	#3,COMOB_3D_vector_Y(a3)
	moveq.l	#20-1,d7
.Loop:	jsr	Update_combat_screen	; Show
	Set_anim	Hit_anim,a2		; Hit !
	move.w	COMOB_Display_width(a3),d0	; Make monster thinner
	subq.w	#4,d0
	cmp.w	#8,d0
	bmi.s	.Skip1
	move.w	d0,COMOB_Display_width(a3)
.Skip1:	move.w	COMOB_Display_width(a0),d0	; Make beam thinner
	subq.w	#4,d0
	cmp.w	#8,d0
	bmi.s	.Skip2
	move.w	d0,COMOB_Display_width(a0)
.Skip2:	addq.w	#7,COMOB_Display_height(a3)	; Make taller
	dbra	d7,.Loop
	jsr	Delete_COMOB		; Delete beam & monster
	move.l	a3,a0
	jsr	Delete_COMOB
	Get	Part_handle(a2),a3		; Process damage
	move.w	Life_points+Maximum(a3),d0
	Free	Part_handle(a2)
	move.l	a1,a0
	jsr	Process_damage
	move.l	a2,a0			; Destroy monster
	jsr	Destroy_monster
.Exit:	rts

; ********** Class 1 spells ***********************
; *** Ghost weapon ***
CGhost_weapon:
	jsr	Handle_spell		; Handle spell
	bne	.Exit
	lea.l	.Do,a2			; Do all targets
	jsr	Do_all_combat_targets
.Exit:	rts

; [ Do Ghost weapon ]
;   IN : a0 - Pointer to victim's participant data (.l)
;        a1 - Pointer to caster's participant data (.l)
; No registers are restored
.Do:
	move.l	a0,a3
; ---------- Create fire pillars ------------------
	; ADVANCED CHANGES - START
	movea.l A1,A4
	Get	Part_handle(a1),a2		; Get caster's damage
	move.w	Damage(a2),d5
	add.w	Damage_magic(a2),d5
	move.w ($0072,A2),D2 ; base spell dmg bonus
	move.w ($0074,A2),D3 ; max spell dmg bonus
	move.w ($0078,A2),D4 ; percentage damage
	Free	Part_handle(a1)
	tst.w	d5			; Too low ?
	bne.s	.Ok1
	moveq.l	#1,d5			; Yes -> Adjust
.Ok1:	move.w	d5,-(sp)			; Save
	cmp.w	#20,d5			; Too high ?
	bmi.s	.Ok2
	moveq.l	#20,d5			; Yes -> Clip
.Ok2:	add.w	d5,d5			; Calculate pillar height/4
	exg	a1,a0
	moveq.l	#40,d0			; Create first
	jsr	Prepare_COMOB_movement
	move.l	a0,FXGFX_workspace
	clr.w	COMOB_3D_Y(a0)		; Over the floor !
	clr.w	COMOB_3D_vector_Y(a0)
	move.w	#32,COMOB_Display_width(a0)	; Set dimensions
	move.w	d5,COMOB_Display_height(a0)
	add.w	#16,COMOB_Display_height(a0)
	move.w	#16,COMOB_Source_width(a0)	; Set other data
	move.w	#32,COMOB_Source_height(a0)
	move.b	FXGFX_handle,COMOB_Gfx_handle(a0)
	move.l	#Firepillar_FXGFX,COMOB_Gfx_base(a0)
	moveq.l	#4,d0			; Create others
	lea.l	.Modify,a0
	jsr	Make_COMOB_chain
	cmp.w	#4,d7			; Less steps
	bmi.s	.Ok
	subq.w	#3,d7
.Ok:	moveq.l	#8,d0			; Move
	moveq.l	#4,d1
	jsr	Move_COMOBs_to_target
	move.w	(sp)+,d0			; Restore
	move.l	a3,a0			; Defend ?
	; ADVANCED CHANGES - START
	movea.l A1,A3
	movea.l A4,A1
	move.l D4,-(SP)
	move.w D0,D4 ; backup damage
	jsr Random	
	mulu.w D3,D0 ; random max bonus
	swap D0
	add.w D2,D0 ; total random bonus
	add.w D4,D0 ; add initial damage
	move.l (SP)+,D4
	tst.w D4
	beq.b .LAB_CalcSpellDamageGhostWeapon
	cmpi.w #-99,D4
	bpl.b .LAB_CalcPercDamageGhostWeapon
	moveq #1,D0 ; limit to 1 damage if perc value is -100% or lower
	bra.b .LAB_CalcSpellDamageGhostWeapon
.LAB_CalcPercDamageGhostWeapon:
	add.w #100,D4
	mulu.w D4,D0
	divu.w #100,D0
	bgt.b .LAB_CalcSpellDamageGhostWeapon
	moveq #1,D0 ; deal at least 1 damage
.LAB_CalcSpellDamageGhostWeapon:
	jsr FUN_CalculateSpellDamage
	movea.l A3,A1
	jsr	Handle_magical_defense
	bne.s	.Exit2
	cmp.b	#1,Part_type(a0)		; No -> Party or monster ?
	bne.s	.Monster
	jsr	Do_combat_damage		; Member gets damage !
	bra.s	.Go_on
.Monster:	jsr	Do_damage_to_monster	; Monster gets damage !
.Go_on:	move.l	a1,a0			; Process
	jsr	Process_damage
.Exit2:	rts

.Modify:
	move.w	COMOB_3D_vector_X(a1),d0	; Move along vector
	move.w	COMOB_3D_vector_Z(a1),d2
	add.w	d0,COMOB_3D_X(a0)		; Store coordinates
	add.w	d2,COMOB_3D_Z(a0)
	add.w	d5,COMOB_Display_height(a0)	; Grow taller
	addq.w	#1,COMOB_Frame(a0)		; Next frame
	rts

; *** Blink ***
Enter_blink_target:
	move.w	#67,ItemSelect_prompt	; "Blink whom ?"
	jsr	Select_party_member
	tst.w	d0			; Any target ?
	bmi.s	.Exit
	move.w	d0,Part_target(a0)		; Yes -> Insert
	jsr	Get_occupied_targets	; Get occupied targets
	move.l	d0,Target_mask
	move.l	d0,d1
	lea.l	Combat_matrix+18*4,a1	; Build occupied target mask
	moveq.l	#0,d0
	moveq.l	#3*6,d7
.Loop:	tst.l	(a1)			; Anyone there ?
	bne.s	.Next
	bset	d7,d0			; No -> Mask
.Next:	addq.l	#4,a1			; Next
	addq.w	#1,d7
	cmp.w	#5*6,d7
	bmi.s	.Loop
	and.l	d0,Target_mask		; No unreachable targets
	not.l	d1			; Remove occupied targets
	and.l	d1,d0
	move.l	d0,Tactic_mask		; Store mask
	move.w	#266,ItemSelect_prompt	; Blink where ?
	move.l	#Show_move_tactic,Tactic_draw_vector
	Push	Module,TacticSel_Mod
	move.w	Selected_tactic,d0		; Anywhere ?
	bmi.s	.Exit
	move.l	Casting_participant,a0	; Yes
	move.w	d0,Part_target+2(a0)	; Store destination
	move.b	#Special_targmode,Part_target+6(a0)
	jsr	Enter_action
.Exit:	rts

CBlink:
	jsr	Handle_spell		; Handle spell
	bne	.Exit
	move.l	a0,a2			; Save
	lea.l	Combat_matrix,a0		; Get target member
	move.w	Part_target(a2),d0
	lsl.w	#2,d0
	move.l	0(a0,d0.w),a0
	Get	Part_handle(a0),a1		; Get conditions
	move.w	Body_conditions(a1),d0
	Free	Part_handle(a0)
	andi.w	#Blink_mask,d0		; Capable of blinking ?
	beq.s	.Yes
	move.w	#268,d0			; " cannot be blinked!"
	jsr	Do_part_prompt
	bra.s	.Exit
.Yes:	move.w	#267,d0			; " is blinked!"
	jsr	Do_part_prompt
	lea.l	Combat_matrix,a1
	move.w	Part_target+2(a2),d0	; Get destination
	lsl.w	#2,d0
	tst.l	0(a1,d0.w)		; Empty ?
	beq.s	.Empty
	move.w	#229,d0			; " blocked!"
	jsr	Do_part_prompt
	bra	.Exit
.Empty:	move.l	a0,0(a1,d0.w)		; Copy to destination
	move.w	Part_Y(a0),d0		; Clear source
	mulu.w	#6,d0
	add.w	Part_X(a0),d0
	lsl.w	#2,d0
	clr.l	0(a1,d0.w)
	moveq.l	#0,d0			; Set new coordinates
	move.w	Part_target+2(a2),d0
	divu.w	#6,d0
	move.w	d0,Part_Y(a0)
	swap	d0
	move.w	d0,Part_X(a0)
	clr.b	Part_action(a0)		; Abort action
	move.w	#-1,Part_target(a0)
	jsr	Update_combat_screen	; Show
.Exit:	rts

; *** Flight ***
CFlight:
	jsr	Handle_spell		; Handle spell
	bne	.Exit
	lea.l	Do_flee,a2		; Do all targets
	jsr	Do_all_combat_targets
.Exit:	rts

; *** Hurry ***
CHurry:
	jsr	Handle_spell		; Handle spell
	bne	.Exit
	lea.l	.Do,a2			; Do all targets
	jsr	Do_all_combat_targets
.Exit:	rts

; [ Do Hurry ]
;   IN : a0 - Pointer to victim's participant data (.l)
;        a1 - Pointer to caster's participant data (.l)
; No registers are restored
.Do:
	bset	#Part_hurried,Part_flags(a0)	; Hurry!
	cmp.b	#1,Part_type(a0)		; Party member ?
	bne.s	.Exit2
	moveq.l	#0,d0			; Yes -> Sparkle
	move.b	Part_nr(a0),d0
	jsr	Do_sparkle
.Exit2:	rts

; *** LP stealer ***
CLP_stealer:
	jsr	Handle_spell		; Handle spell
	bne	.Exit
	lea.l	.Do,a2			; Do all targets
	jsr	Do_all_combat_targets
.Exit:	rts

; [ Do LP stealer ]
;   IN : a0 - Pointer to victim's participant data (.l)
;        a1 - Pointer to caster's participant data (.l)
; No registers are restored
.Do:
	jsr	Handle_magical_defense	; Defend ?
	bne	.Exit2
; ---------- Transfer LP --------------------------
	Get	Part_handle(a0),a2		; Get available LP
	move.w	Life_points(a2),d1
	Free	Part_handle(a0)
	Get	Part_handle(a1),a2		; Get caster's level
	moveq.l	#0,d0
	move.b	Level_nr(a2),d0
	cmp.w	d0,d1			; Enough available ?
	bpl.s	.Ok1
	move.w	d1,d0			; No -> Clip
.Ok1:	cmp.w	#4,d0			; Too small ?
	bpl.s	.Ok2
	moveq.l	#4,d0
.Ok2:	move.w	d0,d5			; Save for later
	cmp.b	#1,Part_type(a0)		; Party or monster ?
	bne.s	.Monster
	jsr	Do_combat_damage		; Member gets damage !
	bra.s	.Go_on
.Monster:	jsr	Do_damage_to_monster	; Monster gets damage !
.Go_on:	exg	a1,a0			; Process
	jsr	Process_damage
	exg	a1,a0
	add.w	Life_points(a2),d0		; Attacker gets LP
	move.w	Life_points+Maximum(a2),d1
	add.w	Life_points+Magic(a2),d1
	cmp.w	d1,d0
	bmi.s	.Ok3
	move.w	d1,d0
.Ok3:	move.w	d0,Life_points(a2)
	Free	Part_handle(a1)
; ---------- Create LP globes ---------------------
	cmp.w	#80/4,d5			; Calculate globe size/4
	bmi.s	.Ok4
	move.w	#80/4,d5
.Ok4:	moveq.l	#30,d0			; Create first
	jsr	Prepare_COMOB_movement
	move.l	a0,FXGFX_workspace
	move.w	d5,COMOB_Display_width(a0)	; Set dimensions
	move.w	d5,COMOB_Display_height(a0)
	move.w	#16,COMOB_Source_width(a0)	; Set other data
	move.w	#16,COMOB_Source_height(a0)
	move.b	FXGFX_handle,COMOB_Gfx_handle(a0)
	move.l	#LP_globe_FXGFX,COMOB_Gfx_base(a0)
	moveq.l	#4,d0			; Create others
	lea.l	.Modify,a0
	jsr	Make_COMOB_chain
	cmp.w	#4,d7			; Less steps
	bmi.s	.Ok5
	subq.w	#3,d7
.Ok5:	moveq.l	#0,d0			; Move
	moveq.l	#4,d1
	jsr	Move_COMOBs_to_target
.Exit2:	rts

.Modify:
	move.w	d5,d1			; Adjust for growth
	lsr.w	#1,d1
	neg.w	d1
	move.w	COMOB_3D_vector_X(a1),d0	; Move along vector
	add.w	COMOB_3D_vector_Y(a1),d1
	move.w	COMOB_3D_vector_Z(a1),d2
	add.w	d0,COMOB_3D_X(a0)		; Store coordinates
	add.w	d1,COMOB_3D_Y(a0)
	add.w	d2,COMOB_3D_Z(a0)
	add.w	d5,COMOB_Display_width(a0)	; Grow bigger
	add.w	d5,COMOB_Display_height(a0)
	rts

; *** PP stealer ***
CPP_stealer:
	jsr	Handle_spell		; Handle spell
	bne	.Exit
	lea.l	.Do,a2			; Do all targets
	jsr	Do_all_combat_targets
.Exit:	rts

; [ Do PP stealer ]
;   IN : a0 - Pointer to victim's participant data (.l)
;        a1 - Pointer to caster's participant data (.l)
; No registers are restored
.Do:
	jsr	Handle_magical_defense	; Defend ?
	bne	.Exit2
; ---------- Transfer PP --------------------------
	Get	Part_handle(a0),a3		; Get available PP
	move.w	Power_points(a3),d1
	Get	Part_handle(a1),a2		; Get caster's level
	moveq.l	#0,d0
	move.b	Level_nr(a2),d0
	cmp.w	d0,d1			; Enough available ?
	bpl.s	.Ok1
	move.w	d1,d0			; No -> Clip
.Ok1:	move.w	d0,d4			; Save for later
	add.w	Power_points(a2),d0		; Attacker gets PP
	move.w	Power_points+Maximum(a2),d1
	add.w	Power_points+Magic(a2),d1
	cmp.w	d1,d0
	bmi.s	.Ok2
	move.w	d1,d0
.Ok2:	move.w	d0,Power_points(a2)
	Free	Part_handle(a1)
	sub.w	d4,Power_points(a3)		; Victim loses PP
					; FIX: Was "sub.w d0,..." (d0 = caster's new PP)
	Free	Part_handle(a0)
; ---------- Victim glows -------------------------
	cmp.b	#2,Part_type(a0)		; Is monster ?
	bne	.Skip
	movem.l	a0/a1,-(sp)
	move.l	a0,a1			; Yes -> Duplicate COMOB
	move.l	Part_COMOB_ptr(a1),a2
	jsr	Add_COMOB
	move.w	COMOB_3D_X(a2),COMOB_3D_X(a0)
	clr.w	COMOB_3D_Y(a0)
	move.w	COMOB_3D_Z(a2),d0		; (behind monster)
	addq.w	#1,d0
	move.w	d0,COMOB_3D_Z(a0)
	move.w	COMOB_Source_width(a2),COMOB_Source_width(a0)
	move.w	COMOB_Source_height(a2),COMOB_Source_height(a0)
	move.w	COMOB_Display_width(a2),COMOB_Display_width(a0)
	move.w	COMOB_Display_height(a2),COMOB_Display_height(a0)
	move.b	COMOB_Gfx_handle(a2),COMOB_Gfx_handle(a0)
	Set_anim	Hit_anim,a1		; Hit !
	lea.l	Glow_colours,a3
.Again:	move.w	(a3)+,COMOB_Colour(a0)	; Set aura colour
	move.w	COMOB_Frame(a2),COMOB_Frame(a0)	; Same frame
	addq.w	#4,COMOB_Display_width(a0)	; Grow bigger
	addq.w	#4,COMOB_Display_height(a0)
	subq.w	#4/2,COMOB_3D_Y(a0)
	bset	#COMOB_update,COMOB_Flags(a0)
	jsr	Update_combat_screen	; Show
	tst.b	Part_anim(a1)		; Animation ended ?
	bne.s	.Again
	jsr	Delete_COMOB		; Yes -> Delete aura
	movem.l	(sp)+,a0/a1
; ---------- Create PP globes ---------------------
.Skip:	tst.w	d4			; Any PP ?
					; FIX: d5 -> d4 here and below. d4 holds the
					;  stolen PP (code was copied from the LP stealer).
	beq	.Exit2
	cmp.w	#80/4,d4			; Calculate globe size/4
	bmi.s	.Ok3
	move.w	#80/4,d4
.Ok3:	moveq.l	#30,d0			; Create first
	jsr	Prepare_COMOB_movement
	move.l	a0,FXGFX_workspace
	move.w	d4,COMOB_Display_width(a0)	; Set dimensions
	move.w	d4,COMOB_Display_height(a0)
	move.w	#16,COMOB_Source_width(a0)	; Set other data
	move.w	#16,COMOB_Source_height(a0)
	move.b	FXGFX_handle,COMOB_Gfx_handle(a0)
	move.l	#PP_globe_FXGFX,COMOB_Gfx_base(a0)
	moveq.l	#4,d0			; Create others
	lea.l	.Modify,a0
	jsr	Make_COMOB_chain
	cmp.w	#4,d7			; Less steps
	bmi.s	.Ok4
	subq.w	#3,d7
.Ok4:	moveq.l	#0,d0			; Move
	moveq.l	#4,d1
	jsr	Move_COMOBs_to_target
.Exit2:	rts

.Modify:
	move.w	d4,d1			; Adjust for growth (FIX: d5 -> d4)
	lsr.w	#1,d1
	neg.w	d1
	move.w	COMOB_3D_vector_X(a1),d0	; Move along vector
	add.w	COMOB_3D_vector_Y(a1),d1
	move.w	COMOB_3D_vector_Z(a1),d2
	add.w	d0,COMOB_3D_X(a0)		; Store coordinates
	add.w	d1,COMOB_3D_Y(a0)
	add.w	d2,COMOB_3D_Z(a0)
	add.w D4,($0012,A0)
	add.w D4,($0014,A0)
	rts
FUN_SpellMysticImitation:
	jsr Handle_spell
	bne.w .End
	lea FUN_CastImitation,A2
	jsr Do_all_combat_targets
.End:
	rts
FUN_CastImitation:
	jsr Handle_magical_defense
	bne.w .End_Adv
	movem.l A1/A0,-(SP)
	jsr FUN_MysticSpellAnimation
	movem.l (SP)+,A0/A1
	; After the animation was played, transform the caster.
	jsr FUN_TransformCaster
.End_Adv:
	rts
; There are at max 3 characters who can use this spell: Valdyn (12), Targor (13) and Chris (5)
; So we have some backups here for all 3.
; We store for each:
; - APR (1 byte)
; - Element (1 byte)
; - Current and MaxLP (2 words)
; - Current and MaxSP (2 words)
; - MBW (1 word)
; - MBR (1 word)
; - Current and Max value for all 8 attributes (16 words)
; - Current and Max value for ATT, PAR, CRI, M-B (8 words)
; - Learned spell bits (2 words)
; Total: 33 words = 66 bytes
	rsreset
Backup_APR: rs.b 1
Backup_Element: rs.b 1
Backup_LP: rs.w 2
Backup_SP: rs.w 2
Backup_MBW: rs.w 1
Backup_MBR: rs.w 1
Backup_STR: rs.w 2
Backup_INT: rs.w 2
Backup_DEX: rs.w 2
Backup_SPD: rs.w 2
Backup_STA: rs.w 2
Backup_CHA: rs.w 2
Backup_LUK: rs.w 2
Backup_A_M: rs.w 2
Backup_ATT: rs.w 2
Backup_PAR: rs.w 2
Backup_CRI: rs.w 2
Backup_U_M: rs.w 2
Backup_Spells: rs.l 1
Backup_data_size: rs.b 0
; NOTE: We keep the caster level and class.
; We do not need to store some values like SpellClass, Base Def, etc as we know their reset values. For example Base Def is always 0.
; We make the inventory inaccessible for the rest of the fight.
Mapping_CharIndex2MysticBackupDataIndex:
	; Use CharIndex - 1 for access.
	dc.b -1,-1,-1,-1,0,-1,-1,-1,-1,-1,-1,1,2,-1
	even
; Expects A1 to be the casting party member's participation data
; Will return the backup area as A3
FUN_GetMysticBackupData:
	move.l D0,-(SP)
	moveq #0,D0
	move.b (1,A1),D0 ; Party member index (1-based)
	lea Member_nrs,A3
	lsl.w #1,D0
	move.w (-2,A3,D0.w),D0 ; Character index
	lea Mapping_CharIndex2MysticBackupDataIndex,A3
	move.b (-1,A3,D0.w),D0 ; Backup index
	mulu.w #Backup_data_size,D0
	lea MysticBackupData,A3
	adda.l D0,A3 ; Now points to the correct backup data
	move.l (SP)+,D0
	rts
FUN_ClearMysticImitationBackupData:
	movem.l A0/D0,-(SP)
	moveq #0,D0
	move.w #Backup_data_size,D0
	lsr.w #1,D0
	mulu.w #3,D0 ; 3 possible chars
	subq #1,D0 ; -1 for dbf
	lea MysticBackupData,A0
.Next:
	clr.w (A0)+
	dbf D0,.Next	
	movem.l (SP)+,D0/A0
	rts
; In D0: Backup data index (0-2)
; In D7: Index in party (0-5)
FUN_RestoreMysticChar:
	movem.l A1/A0/D7/D0,-(SP)
	mulu.w #Backup_data_size,D0 ; 62 bytes per backup data
	lea MysticBackupData,A1
	adda.l D0,A1 ; now points to the right backup data
	tst.b (A1) ; The first byte is the APR value. If 0, there is no valid backup data. It is always >0 otherwise.
	beq.w .End_Adv3
	lea Party_handles,A0
	move.b (0,A0,D7.w),D7
	move.b D7,D0
	jsr Claim_pointer
	movea.l D0,A0 ; A0 is now the mystic data
	; ---------------------------
	; Restore relevant data from backup area
	move.b Backup_APR(A1),$11(A0)
	move.b Backup_Element(A1),$13(A0)
	move.w Backup_MBW(A1),$de(A0)
	move.w Backup_MBR(A1),$e0(A0)
	move.l Backup_STR(A1),$2a(A0) ; current and max value in one go
	move.l Backup_INT(A1),$32(A0)
	move.l Backup_DEX(A1),$3a(A0)
	move.l Backup_SPD(A1),$42(A0)
	move.l Backup_STA(A1),$4a(A0)
	move.l Backup_CHA(A1),$52(A0)
	move.l Backup_LUK(A1),$5a(A0)
	move.l Backup_A_M(A1),$62(A0)
	move.l Backup_ATT(A1),$7a(A0)
	move.l Backup_PAR(A1),$82(A0)
	move.l Backup_CRI(A1),$92(A0)
	move.l Backup_U_M(A1),$c2(A0)
	move.l Backup_Spells(A1),$fa(A0)
	; ---------------------------
	; Adjust some other values
	clr.l $f2(A0) ; Clear learned healing spells
	clr.l $f6(A0) ; Clear learned alchemistic spells
	clr.l $fe(A0) ; Clear learned destruction spells
	move.l #$84,D0 ; usable spell school (for now mystic)
	cmp.b #7,3(A0) ; Mystic class?
	beq.b .Skip_Adv
	moveq #$04,D0 ; If no mystic, it is a ranger
.Skip_Adv:
	move.b D0,$04(A0) ; Reset usable spell types
	clr.w $d6(A0) ; Reset base defense
	clr.w $da(A0) ; Reset base damage
	clr.b $09(A0) ; Make caster inventory accessible again
	; Limit current LP/SP if necessary
	tst.w $ca(A0)
	beq.b .SkipLP ; No LP left? Skip adjusting it
	move.w Backup_LP(A1),D0 ; backed up current LP
	cmp.w $ca(A0),D0 ; compare with now current LP
	bhs.b .SkipLP ; if backed up LP >= current LP, keep the current LP
	move.w D0,$ca(A0) ; otherwise use the backed up LP
.SkipLP:
	move.w Backup_SP(A1),D0 ; backed up current SP
	tst.w $d2(A0) ; Check current max SP
	beq.b .RestoreSP ; If it is 0, restore the previously backed up SP	
	cmp.w $d0(A0),D0 ; compare with now current SP
	bhs.b .SkipSP ; if backed up SP >= current SP, keep the current SP
.RestoreSP:
	move.w D0,$d0(A0) ; set SP to backed up value
.SkipSP:
	move.w Backup_LP+2(A1),$cc(A0) ; update max LP
	move.w Backup_SP+2(A1),$d2(A0) ; update max SP
	; ---------------------------
	; Release data
	move.b D7,D0
	jsr Free_pointer
.End_Adv3:
	movem.l (SP)+,D0/D7/A0/A1
	rts
FUN_RestoreMystics:
	; This is called when the battle ended.
	movem.l A1/A0/D7/D0,-(SP)
	; Check if there is a mystic or ranger in the party
	lea Mapping_CharIndex2MysticBackupDataIndex,A1
	lea Member_nrs,A0
	adda.l #12,A0 ; 6 words
	moveq #5,D7 ; 0 to 5
.CheckMember:
	move.w -(A0),D0
	beq .NextMember
	cmp.w #14,D0
	bge .NextMember ; above 13 we have no mystics/rangers
	move.b (-1,A1,D0.w),D0
	tst.b D0
	bmi .NextMember ; we have no backup data so it is no mystic/ranger
	andi.l #$00ff,D0 ; For safety ensure the word has no garbage, as we use it as an index in FUN_RestoreMysticChar
	jsr FUN_RestoreMysticChar
.NextMember:
	dbf D7,.CheckMember
	movem.l (SP)+,D0/D7/A0/A1
	jmp FUN_ClearMysticImitationBackupData
FUN_TransformCaster:
	cmp.b #1,(A1) ; Is party member
	bne .Abort ; If casted by monster, abort immediately
	movem.l A3/A2/D7/D1/D0,-(SP)
	move.b ($0005,A1),D0 ; Get caster index
	jsr Claim_pointer
	movea.l D0,A2 ; Caster data
	; ---------------------------
	; Copy relevant data to backup area
	jsr FUN_GetMysticBackupData ; = A3
	move.b $11(A2),Backup_APR(A3)
	move.b $13(A2),Backup_Element(A3)
	move.l $ca(A2),Backup_LP(A3) ; current and max value in one go
	move.l $d0(A2),Backup_SP(A3)
	move.w $de(A2),Backup_MBW(A3)
	move.w $e0(A2),Backup_MBR(A3)
	move.l $2a(A2),Backup_STR(A3) ; current and max value in one go
	move.l $32(A2),Backup_INT(A3)
	move.l $3a(A2),Backup_DEX(A3)
	move.l $42(A2),Backup_SPD(A3)
	move.l $4a(A2),Backup_STA(A3)
	move.l $52(A2),Backup_CHA(A3)
	move.l $5a(A2),Backup_LUK(A3)
	move.l $62(A2),Backup_A_M(A3)
	move.l $7a(A2),Backup_ATT(A3)
	move.l $82(A2),Backup_PAR(A3)
	move.l $92(A2),Backup_CRI(A3)
	move.l $c2(A2),Backup_U_M(A3)
	move.l $fa(A2),Backup_Spells(A3)
	; ---------------------------
	; Transfer monster values to the caster	
	move.b ($0005,A0),D0 ; Get target index
	jsr Claim_pointer
	movea.l D0,A3 ; Target data
	move.b $11(A3),$11(A2) ; Transfer APR
	move.b $13(A3),$13(A2) ; Transfer element
	move.l $ca(A3),$ca(A2) ; Transfer current and max hit points
	move.l $d0(A3),$d0(A2) ; Transfer current and max spell points
	move.l $de(A3),$de(A2) ; Transfer MBW and MBR
	move.l $2a(A3),$2a(A2) ; Transfer current and max STR
	move.l $32(A3),$32(A2) ; Transfer current and max INT
	move.l $3a(A3),$3a(A2) ; Transfer current and max DEX
	move.l $42(A3),$42(A2) ; Transfer current and max SPD
	move.l $4a(A3),$4a(A2) ; Transfer current and max STA
	move.l $52(A3),$52(A2) ; Transfer current and max CHA
	move.l $5a(A3),$5a(A2) ; Transfer current and max LUK
	move.l $62(A3),$62(A2) ; Transfer current and max A-M
	move.l $7a(A3),$7a(A2) ; Transfer current and max ATT
	move.l $82(A3),$82(A2) ; Transfer current and max PAR
	move.l $92(A3),$92(A2) ; Transfer current and max CRI
	move.l $c2(A3),$c2(A2) ; Transfer current and max U-M
	move.l $f2(A3),$f2(A2) ; Transfer learned healing spells
	move.l $f6(A3),$f6(A2) ; Transfer learned alchemistic spells
	move.l $fa(A3),$fa(A2) ; Transfer learned mystic spells
	move.l $fe(A3),$fe(A2) ; Transfer learned destruction spells
	move.b $04(A3),$04(A2) ; Transfer usable spell types
	move.w $d6(A3),$d6(A2) ; Transfer base defense
	move.w $da(A3),$da(A2) ; Transfer base damage
	move.b #$ff,$09(A2) ; Make caster inventory inaccessible
	move.b $03(A0),$03(A1) ; Replace battle icon
	
	; TODO: portrait?
	
	; ---------------------------
	; Release the previously claimed pointers
	move.b ($0005,A0),D0 ; Get target index
	jsr Free_pointer
	move.b ($0005,A1),D0 ; Get caster index
	jsr Free_pointer
;.End:
	movem.l (SP)+,D0/D1/D7/A2/A3
.Abort:
	rts

; ********** Class 2 spells ***********************
; *** Monster knowledge ***
CMonster_knowledge:
	jsr	Handle_spell		; Handle spell
	bne	.Exit
	lea.l	.Do,a2			; Do all targets
	jsr	Do_all_combat_targets
.Exit:	rts

; [ Do Monster knowledge ]
;   IN : a0 - Pointer to victim's participant data (.l)
;        a1 - Pointer to caster's participant data (.l)
; No registers are restored
.Do:
	jsr	Handle_magical_defense	; Defend ?
	bne	CMonster_knowledge_Exit2
	jsr FUN_MysticSpellAnimation
	; After the animation was played, show the monster info.
	lea MonKnow_Mod,A0
	jsr Push_Module
	rts
FUN_MysticSpellAnimation:
	move.l	a0,-(sp)
; ---------- Create stars -------------------------
	move.l	a0,a1
	lea.l	FXGFX_workspace,a2
	move.l	Part_COMOB_ptr(a0),a3
	move.w	COMOB_Display_height(a3),d1
	lsr.w	#2,d1
	moveq.l	#8-1,d7
.Loop1:	jsr	Add_COMOB			; Create a star
	move.l	a0,(a2)+
	jsr	Random			; Set X-coordinate
	andi.w	#$001f,d0
	subi.w	#16,d0
	add.w	COMOB_3D_X(a3),d0
	move.w	d0,COMOB_3D_X(a0)
	jsr	Random			; Set Y-coordinate
	mulu.w	d1,d0
	swap	d0
	add.w	d1,d0
	move.w	d0,COMOB_3D_Y(a0)
	jsr	Random			; Set Z-coordinate
	andi.w	#$001f,d0
	subi.w	#16,d0
	add.w	COMOB_3D_Z(a3),d0
	move.w	d0,COMOB_3D_Z(a0)
	jsr	Random			; Set Y-vector
	andi.w	#$0003,d0
	addq.w	#1,d0
	move.w	d0,COMOB_3D_vector_Y(a0)
	jsr	Random			; Set size
	andi.w	#$000f,d0
	addq.w	#8,d0
	move.w	d0,COMOB_Display_width(a0)
	move.w	d0,COMOB_Display_height(a0)
	jsr	Random			; Set frame
	mulu.w	#5,d0
	swap	d0
	move.w	d0,COMOB_Frame(a0)
	move.w	#16,COMOB_Source_width(a0)	; Set other data
	move.w	#16,COMOB_Source_height(a0)
	move.b	FXGFX_handle,COMOB_Gfx_handle(a0)
	move.l	#Star_FXGFX,COMOB_Gfx_base(a0)
	dbra	d7,.Loop1
; ---------- Show ---------------------------------
	moveq.l	#5,d0
	moveq.l	#16-1,d7
.Loop2:	jsr	Update_combat_screen	; Show
	lea.l	FXGFX_workspace,a1		; Animate stars
	moveq.l	#8-1,d6
.Loop3:	move.l	(a1)+,a0
	jsr	Wave_COMOB
	dbra	d6,.Loop3
	dbra	d7,.Loop2
; ---------- The end ------------------------------
	lea.l	FXGFX_workspace,a1		; Destroy stars
	moveq.l	#8-1,d7
.Loop4:	move.l	(a1)+,a0
	jsr	Delete_COMOB
	dbra	d7,.Loop4
	jsr	Switch_screens
	jsr	Switch_screens
; ---------- Show monster knowledge ---------------
	move.l	(sp)+,MonKnow_ptr
	rts
FUN_GetElementName:
	; in A1: monster data
	; out A0: text pointer
	; out D7: text length
	movem.l D2/D1/D0,-(SP)
	move.w #304,D0 ; messaged index 304 is element name "None"
	moveq.l #0,D1
	move.b ($0013,A1),D1 ; monster element
	beq.b .LAB_GetElementName ; 0? just keep the "None" text id
	; check if multiple bits (elements) are set
	move.l D1,D2
	subq.l #1,D2
	and.l D1,D2
	bne.b .LAB_MultipleElements ; not 0? multiple bits (elements) are set
	moveq.l #7,D2 ; check all 8 bits
.LAB_CheckNextElementBit:
	btst.l D2,D1 ; is the bit (element) set?
	bne.b .LAB_ElementFound ; yes? calculate the message index
	dbf D2,.LAB_CheckNextElementBit
	bra.b .LAB_GetElementName
.LAB_ElementFound:
	; D2 now has the bit index (0 to 7)
	add.w D2,D0
	addq.w #1,D0 ; add 1 more to get the right one
	bra.b .LAB_GetElementName
.LAB_MultipleElements:
	move.w #313,D0 ; message index 313 is element name "Multiple"
.LAB_GetElementName:
	movea.l Prompts_ptr,A0
	jsr FUN_GetTextMessageLength
	jsr Find_large_text
	movem.l (SP)+,D0/D1/D2
CMonster_knowledge_Exit2:	rts

MonKnow_ModInit:
	jsr	Set_layout_colours		; %%%1
	move.w	#MonKnowW_X-16,d0		; Open window
	move.w	#MonKnowW_Y-16,d1
	moveq.l	#12,d2
	moveq.l	#10,d3
	sub.l	a0,a0
	jsr	Open_window
	move.w	#31,Ink_colour		; Set ink
	move.l	MonKnow_ptr,a0		; Get monster data
	Get	Part_handle(a0),a1
; ---------- Print monster's tactical icon --------
	move.w	#MonKnowW_X-1,d0		; Draw box around icon
	move.w	#MonKnowW_Y+111,d1
	moveq.l	#16,d2
	moveq.l	#16,d3
	jsr	Draw_standard_box
	addq.w	#1,d0
	addq.w	#2,d1
	moveq.l	#5,d5
	moveq.l	#1,d6
	moveq.l	#14,d7
	moveq.l	#0,d4			; Get icon number
	move.b	Part_icon_nr(a0),d4
	Get	FXGFX_handle,a0		; Get graphics address
	add.l	#Tactical_GFX,a0
	mulu.w	#14*2*Screen_depth,d4
	add.w	d4,a0
	jsr	Put_masked_block		; Display tactical icon
	Free	FXGFX_handle
; --------- Print monster name --------------------
	lea.l	Char_name(a1),a0		; Get name
	jsr	Strlen			; Get length
	move.w	d0,d2
	move.w	#MonKnowW_X+20,d0		; Print name
	move.w #$00a7,D1 ; Y: 167 (was 170)
	jsr	Put_text_line
; ---------- Print monster level ------------------
	move.b	Level_nr(a1),d0		; Convert	level
	moveq.l	#2,d7
	lea.l	Number,a0
	jsr	DecL_convert
	move.w	#MonKnowW_X+20,d0		; Print level
	addq.w	#1,d2
	mulu.w	#Char_width+1,d2
	add.w	d2,d0
	lea.l	Number,a0
	jsr	Put_text_line
; ---------- Print monster's life points ----------
	; ADVANCED CHANGES - START
	; draw the element
	movea.l Prompts_ptr,A0
	move.w #$013a,D0 ; "Element:"
	jsr Find_large_text
	jsr Strlen
	move.w D0,D2 ; text length of "Element:"
	addq.w #$00000001,D2 ; add space
	mulu.w #$0006,D2 ; multiply with text char width
	move.w #$0064,D0 ; X: 100
	add.w #8,D1 ; Y: name Y + 8
	jsr Put_text_line ; draw the header "Element:"
	add.w D2,D0 ; add x offset for the element name
	jsr FUN_GetElementName
	jsr Put_text_line ; draw the element name
	move.w	#29,Ink_colour
	move.l	MonKnow_line_ptr,a0		; Print separation line
	move.w	#MonKnowW_X,d0
	move.w	#MonKnowW_Y+70,d1
	move.w	#160,d2
	jsr	Print_centered_string
	move.w	#31,Ink_colour
	moveq.l	#"0",d6			; Load
	moveq.l	#3,d7
	move.l	LP_txt_ptr,a2
	move.w	Life_points(a1),d0		; Convert	normal LP
	lea.l	5(a2),a0
	jsr	DecR_convert
	move.b	#"/",(a0)			; Correction
	move.w	Life_points+Maximum(a1),d0	; Convert	maximum LP
	add.w	Life_points+Magic(a1),d0
	lea.l	9(a2),a0
	jsr	DecR_convert
	move.w	#MonKnowW_X,d0		; Print LP
	move.w	#MonKnowW_Y+78,d1
	movea.l	a2,a0
	jsr	Put_text_line
; ---------- Print monster's power points ---------
	tst.b	Spell_class_counter(a1)	; Any spell classes	?
	beq	.No_magic
	move.l	PP_txt_ptr,a2
	move.w	Power_points+Maximum(a1),d0	; Convert	maximum PP
	add.w	Power_points+Magic(a1),d0
	lea.l	9(a2),a0
	jsr	DecR_convert
	move.w	Power_points(a1),d0		; Convert	normal PP
	lea.l	5(a2),a0
	jsr	DecR_convert
	move.b	#"/",(a0)			; Correction
	move.w	#MonKnowW_X+78,d0		; Print PP
	move.l	a2,a0
	jsr	Put_text_line
; ---------- Display gold & food ------------------
.No_magic:	move.l	Goldfood_txt_ptr,a2
	move.w	Gold_coins(a1),d0		; Convert gold
	moveq.l	#5,d7
	lea.l	2(a2),a0
	jsr	DecR_convert
	move.w	#MonKnowW_X,d0		; Print gold
	move.w	#MonKnowW_Y+85,d1
	move.l	a2,a0
	jsr	Put_text_line
	move.w	Food_rations(a1),d0		; Convert	food
	lea.l	10(a2),a0
	moveq.l	#4,d7
	jsr	DecR_convert
	move.w	#MonKnowW_X+80,d0		; Print food
	lea.l	8(a2),a0
	jsr	Put_text_line
; ---------- Display sword & shield icons ---------
	move.w	#MonKnowW_X,d0		; Display sword icon
	move.w	#MonKnowW_Y+92,d1
	moveq.l	#24,d4
	moveq.l	#3,d5
	moveq.l	#1,d6
	moveq.l	#9,d7
	lea.l	Swordshield,a0
	jsr	Put_masked_block
	addi.w	#80,d0			; Display	shield icon
	lea.l	9*6(a0),a0
	jsr	Put_masked_block
; ---------- Display protection & damage ----------
	move.l	ProtDam_txt_ptr,a2
	move.w	Protection(a1),d0		; Convert protection
	add.w	Protection_magic(a1),d0
	jsr FUN_AddDefenseAttributeBonus
	moveq.l	#"0",d6
	moveq.l	#3,d7
	lea.l	1(a2),a0
	jsr	SDecR_convert
	move.w	#MonKnowW_X+80+10,d0	; Print protection
	move.w	#MonKnowW_Y+94,d1
	move.l	a2,a0
	jsr	Put_text_line
	move.w	Damage(a1),d0		; Convert	damage
	add.w	Damage_magic(a1),d0
	jsr FUN_AddDamageAttributeBonus
	lea.l	1(a2),a0
	jsr	SDecR_convert
	move.w	#MonKnowW_X+10,d0		; Print damage
	move.l	a2,a0
	jsr	Put_text_line
; ---------- Print APR ----------------------------
	move.l	APR_txt_ptr,a2
	moveq.l	#0,d0			; Convert APR
	move.b	Attacks_per_round(a1),d0
	move.l	MonKnow_ptr,a0		; Hurried ?
	btst	#Part_hurried,Part_flags(a0)
	beq.s	.Skip
	add.w	d0,d0			; Yes
.Skip:	moveq.l	#2,d7
	lea.l	4(a2),a0
	jsr	DecL_convert
	move.w	#MonKnowW_X,d0		; Print APR
	move.w	#MonKnowW_Y+103,d1
	move.l	a2,a0
	jsr	Put_text_line
; ---------- Print monster skills -----------------
	move.w	#29,Ink_colour
	move.w	#MonKnowW_X+80,d0		; Print "SKILLS"
	move.w	#MonKnowW_Y-1,d1
	move.w	#12*6,d2
	move.l	Skills_txt_ptr,a0
	jsr	Print_centered_string
	move.w	#31,Ink_colour
	move.l	Short_skill_names_ptr,a2	; Print skills
	move.l	Skill_txt_ptr,a3
	lea.l	Skills(a1),a4
	move.w	#MonKnowW_X+80,d3
	move.w	#MonKnowW_Y+7,d4
	moveq.l	#1,d5
	moveq.l	#"0",d6
	moveq.l	#2,d7
.Loop1:	move.w	d3,d0			; Print skill name
	move.w	d4,d1
	move.l	a2,a0
	jsr	Put_text_line
	move.w	(a4),d0			; Convert normal skill
	add.w	Magic(a4),d0
	move.l	a3,a0
	jsr	DecR_convert
	move.b	#"%",(a0)			; Correction
	move.w	Maximum(a4),d0		; Convert maximum skill
	lea.l	4(a3),a0
	jsr	DecR_convert
	move.b	#"%",(a0)			; Correction
	move.w	d3,d0			; Print skill
	move.w	d4,d1
	addi.w	#5*(Char_width+1),d0
	move.l	a3,a0
	jsr	Put_text_line
	addq.w	#Char_height+1,d4		; Next skill
.Loop2:	tst.b	(a2)+
	bne.s	.Loop2
	addq.w	#Skill_data_size,a4
	addq.w	#1,d5
	cmpi.w	#Max_skills+1,d5
	bmi.s	.Loop1
	LOCAL
;----------- Print monster attributes -------------
	move.w	#29,Ink_colour
	move.w	#MonKnowW_X,d0		; Print "ATTRIBUTES"
	move.w	#MonKnowW_Y-1,d1
	move.w	#12*6,d2
	move.l	Attrs_txt_ptr,a0
	jsr	Print_centered_string
	move.w	#31,Ink_colour
	move.l	Short_attr_names_ptr,a2		; Print attributes
	move.l	Attr_txt_ptr,a3
	lea.l	Attributes(a1),a4
	move.w	#MonKnowW_X,d3
	move.w	#MonKnowW_Y+7,d4
	moveq.l	#1,d5
	moveq.l	#"0",d6
	moveq.l	#3,d7
.Loop1:	move.w	d3,d0			; Print attribute name
	move.w	d4,d1
	move.l	a2,a0
	jsr	Put_text_line
	move.w	(a4),d0			; Convert normal attribute
	add.w	Magic(a4),d0
	move.l	a3,a0
	jsr	DecR_convert
	move.b	#"/",(a0)			; Correction
	move.w	Maximum(a4),d0		; Convert maximum attribute
	lea.l	4(a3),a0
	jsr	DecR_convert
	move.w	d3,d0			; Print attribute
	move.w	d4,d1
	addi.w	#5*(Char_width+1),d0
	move.l	a3,a0
	jsr	Put_text_line
	addq.w	#Char_height+2,d4		; Next attribute
.Loop2:	tst.b	(a2)+
	bne.s	.Loop2
	addq.w	#Attr_data_size,a4
	addq.w	#1,d5
	cmpi.w	#Max_attrs+1,d5
	bmi.s	.Loop1
	LOCAL
	jmp	Update_screen

MonKnow_ModExit:				; %%%1
	jsr	Close_window		; %%%1
	jmp	Restore_combat_colours	; %%%1

; *** Show monster LP ***
; Show the green stars flying over the battlefield
FUN_ShowMysticStarsAnimation:
; ---------- Create stars -------------------------
	lea.l	FXGFX_workspace,a2
	moveq.l	#16-1,d7
.Loop1:	jsr	Add_COMOB			; Create a star
	move.l	a0,(a2)+
	jsr	Random			; Set X- and Z-coordinates
	mulu.w	#Combat_row_width,d0
	swap	d0
	subi.w	#Combat_row_width/2,d0
	move.w	d0,COMOB_3D_X(a0)
	jsr	Random
	andi.w	#$007f,d0
	neg.w	d0
	move.w	d0,COMOB_3D_Z(a0)
	jsr	Random			; Set Y-coordinate
	andi.w	#$003f,d0
	addi.w	#10,d0
	move.w	d0,COMOB_3D_Y(a0)
	jsr	Random			; Set Z-vector
	andi.w	#$000f,d0
	addi.w	#24,d0
	move.w	d0,COMOB_3D_vector_Z(a0)
	jsr	Random			; Set size
	andi.w	#$000f,d0
	addq.w	#8,d0
	move.w	d0,COMOB_Display_width(a0)
	move.w	d0,COMOB_Display_height(a0)
	jsr	Random			; Set frame
	mulu.w	#5,d0
	swap	d0
	move.w	d0,COMOB_Frame(a0)
	move.w	#16,COMOB_Source_width(a0)	; Set other data
	move.w	#16,COMOB_Source_height(a0)
	move.b	FXGFX_handle,COMOB_Gfx_handle(a0)
	move.l	#Star_FXGFX,COMOB_Gfx_base(a0)
	dbra	d7,.Loop1
; ---------- Show ---------------------------------
	moveq.l	#5,d0
	moveq.l	#32-1,d7
.Loop2:	jsr	Update_combat_screen	; Show
	lea.l	FXGFX_workspace,a1		; Animate stars
	moveq.l	#8-1,d6
.Loop3:	move.l	(a1)+,a0
	jsr	Wave_COMOB
	dbra	d6,.Loop3
	dbra	d7,.Loop2
; ---------- The end ------------------------------
	lea.l	FXGFX_workspace,a1		; Destroy stars
	moveq.l	#16-1,d7
.Loop4:	move.l	(a1)+,a0
	jsr	Delete_COMOB
	dbra	d7,.Loop4
	rts
FUN_SpellMysticDecay:
	jsr Handle_spell
	bne.w .End
	lea FUN_MysticDecay,A2
	jsr Do_all_combat_targets
.End:
	rts
FUN_DealDecayDamage:
	movem.l A3/D2/D1/D0,-(SP)
	; Get caster data
	move.b ($0005,A1),D0 ; Get caster index
	jsr Claim_pointer
	movea.l D0,A2 ; A2 = Caster char data
	; Get caster level (D1)
	moveq #0,D1
	move.b (5,A2),D1 ; caster level
	; Base damage = caster level * 3 / 2
	mulu.w #3,D1
	lsr.w #1,D1 ; now holds the base damage value
	; Get target data
	move.b ($0005,A0),D0 ; Get target index
	jsr Claim_pointer
	movea.l D0,A3 ; A3 = Target char data
	; Dmg Increase % = (1 + (MaxTargetHP - CurrTargetHP) * 10 / MaxTargetHP) ^ 2
	move.w ($cc,A3),D2 ; max target LP
	move.w D2,D0 ; backup max LP in D0
	sub.w ($ca,A3),D2 ; minus current target LP
	mulu.w #10,D2 ; * 10
	divu.w D0,D2 ; / max LP
	addq #1,D2 ; + 1
	mulu.w D2,D2 ; ^ 2
	; Now calc the total damage value
	add.w #100,D2 ; 100% + bonus in %
	mulu.w D1,D2 ; base damage * total percentage
	divu.w #100,D2 ; / 100 to get the value
	cmpi.w #5,D2 ; >= 5?
	bpl.b .Ok ; Ok
	moveq #5,D2 ; Otherwise deal at least 5 damage
.Ok:
	; Now a random value between half and full the damage but still at least 5!
	jsr Random
	move.l D2,D1 ; D2 = full dmg
	lsr.w #1,D1 ; D1 = half dmg
	btst #0,D2 ; odd max dmg?
	beq.b .Ok2 ; no? skip
	addq #1,D1 ; otherwise add 1 to half dmg so we can reach full dmg
.Ok2:
	lsr.w #1,D2 ; half dmg without adjustment
	mulu.w D1,D0
	swap D0 ; now holds random value of 0 to half dmg - 1
	addq #1,D0 ; now 1 to half dmg
	add.w D2,D0 ; random value from half damage to full damage
	cmpi.w #5,D0 ; >= 5?
	bpl.b .Ok3 ; Ok
	moveq #5,D0 ; Always deal at least 5 damage
.Ok3:
	move.l D0,-(SP)
	; Release data pointers
	move.b ($0005,A0),D0
	jsr Free_pointer
	move.b ($0005,A1),D0
	jsr Free_pointer
	move.l (SP)+,D0
	; Calculate damage bonus from level, INT, etc
	jsr FUN_CalculateSpellDamage
	; Deal damage
	jsr Do_damage_to_monster
	movem.l (SP)+,D0/D1/D2/A3
	rts
FUN_MysticDecay:
	; Base Damage = Caster Level
	; Dmg Increase % = (1 + (MaxTargetHP - CurrTargetHP) * 10 / MaxTargetHP) ^ 2
	; MinDmg = 5
	; The max damage at level 50 would be 100 against a target with 10% LP or below.
	; But Level and INT bonus is applied as well which can also increase the damage
	; by 50% or more.
	;
	; The damage is random between half the value and full the value while the min
	; value can still not be below 5.
	;
	; Caster Level 25
	; Target has 10%, 25%, 50%, 75%, 100% LP
	; 10% -> 200% * 25 = 50
	; 25% -> 164% * 25 = 41
	; 50% -> 136% * 25 = 34
	; 75% -> 109% * 25 = 27
	; 100% -> 101% * 25 = 25
	;
	; A0: Target battle data
	; A1: Caster battle data
	;
	; Only A3/A2/A1/D7/D6/D2/D0 are restored!
	; ------------------------------------------------------------------------------
	jsr Handle_magical_defense
	bne.w .Exit2
	; Is caster a monster?
	cmpi.b #$00000002,(A0)
	bne.w .Exit2 ; End, this is a spell against monsters only
	movem.l A1/A0,-(SP)
	; Create green globes
	moveq #5,D4 ; initial globe size
	moveq #$0000001e,D0 ; movement speed = 30
	exg A0,A1 ; let the beam fly from caster to target
	;   IN : d0 - Movement speed (.w)
	;        a0 - Pointer to source participant data (.l)
	;        a1 - Pointer to target participant data (.l)
	jsr Prepare_COMOB_movement
	move.l A0,FXGFX_workspace
	move.w D4,($0012,A0)
	move.w D4,($0014,A0)
	move.w #$0010,($0008,A0)
	move.w #$0010,($000a,A0)
	move.b FXGFX_handle,($0011,A0)
	move.l #$0000a6cc,($001e,A0)
	moveq #$00000004,D0
	lea .Modify,A0
	jsr Make_COMOB_chain
	cmp.w #$0004,D7
	bmi.b .Ok4
	subq.w #$00000003,D7
.Ok4:
	moveq #$00000000,D0
	moveq #$00000004,D1
	jsr Move_COMOBs_to_target
	movem.l (SP)+,A0/A1
	jsr FUN_DealDecayDamage
.Exit2:
	rts
.Modify:
	move.w D4,D1
	lsr.w #$00000001,D1
	neg.w D1
	move.w ($002c,A1),D0
	add.w ($002e,A1),D1
	move.w ($0030,A1),D2
	add.w D0,($0026,A0)
	add.w D1,($0028,A0)
	add.w D2,($002a,A0)
	add.w D4,($0012,A0)
	add.w D4,($0014,A0)
	rts
FUN_SpellWeakenMonster:
	cmpi.b #$00000001,(A0)
	beq .End_Adv ; if target is player, abort
	moveq #0,D0
	move.b ($0005,A0),D0 ; target handle
	moveq #17,D7 ; check up to 18 slots for weakened monsters
	lea Weakened_monsters,A1
.Next:
	tst.b (A1)
	beq .Add ; free slot reached? add the monster handle and end
	cmp.b (A1)+,D0 ; check if the handle is already tracked
	beq .End_Adv ; already there, abort
	dbf D7,.Next
.Add:
	move.b D0,(A1)
.End_Adv:
	rts
FUN_SpellProtectionSphere:
	jsr Handle_spell
	bne .End_Adv3
	moveq #0,D0
	move.w Casting_member,D0
	moveq #0,D1
	move.b Protected_party_members,D1
	bset.l D0,D1
	move.b D1,Protected_party_members
.End_Adv3:
	rts
FUN_SpellForeseeMagic:
	jsr Handle_spell
	bne .End_Adv4
	; create stars
	jsr FUN_ShowMysticStarsAnimation
	st Foresee_magic
.End_Adv4:
	rts
FUN_SpellForeseeAttack:
	jsr Handle_spell
	bne .End_Adv5
	; create stars
	jsr FUN_ShowMysticStarsAnimation
	st Foresee_attack
.End_Adv5:
	rts
FUN_SpellElementToEarth:
	moveq #0,D0
	moveq #2,D7 ; num fade steps
	jmp FUN_ChangeElement
FUN_SpellElementToWind:
	moveq #1,D0
	moveq #2,D7 ; num fade steps
	jmp FUN_ChangeElement
FUN_SpellElementToFire:
	moveq #2,D0
	moveq #3,D7 ; num fade steps
	jmp FUN_ChangeElement
FUN_SpellElementToWater:
	moveq #3,D0
	moveq #2,D7 ; num fade steps
	jmp FUN_ChangeElement
Element_colors:
	dc.w $0861,$0bbc,$0b20,$0019
FUN_ChangeElement:
	jsr Handle_spell
	bne .End_Adv6
	moveq #$10,D1
	lsl.w D0,D1 ; element ($10 to $80)
	lea Element_colors,A2
	add.w D0,D0 ; 2 * D0
	move.w (0,A2,D0.w),D0 ; fade color
	jsr Fade_combat_palette
	lea .Do,A2
	jsr Do_all_combat_targets
	jsr Restore_combat_palette
.Do:
	tst.b ($0001,A0) ; party or monster?
	beq.b .End_Adv6 ; if party, skip
	move.l D0,-(SP)
	move.b ($0005,A0),D0
	jsr Claim_pointer
	movea.l D0,A1
	move.b ($0012,A1),D2 ; get battle flags
	move.l (SP)+,D0
	btst.l #$00000002,D2 ; is boss?
	bne.b .Boss
	move.b D1,($0013,A1) ; set element
	move.b ($0005,A0),D0
	jsr Free_pointer
	jsr FUN_MysticSpellAnimation
	bra .End_Adv6
.Boss:
	move.b ($0005,A0),D0
	jsr Free_pointer
	move.w #$0107,D0 ; immune to spell
	jsr Do_part_prompt
.End_Adv6:
	rts
FUN_SpellShowElements:
	jsr Handle_spell
	bne .End_Adv7
	; create stars
	jsr FUN_ShowMysticStarsAnimation
	st Show_elements
.End_Adv7:
	rts
CShow_monster_LP:
	jsr Handle_spell
	bne .Exit
	; create stars
	jsr FUN_ShowMysticStarsAnimation
	st	Show_monsters		; Show monster LP
.Exit:	rts

; ********** Class 3 spells ***********************
; *** Magical projectiles ***
CMagical_projectiles:
	jsr	Handle_spell		; Handle spell
	bne	.Exit
	lea.l	.Do,a2			; Do all targets
	jsr	Do_all_combat_targets
.Exit:	rts

; [ Do Magical projectile ]
;   IN : a0 - Pointer to victim's participant data (.l)
;        a1 - Pointer to caster's participant data (.l)
; No registers are restored
.Do:
	jsr	Show_missile_to_monster	; ADVANCED: moved to a routine
	jsr	Handle_magical_defense	; Defend ?
	bne	.Exit2
	Get	Part_handle(a1),a2		; Get caster's level
	moveq.l	#0,d0
	move.b	Level_nr(a2),d0
	move.w ($0072,A2),D2 ; base spell dmg bonus
	move.w ($0074,A2),D3 ; max spell dmg bonus
	move.w ($0078,A2),D4 ; percentage damage
	Free	Part_handle(a1)
	lsr.w	#1,d0			; Half
	bne.s	.Notzero
	moveq.l	#1,d0			; At least one
.Notzero:
	; ADVANCED CHANGES - START
	move.l D4,-(SP)
	move.w D0,D4 ; backup damage
	jsr Random
	mulu.w D3,D0 ; random max bonus
	swap D0
	add.w D2,D0 ; total random bonus
	add.w D4,D0 ; add initial damage
	move.l (SP)+,D4
	tst.w D4
	beq.b .LAB_CalcSpellDamageMagicProjectile
	cmpi.w #-99,D4
	bpl.b .LAB_CalcPercDamageMagicProjectile
	moveq #1,D0 ; limit to 1 damage if perc value is -100% or lower
	bra.b .LAB_CalcSpellDamageMagicProjectile
.LAB_CalcPercDamageMagicProjectile:
	add.w #100,D4
	mulu.w D4,D0
	divu.w #100,D0
	bgt.b .LAB_CalcSpellDamageMagicProjectile
	moveq #1,D0 ; deal at least 1 damage
.LAB_CalcSpellDamageMagicProjectile:
	jsr FUN_CalculateSpellDamage
	jsr	Do_damage_to_monster; Do damage !
	move.l	a1,a0			; Process
	jsr	Process_damage
.Exit2:	rts

;*****************************************************************************
; [ Show a magic missile from a party member to a monster ]
;   IN : a0 - Pointer to victim's participant data (.l)
;        a1 - Pointer to caster's participant data (.l)
; All registers are restored
; ADVANCED: moved here from [ CMagical_projectiles ] (also used by the
;  magic sword attack)
;*****************************************************************************
Show_missile_to_monster:
	movem.l	d0-d7/a0/a1,-(sp)
; ---------- Create magic missile -----------------
	exg	a1,a0			; Get source coordinates
	jsr	Get_3D_part_coordinates
	move.w	d1,d4
	cmp.w	#3,Part_X(a0)		; Left or right ?
	bpl.s	.Right
	move.w	#-100,d3			; Left
	bra.s	.Go_on
.Right:	move.w	#100,d3			; Right
.Go_on:	move.w	d3,-(sp)			; Save source X
	move.w	#-150+1,d5		; Set source Z
	exg	a0,a1			; Get target coordinates
	jsr	Get_3D_part_coordinates
	jsr	Add_COMOB			; Create COMOB
	move.w	d3,COMOB_3D_X(a0)		; Set coordinates
	move.w	d4,COMOB_3D_Y(a0)
	move.w	d5,COMOB_3D_Z(a0)
	moveq.l	#Projectile_speed,d6	; Process vector
	jsr	Process_COMOB_vector
	move.w	#32,COMOB_Display_width(a0)	; Initialize COMOB
	move.w	#32,COMOB_Display_height(a0)
	move.w	#32,COMOB_Source_width(a0)
	move.w	#32,COMOB_Source_height(a0)
	move.b	FXGFX_handle,COMOB_Gfx_handle(a0)
	move.l	#Missile_to_FXGFX,COMOB_Gfx_base(a0)
	move.w	(sp)+,d3			; Which direction ?
	bmi.s	.Right2
	bset	#0,COMOB_Mirror_flags(a0)	; Flip
; ---------- Build up missile ---------------------
.Right2:	moveq.l	#17-1,d6			; Show build-up
.Loop1:	jsr	Update_combat_screen	; Show
	addq.w	#1,COMOB_Frame(a0)
	bset	#COMOB_update,COMOB_Flags(a0)
	dbra	d6,.Loop1
; ---------- Move towards targets -----------------
	move.w	d0,COMOB_3D_vector_X(a0)	; Set vector
	move.w	d1,COMOB_3D_vector_Y(a0)
	move.w	d2,COMOB_3D_vector_Z(a0)
	moveq.l	#7,d0
	move.w	#17,COMOB_Frame(a0)
	bra.s	.Entry2
.Loop2:	jsr	Update_combat_screen	; Show
	sub.w	#17,COMOB_Frame(a0)
	jsr	Circle_COMOB
	add.w	#17,COMOB_Frame(a0)
.Entry2:	dbra	d7,.Loop2
; ---------- The end ------------------------------
	jsr	Delete_COMOB		; Delete
	movem.l	(sp)+,d0-d7/a0/a1
	rts

;*****************************************************************************
; [ Magic sword attack (energy sword) ]
;   IN : a0 - Pointer to casting participant data (.l)
; No registers are restored
; NOTES :
;   - ADVANCED: Class 6 spell 26. It is a physical special attack against all
;     enemies in close range (the 8 squares around the attacker), so it can
;     be parried but not deflected by anti-magic, and it can't fail like a
;     spell. Used by party members (via the equipped item) and by monsters.
;   - Damage : attack damage (min. 1) x (APR + 1) / 2, plus 0-25%, plus the
;     spell damage bonus (level, intelligence, spirit element).
;   - The caster is healed by 10% of the damage.
;*****************************************************************************
CMagic_sword_attack:
	tst.b	Magic_object_flag		; From object ?
	beq.s	.No_object
	jsr	Handle_spell		; Yes -> Use charge
	bne	.Exit
.No_object:	jsr	Get_closerange_targets	; Targets in reach NOW
	move.l	d0,Part_target(a0)
	move.b	#Enemy_row_targmode,Part_target+6(a0)
	lea.l	.Do,a2			; Do all targets
	jsr	Do_all_combat_targets
.Exit:	rts

; [ Do magic sword attack ]
;   IN : a0 - Pointer to victim's participant data (.l)
;        a1 - Pointer to caster's participant data (.l)
; No registers are restored
.Do:
	cmp.b	#1,Part_type(a1)		; Party or monster ?
	bne.s	.Monster
	jsr	Show_missile_to_monster	; Show
	bra.s	.Shown
.Monster:	jsr	Show_missile_to_member
.Shown:	exg	a0,a1			; Like a weapon attack
	Get	Part_handle(a0),a2		; Get character data
	Get	Part_handle(a1),a3

; *** R E G I S T E R   C O N T E N T S ***
;  a0 - Pointer to attacker's participant data
;  a1 - Pointer to defender's participant data
;  a2 - Pointer to attacker's character data
;  a3 - Pointer to defender's character data

; ---------- Check undamageability ----------------
	move.w	Body_conditions(a3),d0	; Undamageable ?
	andi.w	#Damage_mask,d0
	beq.s	.Ok1
	move.w	#262,d0			; Yes -> "Cannot damage !"
	jsr	Do_prompt
	bra	.Done
; ---------- Probe defender's parade skill --------
.Ok1:	cmp.b	#Parade_action,Part_action(a1)	; Defending ?
	bne.s	.Ok2
	jsr	FUN_TestDefenderParry
	bpl.s	.Ok2
	move.w	#214,d0			; "Attack was deflected !"
	jsr	Do_part_prompt
	bra	.Done
; ---------- Calculate damage ---------------------
.Ok2:	moveq.l	#0,d0			; Get attack damage
	move.w	Damage(a2),d0
	add.w	Damage_magic(a2),d0
	bgt.s	.Ok3
	moveq.l	#1,d0			; At least 1
.Ok3:	moveq.l	#0,d1			; x (APR + 1) / 2
	move.b	Attacks_per_round(a2),d1
	bne.s	.Ok4
	moveq.l	#1,d1
.Ok4:	addq.w	#1,d1
	mulu.w	d1,d0
	lsr.l	#1,d0
	cmp.l	#$7fff,d0			; Clip
	bls.s	.Ok5
	move.l	#$7fff,d0
.Ok5:	move.w	d0,d2			; Add 0-25%
	move.w	d0,d1
	lsr.w	#2,d1
	addq.w	#1,d1
	jsr	Random
	mulu.w	d1,d0
	swap	d0
	add.w	d2,d0
	exg	a0,a1			; Add spell damage bonus
	jsr	FUN_CalculateSpellDamage
	exg	a0,a1
; ---------- Do damage ----------------------------
	move.l	a0,-(sp)			; Do damage
	move.l	a1,a0
	cmp.b	#1,Part_type(a0)		; Party or monster ?
	bne.s	.Monster2
	jsr	Do_combat_damage
	bra.s	.Damaged
.Monster2:	jsr	Do_damage_to_monster
.Damaged:	move.l	(sp)+,a0
	jsr	Process_damage		; For the records
; ---------- Heal attacker ------------------------
	and.l	#$ffff,d0			; 10% of the damage
	divu.w	#10,d0
	beq.s	.Done
	move.w	Life_points(a2),d1		; Add
	move.w	Life_points+Maximum(a2),d2
	add.w	Life_points+Magic(a2),d2
	add.w	d0,d1
	cmp.w	d2,d1			; Too much ?
	bls.s	.Ok6
	move.w	d2,d1			; Yes -> Clip
.Ok6:	cmp.w	Life_points(a2),d1		; (never decrease)
	bls.s	.Done
	move.w	d1,Life_points(a2)
.Done:	Free	Part_handle(a0)
	Free	Part_handle(a1)
	rts

; *** Set condition spells ***
CCondition:
	jsr	Handle_spell		; Handle spell
	bne	.Exit
	lea.l	.Do_condition,a2		; Do all targets
	jsr	Do_all_combat_targets
.Exit:	rts

; [ Do condition spell ]
;   IN : a0 - Pointer to victim's participant data (.l)
;        a1 - Pointer to caster's participant data (.l)
; No registers are restored
.Do_condition:
	jsr	Handle_magical_defense	; Defend ?
	bne	.Exit2
	move.l	a0,a2
; ---------- Set condition ------------------------
	lea.l	CCondition_table,a1		; Get condition number
	move.w	Selected_spell,d0
	subq.w	#3,d0
	move.b	0(a1,d0.w),d0
	Get	Part_handle(a0),a1
	move.b	Monster_type_status(a1),d1	; End monster ?
	btst	#End_monster_type,d1
	beq.s	.Do
	move.w	#End_monster_mask,d1	; Yes -> Allowed ?
	btst	d0,d1
	beq.s	.Do
	Free	Part_handle(a0)		; No
	move.w	#263,d0			; "Immune !"
	jsr	Do_part_prompt
	bra	.Exit2
.Do:	move.w	Body_conditions(a1),d1	; Yes -> Set condition
	bset	d0,d1
	move.w	d1,Body_conditions(a1)
	Free	Part_handle(a0)
; ---------- Create effect ------------------------
	cmp.b	#1,Part_type(a0)		; Party or monster ?
	bne.s	.Monster1
	moveq.l	#0,d7			; Party -> Get member number
	move.b	Part_nr(a0),d7
	moveq.l	#0,d0			; Do fake damage
	jsr	Do_damage
	bra.s	.Go_on1
.Monster1:	Set_anim	Hit_anim,a0		; Monster -> Hit !
	moveq.l	#0,d0
	jsr	Do_damage_to_monster
.Go_on1:	jsr	Get_3D_part_coordinates	; Get coordinates
	jsr	Add_COMOB			; Create COMOBs
	move.l	a0,a1
	jsr	Add_COMOB
	move.w	d0,COMOB_3D_X(a0)		; Initialize circle
	cmp.b	#1,Part_type(a2)		; Party or monster ?
	bne.s	.Monster2
	move.w	d1,d3			; Party -> x 1.5
	lsr.w	#1,d3
	add.w	d3,d1
	bra.s	.Go_on2
.Monster2:	subq.w	#8,d1			; Monster
.Go_on2:	move.w	d1,COMOB_3D_Y(a0)
	move.w	d2,COMOB_3D_Z(a0)
	move.w	#32-16,COMOB_Display_width(a0)
	move.w	#32-16,COMOB_Display_height(a0)
	move.w	#32,COMOB_Source_width(a0)
	move.w	#32,COMOB_Source_height(a0)
	move.b	FXGFX_handle,COMOB_Gfx_handle(a0)
	move.l	#Condition_circle_FXGFX,COMOB_Gfx_base(a0)
	move.w	d0,COMOB_3D_X(a1)		; Initialize symbol
	addq.w	#4,d1
	move.w	d1,COMOB_3D_Y(a1)
	subq.w	#1,d2			; In front of circle
	move.w	d2,COMOB_3D_Z(a1)
	move.w	#16-8,COMOB_Display_width(a1)
	move.w	#16-8,COMOB_Display_height(a1)
	move.w	#16,COMOB_Source_width(a1)
	move.w	#16,COMOB_Source_height(a1)
	move.b	FXGFX_handle,COMOB_Gfx_handle(a1)
	move.l	#Conditions_FXGFX,COMOB_Gfx_base(a1)
	move.w	Selected_spell,d0
	subq.w	#3,d0
	move.w	d0,COMOB_Frame(a1)
; ---------- Grow larger --------------------------
	moveq.l	#10-1,d7
.Loop1:	jsr	Update_combat_screen
	addq.w	#2,COMOB_Display_width(a0)
	addq.w	#2,COMOB_Display_height(a0)
	subq.w	#1,COMOB_3D_Y(a0)
	bset	#COMOB_update,COMOB_Flags(a0)
	addq.w	#2,COMOB_Display_width(a1)
	addq.w	#2,COMOB_Display_height(a1)
	subq.w	#1,COMOB_3D_Y(a1)
	bset	#COMOB_update,COMOB_Flags(a1)
	dbra	d7,.Loop1
; ---------- Grow smaller -------------------------
	moveq.l	#10-1,d7
.Loop2:	jsr	Update_combat_screen
	subq.w	#2,COMOB_Display_width(a0)
	subq.w	#2,COMOB_Display_height(a0)
	addq.w	#1,COMOB_3D_Y(a0)
	bset	#COMOB_update,COMOB_Flags(a0)
	subq.w	#2,COMOB_Display_width(a1)
	subq.w	#2,COMOB_Display_height(a1)
	addq.w	#1,COMOB_3D_Y(a1)
	bset	#COMOB_update,COMOB_Flags(a1)
	dbra	d7,.Loop2
; ---------- The end ------------------------------
	jsr	Delete_COMOB		; Destroy COMOBs
	move.l	a1,a0
	jsr	Delete_COMOB
.Exit2:	rts

; *** Dissolve victim ***
CDissolve_victim:
	jsr	Handle_spell		; Handle spell
	bne	.Exit
	lea.l	.Do,a2			; Do all targets
	jsr	Do_all_combat_targets
.Exit:	rts

; [ Do Dissolve victim ]
;   IN : a0 - Pointer to victim's participant data (.l)
;        a1 - Pointer to caster's participant data (.l)
; No registers are restored
.Do:
	jsr	Handle_magical_defense	; Defend ?
	bne	.Exit2
	Get	Part_handle(a0),a2		; Yes -> Is end monster ?
	move.b	Monster_type_status(a2),d0
	Free	Part_handle(a0)
	btst	#End_monster_type,d0
	beq.s	.Ok
	move.w	#263,d0			; Yes -> "No way!"
	jsr	Do_part_prompt
	bra	.Exit2
; ---------- Shrink monster -----------------------
.Ok:	move.l	a0,a2
	move.l	Part_COMOB_ptr(a0),a0
	move.w	COMOB_Display_width(a0),d0	; Get 1/16th of width
	lsr.w	#4,d0
	bne.s	.Notzero1
	moveq.l	#1,d0
.Notzero1:	move.w	COMOB_Display_height(a0),d1	; Get 1/16th of height
	lsr.w	#4,d1
	bne.s	.Notzero2
	moveq.l	#1,d1
.Notzero2:	moveq.l	#15-1,d7
.Loop1:	Set_anim	Hit_anim,a2		; Hit !
	move.w	COMOB_Display_width(a0),d2	; Make monster smaller
	sub.w	d0,d2
	move.w	d2,COMOB_Display_width(a0)
	move.w	COMOB_Display_height(a0),d2
	sub.w	d1,d2
	move.w	d2,COMOB_Display_height(a0)
	bset	#COMOB_update,COMOB_Flags(a0)
	jsr	Update_combat_screen	; Show
	dbra	d7,.Loop1
; ---------- Create star --------------------------
	move.l	a0,a3
	jsr	Add_COMOB
	move.w	COMOB_3D_X(a3),COMOB_3D_X(a0)
	move.w	COMOB_3D_Y(a3),d0
	subq.w	#4,d0
	move.w	d0,COMOB_3D_Y(a0)
	move.w	COMOB_3D_Z(a3),COMOB_3D_Z(a0)
	move.w	#24,COMOB_Display_width(a0)
	move.w	#24,COMOB_Display_height(a0)
	move.w	#16,COMOB_Source_width(a0)
	move.w	#16,COMOB_Source_height(a0)
	move.b	FXGFX_handle,COMOB_Gfx_handle(a0)
	move.l	#Star_FXGFX,COMOB_Gfx_base(a0)
	exg	a0,a3			; Delete monster COMOB
	jsr	Delete_COMOB
	move.l	a3,a0
; ---------- Star blinks --------------------------
	moveq.l	#5,d0
	moveq.l	#9-1,d7
.Loop2:	jsr	Update_combat_screen
	jsr	Wave_COMOB
	dbra	d7,.Loop2
	jsr	Delete_COMOB		; Destroy star
; ---------- Destroy monster ----------------------
	Get	Part_handle(a2),a3		; Process damage
	move.w	Life_points+Maximum(a3),d0
	Free	Part_handle(a2)
	move.l	a1,a0
	jsr	Process_damage
	move.l	a2,a0			; Destroy monster
	jsr	Destroy_monster
.Exit2:	rts

; *** Mudsling ***
CMudsling:
	jsr	Handle_spell		; Handle spell
	bne	.Exit
	lea.l	.Do,a2			; Do all targets
	jsr	Do_all_combat_targets
.Exit:	rts

; [ Do Mudsling ]
;   IN : a0 - Pointer to victim's participant data (.l)
;        a1 - Pointer to caster's participant data (.l)
; No registers are restored
.Do:
; ---------- Create rock --------------------------
	move.l	a0,a2
	move.l	Part_COMOB_ptr(a0),a3
	jsr	Add_COMOB
	move.w	COMOB_3D_X(a3),COMOB_3D_X(a0)
	move.w	COMOB_Display_height(a3),d0
	addi.w	#20,d0
	move.w	d0,COMOB_3D_Y(a0)
	move.w	COMOB_3D_Z(a3),COMOB_3D_Z(a0)
	move.w	#32,COMOB_Display_width(a0)
	move.w	#16,COMOB_Display_height(a0)
	move.w	#32,COMOB_Source_width(a0)
	move.w	#16,COMOB_Source_height(a0)
	move.b	FXGFX_handle,COMOB_Gfx_handle(a0)
	move.l	#Rock_FXGFX,COMOB_Gfx_base(a0)
; ---------- Fade rock in as silhouette -----------
	lea.l	Glow_colours,a3
	moveq.l	#21-1,d7
.Loop1:	move.w	(a3)+,COMOB_Colour(a0)	; Set stone colour
	bset	#COMOB_update,COMOB_Flags(a0)
	jsr	Update_combat_screen	; Show
	dbra	d7,.Loop1
	move.w	#-1,COMOB_Colour(a0)	; No silhouette
; ---------- Drop rock ----------------------------
	move.w	#-1,COMOB_3D_vector_Y(a0)	; Down
	moveq.l	#7-1,d7			; Show
.Loop2:	jsr	Update_combat_screen
	subq.w	#1,COMOB_3D_vector_Y(a0)
	dbra	d7,.Loop2
; ---------- Squash monster -----------------------
	move.w	COMOB_3D_vector_Y(a0),d0
	move.l	Part_COMOB_ptr(a2),a3
	moveq.l	#2-1,d7
.Loop3:	add.w	d0,COMOB_Display_height(a3)	; Make monster smaller
	bset	#COMOB_update,COMOB_Flags(a0)
	bset	#COMOB_update,COMOB_Flags(a3)
	jsr	Update_combat_screen	; Show
	dbra	d7,.Loop3
	move.w	COMOB_3D_vector_Y(a0),d1	; Back up
	asr.w	#1,d1
	neg.w	d1
	move.w	d1,COMOB_3D_vector_Y(a0)
	moveq.l	#2-1,d7
.Loop4:	sub.w	d0,COMOB_Display_height(a3)	; Make monster larger
	bset	#COMOB_update,COMOB_Flags(a3)
	jsr	Update_combat_screen	; Show
	dbra	d7,.Loop4
; ---------- Remove rock --------------------------
	lea.l	Glow_colours+20*2,a3
	moveq.l	#7-1,d7
.Loop5:	move.w	(a3),COMOB_Colour(a0)	; Set stone colour
	subq.l	#6,a3
	bset	#COMOB_update,COMOB_Flags(a0)
	jsr	Update_combat_screen	; Show
	dbra	d7,.Loop5
	jsr	Delete_COMOB		; Remove rock
; ---------- Do damage to monster -----------------
	move.l	a2,a0
	jsr	Do_destruction_damage
.Exit2:	rts

; *** Rockfall ***
CRockfall:
	jsr	Handle_spell		; Handle spell
	bne	.Exit
	lea.l	.Do,a2			; Do all targets
	jsr	Do_all_combat_targets
.Exit:	rts

; [ Do Rockfall ]
;   IN : a0 - Pointer to victim's participant data (.l)
;        a1 - Pointer to caster's participant data (.l)
; No registers are restored
.Do:
; ---------- Create rock --------------------------
	move.l	a0,a2
	move.l	Part_COMOB_ptr(a0),a3
	jsr	Add_COMOB
	move.w	COMOB_3D_X(a3),COMOB_3D_X(a0)
	move.w	COMOB_Display_height(a3),d0
	addi.w	#20,d0
	move.w	d0,COMOB_3D_Y(a0)
	move.w	COMOB_3D_Z(a3),COMOB_3D_Z(a0)
	move.w	#64,COMOB_Display_width(a0)
	move.w	#32,COMOB_Display_height(a0)
	move.w	#32,COMOB_Source_width(a0)
	move.w	#16,COMOB_Source_height(a0)
	move.b	FXGFX_handle,COMOB_Gfx_handle(a0)
	move.l	#Rock_FXGFX,COMOB_Gfx_base(a0)
; ---------- Fade rock in as silhouette -----------
	lea.l	Glow_colours,a3
	moveq.l	#21-1,d7
.Loop1:	move.w	(a3)+,COMOB_Colour(a0)	; Set stone colour
	bset	#COMOB_update,COMOB_Flags(a0)
	jsr	Update_combat_screen	; Show
	dbra	d7,.Loop1
	move.w	#-1,COMOB_Colour(a0)	; No silhouette
; ---------- Drop rock ----------------------------
	move.w	#-1,COMOB_3D_vector_Y(a0)	; Down
	moveq.l	#7-1,d7			; Show
.Loop2:	jsr	Update_combat_screen
	subq.w	#1,COMOB_3D_vector_Y(a0)
	dbra	d7,.Loop2
; ---------- Squash monster -----------------------
	move.w	COMOB_3D_vector_Y(a0),d0
	move.l	Part_COMOB_ptr(a2),a3
	moveq.l	#3-1,d7
.Loop3:	add.w	d0,COMOB_Display_height(a3)	; Make monster smaller
	bset	#COMOB_update,COMOB_Flags(a0)
	bset	#COMOB_update,COMOB_Flags(a3)
	jsr	Update_combat_screen	; Show
	dbra	d7,.Loop3
	move.w	COMOB_3D_vector_Y(a0),d1	; Back up
	asr.w	#1,d1
	neg.w	d1
	move.w	d1,COMOB_3D_vector_Y(a0)
	moveq.l	#3-1,d7
.Loop4:	sub.w	d0,COMOB_Display_height(a3)	; Make monster larger
	bset	#COMOB_update,COMOB_Flags(a3)
	jsr	Update_combat_screen	; Show
	dbra	d7,.Loop4
; ---------- Remove rock --------------------------
	lea.l	Glow_colours+20*2,a3
	moveq.l	#7-1,d7
.Loop5:	move.w	(a3),COMOB_Colour(a0)	; Set stone colour
	subq.l	#6,a3
	bset	#COMOB_update,COMOB_Flags(a0)
	jsr	Update_combat_screen	; Show
	dbra	d7,.Loop5
	jsr	Delete_COMOB		; Remove rock
; ---------- Do damage to monster -----------------
	move.l	a2,a0
	jsr	Do_destruction_damage
.Exit2:	rts

; *** Earthslide ***
CEarthslide:
	jsr	Handle_spell		; Handle spell
	bne	.Exit
	move.l	Part_target(a0),d0		; Get row number
	jsr	Get_target_row_number
	move.w	d0,d1			; Get Z-coordinate
	moveq.l	#0,d0
	jsr	Calculate_3D_coordinates
; ---------- Create earthmass ---------------------
	move.l	a0,a1
	jsr	Add_COMOB
	clr.w	COMOB_3D_X(a0)
	move.w	#60,COMOB_3D_Y(a0)
	subq.w	#2,d1
	move.w	d1,COMOB_3D_Z(a0)
	move.w	#Combat_row_width-8*21+20,COMOB_Display_width(a0)
	move.w	#64,COMOB_Display_height(a0)
	move.w	#64,COMOB_Source_width(a0)
	move.w	#32,COMOB_Source_height(a0)
	move.b	FXGFX_handle,COMOB_Gfx_handle(a0)
	move.l	#Earthmass_FXGFX,COMOB_Gfx_base(a0)
; ---------- Fade mass in as silhouette -----------
	lea.l	Glow_colours,a3
	moveq.l	#21-1,d7
.Loop1:	move.w	(a3)+,COMOB_Colour(a0)	; Set colour
	addq.w	#8,COMOB_Display_width(a0)
	bset	#COMOB_update,COMOB_Flags(a0)
	jsr	Update_combat_screen	; Show
	dbra	d7,.Loop1
	move.w	#-1,COMOB_Colour(a0)	; No silhouette
; ---------- Drop mass ----------------------------
	move.w	#-1,COMOB_3D_vector_Y(a0)	; Down
.Again:	jsr	Update_combat_screen
	subq.w	#1,COMOB_3D_vector_Y(a0)
	tst.w	COMOB_3D_Y(a0)
	bgt.s	.Again
	clr.w	COMOB_3D_vector_Y(a0)
; ---------- Do damage ----------------------------
	exg	a0,a1			; Do all targets
	lea.l	Do_destruction_damage,a2
	jsr	Do_all_combat_targets
; ---------- Remove mass --------------------------
	move.l	a1,a0
	moveq.l	#7-1,d7
.Loop2:	jsr	Update_combat_screen	; Make thinner
	sub.w	#8,COMOB_Display_height(a0)
	bset	#COMOB_update,COMOB_Flags(a0)
	dbra	d7,.Loop2
	jsr	Delete_COMOB		; Remove mass
.Exit:	rts

; *** Earthquake ***
CEarthquake:
	jsr	Handle_spell		; Handle spell
	bne	.Exit
	moveq.l	#0,d0			; Get left X-coordinate
	moveq.l	#0,d1
	jsr	Calculate_3D_coordinates
	move.w	d0,d3
	moveq.l	#5,d0			; Get right X-coordinate
	moveq.l	#0,d1
	jsr	Calculate_3D_coordinates
	sub.w	d3,d0			; Calculate width
	addi.w	#70,d0
; ---------- Create earthmass ---------------------
	move.l	a0,a1
	jsr	Add_COMOB
	clr.w	COMOB_3D_X(a0)
	clr.w	COMOB_3D_Y(a0)
	addq.w	#8,d1
	move.w	d1,COMOB_3D_Z(a0)
	subi.w	#8*21-20,d0
	move.w	d0,COMOB_Display_width(a0)
	move.w	#64,COMOB_Display_height(a0)
	move.w	#64,COMOB_Source_width(a0)
	move.w	#32,COMOB_Source_height(a0)
	move.b	FXGFX_handle,COMOB_Gfx_handle(a0)
	move.l	#Earthmass_FXGFX,COMOB_Gfx_base(a0)
; ---------- Fade mass in as silhouette -----------
	lea.l	Glow_colours,a3
	moveq.l	#21-1,d7
.Loop1:	move.w	(a3)+,COMOB_Colour(a0)	; Set colour
	addq.w	#8,COMOB_Display_width(a0)
	bset	#COMOB_update,COMOB_Flags(a0)
	jsr	Update_combat_screen	; Show
	dbra	d7,.Loop1
	move.w	#-1,COMOB_Colour(a0)	; No silhouette
; ---------- Move mass forward --------------------
	move.w	#-20,COMOB_3D_vector_Z(a0)	; Forward
.Again:	jsr	Update_combat_screen	; Show
	jsr	Random			; Shake it, baby !
	andi.w	#$0007,d0
	subq.w	#3,d0
	move.w	d0,Vertical_screen_offset
	jsr	My_vsync
	tst.w	COMOB_3D_Z(a0)		; End ?
	bgt.s	.Again
	clr.w	Vertical_screen_offset	; Stop
; ---------- Move mass down -----------------------
	move.w	#-5,COMOB_3D_vector_Y(a0)	; Down
	clr.w	COMOB_3D_vector_Z(a0)
	moveq.l	#11-1,d7
.Loop2:	jsr	Update_combat_screen
	dbra	d7,.Loop2
	jsr	Delete_COMOB		; Remove mass
; ---------- Do damage ----------------------------
	move.l	a1,a0			; Do all targets
	lea.l	Do_destruction_damage,a2
	jsr	Do_all_combat_targets
.Exit:	rts

; *** Winddevil ***
CWinddevil:
	jsr	Handle_spell		; Handle spell
	bne	.Exit
	lea.l	.Do,a2
	jsr	Do_all_combat_targets
.Exit:	rts

; [ Do Winddevil ]
;   IN : a0 - Pointer to victim's participant data (.l)
;        a1 - Pointer to caster's participant data (.l)
; No registers are restored
.Do:
; ---------- Create whirlwind ---------------------
	move.l	a0,a2
	move.l	Part_COMOB_ptr(a0),a3
	jsr	Add_COMOB
	move.w	COMOB_3D_X(a3),COMOB_3D_X(a0)
	clr.w	COMOB_3D_Y(a0)
	move.w	COMOB_3D_Z(a3),d0
	addq.w	#1,d0
	move.w	d0,COMOB_3D_Z(a0)
	move.w	#40,COMOB_Display_width(a0)
	move.w	#80,COMOB_Display_height(a0)
	move.w	#32,COMOB_Source_width(a0)
	move.w	#64,COMOB_Source_height(a0)
	move.b	FXGFX_handle,COMOB_Gfx_handle(a0)
	move.l	#Whirlwind_FXGFX,COMOB_Gfx_base(a0)
; ---------- Fade in as silhouette ----------------
	lea.l	Glow_colours,a4
	moveq.l	#21-1,d7
.Loop1:	move.w	(a4)+,COMOB_Colour(a0)	; Set colour
	bset	#COMOB_update,COMOB_Flags(a0)
	jsr	Update_combat_screen	; Show
	dbra	d7,.Loop1
	move.w	#-1,COMOB_Colour(a0)	; No silhouette
; ---------- Animate whirlwind & monster ----------
	lea.l	Oscillation,a4
	moveq.l	#4,d0
	moveq.l	#0,d1
	moveq.l	#16-1,d7
.Loop2:	jsr	Update_combat_screen	; Show
	move.b	0(a4,d1.w),d2		; Oscillate
	ext.w	d2
	add.w	d2,COMOB_Display_width(a0)
	add.w	d2,COMOB_Display_width(a3)
	move.b	1(a4,d1.w),d2
	ext.w	d2
	add.w	d2,COMOB_Display_height(a0)
	add.w	d2,COMOB_Display_height(a3)
	Set_anim	Hit_anim,a2		; Hit !
	jsr	Circle_COMOB		; Animate whirlwind
	bset	#COMOB_update,COMOB_Flags(a3)
	addq.w	#1,d1			; Increase index
	andi.w	#$0007,d1
	dbra	d7,.Loop2
; ---------- Remove whirlwind ---------------------
	move.w	COMOB_Display_width(a0),d0	; Get shrink factors
	lsr.w	#3,d0
	move.w	COMOB_Display_height(a0),d1
	lsr.w	#3,d1
	moveq.l	#7-1,d7
.Loop3:	sub.w	d0,COMOB_Display_width(a0)	; Shrink
	sub.w	d1,COMOB_Display_height(a0)
	bset	#COMOB_update,COMOB_Flags(a0)
	jsr	Update_combat_screen	; Show
	dbra	d7,.Loop3
	jsr	Delete_COMOB		; Remove
; ---------- Do damage to monster -----------------
	move.l	a2,a0
	jsr	Do_destruction_damage
.Exit2:	rts

; *** Windhowler ***
CWindhowler:
	jsr	Handle_spell		; Handle spell
	bne	.Exit
	lea.l	.Do,a2
	jsr	Do_all_combat_targets
.Exit:	rts

; [ Do Windhowler ]
;   IN : a0 - Pointer to victim's participant data (.l)
;        a1 - Pointer to caster's participant data (.l)
; No registers are restored
.Do:
; ---------- Create whirlwind ---------------------
	move.l	a0,a2
	move.l	Part_COMOB_ptr(a0),a3
	jsr	Add_COMOB
	move.w	COMOB_3D_X(a3),COMOB_3D_X(a0)
	clr.w	COMOB_3D_Y(a0)
	move.w	COMOB_3D_Z(a3),d0
	addq.w	#1,d0
	move.w	d0,COMOB_3D_Z(a0)
	move.w	#48,COMOB_Display_width(a0)
	move.w	#96,COMOB_Display_height(a0)
	move.w	#32,COMOB_Source_width(a0)
	move.w	#64,COMOB_Source_height(a0)
	move.b	FXGFX_handle,COMOB_Gfx_handle(a0)
	move.l	#Whirlwind_FXGFX,COMOB_Gfx_base(a0)
; ---------- Fade in as silhouette ----------------
	lea.l	Glow_colours,a4
	moveq.l	#21-1,d7
.Loop1:	move.w	(a4)+,COMOB_Colour(a0)	; Set colour
	bset	#COMOB_update,COMOB_Flags(a0)
	jsr	Update_combat_screen	; Show
	dbra	d7,.Loop1
	move.w	#-1,COMOB_Colour(a0)	; No silhouette
; ---------- Animate whirlwind & monster ----------
	lea.l	Oscillation,a4
	moveq.l	#4,d0
	moveq.l	#0,d1
	moveq.l	#24-1,d7
.Loop2:	jsr	Update_combat_screen	; Show
	move.b	0(a4,d1.w),d2		; Oscillate
	ext.w	d2
	asl.w	#1,d2
	add.w	d2,COMOB_Display_width(a0)
	add.w	d2,COMOB_Display_width(a3)
	move.b	1(a4,d1.w),d2
	ext.w	d2
	asl.w	#1,d2
	add.w	d2,COMOB_Display_height(a0)
	add.w	d2,COMOB_Display_height(a3)
	Set_anim	Hit_anim,a2		; Hit !
	jsr	Circle_COMOB		; Animate whirlwind
	bset	#COMOB_update,COMOB_Flags(a3)
	addq.w	#1,d1			; Increase index
	andi.w	#$0007,d1
	dbra	d7,.Loop2
; ---------- Remove whirlwind ---------------------
	move.w	COMOB_Display_width(a0),d0	; Get shrink factors
	lsr.w	#3,d0
	move.w	COMOB_Display_height(a0),d1
	lsr.w	#3,d1
	moveq.l	#7-1,d7
.Loop3:	sub.w	d0,COMOB_Display_width(a0)	; Shrink
	sub.w	d1,COMOB_Display_height(a0)
	bset	#COMOB_update,COMOB_Flags(a0)
	jsr	Update_combat_screen	; Show
	dbra	d7,.Loop3
	jsr	Delete_COMOB		; Remove
; ---------- Do damage to monster -----------------
	move.l	a2,a0
	jsr	Do_destruction_damage
.Exit2:	rts

; *** Thunderbolt ***
CThunderbolt:
	jsr	Handle_spell		; Handle spell
	bne	.Exit
; ---------- Prepare lightning bolts --------------
	move.l	Part_target(a0),d0		; Get row number
	jsr	Get_target_row_number
	move.w	d0,d1			; Get Z-coordinate
	moveq.l	#0,d0
	jsr	Calculate_3D_coordinates
	addq.w	#1,d1
	movem.l	a0/a1,-(sp)		; Save
	lea.l	Combat_pal,a2		; Make white palette
	moveq.l	#32-1,d7
.Loop1:	move.w	#$fff,(a2)+
	dbra	d7,.Loop1
; ---------- Do -----------------------------------
	lea.l	Combat_pal,a2
	lea.l	Combat_backup_pal,a3
	moveq.l	#8-1,d7
.Loop2:	jsr	Add_COMOB			; Make lightning bolt
	jsr	Random			; Set X-coordinate
	andi.w	#$007f,d0
	subi.w	#64,d0
	move.w	d0,COMOB_3D_X(a0)
	jsr	Random			; Set Z-coordinate
	andi.w	#$001f,d0
	subi.w	#16,d0
	add.w	d1,d0
	move.w	d0,COMOB_3D_Z(a0)
	jsr	Random			; Set width
	andi.w	#$000f,d0
	addi.w	#32-8,d0
	move.w	d0,COMOB_Display_width(a0)
	jsr	Random			; Set X-vector
	andi.w	#$001f,d0
	subi.w	#16,d0
	move.w	d0,COMOB_3D_vector_X(a0)
	jsr	Random			; Set Z-vector
	andi.w	#$001f,d0
	subi.w	#16,d0
	move.w	d0,COMOB_3D_vector_Z(a0)
	jsr	Random			; Set mirror flags
	btst	#5,d0
	beq.s	.Zero
	bset	#0,COMOB_Mirror_flags(a0)
.Zero:	clr.w	COMOB_3D_Y(a0)		; Set other parameters
	move.w	#128,COMOB_Display_height(a0)
	move.w	#32,COMOB_Source_width(a0)
	move.w	#64,COMOB_Source_height(a0)
	move.b	FXGFX_handle,COMOB_Gfx_handle(a0)
	move.l	#Lightning_FXGFX,COMOB_Gfx_base(a0)
	move.l	a2,Combat_pal_ptr		; White palette
	jsr	Reset_current_RL
	jsr	Random			; Wait
	andi.w	#$0003,d0
	addq.w	#1,d0
	add.w	d0,d0
	jsr	Delay
	move.l	a3,Combat_pal_ptr		; Normal palette
	jsr	Reset_current_RL
	jsr	Random			; Wait
	andi.w	#$0003,d0
	add.w	d0,d0
.Loop3:	jsr	Update_combat_screen
	dbra	d0,.Loop3
	jsr	Delete_COMOB		; Remove bolt
	dbra	d7,.Loop2
	jsr	Update_combat_screen	; Update
	lea.l	Combat_pal,a0		; Restore palette
	lea.l	Combat_backup_pal,a1
	moveq.l	#Pal_size-1,d7
.Loop4:	move.w	(a1)+,(a0)+
	dbra	d7,.Loop4
; ---------- Do damage ----------------------------
	movem.l	(sp)+,a0/a1		; Do all targets
	lea.l	Do_destruction_damage,a2
	jsr	Do_all_combat_targets
.Exit:	rts

; *** Whirlwind ***
CWhirlwind:
	jsr	Handle_spell		; Handle spell
	bne	.Exit
; ---------- Create whirlwind ---------------------
	move.l	a0,-(sp)
	moveq.l	#5,d0			; Get start coordinates
	moveq.l	#3,d1
	jsr	Calculate_3D_coordinates
	subq.w	#2,d1
	jsr	Add_COMOB			; Create whirlwind
	move.w	d0,COMOB_3D_X(a0)
	clr.w	COMOB_3D_Y(a0)
	move.w	d1,COMOB_3D_Z(a0)
	move.w	#48,COMOB_Display_width(a0)
	move.w	#96,COMOB_Display_height(a0)
	move.w	#32,COMOB_Source_width(a0)
	move.w	#64,COMOB_Source_height(a0)
	move.b	FXGFX_handle,COMOB_Gfx_handle(a0)
	move.l	#Whirlwind_FXGFX,COMOB_Gfx_base(a0)
	move.l	a0,a3
	move.l	(sp)+,a0
; ---------- Fade in as silhouette ----------------
	lea.l	Glow_colours,a4
	moveq.l	#21-1,d7
.Loop1:	move.w	(a4)+,COMOB_Colour(a3)	; Set colour
	bset	#COMOB_update,COMOB_Flags(a3)
	jsr	Update_combat_screen	; Show
	dbra	d7,.Loop1
	move.w	#-1,COMOB_Colour(a3)	; No silhouette
	move.l	a3,FXGFX_workspace		; Store
; ---------- Do -----------------------------------
	lea.l	.Do,a2
	jsr	Do_all_combat_targets
; ---------- Remove whirlwind ---------------------
	move.w	COMOB_Display_width(a3),d0	; Get shrink factors
	lsr.w	#3,d0
	move.w	COMOB_Display_height(a3),d1
	lsr.w	#3,d1
	moveq.l	#7-1,d7
.Loop2:	sub.w	d0,COMOB_Display_width(a3)	; Shrink
	sub.w	d1,COMOB_Display_height(a3)
	bset	#COMOB_update,COMOB_Flags(a3)
	jsr	Update_combat_screen	; Show
	dbra	d7,.Loop2
	move.l	a3,a0			; Remove
	jsr	Delete_COMOB
.Exit:	rts

; [ Do Whirlwind ]
;   IN : a0 - Pointer to victim's participant data (.l)
;        a1 - Pointer to caster's participant data (.l)
; No registers are restored
.Do:
; ---------- Move whirlwind to COMOB --------------
	move.l	FXGFX_workspace,a3
	jsr	Get_3D_part_coordinates	; Get target coordinates
	moveq.l	#0,d1
	move.w	COMOB_3D_X(a3),d3		; Get source coordinates
	moveq.l	#0,d4
	move.w	COMOB_3D_Z(a3),d5
	moveq.l	#Projectile_speed/2,d6	; Get movement vector
	jsr	Process_COMOB_vector
	move.w	d0,COMOB_3D_vector_X(a3)	; Set vector
	clr.w	COMOB_3D_vector_Y(a3)
	move.w	d2,COMOB_3D_vector_Z(a3)
	move.l	a0,a2			; Juggle registers
	move.l	a3,a0
	move.l	Part_COMOB_ptr(a2),a3
	moveq.l	#4,d0			; Show movement
	bra.s	.Entry3
.Loop3:	jsr	Update_combat_screen
	jsr	Circle_COMOB
.Entry3:	dbra	d7,.Loop3
	clr.w	COMOB_3D_vector_X(a0)	; Stop movement
	clr.w	COMOB_3D_vector_Z(a0)
	move.w	COMOB_3D_Z(a3),d0		; Move behind monster
	addq.w	#1,d0
	move.w	d0,COMOB_3D_Z(a0)
; ---------- Animate whirlwind & monster ----------
	lea.l	Oscillation,a4
	moveq.l	#4,d0
	moveq.l	#0,d1
	moveq.l	#8-1,d7
.Loop4:	jsr	Update_combat_screen	; Show
	move.b	0(a4,d1.w),d2		; Oscillate
	ext.w	d2
	asl.w	#1,d2
	add.w	d2,COMOB_Display_width(a0)
	add.w	d2,COMOB_Display_width(a3)
	move.b	1(a4,d1.w),d2
	ext.w	d2
	asl.w	#1,d2
	add.w	d2,COMOB_Display_height(a0)
	add.w	d2,COMOB_Display_height(a3)
	Set_anim	Hit_anim,a2		; Hit !
	jsr	Circle_COMOB		; Animate whirlwind
	bset	#COMOB_update,COMOB_Flags(a3)
	addq.w	#1,d1			; Increase index
	andi.w	#$0007,d1
	dbra	d7,.Loop4
; ---------- Do damage to monster -----------------
	move.l	a2,a0
	jsr	Do_destruction_damage
.Exit2:	rts

; *** Firebeam ***
CFirebeam:
	jsr	Handle_spell		; Handle spell
	bne	.Exit
	move.w	#$b20,d0			; Fade to fire
	moveq.l	#3,d7
	jsr	Fade_combat_palette
	lea.l	.Do,a2			; Do all targets
	jsr	Do_all_combat_targets
	jsr	Restore_combat_palette	; Fade back
.Exit:	rts

; [ Do Firebeam ]
;   IN : a0 - Pointer to victim's participant data (.l)
;        a1 - Pointer to caster's participant data (.l)
; No registers are restored
.Do:
	movem.l	a0/a1,-(sp)
; ---------- Create firebeam ----------------------
	exg	a1,a0
	jsr	Determine_COMOB_flip	; Determine flip
	smi	d1
	moveq.l	#40,d0			; Create first
	jsr	Prepare_COMOB_movement
	move.l	a0,FXGFX_workspace
	tst.b	d1			; Left or right ?
	bne.s	.Right
	bset	#0,COMOB_Mirror_flags(a0)	; Flip
.Right:	sub.w	#8,COMOB_3D_Y(a0)		; Adjust initial Y-coordinate
	move.w	#16,COMOB_Display_width(a0)	; Set dimensions
	move.w	#16,COMOB_Display_height(a0)
	move.w	#16,COMOB_Source_width(a0)	; Set other data
	move.w	#16,COMOB_Source_height(a0)
	move.b	FXGFX_handle,COMOB_Gfx_handle(a0)
	move.l	#Fireball_fro_FXGFX,COMOB_Gfx_base(a0)
	moveq.l	#4,d0			; Create others
	lea.l	.Modify,a0
	jsr	Make_COMOB_chain
	cmp.w	#4,d7			; Less steps
	bmi.s	.Ok
	subq.w	#3,d7
.Ok:	moveq.l	#8,d0			; Move
	moveq.l	#4,d1
	jsr	Move_COMOBs_to_target
	movem.l	(sp)+,a0/a1		; Burn
	jsr	Burn_participant
	jsr	Do_destruction_damage
.Exit2:	rts

.Modify:
	move.w	COMOB_3D_vector_X(a1),d0	; Move along vector
	move.w	COMOB_3D_vector_Y(a1),d1
	move.w	COMOB_3D_vector_Z(a1),d2
	subq.w	#2,d1			; Adjust for growth
	add.w	d0,COMOB_3D_X(a0)		; Store coordinates
	add.w	d1,COMOB_3D_Y(a0)
	add.w	d2,COMOB_3D_Z(a0)
	addq.w	#4,COMOB_Display_width(a0)	; Grow bigger
	addq.w	#4,COMOB_Display_height(a0)
	addq.w	#1,COMOB_Frame(a0)		; Next frame
	rts

; *** Fireball ***
CFireball:
	jsr	Handle_spell		; Handle spell
	bne	.Exit
	move.w	#$b20,d0			; Fade to fire
	moveq.l	#3,d7
	jsr	Fade_combat_palette
	lea.l	.Do,a2			; Do all targets
	jsr	Do_all_combat_targets
	jsr	Restore_combat_palette	; Fade back
.Exit:	rts

; [ Do Fireball ]
;   IN : a0 - Pointer to victim's participant data (.l)
;        a1 - Pointer to caster's participant data (.l)
; No registers are restored
.Do:
	movem.l	a0/a1,-(sp)
; ---------- Create fireball ----------------------
	jsr	Determine_COMOB_flip	; Determine flip
	smi	d6
	moveq.l	#40,d0			; Prepare COMOB
	exg	a1,a0
	jsr	Prepare_COMOB_movement
	move.l	a0,FXGFX_workspace
	move.w	#40,COMOB_Display_width(a0)	; Set dimensions
	move.w	#40,COMOB_Display_height(a0)
	tst.b	d6			; Left or right ?
	beq.s	.Right
	bset	#0,COMOB_Mirror_flags(a0)	; Flip
.Right:	move.w	#16,COMOB_Source_width(a0)	; Set other stuff
	move.w	#16,COMOB_Source_height(a0)
	move.b	FXGFX_handle,COMOB_Gfx_handle(a0)
	move.l	#Fireball_fro_FXGFX,COMOB_Gfx_base(a0)
	moveq.l	#8,d0			; Move
	moveq.l	#1,d1
	jsr	Move_COMOBs_to_target
; ---------- Burn ---------------------------------
	movem.l	(sp)+,a0/a1
	jsr	Burn_participant
	jsr	Do_destruction_damage
.Exit2:	rts

; *** Firestorm ***
CFirestorm:
	jsr	Handle_spell		; Handle spell
	bne	.Exit
	movem.l	a0/a1,-(sp)		; Save
; ---------- Glow up ------------------------------
	move.w	#$b20,d0			; Fade to fire
	moveq.l	#3,d7
	jsr	Fade_combat_palette
; ---------- Prepare firepillars ------------------
	move.l	Part_target(a0),d0		; Get row number
	jsr	Get_target_row_number
	move.w	d0,d1			; Get Z-coordinate
	moveq.l	#0,d0
	jsr	Calculate_3D_coordinates
	move.w	d1,d2
	subq.w	#1,d2
	move.w	#-80,d0
	moveq.l	#0,d1
	move.w	#200,d3
	moveq.l	#0,d4
	move.w	d2,d5
	jsr	Add_COMOB			; Create first
	move.w	d3,COMOB_3D_X(a0)		; Set coordinates
	move.w	d4,COMOB_3D_Y(a0)
	move.w	d5,COMOB_3D_Z(a0)
	moveq.l	#20,d6			; Process vector
	jsr	Process_COMOB_vector
	move.w	d0,COMOB_3D_vector_X(a0)	; Set vector
	move.w	d1,COMOB_3D_vector_Y(a0)
	move.w	d2,COMOB_3D_vector_Z(a0)
	move.l	a0,FXGFX_workspace
	move.w	#32,COMOB_Display_width(a0)	; Set dimensions
	move.w	#32,COMOB_Display_height(a0)
	move.w	#16,COMOB_Source_width(a0)	; Set other data
	move.w	#32,COMOB_Source_height(a0)
	move.b	FXGFX_handle,COMOB_Gfx_handle(a0)
	move.l	#Firepillar_FXGFX,COMOB_Gfx_base(a0)
	moveq.l	#4,d0			; Create others
	lea.l	.Modify,a0
	jsr	Make_COMOB_chain
	cmp.w	#4,d7			; Less steps
	bmi.s	.Ok
	subq.w	#3,d7
; ---------- Move ---------------------------------
.Ok:	moveq.l	#8,d0
	bra.s	.Entry1
.Loop1:	jsr	Update_combat_screen	; Show
	lea.l	FXGFX_workspace,a1		; Animate COMOBs
	moveq.l	#4-1,d6
.Loop2:	move.l	(a1)+,a0
	jsr	Circle_COMOB
	dbra	d6,.Loop2
.Entry1:	dbra	d7,.Loop1
; ---------- Remove -------------------------------
	moveq.l	#8,d0
	moveq.l	#4-1,d7
.Loop4:	lea.l	FXGFX_workspace,a1		; Shrink COMOBs
	moveq.l	#32/8,d1
	moveq.l	#7-1,d6
.Loop5:	move.l	(a1)+,a0
	move.w	COMOB_Display_height(a0),d2
	sub.w	d1,d2
	move.w	d2,COMOB_Display_height(a0)
	jsr	Circle_COMOB		; Animate COMOBs
	addq.w	#32/8,d1
	dbra	d6,.Loop5
	jsr	Update_combat_screen	; Show
	dbra	d7,.Loop4
	lea.l	FXGFX_workspace,a1		; Destroy COMOBs
	moveq.l	#4-1,d7
.Loop6:	move.l	(a1)+,a0
	jsr	Delete_COMOB
	dbra	d7,.Loop6
; ---------- Burn ---------------------------------
	jsr	Restore_combat_palette	; Fade back
	movem.l	(sp)+,a0/a1		; Do all targets
	lea.l	.Do,a2
	jsr	Do_all_combat_targets
	jsr	Update_combat_screen	; Update
.Exit:	rts

.Modify:
	move.w	COMOB_3D_vector_X(a0),d0	; Move along vector
	add.w	d0,COMOB_3D_X(a0)		; Store coordinates
	add.w	#32,COMOB_Display_height(a0)	; Grow taller
	addq.w	#1,COMOB_Frame(a0)		; Next frame
	jsr	Random			; Random Z displacement
	andi.w	#$003f,d0
	subi.w	#32,d0
	add.w	d0,COMOB_3D_Z(a0)
	rts

; [ Do Firestorm damage ]
;   IN : a0 - Pointer to victim's participant data (.l)
;        a1 - Pointer to caster's participant data (.l)
; No registers are restored
.Do:
	jsr	Burn_participant
	jsr	Do_destruction_damage
.Exit2:	rts

; *** Firecolumn ***
CFirecolumn:
	jsr	Handle_spell		; Handle spell
	bne	.Exit
	movem.l	a0/a1,-(sp)
	move.l	a0,a1
	move.w	#$b20,d0			; Fade to fire
	moveq.l	#3,d7
	jsr	Fade_combat_palette
; ---------- Create firepillar --------------------
	jsr	Add_COMOB			; Make firepillar
	clr.w	COMOB_3D_X(a0)		; Set coordinates
	clr.w	COMOB_3D_Y(a0)
	cmp.b	#1,Part_type(a1)		; Party or monster ?
	bne.s	.Monster
	move.w	#64,COMOB_3D_Z(a0)
	bra.s	.Go_on
.Monster:	move.w	#-100,COMOB_3D_Z(a0)
.Go_on:	move.w	#32,COMOB_Display_width(a0)	; Set other parameters
	move.w	#16,COMOB_Source_width(a0)
	move.w	#32,COMOB_Source_height(a0)
	move.b	FXGFX_handle,COMOB_Gfx_handle(a0)
	move.l	#Firepillar_FXGFX,COMOB_Gfx_base(a0)
	moveq.l	#8,d0			; Grow
	moveq.l	#16,d1
	moveq.l	#32,d2
	moveq.l	#30,d6
	bra.s	.Entry1
.Loop1:	jsr	Update_combat_screen	; Show
	jsr	Circle_COMOB		; Animate
	addq.w	#4,d1			; Grow
	addq.w	#6,d2
.Entry1:	move.w	d1,COMOB_Display_width(a0)	; Set size
	move.w	d2,COMOB_Display_height(a0)
	dbra	d6,.Loop1
; ---------- Remove fire-column -------------------
	lea.l	Glow_colours+21*2,a1
	moveq.l	#21-1,d7
.Loop7:	move.w	-(a1),COMOB_Colour(a0)	; Set colour
	addq.w	#3,COMOB_Display_width(a0)	; Shrink
	subq.w	#3,COMOB_Display_height(a0)
	jsr	Circle_COMOB		; Animate
	jsr	Update_combat_screen	; Show
	dbra	d7,.Loop7
	jsr	Delete_COMOB		; Remove
; ---------- Burn ---------------------------------
	jsr	Restore_combat_palette	; Fade back
	movem.l	(sp)+,a0/a1		; Do all targets
	lea.l	.Do,a2
	jsr	Do_all_combat_targets
	jsr	Update_combat_screen	; Update
.Exit:	rts

; [ Do Firecolumn damage ]
;   IN : a0 - Pointer to victim's participant data (.l)
;        a1 - Pointer to caster's participant data (.l)
; No registers are restored
.Do:
	jsr	Burn_participant
	jsr	Do_destruction_damage
.Exit2:	rts

; *** Waterfall ***
CWaterfall:
	jsr	Handle_spell		; Handle spell
	bne	.Exit
	lea.l	.Do,a2			; Do all targets
	jsr	Do_all_combat_targets
.Exit:	rts

; [ Do Waterfall ]
;   IN : a0 - Pointer to victim's participant data (.l)
;        a1 - Pointer to caster's participant data (.l)
; No registers are restored
.Do:
; ---------- Create watermass ---------------------
	move.l	a0,a2
	move.l	Part_COMOB_ptr(a0),a3
	jsr	Add_COMOB
	move.w	COMOB_3D_X(a3),COMOB_3D_X(a0)
	move.w	#88,COMOB_3D_Y(a0)
	move.w	COMOB_3D_Z(a3),d0
	subq.w	#1,d0
	move.w	d0,COMOB_3D_Z(a0)
	move.w	#32,COMOB_Display_width(a0)
	move.w	#32,COMOB_Display_height(a0)
	move.w	#64,COMOB_Source_width(a0)
	move.w	#32,COMOB_Source_height(a0)
	move.b	FXGFX_handle,COMOB_Gfx_handle(a0)
	move.l	#Watermass_FXGFX,COMOB_Gfx_base(a0)
; ---------- Fade water in as silhouette ----------
	lea.l	Glow_colours,a3
	moveq.l	#21-1,d7
.Loop1:	move.w	(a3)+,COMOB_Colour(a0)	; Set stone colour
	bset	#COMOB_update,COMOB_Flags(a0)
	jsr	Update_combat_screen	; Show
	dbra	d7,.Loop1
	move.w	#-1,COMOB_Colour(a0)	; No silhouette
; ---------- Drop watermass -----------------------
	move.w	#-1,COMOB_3D_vector_Y(a0)	; Down
	moveq.l	#11-1,d7
.Loop2:	jsr	Update_combat_screen	; Show
	subq.w	#1,COMOB_3D_vector_Y(a0)	; Faster!
	addq.w	#2,COMOB_Display_height(a0)	; Longer!
	subq.w	#2,COMOB_3D_Y(a0)
	dbra	d7,.Loop2
	clr.w	COMOB_3D_vector_Y(a0)	; Squash
	moveq.l	#15-1,d7
.Loop3:	jsr	Update_combat_screen	; Show
	move.w	COMOB_Display_height(a0),d1	; Flatter!
	subi.w	#11,d1
	cmp.w	#3,d1
	bmi.s	.Skip
	move.w	d1,COMOB_Display_height(a0)
.Skip:	add.w	#11,COMOB_Display_width(a0)	; Wider!
	bset	#COMOB_update,COMOB_Flags(a0)
	dbra	d7,.Loop3
	jsr	Delete_COMOB		; Remove watermass
; ---------- Do damage to monster -----------------
	move.l	a2,a0
	jsr	Do_destruction_damage
.Exit2:	rts

; *** Iceball ***
CIceball:
	jsr	Handle_spell		; Handle spell
	bne	.Exit
	move.w	#$019,d0			; Fade to ice
	moveq.l	#2,d7
	jsr	Fade_combat_palette
	lea.l	.Do,a2			; Do all targets
	jsr	Do_all_combat_targets
	jsr	Restore_combat_palette	; Fade back
.Exit:	rts

; [ Do Iceball ]
;   IN : a0 - Pointer to victim's participant data (.l)
;        a1 - Pointer to caster's participant data (.l)
; No registers are restored
.Do:
	movem.l	a0/a1,-(sp)
; ---------- Create iceball -----------------------
	jsr	Determine_COMOB_flip	; Determine flip
	smi	d6
	moveq.l	#40,d0			; Prepare COMOB
	exg	a1,a0
	jsr	Prepare_COMOB_movement
	move.l	a0,FXGFX_workspace
	move.w	#40,COMOB_Display_width(a0)	; Set dimensions
	move.w	#40,COMOB_Display_height(a0)
	tst.b	d6			; Left or right ?
	beq.s	.Right
	bset	#0,COMOB_Mirror_flags(a0)	; Flip
.Right:	move.w	#16,COMOB_Source_width(a0)	; Set other stuff
	move.w	#16,COMOB_Source_height(a0)
	move.b	FXGFX_handle,COMOB_Gfx_handle(a0)
	move.l	#Iceball_FXGFX,COMOB_Gfx_base(a0)
	moveq.l	#0,d0			; Move
	moveq.l	#1,d1
	jsr	Move_COMOBs_to_target
; ----------- Freeze ------------------------------
	movem.l	(sp)+,a0/a1
	jsr	Freeze_participant
	jsr	Do_destruction_damage
.Exit2:	rts

; *** Icestorm ***
CIcestorm:
	jsr	Handle_spell		; Handle spell
	bne	.Exit
	movem.l	a0/a1,-(sp)		; Save
; ---------- Glow up ------------------------------
	move.w	#$019,d0			; Fade to ice
	moveq.l	#2,d7
	jsr	Fade_combat_palette
; ---------- Prepare icepillars -------------------
	move.l	Part_target(a0),d0		; Get row number
	jsr	Get_target_row_number
	move.w	d0,d1			; Get Z-coordinate
	moveq.l	#0,d0
	jsr	Calculate_3D_coordinates
	move.w	d1,d2
	subq.w	#1,d2
	move.w	#-80,d0
	moveq.l	#0,d1
	move.w	#200,d3
	moveq.l	#0,d4
	move.w	d2,d5
	jsr	Add_COMOB			; Create first
	move.w	d3,COMOB_3D_X(a0)		; Set coordinates
	move.w	d4,COMOB_3D_Y(a0)
	move.w	d5,COMOB_3D_Z(a0)
	moveq.l	#20,d6			; Process vector
	jsr	Process_COMOB_vector
	move.w	d0,COMOB_3D_vector_X(a0)	; Set vector
	move.w	d1,COMOB_3D_vector_Y(a0)
	move.w	d2,COMOB_3D_vector_Z(a0)
	move.l	a0,FXGFX_workspace
	move.w	#24,COMOB_Display_width(a0)	; Set dimensions
	move.w	#24,COMOB_Display_height(a0)
	move.w	#16,COMOB_Source_width(a0)	; Set other data
	move.w	#32,COMOB_Source_height(a0)
	move.b	FXGFX_handle,COMOB_Gfx_handle(a0)
	move.l	#Icepillar_FXGFX,COMOB_Gfx_base(a0)
	moveq.l	#4,d0			; Create others
	lea.l	.Modify,a0
	jsr	Make_COMOB_chain
	cmp.w	#4,d7			; Less steps
	bmi.s	.Ok
	subq.w	#3,d7
; ---------- Move ---------------------------------
.Ok:	bra.s	.Entry1
.Loop1:	jsr	Update_combat_screen	; Show
.Entry1:	dbra	d7,.Loop1
; ---------- Remove -------------------------------
	moveq.l	#4-1,d7
.Loop4:	lea.l	FXGFX_workspace,a1		; Shrink COMOBs
	moveq.l	#24/8,d1
	moveq.l	#7-1,d6
.Loop5:	move.l	(a1)+,a0
	move.w	COMOB_Display_height(a0),d2
	sub.w	d1,d2
	move.w	d2,COMOB_Display_height(a0)
	addq.w	#24/8,d1
	dbra	d6,.Loop5
	jsr	Update_combat_screen	; Show
	dbra	d7,.Loop4
	lea.l	FXGFX_workspace,a1		; Destroy COMOBs
	moveq.l	#4-1,d7
.Loop6:	move.l	(a1)+,a0
	jsr	Delete_COMOB
	dbra	d7,.Loop6
; ---------- Freeze -------------------------------
	jsr	Restore_combat_palette	; Fade back
	movem.l	(sp)+,a0/a1		; Do all targets
	lea.l	.Do,a2
	jsr	Do_all_combat_targets
	jsr	Update_combat_screen	; Update
.Exit:	rts

.Modify:
	move.w	COMOB_3D_vector_X(a0),d0	; Move along vector
	add.w	d0,COMOB_3D_X(a0)		; Store coordinates
	add.w	#24,COMOB_Display_height(a0)	; Grow taller
	move.w	COMOB_Frame(a0),d0		; Next frame
	addq.w	#1,d0
	andi.w	#$0001,d0
	move.w	d0,COMOB_Frame(a0)
	jsr	Random			; Random Z displacement
	andi.w	#$003f,d0
	subi.w	#32,d0
	add.w	d0,COMOB_3D_Z(a0)
	rts

; [ Do Icestorm damage ]
;   IN : a0 - Pointer to victim's participant data (.l)
;        a1 - Pointer to caster's participant data (.l)
; No registers are restored
.Do:
	jsr	Freeze_participant
	jsr	Do_destruction_damage
.Exit2:	rts

; *** Iceshower ***
CIceshower:
	jsr	Handle_spell		; Handle spell
	bne	.Exit
	movem.l	a0/a1,-(sp)
	move.w	#$019,d0			; Fade to ice
	moveq.l	#2,d7
	jsr	Fade_combat_palette
; ---------- Create ice-balls ---------------------
	lea.l	FXGFX_workspace,a2
	moveq.l	#8-1,d7
.Loop1:	jsr	Add_COMOB			; Create
	move.l	a0,(a2)+
	jsr	Random			; Set X- and Z-coordinates
	mulu.w	#Combat_row_width,d0
	swap	d0
	subi.w	#Combat_row_width/2,d0
	move.w	d0,COMOB_3D_X(a0)
	jsr	Random
	andi.w	#$007f,d0
	neg.w	d0
	move.w	d0,COMOB_3D_Z(a0)
	jsr	Random			; Set Y-coordinate
	andi.w	#$003f,d0
	addi.w	#10,d0
	move.w	d0,COMOB_3D_Y(a0)
	jsr	Random			; Set Z-vector
	andi.w	#$000f,d0
	addi.w	#24,d0
	move.w	d0,COMOB_3D_vector_Z(a0)
	jsr	Random			; Set size
	andi.w	#$000f,d0
	addi.w	#16,d0
	move.w	d0,COMOB_Display_width(a0)
	move.w	d0,COMOB_Display_height(a0)
	jsr	Random			; Set mirror flags
	btst	#5,d0
	beq.s	.Zero
	bset	#0,COMOB_Mirror_flags(a0)
.Zero:	move.w	#16,COMOB_Source_width(a0)	; Set other data
	move.w	#16,COMOB_Source_height(a0)
	move.b	FXGFX_handle,COMOB_Gfx_handle(a0)
	move.l	#Iceball_FXGFX,COMOB_Gfx_base(a0)
	dbra	d7,.Loop1
; ---------- Show ---------------------------------
	move.w	#$019,d0			; Fade to ice
	moveq.l	#2,d7
	jsr	Fade_combat_palette
	moveq.l	#24-1,d6
.Loop2:	jsr	Update_combat_screen	; Show
	dbra	d6,.Loop2
; ---------- Remove ice-balls ---------------------
	lea.l	FXGFX_workspace,a1
	moveq.l	#8-1,d7
.Loop3:	move.l	(a1)+,a0
	jsr	Delete_COMOB
	dbra	d7,.Loop3
; ----------- Freeze ------------------------------
	jsr	Restore_combat_palette	; Fade back
	movem.l	(sp)+,a0/a1
	lea.l	.Do,a2			; Do all targets
	jsr	Do_all_combat_targets
	jsr	Update_combat_screen	; Update
.Exit:	rts

; [ Do Iceshower effects ]
;   IN : a0 - Pointer to victim's participant data (.l)
;        a1 - Pointer to caster's participant data (.l)
; No registers are restored
.Do:
	jsr	Freeze_participant
	jmp	Do_destruction_damage

;*****************************************************************************
; [ Spell target handlers - COMBAT / PARTY ]
;   IN : a0 - Pointer to casting participant data (.l)
; No registers are restored
;*****************************************************************************
Member_target:
	move.w	#235,ItemSelect_prompt	; "Which party member ?"
	jsr	Select_party_member
	tst.w	d0			; Any target ?
	bmi.s	.Exit
	move.b	#Friend_targmode,Part_target+6(a0)	; Enter data
	moveq.l	#0,d1
	bset	d0,d1
	move.l	d1,Part_target(a0)
	jsr	Enter_action
.Exit:	rts

Monster_target:
	move.w	#236,ItemSelect_prompt	; "Which monster ?"
	jsr	Select_monster
	tst.w	d0			; Any target ?
	bmi.s	.Exit
	move.b	#Enemy_targmode,Part_target+6(a0)	; Enter data
	moveq.l	#0,d1
	bset	d0,d1
	move.l	d1,Part_target(a0)
	jsr	Enter_action
.Exit:	rts

Member_row_target:
	move.w	#238,ItemSelect_prompt	; "Which member row ?"
	jsr	Select_member_row
	tst.w	d0			; Any target ?
	bmi.s	.Exit
	move.b	#Friend_row_targmode,Part_target+6(a0)	; Enter data
	move.l	#%00000000000000000000000000111111,d1
	mulu.w	#6,d0
	lsl.l	d0,d1
	move.l	d1,Part_target(a0)
	jsr	Enter_action
.Exit:	rts

Monster_row_target:
	move.w	#239,ItemSelect_prompt	; "Which monster row ?"
	jsr	Select_monster_row
	tst.w	d0			; Any target ?
	bmi.s	.Exit
	move.b	#Enemy_row_targmode,Part_target+6(a0)	; Enter data
	move.l	#%00000000000000000000000000111111,d1
	mulu.w	#6,d0
	lsl.l	d0,d1
	move.l	d1,Part_target(a0)
	jsr	Enter_action
.Exit:	rts

; ADVANCED: All enemies in close range (magic sword attack)
Close_range_enemies_target:
	jsr	Get_closerange_targets	; Any targets ?
	tst.l	d0
	bne.s	.Yes
	move.w	#206,d0			; No -> "Out of reach !"
	jsr	Do_prompt
	bra.s	.Exit
.Yes:	move.b	#Enemy_row_targmode,Part_target+6(a0)	; Enter data
	move.l	d0,Part_target(a0)
	jsr	Enter_action
.Exit:	rts

All_members_target:
	move.b	#All_friends_targmode,Part_target+6(a0)	; Enter data
	move.l	#Combat_party_mask,Part_target(a0)
	jmp	Enter_action

All_monsters_target:
	move.b	#All_enemies_targmode,Part_target+6(a0)	; Enter data
	move.l	#Combat_monster_mask,Part_target(a0)
	jmp	Enter_action

Enter_action:
	move.w	Selected_class,d0		; Enter more data
	move.b	d0,Part_target+4(a0)
	move.w	Selected_spell,d0
	move.b	d0,Part_target+5(a0)
	rts

;*****************************************************************************
; [ Determine COMOB X-mirroring ]
;   IN : a0 - Pointer to source participant data (.l)
;        a1 - Pointer to target participant data (.l)
;  OUT : pl - Facing right
;        mi - Facing left
; All registers are restored
;*****************************************************************************
Determine_COMOB_flip:
	movem.l	d0-d5/a0,-(sp)
	moveq.l	#Combat_proj_log,d4
	jsr	Get_3D_part_coordinates	; Get source & target
	move.w	d0,d3			;  coordinates
	move.w	d2,d5
	move.l	a1,a0
	jsr	Get_3D_part_coordinates
	move.w	d2,d1			; Calculate Z-vector
	sub.w	d5,d1
	ext.l	d0			; Project target coordinates
	addi.w	#Combat_proj_factor,d2
	bne.s	.Notzero1
	moveq.l	#1,d2
.Notzero1:	asl.l	d4,d0
	divs.w	d2,d0
	ext.l	d3			; Project source coordinates
	addi.w	#Combat_proj_factor,d5
	bne.s	.Notzero2
	moveq.l	#1,d5
.Notzero2:	asl.l	d4,d3
	divs.w	d5,d3
	tst.w	d1			; To or fro ?
	bmi.s	.Fro
	exg.l	d0,d3			; To -> Swap
.Fro:	cmp.w	d0,d3			; Which direction ?
	movem.l	(sp)+,d0-d5/a0
	rts

;*****************************************************************************
; [ Prepare COMOB for movement through combat area ]
;   IN : d0 - Movement speed (.w)
;        a0 - Pointer to source participant data (.l)
;        a1 - Pointer to target participant data (.l)
;  OUT : a0 - Pointer to prepared COMOB data (.l)
;        d7 - Number of steps (.w)
; Changed registers : d7,a0
;*****************************************************************************
Prepare_COMOB_movement:
	movem.l	d0-d6,-(sp)
	move.w	d0,d6			; Save
	jsr	Get_3D_part_coordinates	; Get source coordinates
	move.w	d0,d3
	move.w	d1,d4
	move.w	d2,d5
	move.l	a1,a0			; Get target coordinates
	jsr	Get_3D_part_coordinates
	jsr	Add_COMOB			; Create COMOB
	move.w	d3,COMOB_3D_X(a0)		; Set coordinates
	move.w	d4,COMOB_3D_Y(a0)
	move.w	d5,COMOB_3D_Z(a0)
	jsr	Process_COMOB_vector	; Process vector
	move.w	d0,COMOB_3D_vector_X(a0)	; Set vector
	move.w	d1,COMOB_3D_vector_Y(a0)
	move.w	d2,COMOB_3D_vector_Z(a0)
.Exit:	movem.l	(sp)+,d0-d6
	rts

;*****************************************************************************
; [ Process COMOB movement vector ]
;   IN : d0 - Target X-coordinate (.w)
;        d1 - Target Y-coordinate (.w)
;        d2 - Target Z-coordinate (.w)
;        d3 - Source X-coordinate (.w)
;        d4 - Source Y-coordinate (.w)
;        d5 - Source Z-coordinate (.w)
;        d6 - Movement speed (.w)
;  OUT : d0 - Movement vector X-component (.w)
;        d1 - Movement vector Y-component (.w)
;        d2 - Movement vector Z-component (.w)
;        d7 - Number of steps (.w)
; Changed registers : d0,d1,d2,d7
;*****************************************************************************
Process_COMOB_vector:
	movem.l	d3-d5,-(sp)
	sub.w	d3,d0			; Calculate total vector
	sub.w	d4,d1
	sub.w	d5,d2
	move.w	d0,d3
	move.w	d1,d4
	move.w	d2,d5
	muls.w	d0,d0			; Calculate total length
	muls.w	d1,d1
	muls.w	d2,d2
	add.l	d1,d0
	add.l	d2,d0
	bne.s	.Notzero1			; Zero ?
	moveq.l	#0,d0			; Yes
	moveq.l	#0,d1
	moveq.l	#0,d2
	moveq.l	#0,d7
	bra.s	.Exit
.Notzero1:	jsr	Square_root		; No
	muls.w	d6,d3			; Calculate movement vector
	muls.w	d6,d4
	muls.w	d6,d5
	divs.w	d0,d3
	divs.w	d0,d4
	divs.w	d0,d5
	ext.l	d0			; Calculate number of steps
	divu.w	d6,d0
	move.w	d0,d7			; Any ?
	bne.s	.Notzero2
	moveq.l	#1,d7			; No -> At least one
.Notzero2:	move.w	d3,d0			; Copy to output
	move.w	d4,d1
	move.w	d5,d2
.Exit:	movem.l	(sp)+,d3-d5
	rts

;*****************************************************************************
; [ Get 3D participant coordinates ]
;   IN : a0 - Pointer to participant data (.l)
;  OUT : d0 - 3D X-coordinate (.w)
;        d1 - 3D Y-coordinate (.w)
;        d2 - 3D Z-coordinate (.w)
; Changed registers : d0,d1
;*****************************************************************************
Get_3D_part_coordinates:
	move.l	a1,-(sp)
	cmp.b	#1,Part_type(a0)		; Party or monster ?
	bne.s	.Monster
; ---------- Party --------------------------------
	move.w	Part_X(a0),d0		; Convert tactical coordinates
	moveq.l	#-1,d1
	jsr	Calculate_3D_coordinates
	move.w	d1,d2
	addq.w	#1,d2			; In front !
	Get	Part_handle(a0),a1		; Get character's race
	moveq.l	#0,d1
	move.b	Char_race(a1),d1
	Free	Part_handle(a0)
	lea.l	Race_heights,a1		; Get height of race
	add.w	d1,d1
	move.w	0(a1,d1.w),d1
	mulu.w	#Projectile_height,d1	; Adjust
	divu.w	(a1),d1
	bra.s	.Exit
; ---------- Monster ------------------------------
.Monster:	move.l	Part_COMOB_ptr(a0),a1	; Convert COMOB data
	move.w	COMOB_3D_X(a1),d0
	move.w	COMOB_Display_height(a1),d1
	lsr.w	#1,d1
	move.w	COMOB_3D_Z(a1),d2
	subq.w	#1,d2			; In front !
.Exit:	move.l	(sp)+,a1
	rts

;*****************************************************************************
; [ Calculate 3D coordinates ]
;   IN : d0 - Tactical X-coordinate (.w)
;        d1 - Tactical Y-coordinate (.w)
;  OUT : d0 - 3D X-coordinate (.w)
;        d1 - 3D Z-coordinate (.w)
; Changed registers : d0,d1
;*****************************************************************************
Calculate_3D_coordinates:
	cmp.w	#-1,d1			; Monster or party ?
	beq	.Party
	subq.w	#3,d0			; Calculate X
	add.w	d0,d0
	addq.w	#1,d0
	mulu.w	#40/2,d0
	subq.w	#2,d1			; Calculate Z
	neg.w	d1
	asl.w	#7,d1
	bra.s	.Exit
.Party:	subq.w	#3,d0			; Calculate X
	add.w	d0,d0
	addq.w	#1,d0
	lsl.w	#3,d0
	move.w	#-256,d1			; Set Z
.Exit:	rts

;*****************************************************************************
; [ Update combat screen display ]
; All registers are restored
;*****************************************************************************
Update_combat_screen:
	jsr	Draw_tactic_window
	jsr	Show_active_member
	jsr	Draw_tactic_icons
	jmp	Switch_screens

;*****************************************************************************
; [ Wait for end of combat animation ]
;   IN : a0 - Pointer to participant data (.l)
; All registers are restored
;*****************************************************************************
Wait_4_animation:
	cmp.b	#2,Part_type(a0)		; Is monster ?
	bne.s	.Exit
.Wait:	tst.b	Part_anim(a0)		; Animation ended ?
	beq.s	.Exit
	jsr	Update_combat_screen	; No -> Update
	bra.s	.Wait
.Exit:	rts

;*****************************************************************************
; [ Do destruction damage ]
;   IN : a0 - Pointer to victim's participant data (.l)
;        a1 - Pointer to caster's participant data (.l)
; All registers are restored
; Notes :
;   - The minimum and maximum damage percentages are retrieved from a table.
;*****************************************************************************
Do_destruction_damage:
	movem.l A2/A0/D4/D3/D2/D1/D0,-(SP)
	jsr	Handle_magical_defense	; Defend ?
	bne	.Exit
	lea.l	Destruction_table,a2	; No -> Get destruction data
	move.w	Selected_spell,d0
	subi.w	#15,d0
	; ADVANCED CHANGES - START
	; spell dmg increase flags
	movem.l A0/D0,-(SP)
	move.b Casting_handle,D0
	move.b D0,D1
	jsr Claim_pointer
	movea.l D0,A0 ; Now A0 is the character data
	move.b D1,D0
	move.b ($0012,A0),D1 ; battle flags
	move.w ($0072,A0),D2 ; possible min additional damage
	move.w ($0074,A0),D3 ; possible max additional damage
	move.w ($0078,A0),D4 ; percentage damage bonus
	jsr Free_pointer
	movem.l (SP)+,D0/A0
	cmpi.w #4,D0 ; earth spells indices are 0..3
	bpl.b .LAB_NO_EARTH_SPELL_DMG_BOOST
	btst.l #4,D1 ; increase earth spell dmg flag
	beq.b .LAB_SPELL_DMG_BOOST_END
	add.w #12,D0 ; spell index +12 (earth spell index -> ice spell index)
	bra.b .LAB_SPELL_DMG_BOOST_END
.LAB_NO_EARTH_SPELL_DMG_BOOST:
	cmpi.w #8,D0 ; wind spells indices are 4..7
	bpl.b .LAB_NO_WIN_SPELL_DMG_BOOST
	btst.l #5,D1 ; increase wind spell dmg flag
	beq.b .LAB_SPELL_DMG_BOOST_END
	addq.w #8,D0 ; spell index +8 (wind spell index -> ice spell index)
	bra.b .LAB_SPELL_DMG_BOOST_END
.LAB_NO_WIN_SPELL_DMG_BOOST:
	cmpi.w #12,D0 ; fire spells indices are 8..11
	bpl.b .LAB_SPELL_DMG_BOOST_END
	btst.l #6,D1 ; increase fire spell dmg flag
	beq.b .LAB_SPELL_DMG_BOOST_END
	addq.w #4,D0 ; spell index +4 (fire spell index -> ice spell index)
.LAB_SPELL_DMG_BOOST_END:
	lsl.w	#2,d0
	add.w	d0,a2
	move.w	2(a2),d1			; Calculate difference
	add.w D2,D1 ; add min damage bonus to max value as well
	add.w D3,D1 ; add max damage bonus
	move.w (A2),D3 ; min damage
	add.w D2,D3 ; add min damage bonus
	sub.w D3,D1 ; min damage (sub to get value range)
	jsr	Random			; Get random damage
	mulu.w	d1,d0
	swap	d0
	add.w D3,D0 ; add random (max - min) to min damage
	tst.w D4
	beq.b .LAB_CalcSpellDamage
	cmpi.w #-99,D4
	bpl.b .LAB_CalcPercDamage
	moveq #1,D0 ; limit to 1 damage if perc value is -100% or lower
	bra.b .LAB_CalcSpellDamage
.LAB_CalcPercDamage:
	add.w #100,D4
	mulu.w D4,D0
	divu.w #100,D0
	bgt.b .LAB_CalcSpellDamage
	moveq #1,D0 ; deal at least 1 damage
.LAB_CalcSpellDamage:
	jsr FUN_CalculateSpellDamage
	cmp.b	#1,Part_type(a0)		; Party or monster ?
	bne.s	.Monster
	jsr	Do_combat_damage		; Party
	bra.s	.Done
.Monster:	jsr	Do_damage_to_monster	; Monster
.Done:	move.l	a1,a0			; Process damage
	jsr	Process_damage
.Exit:
	movem.l (SP)+,D0/D1/D2/D3/D4/A0/A2
	rts

;*****************************************************************************
; [ Show flames on participant ]
;   IN : a0 - Pointer to victim's participant data (.l)
;        a1 - Pointer to caster's participant data (.l)
; All registers are restored
;*****************************************************************************
Burn_participant:
	movem.l	d0-d3/d6/d7/a0/a2,-(sp)
	move.l	a0,a1			; Save
	jsr	Get_3D_part_coordinates	; Get coordinates
	move.w	d2,d3			; Copy
	move.w	d1,d2
	move.w	d0,d1
; ---------- Create flames ------------------------
	lea.l	FXGFX_workspace,a2
	move.w	d2,d6
	lsr.w	#1,d6
	moveq.l	#Nr_flames-1,d7
.Loop:	jsr	Add_COMOB			; Create
	move.l	a0,(a2)+
	jsr	Random			; Set X-coordinate
	andi.w	#$001f,d0
	subi.w	#16,d0
	add.w	d1,d0
	move.w	d0,COMOB_3D_X(a0)
	jsr	Random			; Set Y-coordinate
	mulu.w	d6,d0
	swap	d0
	add.w	d6,d0
	move.w	d0,COMOB_3D_Y(a0)
	jsr	Random			; Set Z-coordinate
	andi.w	#$001f,d0
	subi.w	#16,d0
	add.w	d3,d0
	move.w	d0,COMOB_3D_Z(a0)
	jsr	Random			; Set Y-vector
	andi.w	#$0003,d0
	addq.w	#2,d0
	move.w	d0,COMOB_3D_vector_Y(a0)
	jsr	Random			; Set size
	andi.w	#$000f,d0
	addq.w	#8,d0
	move.w	d0,COMOB_Display_width(a0)
	move.w	d0,COMOB_Display_height(a0)
	jsr	Random			; Set frame
	mulu.w	#5,d0
	swap	d0
	move.w	d0,COMOB_Frame(a0)
	move.w	#16,COMOB_Source_width(a0)	; Set other data
	move.w	#16,COMOB_Source_height(a0)
	move.b	FXGFX_handle,COMOB_Gfx_handle(a0)
	move.l	#Flame_FXGFX,COMOB_Gfx_base(a0)
	dbra	d7,.Loop
	LOCAL
; ---------- Show flames --------------------------
	moveq.l	#6,d0
	moveq.l	#8-1,d7
.Loop1:	jsr	Update_combat_screen	; Show
	lea.l	FXGFX_workspace,a2		; Animate flames
	moveq.l	#Nr_flames-1,d6
.Loop2:	move.l	(a2)+,a0
	jsr	Circle_COMOB
	dbra	d6,.Loop2
	Set_anim	Hit_anim,a1		; Hit !
	dbra	d7,.Loop1
	LOCAL
; ---------- Remove flames ------------------------
	lea.l	FXGFX_workspace,a2		; Destroy flames
	moveq.l	#Nr_flames-1,d7
.Loop:	move.l	(a2)+,a0
	jsr	Delete_COMOB
	dbra	d7,.Loop
	jsr	Update_combat_screen	; Update
	movem.l	(sp)+,d0-d3/d6/d7/a0/a2
	rts

;*****************************************************************************
; [ Show ice-crystals on participant ]
;   IN : a0 - Pointer to victim's participant data (.l)
;        a1 - Pointer to caster's participant data (.l)
; All registers are restored
;*****************************************************************************
Freeze_participant:
	movem.l	d0-d3/d6/d7/a0/a2,-(sp)
	move.l	a0,a1			; Save
	jsr	Get_3D_part_coordinates	; Get coordinates
	move.w	d2,d3			; Copy
	move.w	d1,d2
	move.w	d0,d1
; ---------- Create ice-crystals ------------------
	lea.l	FXGFX_workspace,a2
	move.l	Part_COMOB_ptr(a0),a3
	move.w	d2,d6
	lsr.w	#2,d6
	moveq.l	#Nr_flames-1,d7
.Loop:	jsr	Add_COMOB			; Create
	move.l	a0,(a2)+
	jsr	Random			; Set X-coordinate
	andi.w	#$001f,d0
	subi.w	#16,d0
	add.w	d1,d0
	move.w	d0,COMOB_3D_X(a0)
	jsr	Random			; Set Y-coordinate
	mulu.w	d6,d0
	swap	d0
	add.w	d6,d0
	move.w	d0,COMOB_3D_Y(a0)
	jsr	Random			; Set Z-coordinate
	andi.w	#$001f,d0
	subi.w	#16,d0
	add.w	d3,d0
	move.w	d0,COMOB_3D_Z(a0)
	jsr	Random			; Set Y-vector
	andi.w	#$0003,d0
	addq.w	#2,d0
	move.w	d0,COMOB_3D_vector_Y(a0)
	jsr	Random			; Set size
	andi.w	#$000f,d0
	addq.w	#8,d0
	move.w	d0,COMOB_Display_width(a0)
	move.w	d0,COMOB_Display_height(a0)
	jsr	Random			; Set frame
	mulu.w	#4,d0
	swap	d0
	move.w	d0,COMOB_Frame(a0)
	move.w	#16,COMOB_Source_width(a0)	; Set other data
	move.w	#16,COMOB_Source_height(a0)
	move.b	FXGFX_handle,COMOB_Gfx_handle(a0)
	move.l	#Ice_FXGFX,COMOB_Gfx_base(a0)
	dbra	d7,.Loop
	LOCAL
; ---------- Show ice-crystals --------------------
	moveq.l	#5,d0
	moveq.l	#8-1,d7
.Loop1:	jsr	Update_combat_screen	; Show
	lea.l	FXGFX_workspace,a2		; Animate ice-crystals
	moveq.l	#Nr_flames-1,d6
.Loop2:	move.l	(a2)+,a0
	jsr	Circle_COMOB
	dbra	d6,.Loop2
	Set_anim	Hit_anim,a1		; Hit !
	dbra	d7,.Loop1
	LOCAL
; ---------- Remove ice-crystals ------------------
	lea.l	FXGFX_workspace,a2		; Destroy ice-crystals
	moveq.l	#Nr_flames-1,d7
.Loop:	move.l	(a2)+,a0
	jsr	Delete_COMOB
	dbra	d7,.Loop
	jsr	Update_combat_screen	; Update
	movem.l	(sp)+,d0-d3/d6/d7/a0/a2
	rts

;***************************************************************************
; [ Fade combat palette ]
;   IN : d0 - Target colour (.w)
;        d7 - Number of steps (.w)
; All registers are restored
;***************************************************************************
Fade_combat_palette:
	movem.l	d7/a0,-(sp)
	lea.l	Combat_pal,a0		; Install palette
	move.l	a0,Combat_pal_ptr
	bra.s	.Entry
.Loop:	jsr	Adapt_palette		; Fade
	jsr	Reset_current_RL		; Update
	rept 3				; Wait
	jsr	My_vsync
	endr
.Entry:	dbra	d7,.Loop
	movem.l	(sp)+,d7/a0
	rts

;***************************************************************************
; [ Restore combat palette ]
; All registers are restored
;***************************************************************************
Restore_combat_palette:
	movem.l	d0-d2/d7/a0-a3,-(sp)
	lea.l	Combat_pal+2,a0
	lea.l	Combat_backup_pal+2,a1
.Again:	movea.l	a0,a2			; Fade palette
	movea.l	a1,a3
	moveq.l	#0,d2
	moveq.l	#Pal_size-2,d7
.Loop:	move.w	(a2),d0			; Get source & target
	move.w	(a3)+,d1			;  colour
	cmp.w	d0,d1			; Same ?
	beq.s	.Same
	jsr	Fade_colour		; No -> Fade
	addq.w	#1,d2
.Same:	move.w	d0,(a2)+			; Store
	dbra	d7,.Loop			; Next colour
	jsr	Reset_current_RL		; Update
	rept 3				; Wait
	jsr	My_vsync
	endr
	tst.w	d2			; The end ?
	bne.s	.Again
	movem.l	(sp)+,d0-d2/d7/a0-a3
	rts

;*****************************************************************************
; [ Make chain of COMOB's ]
;   IN : d0 - Total number of COMOB's in chain (.w)
;        a0 - Pointer to modifier routine (.l)
; All registers are restored
; Notes :
;   - The first entry in {FXGFX_workspace} should be a pointer to the first,
;     completely (!) initialized COMOB. This routine will insert the pointers
;     to the other COMOB's behind it.
;*****************************************************************************
Make_COMOB_chain:
	movem.l	d0-d7/a0-a6,-(sp)
	move.l	a0,a3
	lea.l	FXGFX_workspace,a2		; Get first COMOB
	move.l	(a2)+,a1
	subq.w	#1,d0			; Do
	bra.s	.Entry
.Loop:	jsr	Add_COMOB			; Create new COMOB
	move.l	a0,(a2)+
	move.w	COMOB_3D_X(a1),COMOB_3D_X(a0)	; Copy data
	move.w	COMOB_3D_Y(a1),COMOB_3D_Y(a0)
	move.w	COMOB_3D_Z(a1),COMOB_3D_Z(a0)
	move.w	COMOB_3D_vector_X(a1),COMOB_3D_vector_X(a0)
	move.w	COMOB_3D_vector_Y(a1),COMOB_3D_vector_Y(a0)
	move.w	COMOB_3D_vector_Z(a1),COMOB_3D_vector_Z(a0)
	move.w	COMOB_Display_width(a1),COMOB_Display_width(a0)
	move.w	COMOB_Display_height(a1),COMOB_Display_height(a0)
	move.w	COMOB_Source_width(a1),COMOB_Source_width(a0)
	move.w	COMOB_Source_height(a1),COMOB_Source_height(a0)
	move.b	COMOB_Gfx_handle(a1),COMOB_Gfx_handle(a0)
	move.l	COMOB_Gfx_base(a1),COMOB_Gfx_base(a0)
	move.b	COMOB_Mirror_flags(a1),COMOB_Mirror_flags(a0)
	movem.l	d0/a0-a3,-(sp)		; Modify
	jsr	(a3)
	movem.l	(sp)+,d0/a0-a3
	move.l	a0,a1			; Incremental
.Entry:	dbra	d0,.Loop
	movem.l	(sp)+,d0-d7/a0-a6
	rts

;*****************************************************************************
; [ Move COMOBs towards target & destroy ]
;   IN : d0 - Number of animation frames (.w)
;        d1 - Number of COMOB's (.w)
;        d7 - Number of steps (.w)
; All registers are restored
;*****************************************************************************
Move_COMOBs_to_target:
	movem.l	d2/d7/a0/a1,-(sp)
	bra.s	.Entry1
.Loop1:	jsr	Update_combat_screen	; Show
	tst.w	d0			; Any animation ?
	beq.s	.Entry1
	lea.l	FXGFX_workspace,a1		; Animate COMOBs
	move.w	d1,d2
	bra.s	.Entry2
.Loop2:	move.l	(a1)+,a0
	jsr	Circle_COMOB
.Entry2:	dbra	d2,.Loop2
.Entry1:	dbra	d7,.Loop1
	lea.l	FXGFX_workspace,a1		; Destroy COMOBs
	move.w	d1,d2
	bra.s	.Entry3
.Loop3:	move.l	(a1)+,a0
	jsr	Delete_COMOB
.Entry3:	dbra	d2,.Loop3
	movem.l	(sp)+,d2/d7/a0/a1
	rts

;*****************************************************************************
; [ Calculate the damage of a damage spell ]
; IN : d0 - Regular damage (.w)
;      a0 - Pointer to target participant data (.l)
;      a1 - Pointer to caster participant data (.l)
; OUT: d0 - Damage with level, intelligence and element bonus (.w)
; ADVANCED (moved here from KERNEL/TEXTS.S)
;*****************************************************************************
FUN_CalculateSpellDamage:
	; D0: regular damage
	movem.l A1/A0/D5/D4/D3/D2/D1,-(SP)
	moveq #0,D1
	move.w D0,D1 ; damage
	move.b ($0005,A0),D4 ; target handle
	move.b ($0005,A1),D5 ; caster handle
	move.b D5,D0
	jsr Claim_pointer
	movea.l D0,A0 ; Now A0 is the character data
	moveq #0,D2
	moveq #0,D3
	move.b ($0005,A0),D2 ; Get current character level
	move.w ($0032,A0),D3 ; Get current INT
	add.w ($0036,A0),D3 ; Add bonus INT
	move.b D5,D0
	jsr Free_pointer
	lea Spell_data,A1
	move.w Selected_class,D0
	mulu.w #30,D0
	add.w Selected_spell,D0
	subq.w #$00000001,D0
	mulu.w #$0005,D0 ; Calc index to spell info struct (5 bytes long)
	adda.w D0,A1
	; add together all percentage values
	; (INT-50)/5 + level
	sub.w #50,D3
	ext.l D3
	divs.w #5,D3
	add.w D3,D2
	; element bonus
	moveq #0,D3
	move.b ($0004,A1),D3 ; spell element
	lsl.b #3,D3 ; Multiply by 8 (8 entries per element)
	move.b D4,D0
	jsr Claim_pointer
	movea.l D0,A0 ; Now A0 is the target data
	move.b ($0013,A0),D5 ; get target element bits
	move.b D4,D0
	jsr Free_pointer
	jsr FUN_GetWorstElementBonus ; D3 now holds the element bonus in percent
	moveq #0,D0
	move.b D3,D0
	tst.b D0
	beq.b .Skip_element_bonus
	add.w D0,D2 ; + bonus
	; Note: In theory we have to sub 100 to get the
	; right elemental bonus. But in addition we have to
	; add 100% as well as the total value is a bonus.
	; Both would cancel each other out.
.Skip_element_bonus:
	; D2 now holds the total damage bonus in percent
	tst.w D2
	bpl.b .Positive_factor
	moveq #1,D0 ; limit to at least 1 damage
	bra.b .Return_damage
.Positive_factor:
	mulu.w D2,D1 ; multiply bonus with damage
	divu.w #100,D1 ; divide by 100
	moveq #0,D0
	move.w D1,D0
	move.w ($0076,A0),D1 ; possible magic damage reduction
	muls.w D0,D1
	divs.w #100,D1
	sub.w D1,D0
	tst.w D0
	bgt.b .Return_damage
	moveq #1,D0 ; limit to at least 1 damage
.Return_damage:
	movem.l (SP)+,D1/D2/D3/D4/D5/A0/A1
	rts

;*****************************************************************************
; [ Get the worst element bonus of a target ]
; IN : d3 - Row offset into [ DAT_ElementTable ] (.b)
;      d5 - Target element bits (.b)
; OUT: d3 - Worst element bonus in percent (.b)
; ADVANCED (moved here from KERNEL/TEXTS.S)
;*****************************************************************************
FUN_GetWorstElementBonus:
	movem.l A1/D7/D6/D5/D4,-(SP)
	; In D3 : row offset into element table
	; In D5 : target element bits
	; Out D3 : worst element bonus
	moveq #0,D4 ; FIX: D4.w is the table index
	move.b D3,D4
	move.b #$ff,D3
	addq.b #7,D4
	lea DAT_ElementTable,A1
	moveq #7,D7 ; 8 iterations (element bits)
.Loop:
	btst.l D7,D5
	beq.b .Skip
	move.b ($0,A1,D4.w),D6 ; elemental bonus
	cmp.b D6,D3
	bcs.b .Skip ; FIX: unsigned compare (was bmi)
	move.b D6,D3
.Skip:
	subq.b #1,D4
	dbf D7,.Loop
	cmpi.b #$ff,D3
	bne.b .End
	moveq #100,D3 ; if no element at all, use 100% as factor
.End:
	movem.l (SP)+,D4/D5/D6/D7/A1
	rts

;*****************************************************************************
; The DATA & BSS segments
;*****************************************************************************
	SECTION	Fast_DATA,data
; ADVANCED: element bonus in percent (row: spell element, column: target element)
DAT_ElementTable:
	dc.b 0,100,100,100,100,100,100,100 ; Mental spells
	dc.b 125,0,150,150,100,100,100,100 ; Spirit spells
	dc.b 100,100,0,100,100,100,100,100 ; Physical spells
	dc.b 125,50,200,0,75,75,75,75 ; Undead spells (and weapons)
	dc.b 75,100,100,75,0,50,100,150 ; Earth spells
	dc.b 75,100,100,75,150,0,50,100 ; Wind spells (FIX: 100% against water, was 150%)
	dc.b 75,75,100,125,100,150,0,50 ; Fire spells
	dc.b 75,100,100,75,50,100,150,0 ; Water spells

Spell_exception_table:
	dc.w 1,9				; Blink
	dc.l Enter_blink_target,Show_blink_target
	dc.w -1

Member_spell_target_table:
	dc.b %00000001			; 0 - A friend
	dc.b %00001000			; 1 - An enemy 
	dc.b %00000010			; 2 - ADVANCED: Enemies in close range (was: row of friends)
	dc.b %00010000			; 3 - Row of enemies
	dc.b %00000100			; 4 - All friends
	dc.b %00100000			; 5 - All enemies
CCondition_table:
	dc.b Lamed,Poisoned,Petrified,Diseased
	dc.b Aging,Irritated,Mad,Asleep
	dc.b Panicked,Blind,Stoned
	even
Member_spell_target_vectors:
	dc.l Member_target
	dc.l Monster_target
	dc.l Close_range_enemies_target	; ADVANCED (was Member_row_target)
	dc.l Monster_row_target
	dc.l All_members_target
	dc.l All_monsters_target

; ********** Party magic **************************
Party_comma_class_ptrs:
	dc.l .Class_0_ptrs,.Class_1_ptrs,.Class_2_ptrs,.Class_3_ptrs
	dc.l 0,0,.Class_6_ptrs

.Class_0_ptrs:
	dc.l Healing,Remove_cond,Remove_cond,Remove_cond
	dc.l Remove_cond,Remove_cond,Remove_cond,Healing
	dc.l Remove_cond,Remove_cond,Healing,CDestroy_undead
	dc.l CDestroy_undead,CDestroy_undead,0,0
	dc.l 0,Healing,Healing,0
	dc.l Remove_cond,Remove_cond,Remove_cond,Remove_cond
	dc.l Remove_cond,Remove_cond,Remove_cond,Remove_cond
	dc.l Remove_cond,Restore_stamina
.Class_1_ptrs:
	dc.l 0,0,0,0
	dc.l 0,CGhost_weapon,0,0
	dc.l CBlink,0,CFlight,0
	dc.l 0,MShield,MShield,MShield
	dc.l MAttack,MAttack,MAttack,0
	dc.l MAnti_magic,MAnti_magic,0,CHurry
	dc.l CHurry,0,0,CLP_stealer
	dc.l CPP_stealer
	dc.l CGhost_weapon ; ADVANCED: Ghost Inferno / Geisterstunde
.Class_2_ptrs:
	dc.l CMonster_knowledge,0,0,0
	dc.l 0,0,0,0
	dc.l 0,0,0,0
	dc.l 0,0,0,0
	dc.l CShow_monster_LP
	dc.l FUN_SpellShowElements
	dc.l FUN_SpellWeakenMonster
	dc.l FUN_SpellWeakenMonster
	dc.l FUN_SpellWeakenMonster
	dc.l FUN_SpellForeseeMagic
	dc.l FUN_SpellForeseeAttack
	dc.l FUN_SpellMysticDecay
	dc.l FUN_SpellProtectionSphere
	dc.l FUN_SpellElementToEarth
	dc.l FUN_SpellElementToWind
	dc.l FUN_SpellElementToFire
	dc.l FUN_SpellElementToWater
	dc.l FUN_SpellMysticImitation
.Class_3_ptrs:
	dc.l CMagical_projectiles,CMagical_projectiles,CCondition,CCondition
	dc.l CCondition,CCondition,CCondition,CCondition
	dc.l CCondition,CCondition,CCondition,CCondition
	dc.l CCondition,CDissolve_victim,CMudsling,CRockfall
	dc.l CEarthslide,CEarthquake,CWinddevil,CWindhowler
	dc.l CThunderbolt,CWhirlwind,CFirebeam,CFireball
	dc.l CFirestorm,CFirecolumn,CWaterfall,CIceball
	dc.l CIcestorm,CIceshower
.Class_6_ptrs:
	dc.l 0,0,0,0
	dc.l MSpell_points,MSpell_points,MSpell_points,MSpell_points
	dc.l MSpell_points,Heal_all,0,MAttribute
	dc.l MAttribute,MAttribute,MAttribute,MAttribute
	dc.l MAttribute,MAttribute,MAttribute,0
	dc.l Drug
	; ADVANCED CHANGES
	dc.l FUN_SpellSelfHealing ; 22
	dc.l FUN_SpellSelfRevive ; 23
	dc.l FUN_SpellExchangeExp ; 24
	dc.l 0
	dc.l CMagic_sword_attack ; 26
	dc.l 0,0
	dc.l 0,0

; 21 colour values
Glow_colours:
	dc.w 23,23,23
	dc.w 22,22,22
	dc.w 21,21,21
	dc.w 20,20,20
	dc.w 19,19,19
	dc.w 3,3,3
	dc.w 2,2,2
; 8 Jelly oscillation values
Oscillation:
	dc.b 0,2,4,2,0,-2,-4,-2
	dc.b 0,2,4,2,0,-2,-4,-2		; Overflow values
	even
