Формати на документите
======================

Всеки тип документ има собствен формат и правила за валидация. Всички
правила са декларативно дефинирани в :mod:`documents.factory`.

Фактура (``invoice``) — JSON
----------------------------

Пример:

.. code-block:: json

   {
     "type": "invoice",
     "number": "INV-2024-001",
     "date": "2024-03-15",
     "supplier": {"name": "ABC Ltd", "vat": "BG123456789"},
     "customer": {"name": "XYZ OOD", "vat": "BG987654321"},
     "items": [
       {"description": "Лаптоп", "quantity": 2, "unit_price": 1500.00}
     ],
     "total": 3000.00
   }

Правила:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Поле
     - Правило
   * - ``number``
     - regex ``^INV-\d{4}-\d{3}$``
   * - ``date``
     - ISO 8601, дата не в бъдещето
   * - ``supplier.vat``, ``customer.vat``
     - regex ``^BG\d{9}$``
   * - ``items``
     - непразен масив
   * - ``items[].quantity``
     - цяло число ``>= 1``
   * - ``items[].unit_price``
     - число ``>= 0``
   * - ``total``
     - равен на сумата от артикулите (толеранс ``0.01``)


Доклад (``report``) — JSON
--------------------------

Пример:

.. code-block:: json

   {
     "type": "report",
     "title": "Тримесечен отчет",
     "author": "Иван Иванов",
     "department": "Engineering",
     "date": "2024-03-31",
     "pages": 12
   }

Правила:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Поле
     - Правило
   * - ``title``
     - дължина ``3–200`` знака
   * - ``author``
     - непразно
   * - ``department``
     - едно от ``Engineering``, ``Sales``, ``HR``, ``Finance``
   * - ``pages``
     - цяло число ``1–500``


Заявка за материали (``material_request``) — CSV
-------------------------------------------------

Пример:

.. code-block:: text

   material,quantity,unit,urgency,deadline
   Хартия A4,10,пакет,normal,2099-03-20
   Тонер,2,брой,high,2099-03-18

Правила:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Поле
     - Правило
   * - ``material``
     - непразно
   * - ``quantity``
     - цяло число ``>= 1``
   * - ``unit``
     - едно от ``брой``, ``пакет``, ``кг``, ``литър``
   * - ``urgency``
     - едно от ``low``, ``normal``, ``high``
   * - ``deadline``
     - ISO 8601, дата в бъдещето
