
# SPAM - A <u>S</u>oftware <u>PA</u>ckage <u>M</u>anager #

Ok let's be honest,
it's not *really* a package manager,
but merely a wrapper that presents a uniform command-line interface to them.
Across Linux distros and other Unixy things.


## Usage & Features ##

👉  Easy to use every day,
There's less to type due to built-in aliases.
For example, to operate on the *foo* package:

```sh
⏵ spam -h               # note usage and cmd list

⏵ spam up               # short for `spam update; spam upgrade`
⏵ spam in foo           # or install
⏵ spam rm foo           # or uninstall
⏵ spam clean            # clean up downloads, autoremove

# Moar!
⏵ spam add foo://bar    # add repo
⏵ spam info foo         # or show
⏵ spam lsf foo          # or listfiles of pkg
⏵ spam pr /bin/foo      # or provides, what or who-owns file
⏵ spam pu foo           # or purge
⏵ spam se foo           # or search
```

👉  Spam knows when to invoke sudo,
so you rarely need to worry about it.
Even less to type for commands you may be running often across distros.

👉  It also can smooth over annoyances.

For example, by default it often passes `--cacheonly` to dnf subcommands so it
doesn't make you wait to download the index before searching for a package.
(The odds of a brand-new package being indexed in the last few days is quite
small.)
For apt it makes the `… update && dist-upgrade` dance as simple as "up".

👉  It prints each command it runs,
so you can learn how to do it on a package manager you may not be as familiar
with.
Also, if it wasn't able to do what you want,
it is easier to tweak the next command.
Ctrl+C is always available.


## Support ##

Currently supports:

- apt - Linux/Debian/Ubuntu/Mint
- dnf - Linux/Fedora
- opkg - Linux/OpenWRT  (though may be phased out)
- port - MacOS/MacPorts

With hopefully more to come as time allows.
Probably works on the Linux Subsystem for Windows (LSW).


## Install

This is the Python version.
The name "spam" was taken on PyPi,
so the package is called `spam-util` there instead.

    pip install --user spam-util

There are no dependencies so faffing about with virtual-envs is unnecessary.
It can then be run (as at the top of the page),
though you may need to put `~/.local/bin` into your path.

Perhaps you'd prefer a small binary?
I've also
[ported this to Rust](https://bitbucket.org/mixmastamyk/spam-rs/src/main/)
for fun.


## Customization

This is done from a `config.ini` file in your `$XDG_CONFIG_HOME` folder.
A default is placed there on first run,
if it does not exist already:

    ⏵ edit ~/.config/spam/config.ini

May be useful to check it into a "dotfiles" repo.

### Sections

Note: the sections and keys that are used specifically by spam are given a `spam_`
prefix.
All others will be used to configure local commands.
"Package manager" is abbreviated as PM below.

The important sections are these:

```ini
[spam_needs_sudo]
# where sub-commands that require sudo are listed
…

[spam_aliases]
# lists shortcuts, such as in for install, rm for remove
…

# sections, named to match the platform_ids from the
# /etc/os-release file, ID=… value are described below:

[fedora]
# The value of the spam_exec key sets the PM for the platform:
spam_exec = dnf
…

# sub-commands of the PM are listed below the section.
# If there are multiple commands to run; use semicolons:

clean = clean packages; autoremove


[debian]
# A "!" at the front of the command signifies it as stand-alone,
# meaning it is *not* a sub-command of the PM.
# Instead, spam will run the command as is:
…
add = !add-apt-repository

[ubuntu]
# A spam_extends allows a section to inherit from another:
spam_extends = debian

# Yet overrides may be placed into the child section as well:
foo = bar; baz

```

Hope you enjoy.

<!---
* [Learn Markdown](https://bitbucket.org/tutorials/markdowndemo)
-->
