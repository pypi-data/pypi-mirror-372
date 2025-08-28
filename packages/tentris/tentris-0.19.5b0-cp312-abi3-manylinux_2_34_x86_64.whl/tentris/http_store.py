import rdflib.plugins.stores.sparqlstore


class TentrisHTTPStore(rdflib.plugins.stores.sparqlstore.SPARQLUpdateStore):
    """
    :warning: Like the SPARQL store provided in rdflib (https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.plugins.stores.html#rdflib.plugins.stores.sparqlstore.SPARQLStore)
              this does not support blank-nodes!
              When a graph's identifier is a blank node this store queries the default graph.
    """
    context_aware = True  # tentris supports graphs
    formula_aware = False  # tentris does not support quoted triples (triples about other triples)
    transaction_aware = True  # tentris supports transactions (each update is one transaction)
    graph_aware = False  # tentris does not track empty graphs

    def __init__(self,
                 host: str = "http://localhost:9080",
                 autocommit: bool = True,
                 dirty_reads: bool = False,
                 **kwargs,
                 ):
        super().__init__(
            query_endpoint=f"{host}/sparql",
            update_endpoint=f"{host}/update",
            sparql11=True,
            context_aware=True,
            autocommit=autocommit,
            dirty_reads=dirty_reads,
            returnFormat="json",
            **kwargs
        )


rdflib.plugin.register("TentrisHTTP", rdflib.plugin.Store, __name__, "TentrisHTTPStore")
