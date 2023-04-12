#ifndef HAT_RING_H
#define HAT_RING_H

#include <stdint.h>

#include <hat/allocator.h>


#ifdef __cplusplus
extern "C" {
#endif

typedef struct hat_ring_t hat_ring_t;


hat_ring_t *hat_ring_create(hat_allocator_t *a, size_t size);
void hat_ring_destroy(hat_ring_t *r);

size_t hat_ring_len(hat_ring_t *r);
size_t hat_ring_size(hat_ring_t *r);

// len/size is checked (head/tail can't skip each other)
void hat_ring_move_head(hat_ring_t *r, size_t len);
void hat_ring_move_tail(hat_ring_t *r, size_t len);

// read/write copy data from/to ring and moves head/tail
size_t hat_ring_read(hat_ring_t *r, uint8_t *data, size_t data_len);
size_t hat_ring_write(hat_ring_t *r, uint8_t *data, size_t data_len);

// returns used/unused ring data without modifing head/tail
void hat_ring_used(hat_ring_t *r, uint8_t *data[2], size_t data_len[2]);
void hat_ring_unused(hat_ring_t *r, uint8_t *data[2], size_t data_len[2]);

#ifdef __cplusplus
}
#endif

#endif
