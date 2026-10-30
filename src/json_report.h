#ifndef JSON_REPORT_H_
#define JSON_REPORT_H_

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Values are in 0.001 C and 0.001 %RH, respectively. */
struct sensor_reading {
    uint32_t seq;
    uint32_t uptime_ms;
    int32_t temperature_milli;
    int32_t humidity_milli;
    bool valid;
    int32_t error_code;
};

/* Returns number of bytes excluding NUL or -EINVAL / -ENOSPC. */
int json_report_format(char *buffer, size_t capacity,
                       const struct sensor_reading *reading);

#endif
