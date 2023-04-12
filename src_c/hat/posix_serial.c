#include "serial.h"
#include "ring.h"

#include <errno.h>
#include <fcntl.h>
#include <poll.h>
#include <pthread.h>
#include <stdatomic.h>
#include <string.h>
#include <sys/uio.h>
#include <termios.h>
#include <unistd.h>


struct hat_serial_t {
    hat_allocator_t *a;
    hat_ring_t *in_buff;
    hat_ring_t *out_buff;
    hat_serial_cb_t close_cb;
    hat_serial_cb_t in_cb;
    hat_serial_cb_t out_cb;
    void *ctx;
    volatile int port_fd;
    volatile int notify_r_fd;
    int notify_w_fd;
    pthread_t thread;
    bool is_running;
    volatile _Atomic bool is_closing;
};


static void close_fd(volatile int *fd) {
    if (*fd < 0)
        return;

    close(*fd);
    *fd = -1;
}


static hat_serial_error_t clear_notifications(hat_serial_t *s) {
    uint8_t buff[1024];

    while (true) {
        int result = read(s->notify_r_fd, buff, sizeof(buff));

        if (result > 0)
            continue;

        if (result == 0)
            return HAT_SERIAL_SUCCESS;

        if (errno == EAGAIN)
            return HAT_SERIAL_SUCCESS;

        return HAT_SERIAL_ERROR_IO;
    }
}


static void notify_thread(hat_serial_t *s) {
    if (s->notify_w_fd < 0)
        return;

    write(s->notify_w_fd, "x", 1);
}


static hat_serial_error_t get_speed(uint32_t baudrate, speed_t *speed) {
    switch (baudrate) {
    case 0:
        *speed = B0;
        break;
    case 75:
        *speed = B75;
        break;
    case 110:
        *speed = B110;
        break;
    case 134:
        *speed = B134;
        break;
    case 150:
        *speed = B150;
        break;
    case 200:
        *speed = B200;
        break;
    case 300:
        *speed = B300;
        break;
    case 600:
        *speed = B600;
        break;
    case 1200:
        *speed = B1200;
        break;
    case 1800:
        *speed = B1800;
        break;
    case 2400:
        *speed = B2400;
        break;
    case 4800:
        *speed = B4800;
        break;
    case 9600:
        *speed = B9600;
        break;
    case 19200:
        *speed = B19200;
        break;
    case 38400:
        *speed = B38400;
        break;
    case 57600:
        *speed = B57600;
        break;
    case 115200:
        *speed = B115200;
        break;
    case 230400:
        *speed = B230400;
        break;
    case 460800:
        *speed = B460800;
        break;
    case 500000:
        *speed = B500000;
        break;
    case 576000:
        *speed = B576000;
        break;
    case 921600:
        *speed = B921600;
        break;
    case 1000000:
        *speed = B1000000;
        break;
    case 1152000:
        *speed = B1152000;
        break;
    case 1500000:
        *speed = B1500000;
        break;
    case 2000000:
        *speed = B2000000;
        break;
    default:
        return HAT_SERIAL_ERROR_BAUDRATE;
    }

    return HAT_SERIAL_SUCCESS;
}


static hat_serial_error_t set_attr_baudrate(struct termios *attr,
                                            uint32_t baudrate) {
    speed_t speed;
    if (get_speed(baudrate, &speed))
        return HAT_SERIAL_ERROR_BAUDRATE;

    if (cfsetispeed(attr, speed) || cfsetospeed(attr, speed))
        return HAT_SERIAL_ERROR_BAUDRATE;

    return HAT_SERIAL_SUCCESS;
}


static hat_serial_error_t set_attr_bytesize(struct termios *attr,
                                            uint32_t bytesize) {
    attr->c_cflag &= ~CSIZE;

    if (bytesize == 5) {
        attr->c_cflag |= CS5;

    } else if (bytesize == 6) {
        attr->c_cflag |= CS6;

    } else if (bytesize == 7) {
        attr->c_cflag |= CS7;

    } else if (bytesize == 8) {
        attr->c_cflag |= CS8;

    } else {
        return HAT_SERIAL_ERROR_BYTESIZE;
    }

    return HAT_SERIAL_SUCCESS;
}


static hat_serial_error_t set_attr_parity(struct termios *attr, char parity) {
    attr->c_iflag &= ~(INPCK | ISTRIP);

    if (parity == 'N') {
        attr->c_cflag &= ~(PARENB | PARODD);

    } else if (parity == 'E') {
        attr->c_cflag &= ~PARODD;
        attr->c_cflag |= PARENB;

    } else if (parity == 'O') {
        attr->c_cflag |= (PARENB | PARODD);

    } else if (parity == 'M') {
#ifdef _DEFAULT_SOURCE
        attr->c_cflag |= (PARENB | PARODD | CMSPAR);
#else
        attr->c_cflag |= (PARENB | PARODD);
#endif

    } else if (parity == 'S') {
        attr->c_cflag &= ~PARODD;
#ifdef _DEFAULT_SOURCE
        attr->c_cflag |= (PARENB | CMSPAR);
#else
        attr->c_cflag |= PARENB;
#endif

    } else {
        return HAT_SERIAL_ERROR_PARITY;
    }

    return HAT_SERIAL_SUCCESS;
}


static hat_serial_error_t set_attr_stopbits(struct termios *attr,
                                            uint8_t stopbits) {
    if (stopbits == 1) {
        attr->c_cflag &= ~CSTOPB;

    } else if (stopbits == 2) {
        attr->c_cflag |= CSTOPB;

    } else {
        return HAT_SERIAL_ERROR_STOPBITS;
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
#ifdef _DEFAULT_SOURCE
    if (rtscts) {
        attr->c_cflag |= CRTSCTS;

    } else {
        attr->c_cflag &= CRTSCTS;
    }
#endif
}


static void set_attr_dsrdtr(struct termios *attr, bool dsrdtr) {
    // TODO
}


static hat_serial_error_t open_port(char *port, uint32_t baudrate,
                                    uint8_t bytesize, char parity,
                                    uint8_t stopbits, bool xonxoff, bool rtscts,
                                    bool dsrdtr, volatile int *fd) {
    hat_serial_error_t result;

    *fd = open(port, O_RDWR | O_NOCTTY | O_NONBLOCK);
    if (*fd < 0) {
        result = HAT_SERIAL_ERROR_OPEN;
        goto error;
    }

    struct termios attr;
    if (tcgetattr(*fd, &attr)) {
        result = HAT_SERIAL_ERROR_TERMIOS;
        goto error;
    }

    attr.c_iflag &= ~(IGNBRK | INLCR | IGNCR | ICRNL);
    attr.c_oflag &= ~(OPOST | ONLCR | OCRNL);
    attr.c_cflag |= (CREAD | CLOCAL);
    attr.c_lflag &= ~(ISIG | ICANON | ECHO | ECHOE | ECHOK | ECHONL | IEXTEN);

    attr.c_cc[VMIN] = 0;
    attr.c_cc[VTIME] = 0;

    result = set_attr_baudrate(&attr, baudrate);
    if (result)
        goto error;

    result = set_attr_bytesize(&attr, bytesize);
    if (result)
        goto error;

    result = set_attr_parity(&attr, parity);
    if (result)
        goto error;

    result = set_attr_stopbits(&attr, stopbits);
    if (result)
        goto error;

    set_attr_xonxoff(&attr, xonxoff);
    set_attr_rtscts(&attr, rtscts);
    set_attr_dsrdtr(&attr, dsrdtr);

    if (tcsetattr(*fd, TCSANOW, &attr)) {
        result = HAT_SERIAL_ERROR_TERMIOS;
        goto error;
    }

    // TODO update rts and dts

    return HAT_SERIAL_SUCCESS;

error:
    close_fd(fd);

    return result;
}


static hat_serial_error_t serial_read(hat_serial_t *s) {
    hat_ring_t *buff = s->in_buff;

    uint8_t *unused_data[2];
    size_t unused_data_len[2];
    hat_ring_unused(buff, unused_data, unused_data_len);

    if (!unused_data_len[0] && !unused_data_len[1])
        return HAT_SERIAL_SUCCESS;

    struct iovec iov[2] = {
        {.iov_base = unused_data[0], .iov_len = unused_data_len[0]},
        {.iov_base = unused_data[1], .iov_len = unused_data_len[1]}};

    int result = readv(s->port_fd, iov, (unused_data_len[1] ? 2 : 1));

    if (result > 0) {
        hat_ring_move_tail(buff, result);

        if (s->in_cb)
            s->in_cb(s);

        return HAT_SERIAL_SUCCESS;
    }

    if (result == 0)
        return HAT_SERIAL_SUCCESS;

    if (errno == EAGAIN)
        return HAT_SERIAL_SUCCESS;

    return HAT_SERIAL_ERROR_IO;
}


static hat_serial_error_t serial_write(hat_serial_t *s) {
    hat_ring_t *buff = s->out_buff;

    uint8_t *used_data[2];
    size_t used_data_len[2];
    hat_ring_used(buff, used_data, used_data_len);

    if (!used_data_len[0] && !used_data_len[1])
        return HAT_SERIAL_SUCCESS;

    struct iovec iov[2] = {
        {.iov_base = used_data[0], .iov_len = used_data_len[0]},
        {.iov_base = used_data[1], .iov_len = used_data_len[1]}};

    int result = writev(s->port_fd, iov, (used_data_len[1] ? 2 : 1));

    if (result > 0) {
        hat_ring_move_head(buff, result);

        if (s->out_cb && result == used_data_len[0] + used_data_len[1])
            s->out_cb(s);

        return HAT_SERIAL_SUCCESS;
    }

    if (result == 0)
        return HAT_SERIAL_SUCCESS;

    if (errno == EAGAIN)
        return HAT_SERIAL_SUCCESS;

    return HAT_SERIAL_ERROR_IO;
}


static void *serial_thread(void *arg) {
    hat_serial_t *s = arg;
    hat_ring_t *in_buff = s->in_buff;
    hat_ring_t *out_buff = s->out_buff;

    struct pollfd fds[2] = {{.fd = s->notify_r_fd, .events = POLLIN},
                            {.fd = s->port_fd}};

    while (!atomic_load(&(s->is_closing))) {
        if (fds[0].revents & ~POLLIN)
            break;

        if (fds[1].revents & ~(POLLIN | POLLOUT))
            break;

        if (clear_notifications(s))
            break;

        if (serial_read(s))
            break;

        if (serial_write(s))
            break;

        fds[1].events = 0;

        if (hat_ring_size(in_buff) > hat_ring_len(in_buff))
            fds[1].events |= POLLIN;

        if (hat_ring_len(out_buff))
            fds[1].events |= POLLOUT;

        if (poll(fds, 2, -1)) {
            if (errno == EAGAIN)
                continue;
        }
    }

    atomic_store(&(s->is_closing), true);

    close_fd(&(s->port_fd));
    close_fd(&(s->notify_r_fd));

    if (s->close_cb)
        s->close_cb(s);

    return NULL;
}


hat_serial_t *hat_serial_create(hat_allocator_t *a, size_t in_buff_size,
                                size_t out_buff_size, hat_serial_cb_t close_cb,
                                hat_serial_cb_t in_cb, hat_serial_cb_t out_cb,
                                void *ctx) {
    hat_serial_t *s = NULL;
    hat_ring_t *in_buff = NULL;
    hat_ring_t *out_buff = NULL;

    s = hat_allocator_alloc(a, sizeof(hat_serial_t));
    if (!s)
        goto error;

    in_buff = hat_ring_create(a, in_buff_size);
    if (!in_buff)
        goto error;

    out_buff = hat_ring_create(a, out_buff_size);
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
                        .notify_r_fd = -1,
                        .notify_w_fd = -1,
                        .is_running = false,
                        .is_closing = false};

    return s;

error:
    if (in_buff)
        hat_ring_destroy(in_buff);

    if (out_buff)
        hat_ring_destroy(out_buff);

    if (s)
        hat_allocator_free(a, s);

    return NULL;
}


void hat_serial_destroy(hat_serial_t *s) {
    atomic_store(&(s->is_closing), true);

    notify_thread(s);

    if (s->is_running) {
        pthread_join(s->thread, NULL);
        s->is_running = false;
    }

    close_fd(&(s->port_fd));
    close_fd(&(s->notify_r_fd));
    close_fd(&(s->notify_w_fd));

    hat_ring_destroy(s->in_buff);
    hat_ring_destroy(s->out_buff);

    hat_allocator_free(s->a, s);
}


hat_serial_error_t hat_serial_open(hat_serial_t *s, char *port,
                                   uint32_t baudrate, uint8_t bytesize,
                                   char parity, uint8_t stopbits, bool xonxoff,
                                   bool rtscts, bool dsrdtr) {
    if (s->port_fd >= 0 || s->notify_r_fd >= 0 || s->notify_w_fd >= 0 ||
        s->is_running || s->is_closing)
        return HAT_SERIAL_ERROR;

    hat_serial_error_t result =
        open_port(port, baudrate, bytesize, parity, stopbits, xonxoff, rtscts,
                  dsrdtr, &(s->port_fd));
    if (result)
        goto error;

    int ev_fds[2];
    if (pipe(ev_fds)) {
        result = HAT_SERIAL_ERROR_IO;
        goto error;
    }

    s->notify_r_fd = ev_fds[0];
    s->notify_w_fd = ev_fds[1];

    if (fcntl(s->notify_r_fd, F_SETFL, O_NONBLOCK) == -1) {
        result = HAT_SERIAL_ERROR_IO;
        goto error;
    }

    if (fcntl(s->notify_w_fd, F_SETFL, O_NONBLOCK) == -1) {
        result = HAT_SERIAL_ERROR_IO;
        goto error;
    }

    if (pthread_create(&(s->thread), NULL, serial_thread, s)) {
        result = HAT_SERIAL_ERROR_THREAD;
        goto error;
    }

    s->is_running = true;

    return HAT_SERIAL_SUCCESS;

error:
    close_fd(&(s->port_fd));
    close_fd(&(s->notify_r_fd));
    close_fd(&(s->notify_w_fd));

    return result;
}


void hat_serial_close(hat_serial_t *s) {
    atomic_store(&(s->is_closing), true);

    notify_thread(s);

    close_fd(&(s->notify_w_fd));
}


void *hat_serial_ctx(hat_serial_t *s) { return s->ctx; }


size_t hat_serial_available(hat_serial_t *s) {
    return hat_ring_len(s->in_buff);
}


size_t hat_serial_read(hat_serial_t *s, uint8_t *data, size_t data_len) {
    size_t result = hat_ring_read(s->in_buff, data, data_len);

    notify_thread(s);

    return result;
}


size_t hat_serial_write(hat_serial_t *s, uint8_t *data, size_t data_len) {
    size_t result = hat_ring_write(s->out_buff, data, data_len);

    notify_thread(s);

    return result;
}
