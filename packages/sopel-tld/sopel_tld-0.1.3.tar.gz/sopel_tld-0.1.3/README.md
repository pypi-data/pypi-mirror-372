# sopel-tld

Top-level domain (TLD) info plugin for Sopel IRC bots.

## Installing

Releases are hosted on PyPI, so after installing Sopel, all you need is `pip`:

```shell
$ pip install sopel-tld
```

## Using

This plugin provides the `.tld` command, which can be used to look up a
top-level domain with or without the leading `.`:

```
<dgw> .tld .net
<Sopel> [tld] Name: .net | Entity: network | Administrator: Verisign | IDN: Yes
        | DNSSEC: Yes | SLD: Yes | IPv6: Yes | Notes: This is an open TLD; any
        person or entity is permitted to register. According to RFC 1591 (March
        1994) "This domain is intended to hold only the computers of network
        providers."

<dgw> .tld mil
<Sopel> [tld] Name: .mil | Entity: U.S. military | Administrator: United States
        Department of Defense | IDN: No | DNSSEC: Yes | SLD: Yes | IPv6: Yes |
        Notes: The .mil TLD is restricted to departments, services and agencies
        of the United States Department of Defense.
```

Most data is sourced from the English Wikipedia, so code updates might be
required periodically as their table format evolves.
