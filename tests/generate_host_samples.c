/* Generates sample records for host-only integration tests. NOT hardware data. */
#include "json_report.h"
#include <stdio.h>

int main(void)
{
    char line[256];
    const struct sensor_reading readings[] = {
        {.seq=1,.uptime_ms=100,.temperature_milli=25600,
         .humidity_milli=62000,.valid=true,.error_code=0},
        {.seq=2,.uptime_ms=3100,.temperature_milli=25800,
         .humidity_milli=61500,.valid=true,.error_code=0},
        {.seq=3,.uptime_ms=6100,.temperature_milli=0,
         .humidity_milli=0,.valid=false,.error_code=-5}
    };
    for (unsigned int i = 0; i < sizeof(readings)/sizeof(readings[0]); ++i) {
        if (json_report_format(line, sizeof(line), &readings[i]) < 0) {
            return 1;
        }
        fputs(line, stdout);
        fputc('\n', stdout);
    }
    return 0;
}
