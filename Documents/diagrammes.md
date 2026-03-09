                    +----------------------+
                    |   source_donnees    |
                    +----------------------+
                    | id_source (PK)      |
                    | nom                 |
                    | url                 |
                    | date_collecte       |
                    +----------+----------+
                               |
                               | 1
                               |
                               | N
+----------------------+       v
|   bien_immobilier    |<----+----------------------+
+----------------------+     |       annonce        |
| id_bien (PK)        |     +----------------------+
| type_bien           |     | id_annonce (PK)      |
| type_offre          |     | titre                |
| surface_m2          |     | prix                 |
| pieces              |     | prix_m2              |
| id_zone (FK) -------+     | id_bien (FK)         |
+----------+----------+     | id_source (FK)       |
           |                +----------+-----------+
           |                           |
           | N                         |
           |                           |
           v                           |
+----------------------+               |
|   zone_geographique  |---------------+
+----------------------+
| id_zone (PK)         |
| nom                  |
| commune              |
| prefecture           |
+----------+-----------+
           |
           | 1
           |
           | N
           v
+----------------------+
|    valeur_venale     |
+----------------------+
| id_valeur (PK)       |
| id_zone (FK)         |
| prix_m2_officiel     |
| surface_m2           |
| valeur_totale        |
+----------------------+

+----------------------+
| statistiques_zone    |
+----------------------+
| id_stat (PK)         |
| id_zone (FK)         |
| prix_m2_moyen        |
| nb_annonces          |
| date_calcul          |
+----------------------+

+----------------------+
| indice_immobilier    |
+----------------------+
| id_indice (PK)       |
| id_zone (FK)         |
| indice_prix          |
| date_calcul          |
+----------------------+

+----------------------+
| annonces_rejetees    |
+----------------------+
| id_rejet (PK)        |
| titre                |
| zone                 |
| prix                 |
| surface_m2           |
| type_bien            |
| type_offre           |
| source               |
| raison_rejet         |
+----------------------+