from revolution import (
    Application,
    Contexts,
    Debugger,
    Display,
    Driver,
    Miscellaneous,
    Motor,
    Peripheries,
    Power,
    Settings,
    Telemeter,
)

APPLICATION_TYPES: tuple[type[Application], ...] = (
    Debugger,
    Display,
    Driver,
    Miscellaneous,
    Motor,
    Power,
    Telemeter,
)

CONTEXTS: Contexts = Contexts(
)

PERIPHERIES: Peripheries = Peripheries(
)

SETTINGS: Settings = Settings(
)
