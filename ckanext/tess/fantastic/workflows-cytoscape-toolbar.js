//https://github.com/bdparrish/cytoscape.js-toolbar

$(function () {
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
                            action: [addPersonToGraph]
                        },
                        //{
                        //    icon: 'fa fa-home',
                        //    event: ['tap'],
                        //    selector: 'cy',
                        //    options: {
                        //        clazz: 'node-home'
                        //    },
                        //    bubbleToCore: false,
                        //    tooltip: 'House',
                        //    action: [addHouseToGraph]
                        //},
                        //{
                        //    icon: 'fa fa-building-o',
                        //    event: ['tap'],
                        //    selector: 'cy',
                        //    options: {
                        //        clazz: 'node-business'
                        //    },
                        //    bubbleToCore: false,
                        //    tooltip: 'Business',
                        //    action: [addBusinessToGraph]
                        //},
                        //{
                        //    icon: 'fa fa-truck',
                        //    event: ['tap'],
                        //    selector: 'cy',
                        //    options: {
                        //        clazz: 'node-automobile'
                        //    },
                        //    bubbleToCore: false,
                        //    tooltip: 'Automobile',
                        //    action: [addAutoToGraph]
                        //}
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
                    ]//,
                    //[
                    //    {
                    //        icon: 'fa fa-save',
                    //        event: ['click'],
                    //        selector: 'tool-5-0',
                    //        bubbleToCore: true,
                    //        tooltip: 'Save workflow',
                    //        action: [/*performSave*/]
                    //    }
                    //]
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

        elements: {
            nodes: [
                { data: { id: 'a', name: 'Query sequence and variation data'} },
                { data: { id: 'b', name: 'Known structure in pdb?', parent: 'd' } },
                { data: { id: 'c', name: 'Structure analysis and model quality', parent: 'd' } },
                { data: { id: 'd', name: 'Obtain structural data' } },
                { data: { id: 'e', name: 'Close relative - homology modelling', parent: 'g' } },
                { data: { id: 'f', name: 'Remote relative - structure prediction', parent: 'g' } },
                { data: { id: 'g' } },
                { data: { id: 'h', name: 'Structure annotation' } },
                { data: { id: 'i0', name: 'Active site', parent: 'h' } },
                { data: { id: 'i1', name: 'Binding sites', parent: 'h' } },
                { data: { id: 'i2', name: 'Interfaces', parent: 'h' } },
                { data: { id: 'i3', name: 'Post translational modifications', parent: 'h' } },
                { data: { id: 'i4', name: 'Conserved sites', parent: 'h' } }
          ],
            edges: [
                { data: { id: 'ad', source: 'a', target: 'd', name: 'blah' } },
                { data: { id: 'bc', source: 'b', target: 'c' } },
                { data: { id: 'ef', source: 'e', target: 'f' } },
                { data: { id: 'dg', source: 'd', target: 'g' } },
          ]
        },
        layout: {
            name: 'cose',
            padding: 5
        }

    });

    var workflow = {
            nodes: [
                { data: { id: 'a', parent: 'b' } },
                { data: { id: 'b' } },
                { data: { id: 'c', parent: 'b' } },
                { data: { id: 'd' } },
                { data: { id: 'e', parent: 'g' } },
                { data: { id: 'f', parent: 'e' } },
                { data: { id: 'g' } },
            ],
            edges: [
                { data: { id: 'ad', source: 'a', target: 'd' } },
                { data: { id: 'eb', source: 'e', target: 'b' } },
                { data: { id: 'ac', source: 'a', target: 'c' } },

            ]
        };

    //#region node tools
    function addPersonToGraph(e) {
        addObject(e, addPersonToGraph);
    }

    function addHouseToGraph(e) {
        addObject(e, addHouseToGraph);
    }

    function addBusinessToGraph(e) {
        addObject(e, addBusinessToGraph);
    }

    function addAutoToGraph(e) {
        addObject(e, addAutoToGraph);
    }

    function addAssetToGraph(e) {
        addObject(e, addAssetToGraph);
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

    //#Save graph
    function performSave(e) {
        //if (!e.data.canPerform(e, performSave)) {
        //    return;
        //}
        alert('Workflow saved');
        //cy.remove(e.cyTarget);
    }
});

$('#show-json').click(function(){
    $( "#dialog-div").text(JSON.stringify(window.cy.json()));
    $( "#dialog-div" ).dialog({autoOpen : false, modal : true, show : "blind", hide : "blind"});
});