#include "device.h"

#include <atomic>
#include <cerrno>
#include <chrono>
#include <ctime>
#include <functional>
#include <optional>
#include <string>
#include <system_error>
#include <vector>

#include <fcntl.h>
#include <mqueue.h>
#include <signal.h>
#include <sys/stat.h>

namespace Revolution {
    // TODO: https://developer.toradex.com/linux-bsp/application-development/peripheral-access/gpio-linux
    Device::Device(const std::string& name) : name{name} {}

    const std::string& Device::get_name() const {
        return name;
    }

    static void close_message_queue(const mqd_t& descriptor) {
        auto status = mq_close(descriptor);

        if (status < 0)
            throw std::system_error{
                errno,
                std::system_category(),
                "Unable to close the message queue"
            };
    }

    static mq_attr get_message_queue_attributes(const mqd_t& descriptor) {
        mq_attr attributes;
        auto status = mq_getattr(descriptor, &attributes);

        if (status < 0)
            throw std::system_error{
                errno,
                std::system_category(),
                "Unable to get the message queue attributes"
            };

        return attributes;
    }

    static mqd_t open_message_queue(
            const std::string& name,
            const int& open_flag,
            const mode_t& mode = 0600,
            const std::optional<mq_attr> attributes = std::nullopt
    ) {
        auto descriptor = mq_open(
            name.data(),
            open_flag,
            mode,
            attributes ? &attributes.value() : nullptr
        );

        if (descriptor == (mqd_t) - 1)
            throw std::system_error{
                errno,
                std::system_category(),
                "Unable to open the message queue"
            };

        return descriptor;
    }

    std::string MessageQueue::receive() const {
        auto descriptor = open_message_queue(get_name(), O_RDONLY | O_CREAT);
        auto attributes = get_message_queue_attributes(descriptor);
        std::string raw_message(attributes.mq_msgsize, '\0');
        unsigned int priority;
        auto received_size = mq_receive(
            descriptor,
            raw_message.data(),
            raw_message.size(),
            &priority
        );

        close_message_queue(descriptor);

        if (received_size < 0)
            throw std::system_error{
                errno,
                std::system_category(),
                "Unable to receive from the message queue"
            };

        raw_message.resize(received_size);

        return raw_message;
    }

    void MessageQueue::send(
            const std::string& raw_message,
            const unsigned int& priority
    ) const {
        auto descriptor = open_message_queue(get_name(), O_WRONLY | O_CREAT);
        auto received_size = mq_send(
            descriptor,
            raw_message.data(),
            raw_message.size(),
            priority
        );

        close_message_queue(descriptor);

        if (received_size < 0)
            throw std::system_error{
                errno,
                std::system_category(),
                "Unable to receive from the message queue"
            };
    }

    std::string MessageQueue::timed_receive(
            const std::chrono::high_resolution_clock::duration& timeout
    ) const {
        auto absolute_timeout = timeout
            + std::chrono::high_resolution_clock::now().time_since_epoch();
        auto second = std::chrono::duration_cast<std::chrono::seconds>(
            absolute_timeout
        );
        auto nanosecond = std::chrono::duration_cast<std::chrono::nanoseconds>(
            absolute_timeout - second
        );
        std::timespec time_specification{second.count(), nanosecond.count()};

        auto descriptor = open_message_queue(get_name(), O_RDONLY | O_CREAT);
        auto attributes = get_message_queue_attributes(descriptor);
        std::string raw_message(attributes.mq_msgsize, '\0');
        unsigned int priority;
        auto received_size = mq_timedreceive(
            descriptor,
            raw_message.data(),
            raw_message.size(),
            &priority,
            &time_specification
        );

        close_message_queue(descriptor);

        if (received_size < 0)
            throw std::system_error{
                errno,
                std::system_category(),
                "Unable to receive from the message queue"
            };

        raw_message.resize(received_size);

        return raw_message;
    }

    void MessageQueue::unlink() const {
        auto status = mq_unlink(get_name().data());

        if (status < 0)
            throw std::system_error{
                errno,
                std::system_category(),
                "Unable to unlink the message queue"
            };
    }

    void MessageQueue::monitor(
            const std::atomic_bool& status,
            const std::function<void(const std::string&)>& handler,
            const std::chrono::high_resolution_clock::duration& timeout
    ) const {
        while (status) {
            try {
                auto message = timed_receive(timeout);

                handler(message);
            } catch (const std::system_error& system_error) {
                auto equivalent = std::system_category().equivalent(
                    system_error.code(),
                    ETIMEDOUT
                );

                if (!equivalent)
                    throw;
            }
        }
    }

    GPIO::GPIO(const std::string& name, const unsigned int& offset)
            : Device{name}, offset{offset} {}

    const unsigned int& GPIO::get_offset() const {
        return offset;
    }

    bool GPIO::get_active_low() const {
        // TODO: https://github.com/toradex/torizon-samples/blob/bullseye/gpio/c/gpio-toggle.c

        return false;
    }

    void GPIO::set_active_low(const bool& active_low) const {
        // TODO: https://github.com/toradex/torizon-samples/blob/bullseye/gpio/c/gpio-toggle.c

        (void) active_low;
    }

    void GPIO::monitor(
            const std::function<
                void(const std::string&, const unsigned int&, const bool&)
            >& handler
    ) const {
        // TODO: https://github.com/toradex/torizon-samples/blob/bullseye/gpio/c/gpio-event.c

        (void) handler;
    }

    const std::string PWM::Polarity::normal{"normal"};
    const std::string PWM::Polarity::inversed{"inversed"};

    void PWM::enable(
            const unsigned int& period,
            const unsigned int& duty_cycle,
            const Polarity& polarity
    ) const {
        // TODO: https://github.com/toradex/torizon-samples/tree/bullseye/pwm

        (void) period;
        (void) duty_cycle;
        (void) polarity;
    }

    void PWM::disable() const {
        // TODO: https://github.com/toradex/torizon-samples/tree/bullseye/pwm
    }

    void SPI::transmit(const std::string& data) const {
        // TODO: https://github.com/torvalds/linux/blob/v5.15/tools/spi/spidev_test.c

        (void) data;
    }

    std::string SPI::receive() const {
        // TODO: https://github.com/torvalds/linux/blob/v5.15/tools/spi/spidev_test.c

        return "";
    }

    std::string SPI::transmit_and_receive(const std::string& data) const {
        // TODO: https://github.com/torvalds/linux/blob/v5.15/tools/spi/spidev_test.c

        (void) data;

        return "";
    }

    void UART::transmit(const std::string& data) const {
        // TODO: https://developer.toradex.com/linux-bsp/application-development/peripheral-access/uart-linux#boards

        (void) data;
    }

    std::string UART::receive() const {
        // TODO: https://developer.toradex.com/linux-bsp/application-development/peripheral-access/uart-linux#boards

        return "";
    }
}
