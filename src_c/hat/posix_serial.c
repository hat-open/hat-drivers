#include "serial.h"

#include <errno.h>
#include <fcntl.h>
#include <poll.h>
#include <pthread.h>
#include <stdatomic.h>
#include <string.h>
#include <sys/uio.h>
#include <termios.h>
#include <unistd.h>


typedef struct {
    size_t size;
    volatile _Atomic size_t head;
    volatile _Atomic size_t tail;
    uint8_t data[];
} hat_serial_buff_t;

struct hat_serial_t {
    hat_allocator_t *a;
    hat_serial_buff_t *in_buff;
    hat_serial_buff_t *out_buff;
    hat_serial_cb_t close_cb;
    hat_serial_cb_t in_cb;
    hat_serial_cb_t out_cb;
    void *ctx;
    volatile int port_fd;
    volatile int ev_r_fd;
    int ev_w_fd;
    pthread_t thread;
    bool is_running;
    volatile _Atomic bool is_closing;
};


static hat_serial_buff_t *create_buff(hat_allocator_t *a, size_t size) {
    hat_serial_buff_t *buff =
        hat_allocator_alloc(a, sizeof(hat_serial_buff_t) + size + 1);
    if (!buff)
        return NULL;

    buff->size = size;
    buff->head = 0;
    buff->tail = 0;

    return buff;
}


static inline size_t get_buff_len(hat_serial_buff_t *buff) {
    size_t head = atomic_load(&(buff->head));
    size_t tail = atomic_load(&(buff->tail));

    if (head <= tail)
        return tail - head;

    return buff->size + 1 - (head - tail);
}


static inline void move_buff_head(hat_serial_buff_t *buff, size_t len) {
    atomic_store(&(buff->head), (buff->head + len) % (buff->size + 1));
}


static inline void move_buff_tail(hat_serial_buff_t *buff, size_t len) {
    atomic_store(&(buff->tail), (buff->tail + len) % (buff->size + 1));
}


static inline speed_t get_speed(uint32_t baudrate) {
    if (baudrate <= 0)
        return B0;

    if (baudrate <= 75)
        return B75;

    if (baudrate <= 110)
        return B110;

    if (baudrate <= 134)
        return B134;

    if (baudrate <= 150)
        return B150;

    if (baudrate <= 200)
        return B200;

    if (baudrate <= 300)
        return B300;

    if (baudrate <= 600)
        return B600;

    if (baudrate <= 1200)
        return B1200;

    if (baudrate <= 1800)
        return B1800;

    if (baudrate <= 2400)
        return B2400;

    if (baudrate <= 4800)
        return B4800;

    if (baudrate <= 9600)
        return B9600;

    if (baudrate <= 19200)
        return B19200;

    if (baudrate <= 38400)
        return B38400;

    if (baudrate <= 57600)
        return B57600;

    if (baudrate <= 115200)
        return B115200;

    if (baudrate <= 230400)
        return B230400;

    if (baudrate <= 460800)
        return B460800;

    if (baudrate <= 500000)
        return B500000;

    if (baudrate <= 576000)
        return B576000;

    if (baudrate <= 921600)
        return B921600;

    if (baudrate <= 1000000)
        return B1000000;

    if (baudrate <= 1152000)
        return B1152000;

    if (baudrate <= 1500000)
        return B1500000;

    return B2000000;
}


static int set_attr_baudrate(struct termios *attr, uint32_t baudrate) {
    speed_t speed = get_speed(baudrate);

    if (cfsetispeed(attr, speed) || cfsetospeed(attr, speed))
        return HAT_SERIAL_ERROR;

    return HAT_SERIAL_SUCCESS;
}


static int set_attr_byte_size(struct termios *attr, uint32_t byte_size) {
    attr->c_cflag &= ~CSIZE;

    if (byte_size == 5) {
        attr->c_cflag |= CS5;

    } else if (byte_size == 6) {
        attr->c_cflag |= CS6;

    } else if (byte_size == 7) {
        attr->c_cflag |= CS7;

    } else if (byte_size == 8) {
        attr->c_cflag |= CS8;

    } else {
        return HAT_SERIAL_ERROR;
    }

    return HAT_SERIAL_SUCCESS;
}


static int set_attr_parity(struct termios *attr, char parity) {
    attr->c_iflag &= ~(INPCK | ISTRIP);

    if (parity == 'N') {
        attr->c_cflag &= ~(PARENB | PARODD);

    } else if (parity == 'E') {
        attr->c_cflag &= ~PARODD;
        attr->c_cflag |= PARENB;

    } else if (parity == 'O') {
        attr->c_cflag |= (PARENB | PARODD);

    } else if (parity == 'M') {
        // TODO CMSPAR not in POSIX
        // attr->c_cflag |= (PARENB | PARODD | CMSPAR);
        attr->c_cflag |= (PARENB | PARODD);

    } else if (parity == 'S') {
        attr->c_cflag &= ~PARODD;
        // TODO CMSPAR not in POSIX
        // attr->c_cflag |= (PARENB | CMSPAR);
        attr->c_cflag |= PARENB;

    } else {
        return HAT_SERIAL_ERROR;
    }

    return HAT_SERIAL_SUCCESS;
}


static int set_attr_stop_bits(struct termios *attr, uint8_t stop_bits) {
    if (stop_bits == 1) {
        attr->c_cflag &= ~CSTOPB;

    } else if (stop_bits == 2) {
        attr->c_cflag |= CSTOPB;

    } else {
        return HAT_SERIAL_ERROR;
    }

    return HAT_SERIAL_SUCCESS;
}


static void set_attr_xonxoff(struct termios *attr, bool xonxoff) {
    if (xonxoff) {
        attr->c_iflag |= (IXON | IXOFF | IXANY);

    } else {
        attr->c_iflag &= ~(IXON | IXOFF | IXANY);
    }
}


static void set_attr_rtscts(struct termios *attr, bool rtscts) {
    // TODO CRTSCTS not in POSIX
    // if (rtscts) {
    //     attr->c_cflag |= CRTSCTS;

    // } else {
    //     attr->c_cflag &= CRTSCTS;
    // }
}


static void set_attr_dsrdtr(struct termios *attr, bool dsrdtr) {
    // TODO
}


static int open_port(char *port, uint32_t baudrate, uint8_t byte_size,
                     char parity, uint8_t stop_bits, bool xonxoff, bool rtscts,
                     bool dsrdtr) {
    int fd = open(port, O_RDWR | O_NOCTTY | O_NONBLOCK);
    if (fd < 0)
        return -1;

    struct termios attr;
    if (!tcgetattr(fd, &attr))
        goto error;

    attr.c_iflag &= ~(IGNBRK | INLCR | IGNCR | ICRNL);
    attr.c_oflag &= ~(OPOST | ONLCR | OCRNL);
    attr.c_cflag |= (CREAD | CLOCAL);
    attr.c_lflag &= ~(ISIG | ICANON | ECHO | ECHOE | ECHOK | ECHONL | IEXTEN);

    attr.c_cc[VMIN] = 0;
    attr.c_cc[VTIME] = 0;

    if (set_attr_baudrate(&attr, baudrate))
        goto error;

    if (set_attr_byte_size(&attr, byte_size))
        goto error;

    if (set_attr_parity(&attr, parity))
        goto error;

    if (set_attr_stop_bits(&attr, stop_bits))
        goto error;

    set_attr_xonxoff(&attr, xonxoff);
    set_attr_rtscts(&attr, rtscts);
    set_attr_dsrdtr(&attr, dsrdtr);

    if (tcsetattr(fd, TCSANOW, &attr))
        goto error;

    return fd;

error:
    if (fd >= 0)
        close(fd);

    return -1;
}


static int clear_fd(int fd) {
    uint8_t buff[1024];

    while (true) {
        int result = read(fd, buff, sizeof(buff));

        if (result > 0)
            continue;

        if (result == 0)
            return HAT_SERIAL_SUCCESS;

        if (errno == EAGAIN)
            return HAT_SERIAL_SUCCESS;

        if (errno == EINTR)
            continue;

        return HAT_SERIAL_ERROR;
    }
}


static void send_ev(hat_serial_t *s) {
    if (s->ev_w_fd < 0)
        return;

    write(s->ev_w_fd, "x", 1);
}


static int serial_read(hat_serial_t *s) {
    hat_serial_buff_t *buff = s->in_buff;

    size_t buff_len = get_buff_len(buff);
    if (buff->size <= buff_len)
        return HAT_SERIAL_SUCCESS;

    struct iovec iov[2];
    int iov_len;

    if (buff_len <= buff->size - buff->tail) {
        iov[0] = (struct iovec){.iov_base = buff->data + buff->tail + 1,
                                .iov_len = buff_len};
        iov_len = 1;

    } else {
        iov[0] = (struct iovec){.iov_base = buff->data + buff->tail + 1,
                                .iov_len = buff->size - buff->tail};
        iov[1] = (struct iovec){.iov_base = buff->data,
                                .iov_len = buff_len - buff->size + buff->tail};
        iov_len = 2;
    }

    int result = readv(s->port_fd, iov, iov_len);

    if (result > 0) {
        move_buff_tail(buff, result);

        if (s->in_cb)
            s->in_cb(s);

        return HAT_SERIAL_SUCCESS;
    }

    if (result == 0)
        return HAT_SERIAL_SUCCESS;

    if (errno == EAGAIN || errno == EINTR)
        return HAT_SERIAL_SUCCESS;

    return HAT_SERIAL_ERROR;
}


static int serial_write(hat_serial_t *s) {
    hat_serial_buff_t *buff = s->out_buff;

    size_t buff_len = get_buff_len(buff);
    if (!buff_len)
        return HAT_SERIAL_SUCCESS;

    struct iovec iov[2];
    int iov_len;

    if (buff_len <= buff->size - buff->head) {
        iov[0] = (struct iovec){.iov_base = buff->data + buff->head + 1,
                                .iov_len = buff_len};
        iov_len = 1;

    } else {
        iov[0] = (struct iovec){.iov_base = buff->data + buff->head + 1,
                                .iov_len = buff->size - buff->head};
        iov[1] = (struct iovec){.iov_base = buff->data,
                                .iov_len = buff_len - buff->size + buff->head};
        iov_len = 2;
    }

    int result = writev(s->port_fd, iov, iov_len);

    if (result > 0) {
        move_buff_head(buff, result);

        if (s->out_cb && buff_len == result)
            s->out_cb(s);

        return HAT_SERIAL_SUCCESS;
    }

    if (result == 0)
        return HAT_SERIAL_SUCCESS;

    if (errno == EAGAIN || errno == EINTR)
        return HAT_SERIAL_SUCCESS;

    return HAT_SERIAL_ERROR;
}


static void *serial_thread(void *arg) {
    hat_serial_t *s = arg;
    hat_serial_buff_t *in_buff = s->in_buff;
    hat_serial_buff_t *out_buff = s->out_buff;

    struct pollfd fds[2] = {{.fd = s->ev_r_fd, .events = POLLIN},
                            {.fd = s->port_fd}};

    while (!atomic_load(&(s->is_closing))) {
        if (clear_fd(s->ev_r_fd))
            break;

        if (serial_read(s))
            break;

        if (serial_write(s))
            break;

        fds[1].events = 0;

        if (in_buff->size > get_buff_len(in_buff))
            fds[1].events |= POLLIN;

        if (get_buff_len(out_buff))
            fds[1].events |= POLLOUT;

        if (poll(fds, 2, -1)) {
            if (errno != EINTR)
                break;
        }
    }

    if (s->port_fd >= 0) {
        close(s->port_fd);
        s->port_fd = -1;
    }

    if (s->ev_r_fd >= 0) {
        close(s->ev_r_fd);
        s->ev_r_fd = -1;
    }

    if (s->close_cb)
        s->close_cb(s);

    return NULL;
}


hat_serial_t *hat_serial_create(hat_allocator_t *a, size_t in_buff_size,
                                size_t out_buff_size, hat_serial_cb_t close_cb,
                                hat_serial_cb_t in_cb, hat_serial_cb_t out_cb,
                                void *ctx) {
    hat_serial_t *s = NULL;
    hat_serial_buff_t *in_buff = NULL;
    hat_serial_buff_t *out_buff = NULL;

    s = hat_allocator_alloc(a, sizeof(hat_serial_t));
    if (!s)
        goto error;

    in_buff = create_buff(a, in_buff_size);
    if (!in_buff)
        goto error;

    out_buff = create_buff(a, out_buff_size);
    if (!out_buff)
        goto error;

    *s = (hat_serial_t){.a = a,
                        .in_buff = in_buff,
                        .out_buff = out_buff,
                        .close_cb = close_cb,
                        .in_cb = in_cb,
                        .out_cb = out_cb,
                        .ctx = ctx,
                        .port_fd = -1,
                        .ev_r_fd = -1,
                        .ev_w_fd = -1,
                        .is_running = false,
                        .is_closing = false};

    return s;

error:
    if (in_buff)
        hat_allocator_free(a, in_buff);

    if (out_buff)
        hat_allocator_free(a, out_buff);

    if (s)
        hat_allocator_free(a, s);

    return NULL;
}


void hat_serial_destroy(hat_serial_t *s) {
    atomic_store(&(s->is_closing), true);

    send_ev(s);

    if (s->is_running) {
        pthread_join(s->thread, NULL);
        s->is_running = false;
    }

    if (s->port_fd >= 0)
        close(s->port_fd);

    if (s->ev_r_fd >= 0)
        close(s->ev_r_fd);

    if (s->ev_w_fd >= 0)
        close(s->ev_w_fd);

    hat_allocator_free(s->a, s->in_buff);
    hat_allocator_free(s->a, s->out_buff);
    hat_allocator_free(s->a, s);
}


int hat_serial_open(hat_serial_t *s, char *port, uint32_t baudrate,
                    uint8_t byte_size, char parity, uint8_t stop_bits,
                    bool xonxoff, bool rtscts, bool dsrdtr) {
    if (s->port_fd >= 0 || s->ev_r_fd >= 0 || s->ev_w_fd >= 0 ||
        s->is_running || s->is_closing)
        return HAT_SERIAL_ERROR;

    s->port_fd = open_port(port, baudrate, byte_size, parity, stop_bits,
                           xonxoff, rtscts, dsrdtr);
    if (s->port_fd < 0)
        goto error;

    int ev_fds[2];
    if (!pipe(ev_fds))
        goto error;

    s->ev_r_fd = ev_fds[0];
    s->ev_w_fd = ev_fds[1];

    if (!fcntl(s->ev_r_fd, F_SETFL, O_NONBLOCK))
        goto error;

    if (!fcntl(s->ev_w_fd, F_SETFL, O_NONBLOCK))
        goto error;

    if (!pthread_create(&(s->thread), NULL, serial_thread, s))
        goto error;

    s->is_running = true;

error:
    if (s->port_fd >= 0)
        close(s->port_fd);

    if (s->ev_r_fd >= 0)
        close(s->ev_r_fd);

    if (s->ev_w_fd >= 0)
        close(s->ev_w_fd);

    return HAT_SERIAL_ERROR;
}


void hat_serial_close(hat_serial_t *s) {
    atomic_store(&(s->is_closing), true);

    send_ev(s);

    if (s->ev_w_fd >= 0) {
        close(s->ev_w_fd);
        s->ev_w_fd = -1;
    }
}


size_t hat_serial_get_in_buff_size(hat_serial_t *s) { return s->in_buff->size; }


size_t hat_serial_get_out_buff_size(hat_serial_t *s) {
    return s->out_buff->size;
}


size_t hat_serial_get_in_buff_len(hat_serial_t *s) {
    return get_buff_len(s->in_buff);
}


size_t hat_serial_get_out_buff_len(hat_serial_t *s) {
    return get_buff_len(s->out_buff);
}


void *hat_serial_get_ctx(hat_serial_t *s) { return s->ctx; }


int hat_serial_read(hat_serial_t *s, uint8_t *data, size_t data_len) {
    hat_serial_buff_t *buff = s->in_buff;

    if (data_len > get_buff_len(buff))
        return HAT_SERIAL_ERROR;

    if (buff->size - buff->head >= data_len) {
        memcpy(data, buff->data + buff->head + 1, data_len);

    } else {
        memcpy(data, buff->data + buff->head + 1, buff->size - buff->head);
        memcpy(data + buff->size - buff->head, buff->data,
               data_len - buff->size + buff->head);
    }

    move_buff_head(buff, data_len);

    send_ev(s);

    return HAT_SERIAL_SUCCESS;
}


int hat_serial_write(hat_serial_t *s, uint8_t *data, size_t data_len) {
    hat_serial_buff_t *buff = s->out_buff;

    if (data_len > (buff->size - get_buff_len(buff)))
        return HAT_SERIAL_ERROR;

    if (buff->size - buff->tail >= data_len) {
        memcpy(buff->data + buff->tail + 1, data, data_len);

    } else {
        memcpy(buff->data + buff->tail + 1, data, buff->size - buff->tail);
        memcpy(buff->data, data + buff->size - buff->tail,
               data_len - buff->size + buff->tail);
    }

    move_buff_tail(buff, data_len);

    send_ev(s);

    return HAT_SERIAL_SUCCESS;
}


size_t hat_serial_clear_in_buff(hat_serial_t *s) {
    size_t len = hat_serial_get_in_buff_len(s);
    move_buff_head(s->in_buff, len);

    send_ev(s);

    return len;
}
