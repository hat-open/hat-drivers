#include "serial.h"


hat_serial_t *hat_serial_create(hat_allocator_t *a, size_t in_buff_size,
                                size_t out_buff_size, hat_serial_cb_t close_cb,
                                hat_serial_cb_t in_cb, hat_serial_cb_t out_cb,
                                void *ctx) {
    return NULL;
}


void hat_serial_destroy(hat_serial_t *s) {}


hat_serial_error_t hat_serial_open(hat_serial_t *s, char *port,
                                   uint32_t baudrate, uint8_t bytesize,
                                   char parity, uint8_t stopbits, bool xonxoff,
                                   bool rtscts, bool dsrdtr) {
    return HAT_SERIAL_ERROR;
}


void hat_serial_close(hat_serial_t *s) {}


void *hat_serial_ctx(hat_serial_t *s) { return NULL; }


size_t hat_serial_available(hat_serial_t *s) { return 0; }


size_t hat_serial_read(hat_serial_t *s, uint8_t *data, size_t data_len) {
    return 0;
}


size_t hat_serial_write(hat_serial_t *s, uint8_t *data, size_t data_len) {
    return 0;
}
