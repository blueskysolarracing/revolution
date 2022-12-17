#include "device.h"

#include <atomic>
#include <cassert>
#include <cerrno>
#include <chrono>
#include <cstddef>
#include <ctime>
#include <fstream>
#include <functional>
#include <optional>
#include <stdexcept>
#include <string>
#include <system_error>
#include <vector>

#include <fcntl.h>
#include <gpiod.h>
#include <linux/spi/spidev.h>
#include <linux/spi/spi.h>
#include <mqueue.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <termios.h>
#include <unistd.h>

namespace Revolution {
    Device::Device(const std::string& name) : name{name} {}

    const std::string& Device::get_name() const {
        return name;
    }

    MessageQueue::Configuration::Configuration(
            const unsigned int& max_message_count,
            const unsigned int& max_message_size
    ) :
            max_message_count{max_message_count},
            max_message_size{max_message_size} {}

    const unsigned int&
            MessageQueue::Configuration::get_max_message_count() const {
        return max_message_count;
    }

    const unsigned int&
            MessageQueue::Configuration::get_max_message_size() const {
        return max_message_size;
    }

    static mqd_t open_message_queue(
            const std::string& name,
            const std::vector<MessageQueue::Flag>& flags,
            const MessageQueue::Mode& mode,
            const std::optional<MessageQueue::Configuration> configuration
    ) {
        int open_flag{};

        for (const auto& flag : flags)
            open_flag |= static_cast<int>(flag);

        mq_attr attributes;
        mq_attr* attributes_pointer;

        if (configuration) {
            attributes.mq_maxmsg = configuration.value()
                .get_max_message_count();
            attributes.mq_msgsize = configuration.value()
                .get_max_message_size();
            attributes_pointer = &attributes;
        } else
            attributes_pointer = nullptr;

        auto descriptor = mq_open(
            name.data(),
            open_flag,
            (mode_t) mode,
            attributes_pointer
        );

        if (descriptor == (mqd_t) - 1)
            throw std::system_error{
                errno,
                std::system_category(),
                "Unable to open the message queue"
            };

        return descriptor;
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

    std::string MessageQueue::receive(
            const std::vector<Flag> flags,
            const Mode& mode,
            const std::optional<Configuration>& configuration
    ) const {
        auto descriptor = open_message_queue(
            get_name(),
            flags,
            mode,
            configuration
        );
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
            const unsigned int& priority,
            const std::vector<Flag> flags,
            const Mode& mode,
            const std::optional<Configuration>& configuration
    ) const {
        auto descriptor = open_message_queue(
            get_name(),
            flags,
            mode,
            configuration
        );
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
            const std::chrono::high_resolution_clock::duration& timeout,
            const std::vector<Flag> flags,
            const Mode& mode,
            const std::optional<Configuration>& configuration
    ) const {
        auto absolute_timeout = timeout
            + std::chrono::high_resolution_clock::now().time_since_epoch();
        auto time_specification = convert_to_time_specification(
            absolute_timeout
        );
        auto descriptor = open_message_queue(
            get_name(),
            flags,
            mode,
            configuration
        );
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
            const std::function<void(const std::string&)>& callback,
            const std::vector<Flag> flags,
            const Mode& mode,
            const std::optional<Configuration>& configuration
    ) const {
        while (status) {
            try {
                auto message = timed_receive(
                    timeout,
                    flags,
                    mode,
                    configuration
                );

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
        auto active_low = static_cast<bool>(active);
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
        auto active_low = static_cast<bool>(active);
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
        const std::function<void(const GPIO::Event&, const unsigned int&)>&
            callback;
    };

    static int handle_gpio_event(
            int event_type,
            unsigned int offset,
            [[maybe_unused]] const std::timespec* timestamp,
            void* data
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
        auto event_type = static_cast<int>(event);
        auto active_low = static_cast<bool>(active);
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

    static void help_write(
        const std::string& filename,
        const std::string& data
    ) {
        std::ofstream ofstream;

        ofstream.exceptions(std::ofstream::failbit | std::ofstream::badbit);
        ofstream.open(filename, std::fstream::out);
        ofstream << data;
        ofstream.close();
    }

    void PWM::enable(
            const unsigned int& channel_index,
            const std::chrono::high_resolution_clock::duration& period,
            const std::chrono::high_resolution_clock::duration& duty_cycle,
            const Polarity& polarity
    ) const {
        help_write(get_name() + "/export", std::to_string(channel_index));

        auto directory_name = get_name()
            + "/pwmchip"
            + std::to_string(channel_index);

        help_write(
            directory_name + "/period",
            std::to_string(
                std::chrono::duration_cast<std::chrono::nanoseconds>(period)
                    .count()
            )
        );
        help_write(
            directory_name + "/duty_cycle",
            std::to_string(
                std::chrono::duration_cast<std::chrono::nanoseconds>(duty_cycle)
                    .count()
            )
        );

        std::string raw_polarity;

        switch (polarity) {
            case Polarity::normal:
                raw_polarity = "normal";
                break;
            case Polarity::inversed:
                raw_polarity = "inversed";
                break;
            default:
                throw std::domain_error{"Unknown polarity encountered"};
        }

        help_write(directory_name + "/polarity", raw_polarity);
        help_write(directory_name + "/enable", "1");
        help_write(get_name() + "/unexport", std::to_string(channel_index));
    }

    void PWM::disable(const unsigned int& channel_index) const {
        help_write(get_name() + "/export", std::to_string(channel_index));

        auto directory_name = get_name()
            + "/pwmchip"
            + std::to_string(channel_index);

        help_write(directory_name + "/enable", "0");
        help_write(get_name() + "/unexport", std::to_string(channel_index));
    }

    static int help_open(
            const std::string& filename,
            const int& flags
    ) {
        auto descriptor = open(filename.data(), flags);

        if (descriptor < 0)
            throw std::system_error{
                errno,
                std::system_category(),
                "Unable to open file."
            };

        return descriptor;
    }

    static void help_close(const int& descriptor) {
        auto return_value = close(descriptor);

        if (return_value < 0)
            throw std::system_error{
                errno,
                std::system_category(),
                "Unable to close file."
            };
    }

    static void help_ioctl(
        const int& descriptor,
        const unsigned long& request,
        void* const& data
    ) {
        auto return_value = ioctl(descriptor, request, data);

        if (return_value < 0)
            throw std::system_error{
                errno,
                std::system_category(),
                "Unable to manipulate device."
            };
    }

    static void transfer_spi(
            const int& descriptor,
            const std::optional<std::string>& transmitted_data,
            std::optional<std::string> received_data,
            const std::vector<SPI::Mode>& modes,
            const unsigned int& speed_hz,
            const unsigned char& bits_per_word
    ) {
        unsigned int data_size;

        if (transmitted_data && received_data) {
            assert(
                transmitted_data.value().size() == received_data.value().size()
            );

            data_size = transmitted_data.value().size();
        } else if (transmitted_data)
            data_size = transmitted_data.value().size();
        else if (received_data)
            data_size = received_data.value().size();
        else
            throw std::domain_error{
                "None of transmitted or received data supplied."
            };

        int raw_mode{};

        for (const auto& mode : modes)
            raw_mode |= static_cast<int>(mode);

        auto requested_raw_mode = raw_mode;
        auto requested_bits_per_word = bits_per_word;
        auto requested_speed_hz = speed_hz;

        help_ioctl(descriptor, SPI_IOC_WR_MODE32, &requested_raw_mode);
        help_ioctl(descriptor, SPI_IOC_RD_MODE32, &requested_raw_mode);

        if (requested_raw_mode != raw_mode)
            throw std::domain_error{
                "Requested spi mode is not supported by hardware."
            };

        help_ioctl(descriptor, SPI_IOC_WR_MAX_SPEED_HZ, &requested_speed_hz);
        help_ioctl(descriptor, SPI_IOC_RD_MAX_SPEED_HZ, &requested_speed_hz);

        if (requested_speed_hz != speed_hz)
            throw std::domain_error{
                "Requested spi max speed is not supported by hardware."
            };

        help_ioctl(
            descriptor,
            SPI_IOC_WR_BITS_PER_WORD,
            &requested_bits_per_word
        );
        help_ioctl(
            descriptor,
            SPI_IOC_RD_BITS_PER_WORD,
            &requested_bits_per_word
        );

        if (requested_bits_per_word != bits_per_word)
            throw std::domain_error{
                "Requested spi bits per word is not supported by hardware."
            };

        unsigned char transmitted_bit_count;
        unsigned char received_bit_count;

        if (static_cast<int>(raw_mode) & SPI_TX_OCTAL)
            transmitted_bit_count = 8;
        else if (static_cast<int>(raw_mode) & SPI_TX_QUAD)
            transmitted_bit_count = 4;
        else if (static_cast<int>(raw_mode) & SPI_TX_DUAL)
            transmitted_bit_count = 2;
        else
            transmitted_bit_count = 0;

        if (static_cast<int>(raw_mode) & SPI_RX_OCTAL)
            received_bit_count = 8;
        else if (static_cast<int>(raw_mode) & SPI_RX_QUAD)
            received_bit_count = 4;
        else if (static_cast<int>(raw_mode) & SPI_RX_DUAL)
            received_bit_count = 2;
        else
            received_bit_count = 0;

        spi_ioc_transfer spi_ioc_transfer_attributes;

        spi_ioc_transfer_attributes.tx_buf = (unsigned long long) (
            transmitted_data ? transmitted_data.value().data() : nullptr
        );
        spi_ioc_transfer_attributes.rx_buf = (unsigned long long) (
            received_data ? received_data.value().data() : nullptr
        );
        spi_ioc_transfer_attributes.len = data_size;
        spi_ioc_transfer_attributes.speed_hz = speed_hz;
        spi_ioc_transfer_attributes.bits_per_word = bits_per_word;
        spi_ioc_transfer_attributes.tx_nbits = transmitted_bit_count;
        spi_ioc_transfer_attributes.rx_nbits = received_bit_count;

        help_ioctl(
            descriptor,
            SPI_IOC_MESSAGE(1),
            &spi_ioc_transfer_attributes
        );
    }

    void SPI::transmit(
            const std::string& data,
            const std::vector<SPI::Mode>& modes,
            const unsigned int& speed_hz,
            const unsigned char& bits_per_word
    ) const {
        auto descriptor = help_open(get_name().data(), O_RDWR);

        transfer_spi(
            descriptor,
            data,
            std::nullopt,
            modes,
            speed_hz,
            bits_per_word
        );
        help_close(descriptor);
    }

    std::string SPI::receive(
            const std::string::size_type& data_size,
            const std::vector<SPI::Mode>& modes,
            const unsigned int& speed_hz,
            const unsigned char& bits_per_word
    ) const {
        std::string data(data_size, '\0');
        auto descriptor = help_open(get_name().data(), O_RDWR);

        transfer_spi(
            descriptor,
            std::nullopt,
            data,
            modes,
            speed_hz,
            bits_per_word
        );
        help_close(descriptor);

        return data;
    }

    std::string SPI::transmit_and_receive(
            const std::string& data,
            const std::vector<SPI::Mode>& modes,
            const unsigned int& speed_hz,
            const unsigned char& bits_per_word
    ) const {
        std::string received_data(data.size(), '\0');
        auto descriptor = help_open(get_name().data(), O_RDWR);

        transfer_spi(
            descriptor,
            data,
            received_data,
            modes,
            speed_hz,
            bits_per_word
        );
        help_close(descriptor);

        return received_data;
    }

    static void configure_uart(
            int descriptor,
            const UART::BaudRate& baud_rate
    ) {
        termios termios_attributes;
        auto return_value = tcgetattr(descriptor, &termios_attributes);

        if (return_value < 0)
            throw std::system_error{
                errno,
                std::system_category(),
                "Unable to get termios attributes."
            };

        return_value = cfsetspeed(
            &termios_attributes,
            static_cast<int>(baud_rate)
        );

        if (return_value < 0)
            throw std::system_error{
                errno,
                std::system_category(),
                "Unable to set baud rate."
            };

        cfmakeraw(&termios_attributes);

        return_value = tcsetattr(descriptor, TCSANOW, &termios_attributes);

        if (return_value < 0)
            throw std::system_error{
                errno,
                std::system_category(),
                "Unable to set termios attributes."
            };
    }

    void UART::transmit(
            const std::string& data,
            const BaudRate& baud_rate
    ) const {
        auto flag = O_RDWR | O_NOCTTY | O_NONBLOCK;
        auto descriptor = help_open(get_name().data(), flag);

        configure_uart(descriptor, baud_rate);

        auto byte_count = write(descriptor, data.data(), data.size());

        help_close(descriptor);

        if (byte_count < 0)
            throw std::system_error{
                errno,
                std::system_category(),
                "Unable to write to uart."
            };
    }

    std::string UART::receive(
            const std::string::size_type& max_data_size,
            const BaudRate& baud_rate
    ) const {
        std::string data(max_data_size, '\0');
        auto flag = O_RDWR | O_NOCTTY | O_NONBLOCK;
        auto descriptor = help_open(get_name().data(), flag);

        configure_uart(descriptor, baud_rate);

        auto byte_count = read(descriptor, data.data(), data.size());

        help_close(descriptor);

        if (byte_count < 0)
            throw std::system_error{
                errno,
                std::system_category(),
                "Unable to read from uart."
            };

        data.resize(byte_count);

        return data;
    }
}
