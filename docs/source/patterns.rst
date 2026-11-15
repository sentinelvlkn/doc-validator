Използвани шаблони за дизайн
============================

В проекта са приложени два шаблона: **Chain of Responsibility** и **Visitor**.

Chain of Responsibility
-----------------------

Шаблонът се използва за обработка на заявка за валидация на файл.
Заявката минава през поредица от независими проверки. Всяка проверка
може да спре веригата при грешка.

Класова диаграма:

.. uml:: ../diagrams/class_diagram.puml
   :caption: Класова диаграма на Chain of Responsibility

Sequence диаграма:

.. uml:: ../diagrams/sequence_chain.puml
   :caption: Обработка на заявка през веригата

Handler-и във веригата:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Handler
     - Отговорност
   * - ``FileExistsHandler``
     - Проверява, че файлът съществува и е с позволено разширение
   * - ``FormatDetectHandler``
     - Определя ``json`` или ``csv`` по разширението
   * - ``ParseHandler``
     - Прочита файла чрез подходящия парсер
   * - ``TypeCheckHandler``
     - Определя типа на документа и построява ``Document``
   * - ``ContentValidateHandler``
     - Изпълнява ``ValidationVisitor`` върху документа


Visitor
-------

Шаблонът се използва за операции над готовия документ. Документът е
дърво от :class:`documents.base.Document` (корен) и
:class:`documents.base.Field` (листа). Всеки visitor имплементира
операция, която може да бъде приложена върху всеки елемент.

Sequence диаграма:

.. uml:: ../diagrams/sequence_visitor.puml
   :caption: Обхождане на документа чрез Visitor

Конкретни visitor-и:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Visitor
     - Операция
   * - ``ValidationVisitor``
     - Прилага всички правила от ``meta`` и връща грешки
   * - ``SummaryVisitor``
     - Връща резюме (тип, брой полета, брой празни)
   * - ``ExportVisitor``
     - Експортира документа обратно в речник


Защо Visitor е подходящ тук
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Без Visitor всяка нова операция (например нов вид проверка или нов
изходен формат) изисква промяна в класовете ``Document`` и ``Field``.
С Visitor новите операции се добавят като нови класове, без да се
пипа съществуващият код. Това е класическата мотивация за шаблона и
точно това демонстрираме с трите visitor-а.
