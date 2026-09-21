/**
 * Linker script for NexOS on ESP32-C6 (RV32IMAC)
 */

MEMORY
{
    iram_seg (RX)  : ORIGIN = 0x40800000, LENGTH = 0x00020000 /* 128KB Instruction RAM */
    dram_seg (RW)  : ORIGIN = 0x40820000, LENGTH = 0x00060000 /* 384KB Data RAM */
    flash_seg (RX) : ORIGIN = 0x42000000, LENGTH = 0x00400000 /* 4MB Mapped Flash */
}

ENTRY(nex_platform_boot)

SECTIONS
{
    .text :
    {
        . = ALIGN(4);
        *(.entry)
        *(.text)
        *(.text.*)
        *(.rodata)
        *(.rodata.*)
        . = ALIGN(4);
        _etext = .;
    } > flash_seg

    .data : AT(_etext)
    {
        . = ALIGN(4);
        _sdata = .;
        *(.data)
        *(.data.*)
        . = ALIGN(4);
        _edata = .;
    } > dram_seg

    .bss :
    {
        . = ALIGN(4);
        _sbss = .;
        *(.bss)
        *(.bss.*)
        *(COMMON)
        . = ALIGN(4);
        _ebss = .;
    } > dram_seg
}
