# Colorby

**Colorby** is a Python program that makes it easier to understand interleaved
log lines by coloring each line based on a matching part.

Example:

<pre><samp><span class=comment># Color some logs from systemd based on service name</span>
<span class=prompt>$</span> <kbd>journalctl _COMM=systemd --since -20m | grep '\.service' | colorby '\S+\.service'</kbd>
<span class=fg-green>Jun 07 14:36:03 iroh systemd[1]: Starting NetworkManager-dispatcher.service - Network Manager Script Dispatcher Service...</span>
<span class=fg-green>Jun 07 14:36:03 iroh systemd[1]: Started NetworkManager-dispatcher.service - Network Manager Script Dispatcher Service.</span>
<span class=fg-green>Jun 07 14:36:13 iroh systemd[1]: NetworkManager-dispatcher.service: Deactivated successfully.</span>
<span class=fg-blue>Jun 07 14:37:59 iroh systemd[1]: Starting packagekit.service - PackageKit Daemon...</span>
<span class=fg-blue>Jun 07 14:37:59 iroh systemd[1]: Started packagekit.service - PackageKit Daemon.</span>
<span class=fg-yellow>Jun 07 14:37:59 iroh systemd[1]: Starting flatpak-system-helper.service - flatpak system helper...</span>
<span class=fg-yellow>Jun 07 14:37:59 iroh systemd[1]: Started flatpak-system-helper.service - flatpak system helper.</span>
<span class=fg-blue>Jun 07 14:43:09 iroh systemd[1]: packagekit.service: Deactivated successfully.</span>
<span class=fg-blue>Jun 07 14:43:09 iroh systemd[1]: packagekit.service: Consumed 1.177s CPU time, 120.1M memory peak.</span>
<span class=fg-yellow>Jun 07 14:47:59 iroh systemd[1]: flatpak-system-helper.service: Deactivated successfully.</span>
<span class=fg-red>Jun 07 14:51:10 iroh systemd[1]: Starting fprintd.service - Fingerprint Authentication Daemon...</span>
<span class=fg-red>Jun 07 14:51:10 iroh systemd[1]: Started fprintd.service - Fingerprint Authentication Daemon.</span>
<span class=fg-red>Jun 07 14:51:40 iroh systemd[1]: fprintd.service: Deactivated successfully.</span>
</samp></pre>

Note how this makes it easier to identify the lines corresponding to each
service despite their interleaving.

<p class=hidden-on-lumeh-org>
(If you’re reading this on GitHub, you won’t see the colors.
<a href=https://www.lumeh.org/projects/colorby/>Read it on lumeh.org
instead!</a>)
</p>

## Usage

For one-off uses, I recommend running the tool via `uvx` or `pipx`:

<pre><samp><span class=prompt>$</span> <kbd>uvx colorby --help</kbd>
usage: colorby [mode options] [other options] [REGEX]

Color each line from stdin based on its key identified by REGEX.
<span class=abridged>[…]</span>
</samp></pre>

For more regular use, install the package using your preferred Python package
manager.
