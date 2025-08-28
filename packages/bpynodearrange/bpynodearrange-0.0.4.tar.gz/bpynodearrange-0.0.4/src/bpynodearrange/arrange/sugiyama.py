# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Collection, Iterator, Sequence
from itertools import chain
from statistics import fmean
from typing import cast

import networkx as nx
from bpy.types import Node, NodeFrame, NodeTree
from mathutils import Vector
from mathutils.geometry import intersect_line_line_2d

from .. import config
from ..utils import abs_loc, frame_padding, get_ntree, group_by, move
from .graph import (
    FROM_SOCKET,
    TO_SOCKET,
    Cluster,
    ClusterGraph,
    GNode,
    GType,
    MultiEdge,
    Socket,
    add_dummy_edge,
    add_dummy_nodes_to_edge,
    is_real,
    lowest_common_cluster,
    socket_graph,
)
from .ordering import minimize_crossings
from .placement.bk import bk_assign_y_coords
from .placement.linear_segments import linear_segments_assign_y_coords
from .ranking import compute_ranks

# -------------------------------------------------------------------


def precompute_links(ntree: NodeTree) -> None:
    # Precompute links to ignore invalid/hidden links, and avoid `O(len(ntree.links))` time

    for link in ntree.links:
        if not link.is_hidden and link.is_valid:
            config.linked_sockets[link.to_socket].add(link.from_socket)
            config.linked_sockets[link.from_socket].add(link.to_socket)


def get_multidigraph() -> nx.MultiDiGraph[GNode]:
    parents = {
        n.parent: Cluster(cast(NodeFrame | None, n.parent)) for n in get_ntree().nodes
    }
    for c in parents.values():
        if c.node:
            c.cluster = parents[c.node.parent]

    G = nx.MultiDiGraph()
    G.add_nodes_from(
        [
            GNode(n, parents[n.parent])
            for n in config.selected
            if n.bl_idname != "NodeFrame"
        ]
    )
    for u in G:
        for i, from_output in enumerate(u.node.outputs):
            for to_input in config.linked_sockets[from_output]:
                if not to_input.node.select:
                    continue

                v = next(v for v in G if v.node == to_input.node)
                j = to_input.node.inputs[:].index(to_input)
                G.add_edge(
                    u, v, from_socket=Socket(u, i, True), to_socket=Socket(v, j, False)
                )

    return G


def get_nesting_relations(
    v: GNode | Cluster,
) -> Iterator[tuple[Cluster, GNode | Cluster]]:
    if c := v.cluster:
        yield (c, v)
        yield from get_nesting_relations(c)


def save_multi_input_orders(G: nx.MultiDiGraph[GNode]) -> None:
    links = {(l.from_socket, l.to_socket): l for l in get_ntree().links}
    for v, w, d in G.edges.data():
        to_socket = d[TO_SOCKET]

        if not to_socket.bpy.is_multi_input:
            continue

        if v.is_reroute:
            for z, u in chain([(w, v)], nx.bfs_edges(G, v, reverse=True)):
                if not u.is_reroute:
                    break
            base_from_socket = G.edges[u, z, 0][FROM_SOCKET]
        else:
            base_from_socket = d[FROM_SOCKET]

        link = links[(d[FROM_SOCKET].bpy, to_socket.bpy)]
        config.multi_input_sort_ids[to_socket].append(
            (base_from_socket, link.multi_input_sort_id)
        )


# -------------------------------------------------------------------


def get_reroute_paths(
    CG: ClusterGraph,
    function: Callable | None = None,
    *,
    preserve_reroute_clusters: bool = True,
    must_be_aligned: bool = False,
) -> list[list[GNode]]:
    G = CG.G
    reroutes = {v for v in G if v.is_reroute and (not function or function(v))}
    SG = nx.DiGraph(G.subgraph(reroutes))

    for v in SG:
        if G.out_degree[v] > 1:
            SG.remove_edges_from(tuple(SG.out_edges(v)))

    if preserve_reroute_clusters:
        reroute_clusters = {  #
            c
            for c in CG.S
            if all(v.is_reroute for v in CG.T[c] if v.type != GType.CLUSTER)
        }
        SG.remove_edges_from(
            [  #
                (u, v)
                for u, v in SG.edges
                if u.cluster != v.cluster and {u.cluster, v.cluster} & reroute_clusters
            ]
        )

    if must_be_aligned:
        SG.remove_edges_from([(u, v) for u, v in SG.edges if u.y != v.y])

    indicies = {v: i for i, v in enumerate(nx.topological_sort(G)) if v in reroutes}
    paths = [
        sorted(c, key=lambda v: indicies[v]) for c in nx.weakly_connected_components(SG)
    ]
    paths.sort(key=lambda p: indicies[p[0]])
    return paths


def is_safe_to_remove(v: GNode) -> bool:
    if not is_real(v):
        return True

    if v.node.label:
        return False

    for val in config.multi_input_sort_ids.values():
        if any(v == i[0].owner for i in val):
            return False

    return all(
        s.node.select
        for s in chain(
            config.linked_sockets[v.node.inputs[0]],
            config.linked_sockets[v.node.outputs[0]],
        )
    )


def dissolve_reroute_edges(G: nx.DiGraph[GNode], path: list[GNode]) -> None:
    if not G[path[-1]]:
        return

    try:
        u, _, o = next(iter(G.in_edges(path[0], data=FROM_SOCKET)))
    except StopIteration:
        return

    succ_inputs = [e[2] for e in G.out_edges(path[-1], data=TO_SOCKET)]

    # Check if a reroute has been used to link the same output to the same multi-input multiple
    # times
    for *_, d in G.out_edges(u, data=True):
        if d[FROM_SOCKET] == o and d[TO_SOCKET] in succ_inputs:
            path.clear()
            return

    links = get_ntree().links
    for i in succ_inputs:
        G.add_edge(u, i.owner, from_socket=o, to_socket=i)
        links.new(o.bpy, i.bpy)


def remove_reroutes(CG: ClusterGraph) -> None:
    reroute_clusters = {  #
        c
        for c in CG.S
        if all(v.type != GType.CLUSTER and v.is_reroute for v in CG.T[c])
    }
    for path in get_reroute_paths(CG, is_safe_to_remove):
        if path[0].cluster in reroute_clusters:
            if len(path) > 2:
                u, *between, v = path
                add_dummy_edge(CG.G, u, v)
                CG.remove_nodes_from(between)
        else:
            dissolve_reroute_edges(CG.G, path)
            CG.remove_nodes_from(path)


# -------------------------------------------------------------------


def add_columns(G: nx.DiGraph[GNode]) -> None:
    columns = [list(c) for c in group_by(G, key=lambda v: v.rank, sort=True)]
    G.graph["columns"] = columns
    for col in columns:
        col.sort(key=lambda v: abs_loc(v.node).y if is_real(v) else 0, reverse=True)
        for v in col:
            v.col = col


# -------------------------------------------------------------------


def align_reroutes_with_sockets(CG: ClusterGraph) -> None:
    reroute_paths: dict[tuple[GNode, ...], list[Socket]] = {}
    for path in get_reroute_paths(
        CG, preserve_reroute_clusters=False, must_be_aligned=True
    ):
        inputs = CG.G.in_edges(path[0], data=FROM_SOCKET)
        outputs = CG.G.out_edges(path[-1], data=TO_SOCKET)
        reroute_paths[tuple(path)] = [e[2] for e in (*inputs, *outputs)]

    while True:
        changed = False
        for path, foreign_sockets in tuple(reroute_paths.items()):
            y = path[0].y
            foreign_sockets.sort(key=lambda s: abs(y - s.y))
            foreign_sockets.sort(key=lambda s: y == s.owner.y, reverse=True)

            if not foreign_sockets or y - foreign_sockets[0].y == 0:
                del reroute_paths[path]
                continue

            movement = y - foreign_sockets[0].y
            y -= movement
            if movement < 0:
                above_y_vals = [
                    (w := v.col[v.col.index(v) - 1]).y - w.height
                    for v in path
                    if v != v.col[0]
                ]
                if above_y_vals and y > min(above_y_vals):
                    continue
            else:
                below_y_vals = [
                    v.col[v.col.index(v) + 1].y for v in path if v != v.col[-1]
                ]
                if below_y_vals and max(below_y_vals) > y - path[0].height:
                    continue

            for v in path:
                v.y -= movement

            changed = True

        if not changed:
            if reroute_paths:
                for path, foreign_sockets in reroute_paths.items():
                    del foreign_sockets[0]
            else:
                break


def frame_padding_of_col(
    columns: Sequence[Collection[GNode]],
    i: int,
    T: nx.DiGraph[GNode | Cluster],
) -> float:
    col = columns[i]

    if col == columns[-1]:
        return 0

    clusters1 = {cast(Cluster, v.cluster) for v in col}
    clusters2 = {cast(Cluster, v.cluster) for v in columns[i + 1]}

    if not clusters1 ^ clusters2:
        return 0

    ST1 = T.subgraph(chain(clusters1, *[nx.ancestors(T, c) for c in clusters1])).copy()
    ST2 = T.subgraph(chain(clusters2, *[nx.ancestors(T, c) for c in clusters2])).copy()

    for *e, d in ST1.edges(data=True):
        d["weight"] = int(e not in ST2.edges)  # type: ignore

    for *e, d in ST2.edges(data=True):
        d["weight"] = int(e not in ST1.edges)  # type: ignore

    dist = nx.dag_longest_path_length(ST1) + nx.dag_longest_path_length(ST2)  # type: ignore
    return frame_padding() * dist


def assign_x_coords(G: nx.DiGraph[GNode], T: nx.DiGraph[GNode | Cluster]) -> None:
    columns: list[list[GNode]] = G.graph["columns"]
    x = 0
    for i, col in enumerate(columns):
        max_width = max([v.width for v in col])

        for v in col:
            v.x = x if v.is_reroute else x - (v.width - max_width) / 2

        # https://doi.org/10.7155/jgaa.00220 (p. 139)
        delta_i = sum(
            [
                1
                for *_, d in G.out_edges(col, data=True)
                if abs(d[TO_SOCKET].y - d[FROM_SOCKET].y) >= config.MARGIN.x * 3
            ]
        )
        spacing = (1 + min(delta_i / 4, 2)) * config.MARGIN.x
        x += max_width + spacing + frame_padding_of_col(columns, i, T)


def is_unnecessary_bend_point(socket: Socket, other_socket: Socket) -> bool:
    v = socket.owner

    if v.is_reroute:
        return False

    i = v.col.index(v)
    is_above = other_socket.y > socket.y

    try:
        nbr = v.col[i - 1] if is_above else v.col[i + 1]
    except IndexError:
        return True

    if nbr.is_reroute:
        return True

    nbr_x_offset, nbr_y_offset = config.MARGIN / 2
    nbr_y = nbr.y - nbr.height - nbr_y_offset if is_above else nbr.y + nbr_y_offset

    assert nbr.cluster
    if nbr.cluster.node and nbr.cluster != v.cluster:
        nbr_x_offset += frame_padding()
        if is_above:
            nbr_y -= frame_padding()
        else:
            nbr_y += frame_padding() + nbr.cluster.label_height()

    line_a = ((nbr.x - nbr_x_offset, nbr_y), (nbr.x + nbr.width + nbr_x_offset, nbr_y))
    line_b = ((socket.x, socket.y), (other_socket.x, other_socket.y))
    return intersect_line_line_2d(*line_a, *line_b) is None


_MIN_X_DIFF = 30
_MIN_Y_DIFF = 15


def add_bend_points(
    G: nx.MultiDiGraph[GNode],
    v: GNode,
    bend_points: defaultdict[MultiEdge, list[GNode]],
) -> None:
    d: dict[str, Socket]
    largest = max(v.col, key=lambda w: w.width)
    for u, w, k, d in (
        *G.out_edges(v, data=True, keys=True),
        *G.in_edges(v, data=True, keys=True),
    ):
        socket = d[FROM_SOCKET] if v == u else d[TO_SOCKET]
        bend_point = GNode(type=GType.DUMMY)
        bend_point.x = largest.x + largest.width if socket.is_output else largest.x

        if abs(socket.x - bend_point.x) <= _MIN_X_DIFF:
            continue

        bend_point.y = socket.y
        other_socket = next(s for s in d.values() if s != socket)

        if abs(other_socket.y - bend_point.y) <= _MIN_Y_DIFF:
            continue

        if is_unnecessary_bend_point(socket, other_socket):
            continue

        bend_points[u, w, k].append(bend_point)


def node_overlaps_edge(
    v: GNode,
    edge_line: tuple[tuple[float, float], tuple[float, float]],
) -> bool:
    if v.is_reroute:
        return False

    top_line = ((v.x, v.y), (v.x + v.width, v.y))
    if intersect_line_line_2d(*edge_line, *top_line):
        return True

    bottom_line = (
        (v.x, v.y - v.height),
        (v.x + v.width, v.y - v.height),
    )
    if intersect_line_line_2d(*edge_line, *bottom_line):
        return True

    return False


def route_edges(G: nx.MultiDiGraph[GNode], T: nx.DiGraph[GNode | Cluster]) -> None:
    bend_points = defaultdict(list)
    for v in chain(*G.graph["columns"]):
        add_bend_points(G, v, bend_points)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    edge_of = {b: e for e, d in bend_points.items() for b in d}
    key = lambda b: (G.edges[edge_of[b]][FROM_SOCKET], b.x, b.y)
    for (target, *redundant), (from_socket, *_) in group_by(edge_of, key=key).items():
        for b in redundant:
            dummy_nodes = bend_points[edge_of[b]]
            dummy_nodes[dummy_nodes.index(b)] = target

        u = from_socket.owner
        if not u.is_reroute or G.out_degree[u] < 2:  # type: ignore
            continue

        for e in G.out_edges(u, keys=True):
            if target not in bend_points[e] and G.edges[e][TO_SOCKET].y == target.y:
                bend_points[e].append(target)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    for e, dummy_nodes in tuple(bend_points.items()):
        dummy_nodes.sort(key=lambda b: b.x)
        from_socket = G.edges[e][FROM_SOCKET]
        for e_ in G.out_edges(e[0], keys=True):
            d = G.edges[e_]

            if d[FROM_SOCKET] != from_socket or e_ in bend_points:
                continue

            if d[TO_SOCKET].x <= dummy_nodes[-1].x:
                continue

            b = dummy_nodes[-1]
            line = ((b.x, b.y), (d[TO_SOCKET].x, d[TO_SOCKET].y))
            if any(node_overlaps_edge(v, line) for v in e[1].col):
                continue

            bend_points[e_] = dummy_nodes

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    lca = lowest_common_cluster(T, bend_points)
    for (u, v, k), dummy_nodes in bend_points.items():
        add_dummy_nodes_to_edge(G, (u, v, k), dummy_nodes)

        c = lca.get((u, v), u.cluster)
        for w in dummy_nodes:
            w.cluster = c
            T.add_edge(c, w)


# -------------------------------------------------------------------


def simplify_path(CG: ClusterGraph, path: list[GNode]) -> None:
    if len(path) == 1:
        return

    u, *between, v = path
    G = CG.G

    if G.pred[u] and (s := next(iter(G.in_edges(u, data=FROM_SOCKET)))[2]).y == u.y:
        G.add_edge(s.owner, v, from_socket=s, to_socket=Socket(v, 0, False))
        between.append(u)
    elif (
        G.out_degree[v] == 1
        and v.y == (s := next(iter(G.out_edges(v, data=TO_SOCKET)))[2]).y
    ):
        G.add_edge(u, s.owner, from_socket=Socket(u, 0, True), to_socket=s)
        between.append(v)
    elif between:
        add_dummy_edge(G, u, v)

    CG.remove_nodes_from(between)
    for v in between:
        if v not in G:
            path.remove(v)


def add_reroute(v: GNode) -> None:
    reroute = get_ntree().nodes.new(type="NodeReroute")
    assert v.cluster
    reroute.parent = v.cluster.node
    config.selected.append(reroute)
    v.node = reroute
    v.type = GType.NODE


def realize_edges(G: nx.DiGraph[GNode], v: GNode) -> None:
    assert is_real(v)
    links = get_ntree().links

    if G.pred[v]:
        pred_output = next(iter(G.in_edges(v, data=FROM_SOCKET)))[2]
        links.new(pred_output.bpy, v.node.inputs[0])

    for _, w, succ_input in G.out_edges(v, data=TO_SOCKET):
        if is_real(w):
            links.new(v.node.outputs[0], succ_input.bpy)


def realize_dummy_nodes(CG: ClusterGraph) -> None:
    for path in get_reroute_paths(CG, is_safe_to_remove, must_be_aligned=True):
        simplify_path(CG, path)

        for v in path:
            if not is_real(v):
                add_reroute(v)

            realize_edges(CG.G, v)


def restore_multi_input_orders(G: nx.MultiDiGraph[GNode]) -> None:
    links = get_ntree().links
    H = socket_graph(G)
    for socket, sort_ids in config.multi_input_sort_ids.items():
        multi_input = socket.bpy
        assert multi_input

        as_links = {l.from_socket: l for l in links if l.to_socket == multi_input}

        if len(as_links) != len({l.multi_input_sort_id for l in as_links.values()}):
            for link in as_links.values():
                links.remove(link)

            for output in as_links:
                as_links[output] = links.new(output, multi_input)

        SH = H.subgraph(
            {i[0] for i in sort_ids} | {socket} | {v for v in H if v.owner.is_reroute}
        )
        seen = set()
        for base_from_socket, sort_id in sort_ids:
            other = min(
                as_links.values(), key=lambda l: abs(l.multi_input_sort_id - sort_id)
            )
            from_socket = next(
                s
                for s, t in nx.edge_dfs(SH, base_from_socket)
                if t == socket and s not in seen
            )
            as_links[from_socket.bpy].swap_multi_input_sort_id(other)  # type: ignore
            seen.add(from_socket)


def realize_locations(G: nx.DiGraph[GNode], old_center: Vector) -> None:
    new_center = (fmean([v.x for v in G]), fmean([v.y for v in G]))
    offset_x, offset_y = -Vector(new_center) + old_center

    for v in G:
        assert isinstance(v.node, Node)
        assert v.cluster

        # Optimization: avoid using bpy.ops for as many nodes as possible (see `utils.move()`)
        v.node.parent = None

        x, y = v.node.location
        v.x += offset_x
        v.y += offset_y
        move(v.node, x=v.x - x, y=v.corrected_y() - y)

        v.node.parent = v.cluster.node


def resize_unshrunken_frame(CG: ClusterGraph, cluster: Cluster) -> None:
    frame = cluster.node

    if not frame or frame.shrink:
        return

    real_children = [v for v in CG.T[cluster] if is_real(v)]

    for v in real_children:
        v.node.parent = None

    frame.shrink = False
    frame.shrink = True

    for v in real_children:
        v.node.parent = frame


# -------------------------------------------------------------------


def sugiyama_layout(ntree: NodeTree, vertical_spacing: float = 50.0) -> None:
    locs = [abs_loc(n) for n in config.selected if n.bl_idname != "NodeFrame"]

    if not locs:
        return

    old_center = Vector(map(fmean, zip(*locs)))

    precompute_links(ntree)
    CG = ClusterGraph(get_multidigraph())
    G = CG.G
    T = CG.T

    save_multi_input_orders(G)
    remove_reroutes(CG)

    compute_ranks(CG)
    CG.merge_edges()
    CG.insert_dummy_nodes()

    add_columns(G)
    minimize_crossings(G, T)

    if len(CG.S) == 1:
        bk_assign_y_coords(G, vertical_spacing=vertical_spacing)
    else:
        CG.add_vertical_border_nodes()
        linear_segments_assign_y_coords(CG, vertical_spacing=vertical_spacing)
        CG.remove_nodes_from([v for v in G if v.type == GType.VERTICAL_BORDER])

    align_reroutes_with_sockets(CG)
    assign_x_coords(G, T)
    route_edges(G, T)

    realize_dummy_nodes(CG)
    restore_multi_input_orders(G)
    realize_locations(G, old_center)
    for c in CG.S:
        resize_unshrunken_frame(CG, c)
