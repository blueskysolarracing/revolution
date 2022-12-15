#include "device.h"

#include <atomic>
#include <cassert>
#include <cerrno>
#include <chrono>
#include <ctime>
#include <functional>
#include <optional>
#include <string>
#include <system_error>

#include <fcntl.h>
#include <gpiod.h>
#include <mqueue.h>
#include <sys/stat.h>

namespace Revolution {
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

    static std::timespec convert_to_time_specification(
            const std::chrono::high_resolution_clock::duration& timeout
    ) {
        auto second = std::chrono::duration_cast<std::chrono::seconds>(
            timeout
        );
        auto nanosecond = std::chrono::duration_cast<std::chrono::nanoseconds>(
            timeout - second
        );
        std::timespec time_specification{second.count(), nanosecond.count()};

        return time_specification;
    }

    std::string MessageQueue::timed_receive(
            const std::chrono::high_resolution_clock::duration& timeout
    ) const {
        auto absolute_timeout = timeout
            + std::chrono::high_resolution_clock::now().time_since_epoch();
        auto time_specification = convert_to_time_specification(
            absolute_timeout
        );

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
            const std::chrono::high_resolution_clock::duration& timeout,
            const std::function<void(const std::string&)>& callback
    ) const {
        while (status) {
            try {
                auto message = timed_receive(timeout);

                callback(message);
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

    bool GPIO::get_value(
            const unsigned int& offset,
            const bool& active_low,
            const std::string& consumer_name
    ) const {
        auto values = get_values({offset}, active_low, consumer_name);

        assert(values.size() == 1);

        return values.front();
    }

    std::vector<bool> GPIO::get_values(
            const std::vector<unsigned int>& offsets,
            const bool& active_low,
            const std::string& consumer_name
    ) const {
        std::vector<int> raw_values(offsets.size(), 0);

        assert(offsets.size());

        auto status = gpiod_ctxless_get_value_multiple(
            get_name().data(),
            offsets.data(),
            raw_values.data(),
            offsets.size(),
            active_low,
            consumer_name.data()
        );

        if (status < 0)
            throw std::system_error{
                errno,
                std::system_category(),
                "Unable to get gpio value"
            };

        return {raw_values.begin(), raw_values.end()};
    }

    void GPIO::set_value(
            const unsigned int& offset,
            const bool& value,
            const bool& active_low,
            const std::string& consumer_name
    ) const {
        set_values({offset}, {value}, active_low, consumer_name);
    }

    void GPIO::set_values(
            const std::vector<unsigned int>& offsets,
            const std::vector<bool>& values,
            const bool& active_low,
            const std::string& consumer_name
    ) const {
        assert(offsets.size() == values.size());

        std::vector<int> raw_values{values.begin(), values.end()};
        auto status = gpiod_ctxless_set_value_multiple(
            get_name().data(),
            offsets.data(),
            raw_values.data(),
            offsets.size(),
            active_low,
            consumer_name.data(),
            nullptr,
            nullptr
        );

        if (status < 0)
            throw std::system_error{
                errno,
                std::system_category(),
                "Unable to set gpio value"
            };
    }

    void GPIO::monitor_value(
            const Event& event,
            const unsigned int& offset,
            const bool& active_low,
            const std::string& consumer_name,
            const std::chrono::high_resolution_clock::duration& timeout,
            const std::function<bool(const Event& event, const unsigned int&)>&
                callback
    ) const {
        monitor_values(
            event,
            {offset},
            active_low,
            consumer_name,
            timeout,
            callback
        );
    }

    static int handle_gpio_event(
            int event_type,
            unsigned int offset,
            [[maybe_unused]] const struct std::timespec *timestamp,
            void *data
    ) {
        const auto& callback = *(
            const std::function<
                bool(const GPIO::Event& event, const unsigned int&)
            >*
        ) data;

        GPIO::Event event;

        switch (event_type) {
            case GPIOD_LINE_EVENT_RISING_EDGE:
                event = GPIO::Event::rising_edge;
                break;
            case GPIOD_LINE_EVENT_FALLING_EDGE:
                event = GPIO::Event::falling_edge;
                break;
            default:
                return GPIOD_CTXLESS_EVENT_CB_RET_ERR;
        }

        auto status = callback(event, offset);

        return status
            ? GPIOD_CTXLESS_EVENT_CB_RET_OK
            : GPIOD_CTXLESS_EVENT_CB_RET_STOP;
    }

    void GPIO::monitor_values(
            const Event& event,
            const std::vector<unsigned int>& offsets,
            const bool& active_low,
            const std::string& consumer_name,
            const std::chrono::high_resolution_clock::duration& timeout,
            const std::function<bool(const Event& event, const unsigned int&)>&
                callback
    ) const {
        int event_type;

        switch (event) {
            case Event::rising_edge:
                event_type = GPIOD_LINE_EVENT_RISING_EDGE;
                break;
            case Event::falling_edge:
                event_type = GPIOD_LINE_EVENT_FALLING_EDGE;
                break;
            default:
                throw std::domain_error{"Unknown gpio event encountered."};
        }

        auto time_specification = convert_to_time_specification(timeout);

        auto status = gpiod_ctxless_event_monitor_multiple(
            get_name().data(),
            event_type,
            offsets.data(),
            offsets.size(),
            active_low,
            consumer_name.data(),
            &time_specification,
            nullptr,
            &handle_gpio_event,
            (void *) &callback
        );

        if (status < 0)
            throw std::system_error{
                errno,
                std::system_category(),
                "Error occurred while monitoring gpio"
            };
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
