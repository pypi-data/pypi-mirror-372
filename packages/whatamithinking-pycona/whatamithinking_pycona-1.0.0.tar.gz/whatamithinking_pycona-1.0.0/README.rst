pycona Package Documentation
=============================

*IMPORTANT*
----------------------------------------------
*  This is a fork of the fantastic library, *pystray*, created by Moses Palmer. This version still points to his library's documentation as the changes are small.
*  Name change from *pystray* to *pycona*, mostly because i cannot bare to keep saying "piss-tray" in my head
*  This version removes the PILlow dependency for the Windows platform, dramatically reducing the executable size created. This was the primary reason for this fork.
*  Adds support for use of contextvars when running inside a thread
*  Handles WM_CLOSE event on Windows so app can gracefully shutdown, adding the public *Icon.on_shutdown* method to hook into

Otherwise, the library is unchanged. Again kudos to Moses Palmer for this brilliant work.



This library allows you to create a *system tray icon*.

Supported platforms are *Linux* under *Xorg*, *GNOME* and *Ubuntu*, *macOS*
and *Windows*.

See `here <https://pystray.readthedocs.io/en/latest/>`_ for the full
documentation.
