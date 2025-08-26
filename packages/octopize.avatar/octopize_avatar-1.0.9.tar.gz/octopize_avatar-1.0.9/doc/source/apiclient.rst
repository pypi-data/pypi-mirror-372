ApiClient
=========

The ``ApiClient`` is the low-level interface to the Avatar platform.
It manages HTTP communication, authentication token refresh, and exposes
resource-specific helper objects (``jobs``, ``results``, ``datasets``, ``resources``, ``users``, etc.).

When to use it
--------------
Use the ``ApiClient`` directly when you need fine-grained control:

* Custom timeouts or SSL verification settings.
* Injecting a custom ``httpx.Client`` instance (e.g. for proxies or advanced retry logic).
* Building tooling or SDK features on top of exposed resources.

For everyday avatarization tasks, the :doc:`Manager <manager>` plus a :doc:`Runner <runner>` will usually suffice.

Session & authentication
------------------------

``ApiClient.authenticate`` exchanges user credentials for access/refresh tokens.
Tokens are stored internally (``auth_tokens``) and bearer headers are automatically
attached to subsequent requests. If the server issues a refresh token, the client
can refresh it lazily when needed.

Key attributes
--------------

* ``base_url`` – API endpoint root (e.g. ``https://instance/api``)
* ``timeout`` – default request timeout (seconds)
* ``should_verify_ssl`` – SSL certificate verification toggle
* ``verify_auth`` – whether to enforce client-side auth checks
* ``auth`` / ``jobs`` / ``results`` / ``datasets`` / ``users`` / etc. – resource facades

Example
-------

.. code-block:: python

   from avatars.client import ApiClient
   client = ApiClient(base_url="https://instance/api")
   client.authenticate("user", "pass")
   all_jobs = client.jobs.get_jobs().jobs
   if all_jobs:
       first = all_jobs[0]
       result = client.results.get_results(first.name)
       print(result)

Detailed reference
------------------

.. automodule:: avatars.client
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:
