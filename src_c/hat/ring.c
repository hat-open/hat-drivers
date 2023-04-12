#include "ring.h"

#include <stdatomic.h>
#include <string.h>


struct hat_ring_t {
    hat_allocator_t *a;
    size_t size;
    volatile _Atomic size_t head;
    volatile _Atomic size_t tail;
    uint8_t data[];
};


static inline void move_head(hat_ring_t *r, size_t len) {
    atomic_store(&(r->head), (r->head + len) % (r->size + 1));
}


static inline void move_tail(hat_ring_t *r, size_t len) {
    atomic_store(&(r->tail), (r->tail + len) % (r->size + 1));
}


hat_ring_t *hat_ring_create(hat_allocator_t *a, size_t size) {
    hat_ring_t *r = hat_allocator_alloc(a, sizeof(hat_ring_t) + size + 1);
    if (!r)
        return NULL;

    r->a = a;
    r->size = size;
    r->head = 0;
    r->tail = 0;

    return r;
}


void hat_ring_destroy(hat_ring_t *r) { hat_allocator_free(r->a, r); }


size_t hat_ring_len(hat_ring_t *r) {
    size_t head = atomic_load(&(r->head));
    size_t tail = atomic_load(&(r->tail));

    if (head <= tail)
        return tail - head;

    return r->size + 1 - (head - tail);
}


size_t hat_ring_size(hat_ring_t *r) { return r->size; }


void hat_ring_move_head(hat_ring_t *r, size_t len) {
    size_t max_len = hat_ring_len(r);
    move_head(r, (len < max_len ? len : max_len));
}


void hat_ring_move_tail(hat_ring_t *r, size_t len) {
    size_t max_len = r->size - hat_ring_len(r);
    move_tail(r, (len < max_len ? len : max_len));
}


size_t hat_ring_read(hat_ring_t *r, uint8_t *data, size_t data_len) {
    size_t max_len = hat_ring_len(r);

    if (data_len > max_len)
        data_len = max_len;

    if (!data_len)
        return 0;

    if (r->size - r->head >= data_len) {
        memcpy(data, r->data + r->head + 1, data_len);

    } else {
        memcpy(data, r->data + r->head + 1, r->size - r->head);
        memcpy(data + r->size - r->head, r->data, data_len - r->size + r->head);
    }

    move_head(r, data_len);

    return data_len;
}


size_t hat_ring_write(hat_ring_t *r, uint8_t *data, size_t data_len) {
    size_t max_len = r->size - hat_ring_len(r);

    if (data_len > max_len)
        data_len = max_len;

    if (!data_len)
        return 0;

    if (r->size - r->tail >= data_len) {
        memcpy(r->data + r->tail + 1, data, data_len);

    } else {
        memcpy(r->data + r->tail + 1, data, r->size - r->tail);
        memcpy(r->data, data + r->size - r->tail, data_len - r->size + r->tail);
    }

    move_tail(r, data_len);

    return data_len;
}


void hat_ring_used(hat_ring_t *r, uint8_t *data[2], size_t data_len[2]) {
    size_t used_len = hat_ring_len(r);

    data[0] = (r->head == r->size ? r->data : r->data + r->head + 1);
    data[1] = r->data;

    if (used_len <= r->size - r->head || r->head == r->size) {
        data_len[0] = used_len;
        data_len[1] = 0;

    } else {
        data_len[0] = r->size - r->head;
        data_len[1] = used_len - r->size + r->head;
    }
}


void hat_ring_unused(hat_ring_t *r, uint8_t *data[2], size_t data_len[2]) {
    size_t unused_len = r->size - hat_ring_len(r);

    data[0] = (r->tail == r->size ? r->data : r->data + r->tail + 1);
    data[1] = r->data;

    if (unused_len <= r->size - r->tail || r->tail == r->size) {
        data_len[0] = unused_len;
        data_len[1] = 0;

    } else {
        data_len[0] = r->size - r->tail;
        data_len[1] = unused_len - r->size + r->tail;
    }
}
