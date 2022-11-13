# Mail Juicer

![cover](assets/cover.png)
Mail Juicer is a Python tool to help you manage your email. It is a replacement for the filters/sieves functionaly.

It was designed to be intuitive and easy to use, by using compact configuration and sensible defaults: a rule can be as simple as
```yaml
- condition:
    FROM: example@email.org
  move_to: some/folder
```

## Basic Usage

### Running

In order to benefit from Mail Juicer, you will probably need a server, so that it can continuously monitor your IMAP box, and take actions accordingly.

    mail_juicer --config-filer config.yaml monitor

You can also run it as a one-time command, so that it takes action on all the messages of your inbox:

    mail_juicer --config-filer config.yaml tidy

### Configuration

Mail Juicer takes a configuration file as input, that will contain the settings to connect to your IMAP server, and the rules you want to apply.

Example:
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

settings:
  server: imap.email.net
  username: me@email.net
  password: secret
```

Note that the values in the settings section can also be provided as environemnt variables, or in a `.env` file.
