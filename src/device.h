#ifndef REVOLUTION_DEVICE_H
#define REVOLUTION_DEVICE_H

#include <atomic>
#include <chrono>
#include <functional>
#include <optional>
#include <string>

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
            rising_edge,
            falling_edge,
            both_edges
        };

        enum class Active {
            low,
            high
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
