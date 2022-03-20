# Modulo

Versión modificada del módulo Librerias, a17ernestomr. 
El módulo cuenta con tres vistas: list, kanvan y calendar view.
Se han creado e implementado en las vistas tres campos calculados: 
    "Number" corresponde a las existencias disponibles de cada libro, dato que se establece al crear el libro, y sumando o restando uno cada vez que el libro pasa a estar disponible o se presta.
    "numBorrowed" corresponde al total de veces que se ha prestado un libro a lo largo de su vida. El valor siempre se incrementa en uno cada vez que el libro se presta.
    "author_number" es un campo calculado que utiliza el método "_compute_author_number" para devolver el número de ids de autores que tiene cada libro.
Se ha creado un botón "delete" en la vista "form", para borrar un libro con facilidad. 