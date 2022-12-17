#ifndef REVOLUTION_DEVICE_H
#define REVOLUTION_DEVICE_H

#include <atomic>
#include <chrono>
#include <cstddef>
#include <functional>
#include <optional>
#include <string>
#include <vector>

#include <gpiod.h>
#include <linux/spi/spidev.h>
#include <mqueue.h>
#include <termios.h>

namespace Revolution {
    enum class OpenFlag {
        readonly = O_RDONLY,
        writeonly = O_WRONLY,
        read_write = O_RDWR,
        close_on_execution = O_CLOEXEC,
        create = O_CREAT,
        error_if_exists = O_EXCL,
        non_blocking_mode = O_NONBLOCK,
        non_controlled_terminal_device = O_NOCTTY
    };

    class Device {
    public:
        explicit Device(const std::string& name);

        const std::string& get_name() const;
    private:
        const std::string name;
    };

    class MessageQueue : public Device {
    public:
        class Configuration {
        public:
            Configuration(
                const unsigned int& max_message_count,
                const unsigned int& max_message_size
            );

            const unsigned int& get_max_message_count() const;
            const unsigned int& get_max_message_size() const;
        private:
            const unsigned int max_message_count;
            const unsigned int max_message_size;
        };

        using Mode = mode_t;

        explicit MessageQueue(
            const std::string& name, 
            const std::vector<OpenFlag>& open_flags = {
                OpenFlag::read_write,
                OpenFlag::create
            },
            const Mode& mode = 0600,
            const std::optional<Configuration>& configuration = std::nullopt
        );
        ~MessageQueue();

        std::string receive() const;
        void send(
            const std::string& raw_message,
            const unsigned int& priority
        ) const;
        std::string timed_receive(
            const std::chrono::high_resolution_clock::duration& timeout
        ) const;
        void unlink() const;

        void monitor(
            const std::atomic_bool& status,
            const std::chrono::high_resolution_clock::duration& timeout,
            const std::function<void(const std::string&)>& callback
        ) const;
    private:
        using Descriptor = mqd_t;
        using Attributes = mq_attr;

        const Descriptor& get_descriptor() const;
        Descriptor& get_descriptor();
        Attributes get_attributes() const;

        void open(
            const std::vector<OpenFlag>& flags,
            const Mode& mode,
            const std::optional<Configuration>& configuration
        );
        void close();

        Descriptor descriptor;
    };

    class GPIO : public Device {
    public:
        enum class Event {
            rising_edge = GPIOD_CTXLESS_EVENT_RISING_EDGE,
            falling_edge = GPIOD_CTXLESS_EVENT_FALLING_EDGE,
            both_edges = GPIOD_CTXLESS_EVENT_BOTH_EDGES
        };

        enum class Active : bool {
            low = true,
            high = false
        };

        using Device::Device;

        std::vector<bool> get(
            const std::vector<unsigned int>& offsets,
            const Active& active,
            const std::string& consumer_name
        ) const;
        void set(
            const std::vector<unsigned int>& offsets,
            const std::vector<bool>& values,
            const Active& active,
            const std::string& consumer_name
        ) const;
        void monitor(
            const Event& event,
            const std::vector<unsigned int>& offsets,
            const Active& active,
            const std::string& consumer_name,
            const std::atomic_bool& status,
            const std::chrono::high_resolution_clock::duration& timeout,
            const std::function<void(const Event&, const unsigned int&)>&
                callback
        ) const;
    private:
        struct Data {
            const std::atomic_bool& status;
            const std::function<void(const GPIO::Event&, const unsigned int&)>&
                callback;
        };

        static int handle(
            int event_type,
            unsigned int offset,
            const std::timespec* timestamp,
            void* raw_data
        );
    };

    class PWM : public Device {
    public:
        enum class Polarity {
            normal,
            inversed
        };

        explicit PWM(const unsigned int& index);
        ~PWM();

        const unsigned int& get_index() const;

        void enable(
            const std::chrono::high_resolution_clock::duration& period,
            const std::chrono::high_resolution_clock::duration& duty_cycle,
            const Polarity& polarity
        ) const;
        void disable() const;
    private:
        static const std::string& get_path();
        static const std::string& get_name_prefix();

        static const std::string path;
        static const std::string name_prefix;

        void write(const std::string& filename, const std::string& data) const;
        void set_attribute(
            const std::string& key,
            const std::string& value
        ) const;

        const unsigned int index;
    };

    class DevDevice : public Device {
    public:
        DevDevice(
            const std::string& name,
            const std::vector<OpenFlag>& open_flags
        );
        ~DevDevice();
    protected:
        const int& get_descriptor() const;

        std::string read(const std::size_t& max_data_size) const;
        void write(const std::string& data) const;
        void ioctl(const unsigned long& request, void* const& data) const;
    private:
        static const std::string& get_path();

        static const std::string path;

        int& get_descriptor();

        void open(const std::vector<OpenFlag>& open_flags);
        void close();

        int descriptor;
    };

    class SPI : public DevDevice {
    public:
        enum class Mode {
             clock_phase = SPI_CPHA,
             clock_polarity = SPI_CPOL,
             chipselect_active_high = SPI_CS_HIGH,
             least_significant_bit_first = SPI_LSB_FIRST,
             share_slave_in_slave_out = SPI_3WIRE,
             loopback = SPI_LOOP,
             no_chip_select = SPI_NO_CS,
             ready = SPI_READY,
             transmit_dual = SPI_TX_DUAL,
             transmit_quad = SPI_TX_QUAD,
             receive_dual = SPI_RX_DUAL,
             receive_quad = SPI_RX_QUAD,
             chipselect_word = SPI_CS_WORD,
             transmit_octal = SPI_TX_OCTAL,
             receive_octal = SPI_RX_OCTAL,
             high_impedance_turnaround = SPI_3WIRE_HIZ,
        };

        explicit SPI(
            const std::string& name,
            const std::vector<Mode>& modes,
            const unsigned int& speed_hz,
            const unsigned char& bits_per_word
        );

        const std::vector<Mode>& get_modes() const;
        const unsigned int& get_speed_hz() const;
        const unsigned char& get_bits_per_word() const;

        void transmit(const std::string& data) const;
        std::string receive(const std::size_t& data_size) const;
        std::string transmit_and_receive(
            const std::string& transmitted_data
        ) const;
    private:
        using Attributes = spi_ioc_transfer;

        void transfer(
            const std::optional<std::string>& transmitted_data,
            std::optional<std::string> received_data
        ) const;

        const std::vector<Mode> modes;
        const unsigned int speed_hz;
        const unsigned char bits_per_word;
    };

    class UART : public DevDevice {
    public:
        enum class BaudRate {
            BR0 = B0,
            BR50 = B50,
            BR75 = B75,
            BR110 = B110,
            BR134 = B134,
            BR150 = B150,
            BR200 = B200,
            BR300 = B300,
            BR600 = B600,
            BR1200 = B1200,
            BR1800 = B1800,
            BR2400 = B2400,
            BR4800 = B4800,
            BR9600 = B9600,
            BR19200 = B19200,
            BR38400 = B38400,
            BR57600 = B57600,
            BR115200 = B115200,
            BR230400 = B230400
        };

        explicit UART(const std::string& name, const BaudRate& baud_rate);

        void transmit(const std::string& data) const;
        std::string receive(const std::size_t& max_data_size) const;
    private:
        using Attributes = termios;

        Attributes get_attributes() const;
        void set_attributes(const Attributes& attributes) const;
    };
}

#endif  // REVOLUTION_DEVICE_H
