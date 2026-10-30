#include "json_report.h"
#include <assert.h>
#include <errno.h>
#include <stdint.h>
#include <string.h>

int main(void)
{
    char buf[256];
    char tiny[15];
    int n;
    struct sensor_reading good = {
        .seq = 1U, .uptime_ms = 3000U,
        .temperature_milli = 25600, .humidity_milli = 62500,
        .valid = true, .error_code = 0
    };
    struct sensor_reading bad = {
        .seq = 2U, .uptime_ms = 6000U,
        .valid = false, .error_code = -5
    };

    n = json_report_format(buf, sizeof(buf), &good);
    assert(n > 0 && (size_t)n == strlen(buf));
    assert(strstr(buf, "\"temperature\":25.60") != NULL);
    assert(strstr(buf, "\"humidity\":62.50") != NULL);
    assert(strstr(buf, "\"humidity_unit\":\"%RH\"") != NULL);
    assert(strstr(buf, "\"status\":\"OK\"") != NULL);
    /* Exact NUL capacity and one-byte-short capacity, with a canary. */
    size_t needed = (size_t)n + 1U;
    char boundary[257];
    memset(boundary, 'X', sizeof(boundary));
    assert(json_report_format(boundary, needed, &good) == n);
    assert(boundary[needed] == 'X');
    memset(boundary, 'X', sizeof(boundary));
    assert(json_report_format(boundary, needed - 1U, &good) == -ENOSPC);
    assert(boundary[0] == '\0');
    assert(boundary[needed - 1U] == 'X');
    assert(boundary[needed] == 'X');

    n = json_report_format(buf, sizeof(buf), &bad);
    assert(n > 0);
    assert(strstr(buf, "\"temperature\":null") != NULL);
    assert(strstr(buf, "\"humidity\":null") != NULL);
    assert(strstr(buf, "\"error_code\":-5") != NULL);

    good.temperature_milli = -1250;
    good.humidity_milli = 99995;
    n = json_report_format(buf, sizeof(buf), &good);
    assert(n > 0);
    assert(strstr(buf, "\"temperature\":-1.25") != NULL);
    assert(strstr(buf, "\"humidity\":100.00") != NULL);

    bad.error_code = INT32_MIN;
    n = json_report_format(buf, sizeof(buf), &bad);
    assert(n > 0 && strstr(buf, "-2147483648") != NULL);
    good.seq = UINT32_MAX;
    good.uptime_ms = UINT32_MAX;
    good.temperature_milli = INT32_MIN;
    good.humidity_milli = INT32_MAX;
    n = json_report_format(buf, sizeof(buf), &good);
    assert(n > 0);
    assert(strstr(buf, "\"seq\":4294967295") != NULL);
    assert(strstr(buf, "\"temperature\":-2147483.65") != NULL);
    assert(strstr(buf, "\"humidity\":2147483.65") != NULL);

    n = json_report_format(tiny, sizeof(tiny), &good);
    assert(n == -ENOSPC && tiny[0] == '\0');
    assert(json_report_format(NULL, sizeof(buf), &good) == -EINVAL);
    assert(json_report_format(buf, 0, &good) == -EINVAL);

    good.error_code = -1;
    assert(json_report_format(buf, sizeof(buf), &good) == -EINVAL);
    bad.error_code = 0;
    assert(json_report_format(buf, sizeof(buf), &bad) == -EINVAL);
    return 0;
}
