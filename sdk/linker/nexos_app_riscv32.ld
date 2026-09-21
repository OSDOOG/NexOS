/**
 * @file nexos_app_riscv32.ld
 * @brief Linker script for NexOS Relocatable User Applications (ESP32-C6 RISC-V)
 *
 * Applications are loaded by NexOS Application Loader from MicroSD into an
 * allocated SRAM buffer. The entry point _nex_app_start is positioned at offset 0.
 */

OUTPUT_ARCH(riscv)
ENTRY(_nex_app_start)

SECTIONS
{
    . = 0x0;

    .text :
    {
        KEEP(*(.text.entry))
        *(.text)
        *(.text.*)
        . = ALIGN(4);
    }

    .rodata :
    {
        *(.rodata)
        *(.rodata.*)
        *(.srodata)
        *(.srodata.*)
        . = ALIGN(4);
    }

    .data :
    {
        *(.data)
        *(.data.*)
        *(.sdata)
        *(.sdata.*)
        . = ALIGN(4);
    }

    .bss (NOLOAD) :
    {
        *(.bss)
        *(.bss.*)
        *(.sbss)
        *(.sbss.*)
        *(COMMON)
        . = ALIGN(4);
    }

    /DISCARD/ :
    {
        *(.comment)
        *(.note.*)
        *(.eh_frame)
    }
}
