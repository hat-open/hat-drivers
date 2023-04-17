#include "serial.h"


char *hat_serial_error_msg(hat_serial_error_t error) {
    switch (error) {
    case HAT_SERIAL_ERROR_MEMORY:
        return "memory allocation error";

    case HAT_SERIAL_ERROR_IO:
        return "IO error";

    case HAT_SERIAL_ERROR_BAUDRATE:
        return "invalid baudrate";

    case HAT_SERIAL_ERROR_BYTESIZE:
        return "invalid byte size";

    case HAT_SERIAL_ERROR_PARITY:
        return "invalid parity";

    case HAT_SERIAL_ERROR_STOPBITS:
        return "invalid stop bits";

    case HAT_SERIAL_ERROR_OPEN:
        return "open error";

    case HAT_SERIAL_ERROR_TERMIOS:
        return "termios error";

    case HAT_SERIAL_ERROR_THREAD:
        return "thread create error";

    case HAT_SERIAL_ERROR_IOCTL:
        return "ioctl error";
    }

    return "unknown error";
}
