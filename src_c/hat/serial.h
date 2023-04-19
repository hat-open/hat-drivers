#ifndef HAT_SERIAL_H
#define HAT_SERIAL_H

#include <stdbool.h>
#include <stdint.h>

#include <hat/allocator.h>


#define HAT_SERIAL_SUCCESS 0
#define HAT_SERIAL_ERROR 1
#define HAT_SERIAL_ERROR_MEMORY 2
#define HAT_SERIAL_ERROR_IO 3
#define HAT_SERIAL_ERROR_BAUDRATE 4
#define HAT_SERIAL_ERROR_BYTESIZE 5
#define HAT_SERIAL_ERROR_PARITY 6
#define HAT_SERIAL_ERROR_STOPBITS 7
#define HAT_SERIAL_ERROR_OPEN 8
#define HAT_SERIAL_ERROR_TERMIOS 9
#define HAT_SERIAL_ERROR_THREAD 10
#define HAT_SERIAL_ERROR_IOCTL 11


#ifdef __cplusplus
extern "C" {
#endif

typedef int hat_serial_error_t;

typedef struct hat_serial_t hat_serial_t;

typedef void (*hat_serial_cb_t)(hat_serial_t *s);


char *hat_serial_error_msg(hat_serial_error_t error);

hat_serial_t *hat_serial_create(hat_allocator_t *a, size_t in_buff_size,
                                size_t out_buff_size, hat_serial_cb_t close_cb,
                                hat_serial_cb_t in_change_cb,
                                hat_serial_cb_t in_full_cb,
                                hat_serial_cb_t out_change_cb,
                                hat_serial_cb_t out_empty_cb, void *ctx);
void hat_serial_destroy(hat_serial_t *s);

hat_serial_error_t hat_serial_open(hat_serial_t *s, char *port,
                                   uint32_t baudrate, uint8_t bytesize,
                                   char parity, uint8_t stopbits, bool xonxoff,
                                   bool rtscts, bool dsrdtr);
void hat_serial_close(hat_serial_t *s);

void *hat_serial_get_ctx(hat_serial_t *s);
size_t hat_serial_get_available(hat_serial_t *s);

size_t hat_serial_read(hat_serial_t *s, uint8_t *data, size_t data_len);
size_t hat_serial_write(hat_serial_t *s, uint8_t *data, size_t data_len);

#ifdef __cplusplus
}
#endif

#endif
