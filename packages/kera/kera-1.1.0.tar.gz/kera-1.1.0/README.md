# NAME

kera — Fill template files with structured data

# SYNOPSIS

**kera** *plate_files*... *data_files*...

# OPTIONS

-o, \--out-dir
:   The directory in which to write all files.  Defaults to the current
    directory.

# INSTALL

kera can be installed using the pip package manager.

    pipx install kera

# DESCRIPTION

This program takes a collection of template files (.plate) and a collection of
data files (.json or .yaml) and then uses the data to fill placeholder "keys"
in the templates.  Each individual data file produces an output for each
individual template file.

To represent a simple key in a template file, surround it in double hashes:

```
= ##title##
by ##name## on ##date##

##content##
```

And provide the data in your format of choice:

```
{
    "title": "kera",
    "name": "Carston Wiebe",
    "date": "JAN 01 1970",
    "content": "Fill template files with structured data."
}
```

This results in:

```
= kera
by Carston Wiebe on JAN 01 1970

Fill template files with structured data.
```

Template files can have the extension .plate, but any file that isn't a data
file will be read as a template by default.

Supported data filetypes are:

- JSON
- YAML

If you want to use a data file as a template file, it must have the .plate
extension, e.g. .json.plate

The default filename of the filled template is the name of the data file (minus
extension), an underscore, and the name of the template file (with extension,
minus .plate if present).  These output files can be redirected to a different
directory with the \--out option.

As an example:

```
$ ls
> 123.sql 456.sql.plate abc.json def.yml
$ kera --out output 123.sql 456.sql.plate abc.json def.yml
$ ls output
> abc_123.sql abc_456.sql def_123.sql def_456.sql
```

---

kera also supports conditional keys and collection keys.  Conditional keys can
be represented as such:

```
##[ condition ]{{ if true }}{{ if false (optional) }}
```

The condition is simply a key found in the data, and it is true if the value
of the key is truthy according to Python.  If the key is not found, it is
automatically false.  The "body" of the conditional slot is treated as normal
body text, you can include other slots inside it and nest slots as much as you
wish.  For instance:

```
<div class="profile">
    <h3>##name##</h3>
    <ul class="inline">
        ##[pronouns]{{ <li>##pronouns##</li> }}
        ##[language]{{ <li>##language##</li> }}
        ##[join-date]{{ <li>Joined ##joined-date##</li> }}
    </ul>
    ##[desc]{{
        ##desc##
    }}{{
        <p>No bio provided.</p>
    }}
</div>
```

With this, you process full profiles:

```
name: Scofflaw Saxwulf
pronouns: he/him
language: ENG | FIN
join-date: AUG 23 2025
desc: <p>INSERT INTERESTING BIO HERE</p>
```

```
<div class="profile">
    <h3>Scofflaw Saxwulf</h3>
    <ul class="inline">
        <li>he/him</li>
        <li>ENG | FIN</li>
        <li>Joined </li>
    </ul>
    <p>INSERT INTERESTING BIO HERE</p>
</div>
```

And partial profiles:

```
name: Lusaka Hernesto
pronouns: she/her
```

```
<div class="profile">
    <h3>Lusaka Hernesto</h3>
    <ul class="inline">
        <li>she/her</li>
        
        
    </ul>
    <p>No bio provided.</p>
</div>
```

---

Collection keys are represented as:

```
##collection{{ body for each collection member }}
```

In a collection body, the "scope" that contains available keys is not the
original data, but rather the keys nested insided the collection key.  This
is easier shown than explained:

```
table: Person
joins:
  - table: Place
    alias: a
    join-on: addressId

  - table: Place
    alias: w
    join-on: workAddressId

  - table: Job
    alias: j
    join-on: workId
```

```
SELECT  *
FROM    ##table##
##joins{{
    JOIN    ##table## ##alias## ON ##join-on## = ##alias##.id
}};
```

```
SELECT  *
FROM    Person
JOIN    Place a ON addressId = a.id
JOIN    Place w ON workAddressId = w.id
JOIN    Job j ON workId = j.id;
```

By default each member of the collection is joined with a newline, but you
can alter this by providing a join string before the collection body:

```
table: Record
columns:
  - name: create_date
    type: DATE

  - name: update_date
    type: DATE

  - name: id
    type: INTEGER

  - name: content
    type: TEXT
```

```
CREATE PROCEDURE insert_into_##table##
( ##columns(\n, ){{
    p_##name## IN ##type##
  }}
)
BEGIN

    INSERT
    INTO    ##table##
            ( ##columns(\n            , ){{
                ##name##
              }}
            )
    VALUES  ( ##columns(\n            , ){{
                p_##name##
              }}
            );

END insert_into_##table##;
```

```
CREATE PROCEDURE insert_into_Record
( p_create_date IN DATE
, p_update_date IN DATE
, p_id IN INTEGER
, p_content IN TEXT
)
BEGIN

    INSERT
    INTO    Record
            ( create_date
            , update_date
            , id
            , content
            )
    VALUES  ( p_create_date
            , p_update_date
            , p_id
            , p_content
            );

END insert_into_Record;
```

# RETURN CODES

0, RETCODE_OK
:   Code execution was successful.

1, RETCODE_NOCREATE_OUTDIR
:   Unable to create or find the given output directory.

# BUGS

1.  If a key in YAML is made up of numbers and only numbers, the YAML parser
    will store it as an integer, which won't be resolved properly when kera
    tries to retrieve it as a string.  To prevent this, surround such keys with
    double quotes:

    ```
    # bad:
    1: this won't be resolved
    # good:
    "1": this WILL be resolved
    ```
