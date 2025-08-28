import abc
import typing

import rdflib.parser
import rdflib.query
import rdflib.store
import tentris_sys

_Triple = typing.Tuple[rdflib.term.Node, rdflib.term.Node, rdflib.term.Node]
_Quad = typing.Tuple[rdflib.term.Node, rdflib.term.Node, rdflib.term.Node, rdflib.Graph]
_TriplePattern = typing.Tuple[
    typing.Optional[rdflib.term.Node], typing.Optional[rdflib.term.Node], typing.Optional[rdflib.term.Node]]
_ContextIdentifierType = typing.Union[rdflib.term.URIRef, rdflib.term.BNode]

_VAR_LUT = ["?s", "?p", "?o"]


def _from_tentris(raw_node: tentris_sys.rdf4cpp_node) -> typing.Optional[rdflib.term.Node]:
    """
    Convert a tentris node into an rdflib node

    :param raw_node: tentris node
    :return: rdflib node
    """
    if tentris_sys.rdf4cpp_term_null(raw_node):
        return None

    if tentris_sys.rdf4cpp_is_literal(raw_node):
        lex = tentris_sys.rdf4cpp_literal_lexical_form(raw_node)
        lang = tentris_sys.rdf4cpp_literal_lang(raw_node)

        if lang:
            return rdflib.term.Literal(lex, lang=lang)

        datatype = tentris_sys.rdf4cpp_iri_identifier(tentris_sys.rdf4cpp_literal_datatype(raw_node))
        if datatype == "http://www.w3.org/2001/XMLSchema#string":
            return rdflib.term.Literal(lex)

        return rdflib.term.Literal(lex, datatype=rdflib.term.URIRef(datatype))
    elif tentris_sys.rdf4cpp_is_iri(raw_node):
        return rdflib.term.URIRef(tentris_sys.rdf4cpp_iri_identifier(raw_node))
    elif tentris_sys.rdf4cpp_is_bnode(raw_node):
        return rdflib.term.BNode(tentris_sys.rdf4cpp_bnode_identifier(raw_node))
    else:
        return rdflib.term.Variable(tentris_sys.rdf4cpp_variable_name(raw_node))


def _to_query_tp(tp: typing.Union[_Triple, _TriplePattern]) -> str:
    """
    Translate a triple pattern into a string for interpolating into the where clause of the query.
    Example: _to_query_tp((None, rdflib.URIRef("http://example.com#p"), None)) -> "?s <http://example.com#p> ?o"

    :param tp: triple pattern
    :return: string representation of the triple pattern for a WHERE clause of a SPARQL query
    """
    return " ".join(val.n3() if val is not None else _VAR_LUT[ix] for ix, val in enumerate(tp)) + " ."


def _to_query_proj(tp: typing.Union[_Triple, _TriplePattern]) -> str:
    """
    Translate a triple pattern into a string for interpolating into the projection clause of a query.
    Example: _to_query_proj((None, rdflib.URIRef("http://example.com#p"), None)) -> "?s (<http://example.com#p> AS ?p) ?o"

    :param tp: triple pattern
    :return: string representation of the triple pattern for the projection clause of a SPARQL query
    """
    return " ".join(f"({val.n3()} AS {_VAR_LUT[ix]})" if val is not None else _VAR_LUT[ix] for ix, val in enumerate(tp))


def _to_query_quad(quad: _Quad) -> str:
    """
    Translate a quad into a string for interpolating into the body of an INSERT DATA update

    :param quad: quad
    :return: string representation of the quad for the body of an INSERT DATA query
    """
    triple = _to_query_tp((quad[0], quad[1], quad[2]))
    graph = _to_query_graph(quad[3])

    if graph is None:
        return triple
    else:
        return f"GRAPH {graph.n3()} {{ {triple} }} ."


def _to_query_prefixes(prefixes: typing.Mapping[str, rdflib.term.Identifier]) -> str:
    return " ".join(f"PREFIX {prefix}: <{namespace}>" for prefix, namespace in prefixes.items())


def _to_query_values(values: typing.Mapping[str, rdflib.term.Identifier]) -> str:
    if len(values) == 0:
        return ""

    vars_str = " ".join(f"?{var}" for var in values.keys())
    vals_str = " ".join(f"{val.n3()}" for val in values.values())

    return f"VALUES ({vars_str}) {{ ({vals_str}) }}"


def _to_query_graph(context: typing.Optional[typing.Union[rdflib.Graph, rdflib.URIRef, rdflib.BNode]]) -> \
        typing.Optional[rdflib.URIRef]:
    """
    Convert an rdflib context into an IRI for the triplestore

    :context: context to convert
    :return: None if the context refers to the default graph or an IRI if it refers to a named graph
    """

    if isinstance(context, rdflib.Graph):
        return _to_query_graph(context.identifier)

    if context is None or context == rdflib.graph.DATASET_DEFAULT_GRAPH_ID:
        return None
    elif isinstance(context, rdflib.BNode):
        return context.skolemize("https://tentris.io", "/.well-known/genid/")
    else:
        return context


class TentrisStore(rdflib.store.Store):
    context_aware = True  # tentris supports graphs
    formula_aware = False  # tentris does not support quoted triples (triples about other triples)
    transaction_aware = True  # tentris supports transactions (each update is one transaction)
    graph_aware = False  # tentris does not track empty graphs

    def __init__(self, autocommit: bool = True, dirty_reads: bool = False):
        """
        Construct a Tentris rdf store

        :param autocommit: If true, the store will commit after each update. If false, will only commit once `commit()` is called
        :param dirty_reads: If true, will not commit before reading. So you cannot read what you wrote before manually calling commit.
        """

        self._store = None
        self._mutations = []
        self.autocommit = autocommit
        self.dirty_reads = dirty_reads

        super().__init__()

    def __del__(self):
        if self._store is not None:
            tentris_sys.tentris_triplestore_free(self._store)
            self._store = None

    def gc(self) -> None:
        if self._store is not None:
            tentris_sys.tentris_triplestore_collect_garbage(self._store)

    @property
    def _inner(self):
        if self._store is None:
            self._manager = None
            self._store = tentris_sys.tentris_triplestore_new_in_memory()
        return self._store

    def add(self, triple: _Triple, context: rdflib.Graph, quoted: bool = False):
        if quoted:
            raise ValueError("Tentris is not formula-aware")

        self.addN([(triple[0], triple[1], triple[2], context)])

    def addN(self, quads: typing.Iterable[_Quad]) -> None:
        triples = " ".join(_to_query_quad(quad) for quad in quads)
        query = f"INSERT DATA {{ {triples} }}"

        self._update(query)

    def remove(
            self,
            triple: _TriplePattern,
            context: typing.Optional[rdflib.Graph] = None,
    ) -> None:
        graph = _to_query_graph(context)
        if graph is None:
            query = f"DELETE {{ {_to_query_tp(triple)} }} WHERE {{ {_to_query_tp(triple)} }}"
        else:
            query = f"WITH {graph.n3()} DELETE {{ {_to_query_tp(triple)} }} WHERE {{ {_to_query_tp(triple)} }}"

        self._update(query)

    def triples(
            self,
            triple_pattern: _TriplePattern,
            context: typing.Optional[rdflib.Graph] = None,
    ) -> typing.Iterator[typing.Tuple[_Triple, typing.Iterator[typing.Optional[rdflib.Graph]]]]:
        query = f"SELECT {_to_query_proj(triple_pattern)} WHERE {{ {_to_query_tp(triple_pattern)} }}"
        return (((binding.s, binding.p, binding.o), iter([context])) for binding in self._query(query, context))

    def contexts(self, triple: typing.Optional[_Triple] = None) -> typing.Iterator[_ContextIdentifierType]:
        if triple is None:
            query = "SELECT DISTINCT ?g WHERE { GRAPH ?g { ?s ?p ?o } }"
        else:
            query = f"SELECT DISTINCT ?g WHERE {{ GRAPH ?g {{ {_to_query_tp(triple)} }} }}"

        return (binding.g for binding in self._query(query, context=None))

    def __len__(self, context: typing.Optional[rdflib.Graph] = None) -> int:
        query = "SELECT (COUNT(*) as ?c) WHERE { ?s ?p ?o }"
        res = rdflib.util.first(self._query(query, context))
        return int(res.c)

    def _query(self, query: str, context) -> rdflib.query.Result:
        if not self.autocommit and not self.dirty_reads:
            self.commit()

        target_graph = _to_query_graph(context)
        gen = tentris_sys.tentris_triplestore_eval_query(self._inner, query,
                                                         str(target_graph) if target_graph is not None else None)

        try:
            qt = tentris_sys.tentris_solution_generator_get_query_type(gen)

            if qt == tentris_sys.QT_ASK:
                out = rdflib.query.Result("ASK")

                try:
                    sol = tentris_sys.tentris_solution_generator_next(gen)
                    out.askAnswer = sol[1] > 0
                except StopIteration:
                    out.askAnswer = False
            elif qt == tentris_sys.QT_SELECT:
                out = rdflib.query.Result("SELECT")
                out.vars = [rdflib.term.Variable(tentris_sys.rdf4cpp_variable_name(var)) for var in
                            tentris_sys.tentris_solution_generator_get_projected_variables(gen)]
                out.bindings = []

                while True:
                    try:
                        sol = tentris_sys.tentris_solution_generator_next(gen)
                        for _ in range(sol[1]):
                            out.bindings += [{var: _from_tentris(value) for var, value in zip(out.vars, sol[0])}]
                    except StopIteration:
                        break
            elif qt == tentris_sys.QT_CONSTRUCT or qt == tentris_sys.QT_DESCRIBE:
                out = rdflib.query.Result("CONSTRUCT" if qt == tentris_sys.QT_CONSTRUCT else "DESCRIBE")
                out.graph = rdflib.Graph()

                while True:
                    try:
                        sol = tentris_sys.tentris_solution_generator_next(gen)
                        if sol[1] > 0:
                            out.graph.add(
                                (_from_tentris(sol[0][0]), _from_tentris(sol[0][1]), _from_tentris(sol[0][2])))
                    except StopIteration:
                        break
            else:
                raise ValueError("Unexpected query result")

            return out
        finally:
            tentris_sys.tentris_solution_generator_free(gen)

    def query(
            self,
            query: str,
            initNs: typing.Mapping[str, rdflib.term.Identifier],
            initBindings: typing.Mapping[str, rdflib.term.Identifier],
            queryGraph: typing.Union[str, rdflib.term.URIRef, rdflib.term.BNode],
            **kwargs,
    ) -> rdflib.query.Result:
        if not isinstance(query, str):
            raise NotImplementedError("Only str updates are supported by Tentris store")
        if isinstance(queryGraph, str) and queryGraph == "__UNION__":
            raise NotImplementedError("Per query union default graph is not supported by Tentris store")
        for kwarg, kwvalue in kwargs:
            raise NotImplementedError(f"The parameter {kwarg} is not supported by Tentris store")

        query = _to_query_prefixes(initNs) + " " + query + " " + _to_query_values(initBindings)
        return self._query(query, queryGraph)

    def _update(self, update: str) -> None:
        if self.autocommit:
            tentris_sys.tentris_triplestore_eval_update(self._inner, update)
        else:
            self._mutations.append(update)

    def update(
            self,
            update: str,
            initNs: typing.Mapping[str, rdflib.term.Identifier],
            initBindings: typing.Mapping[str, rdflib.term.Identifier],
            queryGraph: typing.Union[rdflib.term.URIRef, rdflib.term.BNode],
            **kwargs,
    ) -> None:
        if not isinstance(update, str):
            raise NotImplementedError("Only str updates are supported by Tentris store")
        if initBindings:
            raise NotImplementedError("initBindings is not supported by Tentris store")
        if queryGraph != rdflib.graph.DATASET_DEFAULT_GRAPH_ID:
            raise NotImplementedError(f"Only {rdflib.graph.DATASET_DEFAULT_GRAPH_ID} is supported by Tentris store")
        for kwarg in kwargs:
            raise NotImplementedError(f"The parameter {kwarg} is not supported by Tentris store")

        update = _to_query_prefixes(initNs) + " " + update
        self._update(update)

    def commit(self) -> None:
        if len(self._mutations) == 0:
            return

        update = "; ".join(self._mutations)
        tentris_sys.tentris_triplestore_eval_update(self._inner, update)

    def rollback(self) -> None:
        self._mutations.clear()


class _TentrisParser(rdflib.parser.Parser, abc.ABC):
    @property
    @abc.abstractmethod
    def _format(self) -> int:
        raise NotImplementedError

    def parse(self, source: rdflib.parser.InputSource, sink: rdflib.Graph) -> None:
        if not isinstance(sink.store, TentrisStore):
            raise ValueError("Only Tentris store is supported for Tentris parser")

        if not isinstance(source, rdflib.parser.FileInputSource):
            raise ValueError("Only file input source is supported for Tentris parser")

        target_graph = _to_query_graph(sink.identifier)
        tentris_sys.tentris_triplestore_load_rdf_data(sink.store._inner, source.file.name, target_graph, self._format)


class TentrisNTriplesParser(_TentrisParser):
    _format = tentris_sys.TRF_NTRIPLES


class TentrisTurtleParser(_TentrisParser):
    _format = tentris_sys.TRF_TURTLE


rdflib.plugin.register("Tentris", rdflib.plugin.Store, __name__, "TentrisStore")

rdflib.plugin.register("tentris-ntriples", rdflib.plugin.Parser, __name__, "TentrisNTriplesParser")
rdflib.plugin.register("tentris-nt", rdflib.plugin.Parser, __name__, "TentrisNTriplesParser")
rdflib.plugin.register("tentris-turtle", rdflib.plugin.Parser, __name__, "TentrisTurtleParser")
rdflib.plugin.register("tentris-ttl", rdflib.plugin.Parser, __name__, "TentrisTurtleParser")
