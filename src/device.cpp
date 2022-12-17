#include "device.h"

#include <cassert>
#include <cerrno>
#include <ctime>
#include <fstream>
#include <stdexcept>
#include <system_error>

#include <sys/ioctl.h>

namespace Revolution {
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

    MessageQueue::MessageQueue(
            const std::string& name, 
            const std::vector<OpenFlag>& open_flags,
            const Mode& mode,
            const std::optional<Configuration>& configuration
    ) : Device{name} {
        open(open_flags, mode, configuration);
    }

    MessageQueue::~MessageQueue() {
        close();
    }

    std::string MessageQueue::receive() const {
        std::string raw_message(get_attributes().mq_msgsize, '\0');
        unsigned int priority;
        auto received_size = mq_receive(
            get_descriptor(),
            raw_message.data(),
            raw_message.size(),
            &priority
        );

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
        auto received_size = mq_send(
            get_descriptor(),
            raw_message.data(),
            raw_message.size(),
            priority
        );

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
        auto time_specification = convert_to_time_specification(
            absolute_timeout
        );
        std::string raw_message(get_attributes().mq_msgsize, '\0');
        unsigned int priority;
        auto received_size = mq_timedreceive(
            get_descriptor(),
            raw_message.data(),
            raw_message.size(),
            &priority,
            &time_specification
        );

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

    const MessageQueue::Descriptor& MessageQueue::get_descriptor() const {
        return descriptor;
    }

    MessageQueue::Descriptor& MessageQueue::get_descriptor() {
        return descriptor;
    }

    MessageQueue::Attributes MessageQueue::get_attributes() const {
        Attributes attributes;
        auto return_value = mq_getattr(get_descriptor(), &attributes);

        if (return_value < 0)
            throw std::system_error{
                errno,
                std::system_category(),
                "Unable to get the message queue attributes"
            };

        return attributes;
    }

    void MessageQueue::open(
            const std::vector<OpenFlag>& open_flags,
            const MessageQueue::Mode& mode,
            const std::optional<MessageQueue::Configuration>& configuration
    ) {
        int raw_open_flags{};

        for (const auto& open_flag : open_flags)
            raw_open_flags |= static_cast<int>(open_flag);

        std::optional<Attributes> attributes;

        if (configuration) {
            attributes = Attributes{};
            attributes->mq_maxmsg = configuration->get_max_message_count();
            attributes->mq_msgsize = configuration->get_max_message_size();
        }

        get_descriptor() = mq_open(
            get_name().data(),
            raw_open_flags,
            mode,
            attributes ? &*attributes : nullptr
        );

        if (get_descriptor() == (Descriptor) - 1)
            throw std::system_error{
                errno,
                std::system_category(),
                "Unable to open the message queue"
            };
    }

    void MessageQueue::close() {
        auto return_value = mq_close(get_descriptor());

        if (return_value < 0)
            throw std::system_error{
                errno,
                std::system_category(),
                "Unable to close the message queue"
            };

        get_descriptor() = (Descriptor) - 1;
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

    PWM::PWM(const unsigned int& index) :
            Device{get_name_prefix() + std::to_string(index)},
            index{index} {
        write("/export", std::to_string(get_index()));
    }

    PWM::~PWM() {
        write("/unexport", std::to_string(get_index()));
    }

    const unsigned int& PWM::get_index() const {
        return index;
    }

    void PWM::enable(
            const std::chrono::high_resolution_clock::duration& period,
            const std::chrono::high_resolution_clock::duration& duty_cycle,
            const Polarity& polarity
    ) const {
        set_attribute(
            "/period",
            std::to_string(
                std::chrono::duration_cast<std::chrono::nanoseconds>(
                    period
                ).count()
            )
        );
        set_attribute(
            "/duty_cycle",
            std::to_string(
                std::chrono::duration_cast<std::chrono::nanoseconds>(
                    duty_cycle
                ).count()
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

        set_attribute("/polarity", raw_polarity);
        set_attribute("/enable", "1");
    }

    void PWM::disable() const {
        set_attribute("/enable", "0");
    }

    const std::string& PWM::get_path() {
        return path;
    }

    const std::string& PWM::get_name_prefix() {
        return name_prefix;
    }

    const std::string PWM::path{"/sys/class/pwm/pwmchip"};
    const std::string PWM::name_prefix{"/pwmchip"};

    void PWM::write(
            const std::string& filename,
            const std::string& data
    ) const {
        std::ofstream ofstream;

        ofstream.exceptions(std::ofstream::failbit | std::ofstream::badbit);
        ofstream.open(get_path() + filename, std::fstream::out);
        ofstream << data;
        ofstream.close();
    }

    void PWM::set_attribute(
            const std::string& key,
            const std::string& value
    ) const {
        write(get_name() + key, value);
    }

    DevDevice::DevDevice(
            const std::string& name,
            const std::vector<OpenFlag>& open_flags
    ) : Device{name}, descriptor{-1} {
        open(open_flags);
    }

    DevDevice::~DevDevice() {
        close();
    }

    const int& DevDevice::get_descriptor() const {
        return descriptor;
    }

    std::string DevDevice::read(const std::size_t& max_data_size) const {
        std::string data(max_data_size, '\0');
        auto data_size = ::read(get_descriptor(), data.data(), data.size());

        if (data_size < 0)
            throw std::system_error{
                errno,
                std::system_category(),
                "Unable to read from device."
            };

        data.resize(data_size);

        return data;
    }

    void DevDevice::write(const std::string& data) const {
        auto data_size = ::write(get_descriptor(), data.data(), data.size());

        if (data_size < 0)
            throw std::system_error{
                errno,
                std::system_category(),
                "Unable to write to device."
            };
    }

    void DevDevice::ioctl(
            const unsigned long& request,
            void* const& data
    ) const {
        auto return_value = ::ioctl(get_descriptor(), request, data);

        if (return_value < 0)
            throw std::system_error{
                errno,
                std::system_category(),
                "Unable to manipulate device."
            };
    }

    const std::string& DevDevice::get_path() {
        return path;
    }

    const std::string DevDevice::path{"/dev"};

    int& DevDevice::get_descriptor() {
        return descriptor;
    }

    void DevDevice::open(const std::vector<OpenFlag>& open_flags) {
        int raw_open_flags{};

        for (const auto& open_flag : open_flags)
            raw_open_flags |= static_cast<int>(open_flag);

        get_descriptor() = ::open(
            (get_path() + get_name()).data(),
            raw_open_flags
        );

        if (get_descriptor() < 0)
            throw std::system_error{
                errno,
                std::system_category(),
                "Unable to open file."
            };
    }

    void DevDevice::close() {
        auto return_value = ::close(get_descriptor());

        if (return_value < 0)
            throw std::system_error{
                errno,
                std::system_category(),
                "Unable to close file."
            };

        get_descriptor() = -1;
    }

    SPI::SPI(
            const std::string& name,
            const std::vector<Mode>& modes,
            const unsigned int& speed_hz,
            const unsigned char& bits_per_word
    ) :
            DevDevice{name, {OpenFlag::read_write}},
            modes{modes},
            speed_hz{speed_hz},
            bits_per_word{bits_per_word} {
        int raw_mode{};

        for (const auto& mode : modes)
            raw_mode |= static_cast<int>(mode);

        auto requested_raw_mode = raw_mode;
        auto requested_bits_per_word = get_bits_per_word();
        auto requested_speed_hz = get_speed_hz();

        ioctl(SPI_IOC_WR_MODE32, &requested_raw_mode);
        ioctl(SPI_IOC_RD_MODE32, &requested_raw_mode);
        ioctl(SPI_IOC_WR_MAX_SPEED_HZ, &requested_speed_hz);
        ioctl(SPI_IOC_RD_MAX_SPEED_HZ, &requested_speed_hz);
        ioctl(SPI_IOC_WR_BITS_PER_WORD, &requested_bits_per_word);
        ioctl(SPI_IOC_RD_BITS_PER_WORD, &requested_bits_per_word);

        if (requested_raw_mode != raw_mode)
            throw std::domain_error{
                "Requested spi mode is not supported by hardware."
            };
        else if (requested_speed_hz != get_speed_hz())
            throw std::domain_error{
                "Requested spi max speed is not supported by hardware."
            };
        else if (requested_bits_per_word != get_bits_per_word())
            throw std::domain_error{
                "Requested spi bits per word is not supported by hardware."
            };
    }

    const std::vector<SPI::Mode>& SPI::get_modes() const {
        return modes;
    }

    const unsigned int& SPI::get_speed_hz() const {
        return speed_hz;
    }

    const unsigned char& SPI::get_bits_per_word() const {
        return bits_per_word;
    }

    void SPI::transmit(const std::string& data) const {
        transfer(data, std::nullopt);
    }

    std::string SPI::receive(const std::size_t& data_size) const {
        std::string data(data_size, '\0');

        transfer(std::nullopt, data);

        return data;
    }

    std::string SPI::transmit_and_receive(
            const std::string& transmitted_data
    ) const {
        std::string received_data(transmitted_data.size(), '\0');

        transfer(transmitted_data, received_data);

        return received_data;
    }

    void SPI::transfer(
            const std::optional<std::string>& transmitted_data,
            std::optional<std::string> received_data
    ) const {
        unsigned int data_size;

        if (transmitted_data && received_data) {
            assert(transmitted_data->size() == received_data->size());

            data_size = transmitted_data->size();
        } else if (transmitted_data)
            data_size = transmitted_data->size();
        else if (received_data)
            data_size = received_data->size();
        else
            throw std::domain_error{
                "None of transmitted or received data supplied."
            };

        int raw_mode{};

        for (const auto& mode : get_modes())
            raw_mode |= static_cast<int>(mode);

        Attributes attributes;

        attributes.tx_buf = (unsigned long long) (
            transmitted_data ? transmitted_data->data() : nullptr
        );
        attributes.rx_buf = (unsigned long long) (
            received_data ? received_data->data() : nullptr
        );
        attributes.len = data_size;
        attributes.speed_hz = get_speed_hz();
        attributes.bits_per_word = get_bits_per_word();

        if (static_cast<int>(raw_mode)
                & static_cast<int>(Mode::transmit_octal))
            attributes.tx_nbits = 8;
        else if (static_cast<int>(raw_mode)
                & static_cast<int>(Mode::transmit_quad))
            attributes.tx_nbits = 4;
        else if (static_cast<int>(raw_mode)
                & static_cast<int>(Mode::transmit_dual))
            attributes.tx_nbits = 2;
        else
            attributes.tx_nbits = 0;

        if (static_cast<int>(raw_mode)
                & static_cast<int>(Mode::receive_octal))
            attributes.rx_nbits = 8;
        else if (static_cast<int>(raw_mode)
                & static_cast<int>(Mode::receive_quad))
            attributes.rx_nbits = 4;
        else if (static_cast<int>(raw_mode)
                & static_cast<int>(Mode::receive_dual))
            attributes.rx_nbits = 2;
        else
            attributes.rx_nbits = 0;

        ioctl(SPI_IOC_MESSAGE(1), &attributes);
    }

    UART::UART(const std::string& name, const BaudRate& baud_rate) :
            DevDevice{
                name,
                {
                    OpenFlag::read_write,
                    OpenFlag::non_blocking_mode,
                    OpenFlag::non_controlled_terminal_device
                }
            } {
        auto attributes = get_attributes();
        auto return_value = cfsetspeed(
            &attributes,
            static_cast<int>(baud_rate)
        );

        if (return_value < 0)
            throw std::system_error{
                errno,
                std::system_category(),
                "Unable to set baud rate."
            };

        cfmakeraw(&attributes);

        set_attributes(attributes);
    }

    void UART::transmit(const std::string& data) const {
        write(data);
    }

    std::string UART::receive(const std::size_t& max_data_size) const {
        return read(max_data_size);
    }

    UART::Attributes UART::get_attributes() const {
        Attributes attributes;
        auto return_value = tcgetattr(get_descriptor(), &attributes);

        if (return_value < 0)
            throw std::system_error{
                errno,
                std::system_category(),
                "Unable to get termios attributes."
            };

        return attributes;
    }

    void UART::set_attributes(const Attributes& attributes) const {
        auto return_value = tcsetattr(get_descriptor(), TCSANOW, &attributes);

        if (return_value < 0)
            throw std::system_error{
                errno,
                std::system_category(),
                "Unable to set termios attributes."
            };
    }
}
