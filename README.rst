talon
=====

Mailgun library to extract message quotations and signatures.

**This library requires Python 3.8 or newer.**

If you ever tried to parse message quotations or signatures you know that absence of any formatting standards in this area could make this task a nightmare. Hopefully this library will make your life much easier. The name of the project is inspired by TALON - multipurpose robot designed to perform missions ranging from reconnaissance to combat and operate in a number of hostile environments. That's what a good quotations and signature parser should be like :smile:

Installation
------------

You can install Talon using pip:

.. code:: bash

    pip install talon

Or, if you want to install it from source:

.. code:: bash

    git clone https://github.com/mailgun/talon.git
    cd talon
    python setup.py install

If you don't need the machine learning based signature extraction, you can install a lighter version:

.. code:: bash

    python setup.py install --no-ml


Usage
-----

Here's how you initialize the library and extract a reply from a text
message:

.. code:: python

    import talon
    from talon import quotations

    talon.init() # Necessary if using ML-based signature extraction

    text =  """Reply

    -----Original Message-----

    Quote"""

    reply = quotations.extract_from(text, 'text/plain')
    # or directly:
    # reply = quotations.extract_from_plain(text)
    # reply == "Reply"

To extract a reply from html:

.. code:: python

    # Assuming talon and quotations are already imported, and talon.init() called if needed.
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
    # or directly:
    # reply = quotations.extract_from_html(html)
    # reply == "<html><body><p>Reply</p></body></html>"

Often the best way is the easiest one. Here's how you can extract
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
the power of machine learning algorithms (this requires `scikit-learn>=1.0.0`, `numpy`, `scipy`, and `joblib`):

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

For machine learning talon currently uses the `scikit-learn`_ library (version 1.0.0 or newer) to build SVM
classifiers. The core of machine learning algorithm lays in
``talon.signature.learning package``. It defines a set of features to
apply to a message (``featurespace.py``), how data sets are built
(``dataset.py``), classifier's interface (``classifier.py``).

Currently the data used for training is taken from our personal email
conversations and from `ENRON`_ dataset. As a result of applying our set
of features to the dataset we provide files ``classifier`` and
``train.data`` that don't have any personal information but could be
used to load trained classifier. Those files should be regenerated every
time the feature/data set is changed.

To regenerate the model files, you can run:

.. code:: sh

    python train.py

or programmatically:

.. code:: python
    
    from talon.signature.learning.classifier import train, init
    from talon.signature import EXTRACTOR_FILENAME, EXTRACTOR_DATA # Assuming these are defined in talon.signature
    
    # Ensure EXTRACTOR_FILENAME and EXTRACTOR_DATA point to the correct paths for your model and training data
    # e.g., talon.signature.EXTRACTOR_DATA = "talon/signature/data/train.data"
    #       talon.signature.EXTRACTOR_FILENAME = "talon/signature/data/classifier"

    train(init(), EXTRACTOR_DATA, EXTRACTOR_FILENAME)

Open-source Dataset
-------------------

We have started a `forge`_ project to create an open-source, annotated dataset of raw emails. In the project we
used a subset of `ENRON`_ data, cleansed of private, health and financial information by `EDRM`_. At the moment over 190
emails are annotated. Any contribution and collaboration on the project are welcome. Once the dataset is ready we plan to
start using it for talon.

.. _scikit-learn: https://scikit-learn.org/stable/
.. _ENRON: https://www.cs.cmu.edu/~enron/
.. _EDRM: http://www.edrm.net/resources/data-sets/edrm-enron-email-data-set
.. _forge: https://github.com/mailgun/forge

Training on your dataset
------------------------

Talon comes with a pre-processed dataset and a pre-trained classifier. To retrain the classifier on your own dataset of raw emails, structure and annotate them in the same way the `forge`_ project does. Then do:

.. code:: python

    from talon.signature.learning.dataset import build_extraction_dataset
    from talon.signature.learning import classifier as c 
    
    # Define paths to your data and where the talon model files are located
    your_p_folder_path = "/path/to/your/P/folder"
    talon_train_data_path = "/path/to/talon/signature/data/train.data" # Or where you want to save it
    talon_classifier_path = "/path/to/talon/signature/data/classifier" # Or where you want to save it

    build_extraction_dataset(your_p_folder_path, talon_train_data_path)
    c.train(c.init(), talon_train_data_path, talon_classifier_path)

Note that for signature extraction you need just the folder with the positive samples with annotated signature lines (P folder).

Research
--------

The library is inspired by the following research papers and projects:

-  `Identifying Signatures in Email <http://www.cs.cmu.edu/~vitor/papers/sigFilePaper_finalversion.pdf>`_
-  `Learning to Classify Text from Labeled and Unlabeled Documents <http://www.cs.cornell.edu/people/tj/publications/joachims_01a.pdf>`_
