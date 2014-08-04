function renderGraph() {
    var path_to_file = $("#gexf").data("gexf");
    sigma.classes.graph.addMethod('neighbors', function(nodeId) {
        var k,
            neighbors = {},
            index = this.allNeighborsIndex[nodeId] || {};

        for (k in index)
            neighbors[k] = this.nodesIndex[k];

        return neighbors;
    });

    var s1 = new sigma(
        {
            container: 'container',
            settings: {
                defaultNodeColor: '#66FF33'
            }
        }
    );

    sigma.parsers.gexf(
        path_to_file,
        s1,
        function(s) {
            // We first need to save the original colors of our
            // nodes and edges, like this:
            s.graph.nodes().forEach(function (n) {
                //n.color = '#ec5148';
                n.originalColor = n.color;
            });
            s.graph.edges().forEach(function (e) {
                //e.color = '#ec5148';
                e.originalColor = e.color;
            });

            // When a node is clicked, we check for each node
            // if it is a neighbor of the clicked one. If not,
            // we set its color as grey, and else, it takes its
            // original color.
            // We do the same for the edges, and we only keep
            // edges that have both extremities colored.
            s.bind('clickNode', function (e) {
                var nodeId = e.data.node.id,
                    toKeep = s.graph.neighbors(nodeId);
                toKeep[nodeId] = e.data.node;

                s.graph.nodes().forEach(function (n) {
                    if (toKeep[n.id])
                        n.color = n.originalColor;
                    else
                        n.color = '#eee';
                });

                s.graph.edges().forEach(function (e) {
                    if (toKeep[e.source] && toKeep[e.target])
                        e.color = e.originalColor;
                    else
                        e.color = '#eee';
                });

                // Since the data has been modified, we need to
                // call the refresh method to make the colors
                // update effective.
                s.refresh();
            });

            // When the stage is clicked, we just color each
            // node and edge with its original color.
            s.bind('clickStage', function (e) {
                s.graph.nodes().forEach(function (n) {
                    n.color = n.originalColor;

                });

                s.graph.edges().forEach(function (e) {
                    e.color = e.originalColor;
                });

                // Same as in the previous event:
                s.refresh();
            });

            var settings = s.settings;
            settings.defaultNodeColor = '#66FF33';
            s.settings = settings;

            var renderers = s.renderers;
            var renderer = renderers[0];
            var rsettings = renderer.settings;


            s.refresh();
        });
}

$(document).ready(function() {
    renderGraph();
});