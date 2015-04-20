$(function(){ // on dom ready

    var cy = cytoscape({
        container: document.getElementById('cy'),

        style: [
            {
                selector: 'node',
                css: {
                    'content': 'data(id)',
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
                    'target-arrow-shape': 'triangle'
                }
            },
            {
                selector: ':selected',
                css: {
                    'background-color': 'black',
                    'line-color': 'black',
                    'target-arrow-color': 'black',
                    'source-arrow-color': 'black'
                }
            }
        ],

        elements: {
            nodes: [
                { data: { id: 'a', parent: 'b' } },
                { data: { id: 'b' } },
                { data: { id: 'c', parent: 'b' } },
                { data: { id: 'd' } },
                { data: { id: 'e' } },
                { data: { id: 'f', parent: 'e' } }
            ],
            edges: [
                { data: { id: 'ad', source: 'a', target: 'd' } },
                { data: { id: 'eb', source: 'e', target: 'b' } }

            ]
        },

        layout: {
            name: 'cose',
            padding: 5
        }
        //ready: function () {
        //    cy.toolbar({
        //        toolbarClass: "cy-overall-toolbar",
        //        tools: [
        //            [
        //                {
        //                    icon: 'fa fa-search-plus',
        //                    event: ['tap'],
        //                    selector: 'cy',
        //                    options: {
        //                        cy: {
        //                            zoom: 0.1,
        //                            minZoom: 0.1,
        //                            maxZoom: 10,
        //                            zoomDelay: 45
        //                        }
        //                    },
        //                    bubbleToCore: false,
        //                    tooltip: 'Zoom In',
        //                    action: [performZoomIn]
        //                },
        //                {
        //                    icon: 'fa fa-search-minus',
        //                    event: ['tap'],
        //                    selector: 'cy',
        //                    options: {
        //                        cy: {
        //                            zoom: -0.1,
        //                            minZoom: 0.1,
        //                            maxZoom: 10,
        //                            zoomDelay: 45
        //                        }
        //                    },
        //                    bubbleToCore: false,
        //                    tooltip: 'Zoom Out',
        //                    action: [performZoomOut]
        //                }
        //            ],
        //            [
        //                {
        //                    icon: 'fa fa-arrow-right',
        //                    event: ['tap'],
        //                    selector: 'cy',
        //                    options: {
        //                        cy: {
        //                            distance: -80
        //                        }
        //                    },
        //                    bubbleToCore: true,
        //                    tooltip: 'Pan Right',
        //                    action: [performPanRight]
        //                },
        //                {
        //                    icon: 'fa fa-arrow-down',
        //                    event: ['tap'],
        //                    selector: 'cy',
        //                    options: {
        //                        cy: {
        //                            distance: -80
        //                        }
        //                    },
        //                    bubbleToCore: true,
        //                    tooltip: 'Pan Down',
        //                    action: [performPanDown]
        //                },
        //                {
        //                    icon: 'fa fa-arrow-left',
        //                    event: ['tap'],
        //                    selector: 'cy',
        //                    options: {
        //                        cy: {
        //                            distance: 80
        //                        }
        //                    },
        //                    bubbleToCore: true,
        //                    tooltip: 'Pan Left',
        //                    action: [performPanLeft]
        //                },
        //                {
        //                    icon: 'fa fa-arrow-up',
        //                    event: ['tap'],
        //                    selector: 'cy',
        //                    options: {
        //                        cy: {
        //                            distance: 80
        //                        }
        //                    },
        //                    bubbleToCore: true,
        //                    tooltip: 'Pan Up',
        //                    action: [performPanUp]
        //                }
        //            ],
        //            [
        //                {
        //                    icon: 'fa fa-male',
        //                    event: ['tap'],
        //                    selector: 'cy',
        //                    options: {
        //                        clazz: 'node-person'
        //                    },
        //                    bubbleToCore: false,
        //                    tooltip: 'Person',
        //                    action: [addPersonToGraph]
        //                },
        //                {
        //                    icon: 'fa fa-home',
        //                    event: ['tap'],
        //                    selector: 'cy',
        //                    options: {
        //                        clazz: 'node-home'
        //                    },
        //                    bubbleToCore: false,
        //                    tooltip: 'House',
        //                    action: [addHouseToGraph]
        //                },
        //                {
        //                    icon: 'fa fa-building-o',
        //                    event: ['tap'],
        //                    selector: 'cy',
        //                    options: {
        //                        clazz: 'node-business'
        //                    },
        //                    bubbleToCore: false,
        //                    tooltip: 'Business',
        //                    action: [addBusinessToGraph]
        //                },
        //                {
        //                    icon: 'fa fa-truck',
        //                    event: ['tap'],
        //                    selector: 'cy',
        //                    options: {
        //                        clazz: 'node-automobile'
        //                    },
        //                    bubbleToCore: false,
        //                    tooltip: 'Automobile',
        //                    action: [addAutoToGraph]
        //                }
        //            ],
        //            [
        //                {
        //                    icon: 'fa fa-link',
        //                    event: ['tap'],
        //                    selector: 'node',
        //                    bubbleToCore: false,
        //                    tooltip: 'Link',
        //                    action: [performLink]
        //                }
        //            ],
        //            [
        //                {
        //                    icon: 'fa fa-trash-o',
        //                    event: ['tap'],
        //                    selector: 'edge,node',
        //                    bubbleToCore: false,
        //                    tooltip: 'Remove Node/Edge',
        //                    action: [performRemove]
        //                }
        //            ]
        //
        //        ],
        //        appendTools: false
        //    });
        //}
    });

}); // on dom ready