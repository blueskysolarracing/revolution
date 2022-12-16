#ifndef REVOLUTION_DEVICE_H
#define REVOLUTION_DEVICE_H

#include <atomic>
#include <chrono>
#include <functional>
#include <optional>
#include <string>

#include <gpiod.h>
#include <linux/spi/spi.h>

namespace Revolution {
    class Device {
    public:
        explicit Device(const std::string& name);

        const std::string& get_name() const;
    private:
        const std::string name;
    };

    class MessageQueue : public Device {
    public:
        using Device::Device;

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
            const unsigned int& period,
            const unsigned int& duty_cycle,
            const Polarity& polarity
        ) const;
        void disable() const;
    };

    class SPI : public Device {
    public:
        enum class Mode {
             clock_phase = SPI_CPHA,
             clock_polarity = SPI_CPOL,
             chipselect_active_high = SPI_CS_HIGH,
             least_significant_bit_first = SPI_LSB_FIRST,
             share_slave_in_and_slave_out = SPI_3WIRE,
             loopback = SPI_LOOP,
             no_chip_select = SPI_NO_CS,
             ready = SPI_READY,
             transmit_dual = SPI_TX_DUAL,
             transmit_quad = SPI_TX_QUAD,
             receive_dual = SPI_RX_DUAL,
             receive_quad = SPI_RX_QUAD,
             toggle_chipselect_after_word = SPI_CS_WORD,
             transmit_octal = SPI_TX_OCTAL,
             receive_octal = SPI_RX_OCTAL,
             high_impedance_turnaround = SPI_3WIRE_HIZ,
        };

        using Device::Device;

        void transmit(
            const std::string& data,
            const SPI::Mode& mode,
            const unsigned int& speed,
            const unsigned char& word_bit_count
        ) const;
        std::string receive(
            const std::size_t& data_size,
            const SPI::Mode& mode,
            const unsigned int& speed,
            const unsigned char& word_bit_count
        ) const;
        std::string transmit_and_receive(
            const std::string& data,
            const SPI::Mode& mode,
            const unsigned int& speed,
            const unsigned char& word_bit_count
        ) const;
    };

    SPI::Mode operator|(const SPI::Mode& lhs, const SPI::Mode& rhs);
    SPI::Mode operator&(const SPI::Mode& lhs, const SPI::Mode& rhs);

    class UART : public Device {
    public:
        using Device::Device;

        void transmit(const std::string& data) const;
        std::string receive() const;
    };
}

#endif  // REVOLUTION_DEVICE_H
