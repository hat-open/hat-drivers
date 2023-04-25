#ifndef HAT_TCP_H
#define HAT_TCP_H

#include <stdint.h>

#include <hat/allocator.h>


#ifdef __cplusplus
extern "C" {
#endif

typedef struct hat_tcp_loop_t hat_tcp_loop_t;
typedef struct hat_tcp_srv_t hat_tcp_srv_t;
typedef struct hat_tcp_conn_t hat_tcp_conn_t;
typedef uint32_t hat_tcp_addr_t;
typedef uint16_t hat_tcp_port_t;
typedef void (*hat_tcp_cb_t)(hat_tcp_loop_t *l, hat_tcp_srv_t *s,
                             hat_tcp_conn_t *c);


hat_tcp_loop_t *hat_tcp_loop_create(hat_allocator_t *a, hat_tcp_cb_t close_cb,
                                    void *ctx);
void hat_tcp_loop_close(hat_tcp_loop_t *l);
void hat_tcp_loop_destroy(hat_tcp_loop_t *l);
void *hat_tcp_loop_get_ctx(hat_tcp_loop_t *l);

hat_tcp_srv_t *
hat_tcp_srv_create(hat_tcp_loop_t *l, hat_tcp_addr_t addr, hat_tcp_port_t port,
                   size_t in_buff_size, size_t out_buff_size,
                   hat_tcp_cb_t srv_open_cb, hat_tcp_cb_t srv_close_cb,
                   hat_tcp_cb_t conn_open_cb, hat_tcp_cb_t conn_close_cb,
                   hat_tcp_cb_t in_change_cb, hat_tcp_cb_t in_full_cb,
                   hat_tcp_cb_t out_change_cb, hat_tcp_cb_t out_empty_cb,
                   void *ctx);
void hat_tcp_srv_close(hat_tcp_srv_t *s);
void hat_tcp_srv_destroy(hat_tcp_srv_t *s);
void *hat_tcp_srv_get_ctx(hat_tcp_srv_t *s);

hat_tcp_conn_t *hat_tcp_conn_create(
    hat_tcp_loop_t *l, hat_tcp_addr_t addr, hat_tcp_port_t port,
    size_t in_buff_size, size_t out_buff_size, hat_tcp_cb_t open_cb,
    hat_tcp_cb_t close_cb, hat_tcp_cb_t in_change_cb, hat_tcp_cb_t in_full_cb,
    hat_tcp_cb_t out_change_cb, hat_tcp_cb_t out_empty_cb, void *ctx);
void hat_tcp_conn_close(hat_tcp_conn_t *s);
void hat_tcp_conn_destroy(hat_tcp_conn_t *s);
void *hat_tcp_conn_get_ctx(hat_tcp_conn_t *s);
void hat_tcp_conn_set_ctx(hat_tcp_conn_t *s, void *ctx);
size_t hat_tcp_conn_get_available(hat_tcp_conn_t *s);
size_t hat_tcp_conn_read(hat_tcp_conn_t *s, uint8_t *data, size_t data_len);
size_t hat_tcp_conn_write(hat_tcp_conn_t *s, uint8_t *data, size_t data_len);

#ifdef __cplusplus
}
#endif

#endif
