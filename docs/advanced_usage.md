# Advanced usage

## Configuration

Mail Muxer takes a configuration file as input, that will contain the settings to connect to your IMAP server, and the rules you want to apply.


Note that the values in the settings section can also be provided as environemnt variables, or in a `.env` file.

## Conditions

### Base conditions

The supported fields for the conditions are `TO`, `FROM`, `SUBJECT` and `BODY`.

The comporison operators between the value of the email and the provided value are:
- `CONTAINS`: matches if the email value contains the provided value **(default)**
- `EQUALS`: matches if the email value is exactly the provided value

**Note***: comparisons are case-insensitive.

### Composed conditions

It is also possible to compose conditions with boolean operators:
 - `ALL`: takes as input a list of conditions
 - `ANY`: takes as input a list of conditions
 - `NOT`: takes as input a single condition

### Example

The following condition will match emails that are not from `someone@example.com`, and whose subject contains either `keyword1` or `keyword2`:

```yaml
condition:
  ALL:
    - NOT:
        FROM: someone@example.com
        operator: EQUALS
    - ANY:
      - SUBJECT: keyword1
      - SUBJECT: keyword2
```

## Keep evaluating

By default, once a rule condition matches an email, evaluation will stop, and sub-sequent rules will not be applied. This can be changed per rule by setting `keep_evaluating` to `true`:
```yaml
- condition:
    FROM: example@email.org
  move_to: some/folder
  keep_evaluating: true
```

## Actions

Actions allow to do more than just moving your emails around.

Some common actions are pre-defined, and can be used like so:

```yaml
- condition:
    FROM: example@email.org
  actions:
   - mark_read  # mark email as read
   - trash      # move email to Trash folder
   - delete     # deletes the email ()
```


Other actions are

### Flag / Unflag

Allow to either set or unset an IMAP flag to a message. Possible flags are:
- `SEEN`
- `ANSWERED`
- `FLAGGED` (often marked as a star in UIs)
- `DELETED` (will delete the message)
- `DRAFT`

Examples:
```yaml
- condition:
    FROM: example@email.org
  actions:
   - action: flag
     flag: SEEN
```

```yaml
- condition:
    FROM: example@email.org
  actions:
   - action: unflag
     flag: SEEN
```

Using custom flags is also supported:
```yaml
- condition:
    FROM: example@email.org
  actions:
   - action: flag
     custom_flag: MYCUSTOMFLAG
```


### Pre-configured actions

It is possible to define actions globally, and re-use them across the rules:

```yaml
actions:
  mark_important:
    action: flag
    flag: FLAGGED

rules:
  - condition:
      FROM: example@email.org
    actions:
     - mark_important
```

## Manage IMAP folders

Run the following to see the available commands:

    mmuxer folder --help

The `compare-destinations` command ispecially useful, as it will compare the move destinations of your config file with the IMAP folders on your server, and display the differences (allowing you to spot mistakes in your configuration, or missing folders on your server).

## SSL configuration

Depending on the server your are connecting to, you may need specific cipher suite. You can specify it in the settings part of the configuration file:

```
settings:
  ssl_ciphers: DEFAULT@SECLEVEL=1  # value that actually works for me
```

The value that actually worked for me was `DEFAULT@SECLEVEL=1` (I believe the default on most linux distributions is `DEFAULT@SECLEVEL=2`).

See [the openssl page](https://www.openssl.org/docs/man1.0.2/man1/ciphers.html) about cipher suites (this escalated quickly).

