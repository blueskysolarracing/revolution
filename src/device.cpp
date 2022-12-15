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
        auto return_value = mq_close(descriptor);

        if (return_value < 0)
            throw std::system_error{
                errno,
                std::system_category(),
                "Unable to close the message queue"
            };
    }

    static mq_attr get_message_queue_attributes(const mqd_t& descriptor) {
        mq_attr attributes;
        auto return_value = mq_getattr(descriptor, &attributes);

        if (return_value < 0)
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
        auto return_value = mq_unlink(get_name().data());

        if (return_value < 0)
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

    std::vector<bool> GPIO::get(
            const std::vector<unsigned int>& offsets,
            const Active& active,
            const std::string& consumer_name
    ) const {
        std::vector<int> raw_values(offsets.size(), 0);

        bool active_low;

        switch (active) {
            case Active::low:
                active_low = true;
                break;
            case Active::high:
                active_low = false;
                break;
            default:
                throw std::domain_error{"Unknown gpio active encountered."};
        }

        auto return_value = gpiod_ctxless_get_value_multiple(
            get_name().data(),
            offsets.data(),
            raw_values.data(),
            offsets.size(),
            active_low,
            consumer_name.data()
        );

        if (return_value < 0)
            throw std::system_error{
                errno,
                std::system_category(),
                "Unable to get gpio value"
            };

        return {raw_values.begin(), raw_values.end()};
    }

    void GPIO::set(
            const std::vector<unsigned int>& offsets,
            const std::vector<bool>& values,
            const Active& active,
            const std::string& consumer_name
    ) const {
        assert(offsets.size() == values.size());

        std::vector<int> raw_values{values.begin(), values.end()};
        bool active_low;

        switch (active) {
            case Active::low:
                active_low = true;
                break;
            case Active::high:
                active_low = false;
                break;
            default:
                throw std::domain_error{"Unknown gpio active encountered."};
        }

        auto return_value = gpiod_ctxless_set_value_multiple(
            get_name().data(),
            offsets.data(),
            raw_values.data(),
            offsets.size(),
            active_low,
            consumer_name.data(),
            nullptr,
            nullptr
        );

        if (return_value < 0)
            throw std::system_error{
                errno,
                std::system_category(),
                "Unable to set gpio value"
            };
    }

    struct GPIOEventData {
        const std::atomic_bool& status;
        const std::function<void(const GPIO::Event&, const unsigned int&)>& callback;
    };

    static int handle_gpio_event(
            int event_type,
            unsigned int offset,
            [[maybe_unused]] const std::timespec *timestamp,
            void *data
    ) {
        const auto& gpio_event_data = *(GPIOEventData*) data;

        switch (event_type) {
            case GPIOD_CTXLESS_EVENT_CB_TIMEOUT:
                break;
            case GPIOD_CTXLESS_EVENT_CB_RISING_EDGE:
                gpio_event_data.callback(GPIO::Event::rising_edge, offset);
                break;
            case GPIOD_CTXLESS_EVENT_CB_FALLING_EDGE:
                gpio_event_data.callback(GPIO::Event::falling_edge, offset);
                break;
            default:
                return GPIOD_CTXLESS_EVENT_CB_RET_ERR;
        }

        return gpio_event_data.status
            ? GPIOD_CTXLESS_EVENT_CB_RET_OK
            : GPIOD_CTXLESS_EVENT_CB_RET_STOP;
    }

    void GPIO::monitor(
            const Event& event,
            const std::vector<unsigned int>& offsets,
            const Active& active,
            const std::string& consumer_name,
            const std::atomic_bool& status,
            const std::chrono::high_resolution_clock::duration& timeout,
            const std::function<void(const Event&, const unsigned int&)>&
                callback
    ) const {
        int event_type;

        switch (event) {
            case Event::rising_edge:
                event_type = GPIOD_CTXLESS_EVENT_RISING_EDGE;
                break;
            case Event::falling_edge:
                event_type = GPIOD_CTXLESS_EVENT_FALLING_EDGE;
                break;
            case Event::both_edges:
                event_type = GPIOD_CTXLESS_EVENT_BOTH_EDGES;
                break;
            default:
                throw std::domain_error{"Unknown gpio event encountered."};
        }

        bool active_low;

        switch (active) {
            case Active::low:
                active_low = true;
                break;
            case Active::high:
                active_low = false;
                break;
            default:
                throw std::domain_error{"Unknown gpio active encountered."};
        }

        auto time_specification = convert_to_time_specification(timeout);
        GPIOEventData gpio_event_data{status, callback};
        auto return_value = gpiod_ctxless_event_monitor_multiple(
            get_name().data(),
            event_type,
            offsets.data(),
            offsets.size(),
            active_low,
            consumer_name.data(),
            &time_specification,
            nullptr,
            &handle_gpio_event,
            &gpio_event_data
        );

        if (return_value < 0)
            throw std::system_error{
                errno,
                std::system_category(),
                "Error occurred while monitoring gpio"
            };
    }

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
