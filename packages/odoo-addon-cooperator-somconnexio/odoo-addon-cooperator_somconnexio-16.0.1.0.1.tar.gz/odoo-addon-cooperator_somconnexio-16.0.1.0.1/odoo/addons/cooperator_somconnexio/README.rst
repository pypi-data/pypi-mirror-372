##########################
 Cooperator - SomConnexio
##########################

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
   :alt: Beta
   :target: https://odoo-community.org/page/development-status

.. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
   :alt: License: AGPL-3
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html

.. |badge3| image:: https://img.shields.io/badge/gitlab-coopdevs%2Fodoo--somconnexio-lightgray.png?logo=gitlab
   :alt: coopdevs/som-connexio/odoo-somconnexio
   :target: https://git.coopdevs.org/coopdevs/som-connexio/odoo-somconnexio

.. |badge4| image:: https://img.shields.io/badge/weblate-Translate%20me-F47D42.png
   :alt: Translate me on Weblate
   :target: https://translation.odoo-community.org/projects/odoo-somconnexio-12-0/odoo-somconnexio-12-0-cooperator_somconnexio

|badge1| |badge2| |badge3| |badge4|

This module is a part of SomConnexió original module.

We are working to separate the monolitic original module in small
modules splited by functionalities.

This module manage the integration between Odoo an OpenCell.

Cooperator module allow us to include in our organization members,
sponsees by members or sponsees by company agreements. Each cooperator
type have specific business logic (i.e. different products can be
offered)

Add a discovery channel field to subscription requests to know how the
users knew about our organization. Add sponsorship information in
SomConnexio's SQL query to allow OTRS to check partner information in
our DB. Using listeners, we observe if a sponsee's member quits the
cooperative, so this sponsee recieves an email to offer them other
possibilities to continue belonging to our coooperative.

**Table of contents**

.. contents::
   :local:

***************
 Configuration
***************

Products
========

To configure products available for each cooperative agreement:

> Menu / Cooperator / Contacts / Coop Agreements

*******
 Usage
*******

The usage is full integrated with the ORM of Odoo using listeners.

More info about the listeners:
https://odoo-connector.com/api/api_components.html#listeners

**************
 Contributors
**************

-  ``Som Connexió SCCL <https://somconnexio.coop/>``\_\_

   -  Gerard Funonsas gerard.funosas@somconnexio.coop
   -  Borja Gimeno borja.gimeno@somconnexio.coop

-  ``Coopdevs Treball SCCL <https://coopdevs.coop/>``\_\_

   -  Daniel Palomar daniel.palomar@coopdevs.org
   -  Cesar Lopez cesar.lopez@coopdevs.org
   -  Carla Berenguer carla.berenguer@coopdevs.org
