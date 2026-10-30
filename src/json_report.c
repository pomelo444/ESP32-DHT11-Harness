#include "json_report.h"

#include <errno.h>
#include <stdint.h>

struct json_writer {
    char *buf;
    size_t cap;
    size_t len;
    bool ok;
};

static void append_char(struct json_writer *w, char ch)
{
    if (!w->ok) {
        return;
    }
    if (w->len + 1U >= w->cap) {
        w->ok = false;
        return;
    }
    w->buf[w->len++] = ch;
    w->buf[w->len] = '\0';
}

static void append_str(struct json_writer *w, const char *text)
{
    while (*text != '\0' && w->ok) {
        append_char(w, *text++);
    }
}

static void append_uint64(struct json_writer *w, uint64_t number)
{
    char digits[20];
    size_t n = 0;

    do {
        digits[n++] = (char)('0' + (number % 10U));
        number /= 10U;
    } while (number != 0U);

    while (n > 0U) {
        append_char(w, digits[--n]);
    }
}

static void append_int32(struct json_writer *w, int32_t number)
{
    int64_t promoted = number;
    if (promoted < 0) {
        append_char(w, '-');
        promoted = -promoted;
    }
    append_uint64(w, (uint64_t)promoted);
}

/* Rounds milli-units to two decimal places without floating point/printf. */
static void append_milli2(struct json_writer *w, int32_t value_milli)
{
    int64_t scaled = value_milli;
    uint64_t positive_centi;

    if (scaled < 0) {
        append_char(w, '-');
        scaled = -scaled;
    }
    positive_centi = (uint64_t)((scaled + 5) / 10);
    append_uint64(w, positive_centi / 100U);
    append_char(w, '.');
    append_char(w, (char)('0' + ((positive_centi / 10U) % 10U)));
    append_char(w, (char)('0' + (positive_centi % 10U)));
}

int json_report_format(char *buffer, size_t capacity,
                       const struct sensor_reading *reading)
{
    struct json_writer writer;

    if (buffer == NULL || reading == NULL || capacity == 0U) {
        return -EINVAL;
    }
    buffer[0] = '\0';
    if (reading->valid && reading->error_code != 0) {
        return -EINVAL;
    }
    if (!reading->valid && reading->error_code == 0) {
        return -EINVAL;
    }

    writer.buf = buffer;
    writer.cap = capacity;
    writer.len = 0;
    writer.ok = true;

    append_str(&writer, "{\"device\":\"ESP32-DHT11\",\"seq\":");
    append_uint64(&writer, reading->seq);
    append_str(&writer, ",\"uptime_ms\":");
    append_uint64(&writer, reading->uptime_ms);
    append_str(&writer, ",\"temperature\":");
    if (reading->valid) {
        append_milli2(&writer, reading->temperature_milli);
    } else {
        append_str(&writer, "null");
    }
    append_str(&writer, ",\"temperature_unit\":\"C\",\"humidity\":");
    if (reading->valid) {
        append_milli2(&writer, reading->humidity_milli);
    } else {
        append_str(&writer, "null");
    }
    append_str(&writer, ",\"humidity_unit\":\"%RH\",\"status\":\"");
    append_str(&writer, reading->valid ? "OK" : "ERROR");
    append_str(&writer, "\",\"error_code\":");
    append_int32(&writer, reading->error_code);
    append_char(&writer, '}');

    if (!writer.ok) {
        buffer[0] = '\0';
        return -ENOSPC;
    }
    return (int)writer.len;
}
