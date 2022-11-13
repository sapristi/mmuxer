# Mail Juicer

![cover](assets/cover.png)
Mail Juicer is a Python tool to help you manage your email. It is a replacement for the filters/sieves functionaly.

It was designed to be intuitive and easy to use, by using compact configuration and sensible defaults: a rule can be as simple as
```yaml
- condition:
    FROM: example@email.org
  move_to: some/folder
```

## Usage

In order to benefit from Mail Juicer, you will probably need a server, so that it can continuously monitor your IMAP box, and take actions accordingly.

