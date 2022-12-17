#ifndef REVOLUTION_DEVICE_H
#define REVOLUTION_DEVICE_H

#include <atomic>
#include <chrono>
#include <cstddef>
#include <functional>
#include <optional>
#include <string>
#include <vector>

#include <fcntl.h>
#include <gpiod.h>
#include <linux/spi/spi.h>
#include <termios.h>

namespace Revolution {
    class Device {
    public:
        Device(const std::string& name);

        const std::string& get_name() const;
    private:
        const std::string name;
    };

    class MessageQueue : public Device {
    public:
        enum class Flag {
            readonly = O_RDONLY,
            writeonly = O_WRONLY,
            read_and_write = O_RDWR,
            close_on_execution = O_CLOEXEC,
            create = O_CREAT,
            error_if_exists = O_EXCL,
            non_blocking = O_NONBLOCK
        };

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

        using Device::Device;

        std::string receive(
            const std::vector<Flag> flags = {Flag::readonly, Flag::create},
            const unsigned int& mode = 0600,
            const std::optional<Configuration>& configuration = std::nullopt
        ) const;
        void send(
            const std::string& raw_message,
            const unsigned int& priority,
            const std::vector<Flag> flags = {Flag::writeonly, Flag::create},
            const unsigned int& mode = 0600,
            const std::optional<Configuration>& configuration = std::nullopt
        ) const;
        std::string timed_receive(
            const std::chrono::high_resolution_clock::duration& timeout,
            const std::vector<Flag> flags = {Flag::readonly, Flag::create},
            const unsigned int& mode = 0600,
            const std::optional<Configuration>& configuration = std::nullopt
        ) const;
        void unlink() const;
        void monitor(
            const std::atomic_bool& status,
            const std::chrono::high_resolution_clock::duration& timeout,
            const std::function<void(const std::string&)>& callback,
            const std::vector<Flag> flags = {Flag::readonly, Flag::create},
            const unsigned int& mode = 0600,
            const std::optional<Configuration>& configuration = std::nullopt
        ) const;
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
    };

    class PWM : public Device {
    public:
        using Device::Device;

        enum class Polarity {
            normal,
            inversed
        };

        void enable(
            const unsigned int& channel_index,
            const std::chrono::high_resolution_clock::duration& period,
            const std::chrono::high_resolution_clock::duration& duty_cycle,
            const Polarity& polarity
        ) const;
        void disable(const unsigned int& channel_index) const;
    };

    class SPI : public Device {
    public:
        enum class Mode {
             clock_phase = SPI_CPHA,
             clock_polarity = SPI_CPOL,
             chipselect_active_high = SPI_CS_HIGH,
             per_word_bits_on_wire = SPI_LSB_FIRST,
             slave_in_slave_out_signals_shared = SPI_3WIRE,
             loopback_mode = SPI_LOOP,
             no_chip_select = SPI_NO_CS,
             slave_pulls_low_to_pause = SPI_READY,
             transmit_with_two_wires = SPI_TX_DUAL,
             transmit_with_four_wires = SPI_TX_QUAD,
             receive_with_two_wires = SPI_RX_DUAL,
             receive_with_four_wires = SPI_RX_QUAD,
             toggle_chipselect_after_each_word = SPI_CS_WORD,
             transmit_with_eight_wires = SPI_TX_OCTAL,
             receive_with_eight_wires = SPI_RX_OCTAL,
             high_impedance_turnaround = SPI_3WIRE_HIZ,
        };

        using Device::Device;

        void transmit(
            const std::string& data,
            const std::vector<SPI::Mode>& modes,
            const unsigned int& speed_hz,
            const unsigned char& bits_per_word
        ) const;
        std::string receive(
            const std::string::size_type& data_size,
            const std::vector<SPI::Mode>& modes,
            const unsigned int& speed_hz,
            const unsigned char& bits_per_word
        ) const;
        std::string transmit_and_receive(
            const std::string& data,
            const std::vector<SPI::Mode>& modes,
            const unsigned int& speed_hz,
            const unsigned char& bits_per_word
        ) const;
    };

    class UART : public Device {
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

        using Device::Device;

        void transmit(
            const std::string& data,
            const BaudRate& baud_rate
        ) const;
        std::string receive(
            const std::string::size_type& max_data_size,
            const BaudRate& baud_rate
        ) const;
    };
}

#endif  // REVOLUTION_DEVICE_H
