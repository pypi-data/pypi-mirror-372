BiSO
====

| Romain THOMAS 2025
| DiBISO - Université Paris-Saclay

ANR Projects
------------

.. code:: ipython3

    from dibisoplot.biso import AnrProjects
    
    anr_projects = AnrProjects(
        lab = "SUP_SONDRA",
        year = "2023",
    )
    
    anr_fig = anr_projects.get_figure()
    
    anr_fig.show()

Chapters
--------

.. code:: ipython3

    from dibisoplot.biso import Chapters
    
    chapters = Chapters(
        lab = "IEDP",
        year = "2023",
    )
    
    chapters_latex = chapters.get_figure()
    
    print(chapters_latex)

Collaboration Map
-----------------

.. code:: ipython3

    from dibisoplot.biso import CollaborationMap
    
    collab_map = CollaborationMap(
        lab = "LISN",
        year = "2023",
    )
    
    collab_map_fig = collab_map.get_figure(countries_to_ignore = ["France"])
    
    collab_map_fig.show()

Collaboration Names
-------------------

.. code:: ipython3

    from dibisoplot.biso import CollaborationNames
    
    collabs = CollaborationNames(
        lab = "LISN",
        year = "2023",
    )
    
    collabs_fig = collabs.get_figure(countries_to_exclude = ['fr'])
    
    collabs_fig.show()

Conferences
-----------

.. code:: ipython3

    from dibisoplot.biso import Conferences
    
    conf = Conferences(
        lab = "LGI",
        year = "2023",
    )
    
    conf_fig = conf.get_figure()
    
    conf_fig.show()

European Projects
-----------------

.. code:: ipython3

    from dibisoplot.biso import EuropeanProjects
    
    eu_projects = EuropeanProjects(
        lab = "UMPHY",
        year = "2023",
    )
    
    eu_projects_fig = eu_projects.get_figure()
    
    eu_projects_fig.show()

Journals
--------

.. code:: ipython3

    from dibisoplot.biso import Journals
    
    # TODO
    # journals = Journals(
    #     lab = "",
    #     year = "2023",
    # )
    
    # journals_fig = journals.get_figure()
    
    # journals_fig.show()

Open Access Works
-----------------

.. code:: ipython3

    from dibisoplot.biso import OpenAccessWorks
    
    oa_works = OpenAccessWorks(
        lab = "EM2C",
        year = 2023,
    )
    
    oa_works_fig = oa_works.get_figure()
    
    oa_works_fig.show()

Works Type
----------

.. code:: ipython3

    from dibisoplot.biso import WorksType
    
    works_type = WorksType(
        lab = "LGI",
        year = "2023",
    )
    
    works_type_fig = works_type.get_figure()
    
    works_type_fig.show()
