talon
=====

Mailgun library to extract message quotations and signatures.

If you ever tried to parse message quotations or signatures you know that absence of any formatting standards in this area could make this task a nightmare. Hopefully this library will make your life much easier. The name of the project is inspired by TALON - multipurpose robot designed to perform missions ranging from reconnaissance to combat and operate in a number of hostile environments. That’s what a good quotations and signature parser should be like :smile:

Usage
-----

Here’s how you initialize the library and extract a reply from a text
message:

.. code:: python

    import talon
    from talon import quotations

    talon.init()

    text =  """Reply

    -----Original Message-----

    Quote"""

    reply = quotations.extract_from(text, 'text/plain')
    reply = quotations.extract_from_plain(text)
    # reply == "Reply"

To extract a reply from html:

.. code:: python

    html = """Reply
    <blockquote>

      <div>
        On 11-Apr-2011, at 6:54 PM, Bob &lt;bob@example.com&gt; wrote:
      </div>

      <div>
        Quote
      </div>

    </blockquote>"""

    reply = quotations.extract_from(html, 'text/html')
    reply = quotations.extract_from_html(html)
    # reply == "<html><body><p>Reply</p></body></html>"

Often the best way is the easiest one. Here’s how you can extract
signature from email message without any
machine learning fancy stuff:

.. code:: python

    from talon.signature.bruteforce import extract_signature


    message = """Wow. Awesome!
    --
    Bob Smith"""

    text, signature = extract_signature(message)
    # text == "Wow. Awesome!"
    # signature == "--\nBob Smith"

Quick and works like a charm 90% of the time. For other 10% you can use
the power of machine learning algorithms:

.. code:: python

    import talon
    # don't forget to init the library first
    # it loads machine learning classifiers
    talon.init()

    from talon import signature


    message = """Thanks Sasha, I can't go any higher and is why I limited it to the
    homepage.

    John Doe
    via mobile"""

    text, signature = signature.extract(message, sender='john.doe@example.com')
    # text == "Thanks Sasha, I can't go any higher and is why I limited it to the\nhomepage."
    # signature == "John Doe\nvia mobile"

For machine learning talon currently uses the `scikit-learn`_ library to build SVM
classifiers. The core of machine learning algorithm lays in
``talon.signature.learning package``. It defines a set of features to
apply to a message (``featurespace.py``), how data sets are built
(``dataset.py``), classifier’s interface (``classifier.py``).

Currently the data used for training is taken from our personal email
conversations and from `ENRON`_ dataset. As a result of applying our set
of features to the dataset we provide files ``classifier`` and
``train.data`` that don’t have any personal information but could be
used to load trained classifier. Those files should be regenerated every
time the feature/data set is changed.

To regenerate the model files, you can run

.. code:: sh

    python train.py

or

.. code:: python
    
    from talon.signature import EXTRACTOR_FILENAME, EXTRACTOR_DATA
    from talon.signature.learning.classifier import train, init
    train(init(), EXTRACTOR_DATA, EXTRACTOR_FILENAME)

Open-source Dataset
-------------------

Recently we started a `forge`_ project to create an open-source, annotated dataset of raw emails. In the project we
used a subset of `ENRON`_ data, cleansed of private, health and financial information by `EDRM`_. At the moment over 190
emails are annotated. Any contribution and collaboration on the project are welcome. Once the dataset is ready we plan to
start using it for talon.

.. _scikit-learn: http://scikit-learn.org
.. _ENRON: https://www.cs.cmu.edu/~enron/
.. _EDRM: http://www.edrm.net/resources/data-sets/edrm-enron-email-data-set
.. _forge: https://github.com/mailgun/forge


Research
--------

The library is inspired by the following research papers and projects:

-  http://www.cs.cmu.edu/~vitor/papers/sigFilePaper_finalversion.pdf
-  http://www.cs.cornell.edu/people/tj/publications/joachims_01a.pdf
