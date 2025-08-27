# NAME

piknik - Issue tracking using CLI

# SYNOPSIS

**piknik** add \[ -d store_dir \] \[ \--alias issue_alias \] caption

**piknik** show \[ -i issue_id \] \[ -d store_dir \] \[ -r renderer \]
\[ \--state state \]

**piknik** show \[ -d store_dir \] -r html \[ -o output_dir \]

**piknik** mod \< -i issue_id \> \[ -d store_dir \] \[ \--state state
\] \[ -t tag \] \[ -u tag \] \[ \--dep issue_id \] \[ \--undep issue_id
\] \[ \--assign id \] \[ \--unassign id \]

**piknik** mod \< -i issue_id \> \[ -d store_dir \] \[ \--block \]

**piknik** mod \< -i issue_id \> \[ -d store_dir \] \[ \--unblock \]

**piknik** comment \< -i issue_id \> \[ -d store_dir \] \[ \[ -x \"text
content\" \... \] \[ -y file \... \] \... \]

# DESCRIPTION

This tool enables issue tracking by command line interface.

After an issue has been created it can move through different
pre-defined, kanban-like states. They can also be tagged, assigned and
commented on.

# COMMANDS

The following commands are available:

> **show** - Output all issues for all or selected issue states.
>
> **add** - Propose a new issue.
>
> **mod** - Tag, assign, set dependencies and modify state of an
> existing issue.
>
> **comment** - Add comment to an existing issue.

## Common options

**-d**

:   Issue state store directory.

**-h**

**\--help** Command help summary.

**-i***issue_id*

**\--issue-id***issue_id* Issue to operate on. Argument can be issue
alias or full issue uuid. Only available with **mod** and **comment**.

**-s***state*

**\--state***state* Limit output to issue having the given *state*.
(Only valid with **show** or **mod**).

-v

:   Write debugging log to standard error.

## Options for add

**\--alias**

:   Specify alias used to refer to issue when using **-i**. If not
    specified, an alias will be auto-generated. See **ALIAS**. Only
    available with **add**.

## Options for show

**-f**

**\--files** Save attachments to filesystem. Can be used in the context
of viewing details of a single issue, or in conjunction with **-r html
-o**. Only available with **show**.

**-o***dir*

**\--files-dir***dir* Output issue details to individual files in *dir*.
Only available with **show -r html \...**.

**-r***format*

**\--renderer***format* Output format. Valid values are *plain* and
*html*.

**-reverse**

:   Sort comments with oldest first. Only available with **show**.

**\--show-finished**

:   Include issues with state **FINISHED** in output. Only available
    with **show**.

## Options for mod

**\--assign***key_id*

:   Assign the issue to entity defined by *key_id*. If it is the first
    assignment for an issue, the assigned will become the issue *owner*
    (see **\--owner** and **ACTIONS/Assignment** below. Only available
    with **mod**.

**\--block**

:   Set the **BLOCKED** state on the issue. Preserves the previous
    state; a following **\--unblock** instruction will return the issue
    to the pre-blocked state. Only available with **mod**.

**\--dep***issue_id*

:   Make the current issue (identified by **-i** dependent on
    *issue_id*. Only available with **mod**.

**\--owner***key_id*

:   Set the entity represented by *key_id* as issue owner.

**-t***tag*

**\--tag***tag* Add the given tag to the issue. Only available with
**mod**.

**\--unassign***key_id*

:   Remove the assignment of the issue to entity defined by *key_id*.
    Only available with **mod**.

**\--unblock**

:   Remove block on issue. Will return the issue to its previous state
    (before the block). Only available with **mod**.

**\--undep***issue_id*

:   Remove dependency on *issue_id*. Only available with **mod**.

**-u***tag*

**\--untag***tag* Remove the given tag from the issue. Only available
with **mod**.

## Options for comment

**-s***pgp_key_fingerprint*

**\--sign-as***pgp_key_fingerprint* Use the private key matching the
fingerprint to sign (instead of the default key). Only available with
**comment**.

**-x***text*

**\--text***text* Add a text content part to the comment. Must be
enclosed by double quotes. Only available with **comment**.

**-y***file*

**\--file***file* Add file as content part to the comment. Can be any
type of file. Only available with **comment**. See the **COMMENT**
section for more information.

# STATES

The tracking of the issue lifetime is organized using a pre-defined set
of kanban-like states.

**PROPOSED**

:   The initial state of an issue after being created by **piknik add**.
    Is intended for review by issue board moderator.

**BACKLOG**

:   The initial state of an issue after being \"accepted\" by a
    moderator.

**PENDING**

:   An issue has been queued for imminent processing.

**DOING**

:   An issue is currently being worked on.

**REVIEW**

:   Work that was done on an issue is currently in review.

**BLOCKED**

:   Progress on a **PENDING** issue is currently not possible.

**FINISHED**

:   Processing of an issue has been completed.

# ACTIONS

## Assignment

Indicates an individual or entity that is responsible for processing the
issue.

Currently assigments are defined as hexadecimal values. By convention,
the value should correspond to e.g. a public key or a key fingerprint
(e.g. PGP). **piknik** will check that the value is hexadecimal, but
will not do additional verification.

The first assigned entity to an issue automatically becomes the issue
owner. The issue ownership may be changed using **\--owner**, but
ownership cannot be removed entirely after the initial assignment.

## Tagging

Any issue may be assigned any number of tags. Tags may be added and
removed individually.

## Dependencies

Any issue may be set as dependent on another issue. Dependencies may be
set or unset. Dependencies must be manually managed, and will not be
magically removed as a side-effect of state transitions.

# COMMENTING

Comments are stored as email-like Multipart MIME message logs. They may
include any number of plaintext and file attachment parts intermingled.

All comments must be **signed** using a PGP key. Unless the **-s** flag
is used, the default signing key will be used. It is currently not
possible to comment without a PGP key.

# RENDERING

There are currently two rendering options for displaying issue indices
and individual issue details, *plain* (plain text) and *html*.
Ideosyncracies for each are described below.

## PLAIN

When listing the issue index, output will be in the form:

    [STATE]
    <caption>	<tags>	<uuid>	[(alias)]

Per-issue render should be self-explanatory.

## HTML

If rendered with **-o** *outdir* it creates a browseable version of
individual issues from the issue index in the specified directory.

Some image types will by default be displayed inline. There is currently
no way to toggle this behavior.

# EXAMPLE

This example illustrates a possible lifetime of an issue.

    # propose new issue
    piknik add Title describing the issue --alias myissue

    # accept proposed issue (move to backlog state)
    piknik mod -i myissue --accept

    # move the issue to state "DOING"
    piknik mod -i myissue --state doing

    # tag the issue as a "BUG"
    piknik mod -i myissue --tag bug

    # Add a signed text comment to the issue
    piknik comment -i myissue -x "This is a text comment"

    # Add a comment with intermixed text and attachment contents to the issue
    piknik comment -i myissue -x "This is a text comment with two attachments " -y attachment.png -y another.pdf -x "This text follows the attachments"

    # Write index of all issues as plain text to standard output
    piknik show

    # Write issue details as plain text to standard output
    piknik show -i myissue

    # Write index of all issues as html to standard output
    piknik show --render html

    # Write index and individual issue as browseable html to directory "outdir"
    piknik show --render html -o outdir

    # Mark issue as finished
    piknik mod -i myissue --finish

# KNOWN ISSUES

Currently issues are tracked using - in fact - **piknik**. An HTML
(read-only) render can be found at
[](https://holbrook.no/issues/piknik)https://holbrook.no/issues/piknik

# LICENSE

This documentation and its source is licensed under the Creative Commons
Attribution-Sharealike 4.0 International license.

The source code of the tool this documentation describes is licensed
under the GNU General Public License 3.0.

# COPYRIGHT AND CONTACT

[Louis Holbrook](mailto:dev@holbrook.no)

[](https://holbrook.no)https://holbrook.no

PGP: 59A844A484AC11253D3A3E9DCDCBD24DD1D0E001

# SOURCE CODE

https://git.defalsify.org/piknik


# ABOUT THIS DOCUMENT

This document was generated using `pandoc -f man -t markdown ...`
