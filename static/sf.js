function renderGraph() {
    var s1 = new sigma('container');
    var path_to_file = $("#gexf").data("gexf");
      sigma.parsers.gexf(
    path_to_file,
    s1,
    function(s) {
        var nodes = s.graph.nodes();
        for (i=0; i<nodes.length; i++) {
            var node = nodes[i];
        }
        var edges = s.graph.edges();
        for (i=0; i<edges.length; i++) {
            var edge = edges[i];
        }
        var renderer = s.graph.renderers[0];
        var renderer_settings = renderer.settings;

    }
  );
}

$(document).ready(function() {
    renderGraph();
});