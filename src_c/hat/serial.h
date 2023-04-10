#ifndef HAT_SERIAL_H
#define HAT_SERIAL_H

#include <stdbool.h>
#include <stdint.h>

#include <hat/allocator.h>

#define HAT_SERIAL_SUCCESS 0
#define HAT_SERIAL_ERROR 1


#ifdef __cplusplus
extern "C" {
#endif

typedef struct hat_serial_t hat_serial_t;

typedef void (*hat_serial_cb_t)(hat_serial_t *s);


hat_serial_t *hat_serial_create(hat_allocator_t *a, size_t in_buff_size,
                                size_t out_buff_size, hat_serial_cb_t close_cb,
                                hat_serial_cb_t in_cb, hat_serial_cb_t out_cb,
                                void *ctx);
void hat_serial_destroy(hat_serial_t *s);

int hat_serial_open(hat_serial_t *s, char *port, uint32_t baudrate,
                    uint8_t byte_size, char parity, uint8_t stop_bits,
                    bool xonxoff, bool rtscts, bool dsrdtr);
void hat_serial_close(hat_serial_t *s);

size_t hat_serial_get_in_buff_size(hat_serial_t *s);
size_t hat_serial_get_out_buff_size(hat_serial_t *s);

size_t hat_serial_get_in_buff_len(hat_serial_t *s);
size_t hat_serial_get_out_buff_len(hat_serial_t *s);

void *hat_serial_get_ctx(hat_serial_t *s);

int hat_serial_read(hat_serial_t *s, uint8_t *data, size_t data_len);
int hat_serial_write(hat_serial_t *s, uint8_t *data, size_t data_len);

size_t hat_serial_clear_in_buff(hat_serial_t *s);

#ifdef __cplusplus
}
#endif

#endif
