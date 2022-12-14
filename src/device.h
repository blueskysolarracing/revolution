#ifndef REVOLUTION_DEVICE_H
#define REVOLUTION_DEVICE_H

#include <atomic>
#include <chrono>
#include <functional>
#include <optional>
#include <string>
#include <vector>

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
            const std::function<void(const std::string&)>& handler,
            const std::chrono::high_resolution_clock::duration& timeout
        ) const;
    };

    class GPIO : public Device {
    public:
        explicit GPIO(
            const std::string& name,
            const unsigned int& offset
        );

        const unsigned int& get_offset() const;

        bool get_active_low() const;
        void set_active_low(const bool& active_low) const;
        void monitor(
            const std::function<
                void(const std::string&, const unsigned int&, const bool&)
            >& handler
        ) const;
    private:
        const unsigned int offset;
    };

    class PWM : public Device {
    public:
        using Device::Device;

        class Polarity {
        public:
            static const std::string normal;
            static const std::string inversed;
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
        using Device::Device;

        void transmit(const std::string& data) const;
        std::string receive() const;
        std::string transmit_and_receive(const std::string& data) const;
    };

    class UART : public Device {
    public:
        using Device::Device;

        void transmit(const std::string& data) const;
        std::string receive() const;
    };
}

#endif  // REVOLUTION_DEVICE_H
