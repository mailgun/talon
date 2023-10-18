# talon <-> cchardet <-> cython issue

`talon` is a package we use in `messaging-template-manager` to parse inbound emails so that we can extract
the latest message from a series of email responses.

`talon` depends on `cchardet` and `cchardet` depends on `cython`.

The `cython` project has recently moved a bunch of include file locations by pushing them into a subdirectory.

The `cchardet` package definition of its dependencies hasn’t been updated in years. Many threads seem to
indicate the single maintainer has abandoned the project.

There is a fork of `cchardet` called `faust-cchardet` that installs as `cchardet` so that code can use it
without changing imports. This works great if you are running manual pip installs, but doesn’t work for
dependency resolution (i.e. if a package depends on `cchardet` you cannot use `faust-cchardet` in your
`requirements.txt` since the parent package defines `ccardet` as its requirement.

The `talon` package also hasn’t been updated in years. Therefore it is still using `cchardet`.

# Solution Options

Our options were:

 1. Stop using `talon` entirely
 2. Find a `talon` alternative
 3. Fork `talon` and change its dependcy from `cchardet` to `faust-cchardet`

## Option 1: Stop using `talon`

The user experience without `talon` is abysmal. In an email chain with 3+ responses the in-app messaging
gets very unwieldy and ugly, so option 1 is out.

## Option 2: Find a `talon` alternative

There really isn’t a `talon` alternative. There is nothing close to what it does. Parsing email is a
nightmare, message response bodies are the worst part. Mailgun is the company that maintains Talon
and email management and services is their product. So option 2 is out.

## Option 3: Fork `talon`

Forking, while ugly will work for now.

For a while, someone had already done this for us. But at some point in time they deleted
the patch we were using. Therefore we forked `talon` ourselves and implemented the same
patch:

Diff to `requirements.txt`:
```
  chardet>=1.0.1        chardet>=1.0.1
- cchardet>=0.3.5     + faust-cchardet
  cssselect             cssselect
  html5lib              html5lib
  joblib                joblib
```

Diff to `setup.py`:

```
  "scipy",                  "scipy",
  "scikit-learn>=1.0.0",    "scikit-learn>=1.0.0",
  "chardet",                "chardet",
- "cchardet",             + "faust-cchardet",
  "cssselect",              "cssselect",
  "six",                    "six",
  "html5lib",               "html5lib",
```
# Usage

In our `messaging-template-manager` repo we need to define the `talon` requirement as:

```
talon @ git+https://github.com/axialmarket/talon@fix-cchardet
```

