//https://github.com/bdparrish/cytoscape.js-toolbar

function drawGraph(elements) {
    //alert(JSON.stringify(elements));
    var cy = window.cy = cytoscape({
        container: document.getElementById('cy'),

        ready: function () {
            cy.toolbar({
                toolbarClass: "cy-overall-toolbar",
                tools: [
                    [
                        {
                            icon: 'fa fa-search-plus',
                            event: ['tap'],
                            selector: 'cy',
                            options: {
                                cy: {
                                    zoom: 0.1,
                                    minZoom: 0.1,
                                    maxZoom: 10,
                                    zoomDelay: 45
                                }
                            },
                            bubbleToCore: false,
                            tooltip: 'Zoom in',
                            action: [performZoomIn]
                        },
                        {
                            icon: 'fa fa-search-minus',
                            event: ['tap'],
                            selector: 'cy',
                            options: {
                                cy: {
                                    zoom: -0.1,
                                    minZoom: 0.1,
                                    maxZoom: 10,
                                    zoomDelay: 45
                                }
                            },
                            bubbleToCore: false,
                            tooltip: 'Zoom out',
                            action: [performZoomOut]
                        }
                    ],
                    [
                        {
                            icon: 'fa fa-arrow-right',
                            event: ['tap'],
                            selector: 'cy',
                            options: {
                                cy: {
                                    distance: -80
                                }
                            },
                            bubbleToCore: true,
                            tooltip: 'Pan right',
                            action: [performPanRight]
                        },
                        {
                            icon: 'fa fa-arrow-down',
                            event: ['tap'],
                            selector: 'cy',
                            options: {
                                cy: {
                                    distance: -80
                                }
                            },
                            bubbleToCore: true,
                            tooltip: 'Pan Down',
                            action: [performPanDown]
                        },
                        {
                            icon: 'fa fa-arrow-left',
                            event: ['tap'],
                            selector: 'cy',
                            options: {
                                cy: {
                                    distance: 80
                                }
                            },
                            bubbleToCore: true,
                            tooltip: 'Pan left',
                            action: [performPanLeft]
                        },
                        {
                            icon: 'fa fa-arrow-up',
                            event: ['tap'],
                            selector: 'cy',
                            options: {
                                cy: {
                                    distance: 80
                                }
                            },
                            bubbleToCore: true,
                            tooltip: 'Pan up',
                            action: [performPanUp]
                        }
                    ],
                    [
                        {
                            icon: 'fa fa-plus',
                            event: ['click'],
                            selector: 'cy',
                            options: {
                                clazz: 'node-person'
                            },
                            bubbleToCore: false,
                            tooltip: 'Add node',
                            action: [addNodeToGraph]
                        }
                    ],
                    [
                        {
                            icon: 'fa fa-link',
                            event: ['tap'],
                            selector: 'node',
                            bubbleToCore: false,
                            tooltip: 'Link nodes',
                            action: [performLink]
                        }
                    ],
                    [
                        {
                            icon: 'fa fa-trash-o',
                            event: ['tap'],
                            selector: 'edge,node',
                            bubbleToCore: false,
                            tooltip: 'Remove node/arrow',
                            action: [performRemove]
                        }
                    ]
                ],
                appendTools: false
            });
        },

        style: [
            {
                selector: 'node',
                css: {
                    'content': 'data(name)',
                    'text-valign': 'center',
                    'text-halign': 'center'
                }
            },
            {
                selector: '$node > node',
                css: {
                    'padding-top': '10px',
                    'padding-left': '10px',
                    'padding-bottom': '10px',
                    'padding-right': '10px',
                    'text-valign': 'top',
                    'text-halign': 'center'
                }
            },
            {
                selector: 'edge',
                css: {
                    'target-arrow-shape': 'triangle',
                    'content': 'data(name)'
                }
            },
            {
                selector: ':selected',
                css: {
                    'background-color': 'blue',
                    'line-color': 'blue',
                    'target-arrow-color': 'blue',
                    'source-arrow-color': 'blue'
                }
            }
        ],

        elements: elements,
        layout: {
            name: 'cose',
            padding: 5
        }

    });
};

//#region node tools
function addNodeToGraph(e) {
    addObject(e, addNodeToGraph);
}

function addObject(e, action) {
    if (!e.data.canPerform(e, action)) {
        return;
    }

    var toolIndexes = e.data.data.selectedTool;
    var tool = e.data.data.options.tools[toolIndexes[0]][toolIndexes[1]];

    var object = {
        group: 'nodes',
        data: {
            name: tool.options.text
        },
        position: {
            x: e.cyPosition.x,
            y: e.cyPosition.y
        }
    }

    e.cy.add(object).addClass('tool-node').addClass(tool.options.clazz);
}
//#endregion

//#region linking
var src;
function performLink(e) {
    if (!e.data.canPerform(e, performLink)) {
        return;
    }

    if (src) {
        tgt = e.cyTarget;

        e.cy.add({
            group: "edges",
            data: {
                source: src.id(),
                target: tgt.id()
            }
        });

        src.removeClass('selected-node');
        src = undefined;
    } else {
        src = e.cyTarget;
        src.addClass('selected-node');
    }
}

function getLinkName(src, tgt) {
    return src.id() + "->" + tgt.id();
}
//#endregion

//#region Remove
function performRemove(e) {
    if (!e.data.canPerform(e, performRemove)) {
        return;
    }

    cy.remove(e.cyTarget);
}
//#endregion


/////////////////////////////////////////////////////
$('#show-wf').click(function(){
    $( "#dialog-div").text(JSON.stringify(window.cy.json()));
    $( "#dialog-div" ).dialog({autoOpen : false, modal : true, show : "blind", hide : "blind"});
});

$('#load-wf').click(function(){
    workflow = {
        nodes: [
            { data: { id: 'a', parent: 'b' } },
            { data: { id: 'b' } },
            { data: { id: 'c', parent: 'b' } },
            { data: { id: 'd' } },
            { data: { id: 'e', parent: 'g' } },
            { data: { id: 'f', parent: 'e' } },
            { data: { id: 'g' } }
        ],
        edges: [
            { data: { id: 'ad', source: 'a', target: 'd' } },
            { data: { id: 'eb', source: 'e', target: 'b' } }

        ]
    };
    drawGraph(workflow);
});