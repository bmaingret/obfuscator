#include <stdint.h>

uint8_t f(uint32_t a, uint32_t b, uint32_t c)
{
    uint8_t res;
    c = a + b;
    res = c + 42;
    res = res ^ 420;
    return res;
}
