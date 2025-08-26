Manager
=======

The Manager is the high-level entry point for most users.
It wraps an authenticated ``ApiClient`` and offers helper methods
that reduce boilerplate when running avatarizations.

Why use the Manager?
--------------------

* Single place to authenticate.
* Shortcuts to create a ``Runner`` and load YAML configs.
* Convenience helpers to inspect recent jobs / results.

Quick example
-------------

.. code-block:: python

   from avatars import Manager
   manager = Manager(base_url="https://your.instance/api")
   manager.authenticate(username="user", password="pass")
   runner = manager.create_runner(set_name="demo")
   runner.add_table("wbcd", "fixtures/wbcd.csv")
   runner.set_parameters("wbcd", k=15)
   runner.run()

Detailed reference
------------------

.. automodule:: avatars.manager
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:
