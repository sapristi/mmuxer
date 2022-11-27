# Mail Muxer

![cover](assets/cover.png)

Are you tired of managing IMAP filters through cumbersome, slow and unintuive web interfaces ? Then Mail Muxer is here to save you from this pain !

Mail Muxer is a Python tool that will monitor your Inbox, and filter incomming emails according to the given configuration. It was designed to be intuitive and easy to use, by using compact configuration and sensible defaults: a rule can be as simple as
```yaml
- condition:
    FROM: example@email.org
  move_to: some/folder
```

## Basic Usage

1. Install:

        pip install mmuxer

2. Create configuration file:
    ```yaml
    rules:
      - move_to: receipts
        condition:
          ANY:
            - FROM: some_store@ok.ok
            - FROM: some_other_store@store.net
      - move_to: important
        condition:
          SUBJECT: important
      - condition:
          FROM: spammer@example.com
        actions:
          - delete

    settings:
      server: imap.email.net
      username: me@email.net
      password: secret
    ```
3. Check your configuration:

       mmuxer check --config-file config.yaml

4. Check your folders:

       mmuxer folder --config-file config.yaml compare-destinations

5. Monitor your inbox:

       mmuxer monitor --config-file config.yaml

6. Or apply on all messages of a given IMAP folder:

       mmuxer tidy --config-file config.yaml --folder FOLDER

7. Finally, to get help on a given command, add a `--help` to it, e.g.

       mmuxer monitor --help

### Note on SSL

If you get SSL errors while connecting to your server, see the [SSL Configuration](#SSL-Configuration) section.

### Python compatibility

This program should work with Python >= 3.8.

## Going further on

- [Advanced usage](./docs/advanced_usage.md)
- Use with docker/systemd: see [doc](./service/README.md)

## What's next

The current implementation is mostly feature complete for me, but here are some features that could be implemented:

- Improve `tidy` operation:
  - make `tidy` operation more performant by using IMAP search features
  - allow to run `tidy` on many / all folders
- Better conditions:
  - add a `REGEX` operator (although not compatible with IMAP search)
  - support more fields
- Add more actions:
  - tag emails
  - forward emails
  - move destination based on regex match group
  - automatic folder creation
  - anything else ?
- Hot-reload config file
- Re-configure (or execute actions) by sending emails
- Support OAuth / Gmail (I'm not sure how feasible that would be).

Don't hesitate to ask, or make a pull request !

## Credit

This program relies on
- the [imap-tools](https://github.com/ikvk/imap_tools) library for everything involving IMAP
- the mock IMAP server from [aioimaplib](https://github.com/bamthomas/aioimaplib) for it's tests
- the ever excellent Typer and Pydantic libs

Many thanks to them !
