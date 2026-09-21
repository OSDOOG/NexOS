#include <nexos.h>

void app_main(void)
{
    nex_log("Hello from NexOS!");

    while (1)
    {
        nex_delay_ms(1000);
    }
}
