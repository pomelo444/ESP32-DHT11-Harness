#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/devicetree.h>
#include <zephyr/drivers/sensor.h>
#include <zephyr/drivers/uart.h>
#include <zephyr/sys/atomic.h>
#include <errno.h>
#include <stdint.h>

#include "json_report.h"

#if !DT_NODE_EXISTS(DT_ALIAS(dht0))
#error "Missing dht0 devicetree alias; see app.overlay"
#endif
#if !DT_NODE_EXISTS(DT_CHOSEN(zephyr_console))
#error "No zephyr,console device is selected"
#endif

#define SAMPLE_PERIOD_MS 3000
#define JSON_BUFFER_SIZE 256

static const struct device *const dht_device = DEVICE_DT_GET(DT_ALIAS(dht0));
static const struct device *const console_uart = DEVICE_DT_GET(DT_CHOSEN(zephyr_console));

K_MSGQ_DEFINE(reading_queue, sizeof(struct sensor_reading), 8, 4);
static atomic_t dropped_messages = ATOMIC_INIT(0);

static void read_sensor(struct sensor_reading *reading)
{
    struct sensor_value temperature;
    struct sensor_value humidity;
    int err;

    if (!device_is_ready(dht_device)) {
        reading->error_code = -ENODEV;
        return;
    }
    err = sensor_sample_fetch(dht_device);
    if (err == 0) {
        err = sensor_channel_get(dht_device, SENSOR_CHAN_AMBIENT_TEMP,
                                 &temperature);
    }
    if (err == 0) {
        err = sensor_channel_get(dht_device, SENSOR_CHAN_HUMIDITY, &humidity);
    }
    if (err != 0) {
        reading->error_code = err;
        return;
    }

    reading->temperature_milli = (int32_t)sensor_value_to_milli(&temperature);
    reading->humidity_milli = (int32_t)sensor_value_to_milli(&humidity);
    reading->valid = true;
    reading->error_code = 0;
}

static void sensor_thread(void *arg1, void *arg2, void *arg3)
{
    uint32_t seq = 0;
    (void)arg1;
    (void)arg2;
    (void)arg3;

    while (true) {
        struct sensor_reading reading = {0};
        reading.seq = ++seq;
        reading.uptime_ms = k_uptime_get_32();
        read_sensor(&reading);

        if (k_msgq_put(&reading_queue, &reading, K_NO_WAIT) != 0) {
            atomic_inc(&dropped_messages);
        }
        k_sleep(K_MSEC(SAMPLE_PERIOD_MS));
    }
}

static void output_line(const char *data, int count)
{
    for (int index = 0; index < count; ++index) {
        uart_poll_out(console_uart, (unsigned char)data[index]);
    }
    uart_poll_out(console_uart, '\r');
    uart_poll_out(console_uart, '\n');
}

static void output_thread(void *arg1, void *arg2, void *arg3)
{
    char line[JSON_BUFFER_SIZE];
    (void)arg1;
    (void)arg2;
    (void)arg3;

    if (!device_is_ready(console_uart)) {
        return;
    }
    while (true) {
        struct sensor_reading reading;
        if (k_msgq_get(&reading_queue, &reading, K_FOREVER) != 0) {
            continue;
        }
        int size = json_report_format(line, sizeof(line), &reading);
        if (size > 0) {
            output_line(line, size);
        }
    }
}

K_THREAD_DEFINE(sensor_thread_id, 2048, sensor_thread, NULL, NULL, NULL, 5, 0, 0);
K_THREAD_DEFINE(output_thread_id, 2048, output_thread, NULL, NULL, NULL, 5, 0, 0);

int main(void)
{
    /* The two statically declared threads do the work. */
    return 0;
}
