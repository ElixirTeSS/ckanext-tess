//Modified from https://github.com/bdparrish/cytoscape.js-toolbar

jQuery.noConflict();

var default_node_width = 150;
var default_node_height = 30;
var default_font_size = 11;
var default_node_colour = '#9FBD6E';
var default_edge_colour = '#848383';
var default_selected_colour = '#2A62E4';
var action; // 'show', 'new' or 'edit'


//$( document ).one('click', '.tool-item, .selected-tool', function(event) {
//    alert('you clicked a '+$(event.target).attr('class')+' element');
//    if(event.handled !== true) {
//        if ($(this).hasClass('selected-tool')) {
//            $(this).removeClass('selected-tool');
//            alert('element now has classes ' + $(event.target).attr('class'));
//        }
//    }
//});

function drawGraph(workflow, workflow_action) {
    $("#workflow_element_info").hide();
    action = (typeof workflow_action === 'undefined') ? 'show' : workflow_action; // what kind of action we are handling - new workflow, show workflow or edit workflow

    $('#update_editor').on('click', function(event){
        console.log('click');
    });


    var cy = window.cy = cytoscape({
        container: document.getElementById('cy'),

        ready: function () {
            if (workflow_action != 'show') {
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
                                        maxZoom: 0.5,
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
                                        maxZoom: 0.5,
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
                                tooltip: 'Remove workflow element',
                                action: [performRemove]
                            }
                        ]
                    ],
                    appendTools: false
                });
            }
        },

        style: [
            {
                selector: 'node',
                css: {
                    'shape': 'roundrectangle',
                    'content': 'data(short_name)',
                    'background-color': default_node_colour,
                    'text-valign': 'center',
                    'text-halign': 'center',
                    'width':default_node_width,
                    'height':default_node_height,
                    'font-size':default_font_size
                }
            },
            {
                selector: '$node > node',
                css: {
                    'shape': 'roundrectangle',
                    'padding-top': '10px',
                    'font-weight': 'bold',
                    'padding-left': '10px',
                    'padding-bottom': '10px',
                    'padding-right': '10px',
                    'text-valign': 'top',
                    'text-halign': 'center',
                    'width': 'auto',
                    'height': 'auto',
                    'font-size': default_font_size + 2
                }
            },
            {
                selector: 'edge',
                css: {
                    'target-arrow-shape': 'triangle',
                    'content': 'data(name)',
                    'line-color': default_edge_colour,
                    'source-arrow-color': default_edge_colour,
                    'target-arrow-color': default_edge_colour
                }
            },
            {
                selector: ':selected',
                css: {
                    'background-color': default_selected_colour,
                    'line-color': default_selected_colour,
                    'target-arrow-color': default_selected_colour,
                    'source-arrow-color': default_selected_colour
                }
            }
        ],

        elements: (action != 'new' && workflow != undefined)? workflow['elements'] : [],
        layout: {
            name: 'preset',
            padding: 5
        },

        autolock: (action == "show")? true : false,

        autoungrabify: (action == "show")? true : false

    });

    cy.on('tap', function(event){
        updateStage();
        // cyTarget holds a reference to the originator
        // of the event (core or element)
        var evtTarget = event.cyTarget;

        if( evtTarget === cy ){
            // Tap on a background
            clearPropertyEditor();
        } else {
            var element = cy.getElementById(evtTarget.id()).json(); // Get wf element with this id
            //alert(JSON.stringify(element));
            if (element['group'] == 'nodes') {
            /*
                $("#workflow_element_info").html(
                    '<ul class="items">' +
                    '<li><b>Type:</b> Node</li><hr style="margin: 0px;">' +
                    '<li><b>Name:</b><br>' +
                        '<input type="text">' + (typeof element['data']['name'] === "undefined" ? undefined : element['data']['name']) + '</input>' +
                    '</li><hr style="margin: 0px;">' +

                    '<li><b>Colour:</b><br>' + (typeof element['data']['background-color'] === "undefined" ? default_node_colour : element['data']['background-color']) + '</li><hr style="margin: 0px;">' +
                    '<li><b>Training material:</b><br>' + (typeof element['data']['training-material'] === "undefined" ? undefined : element['data']['training-material']) + '</li>' +
                    '</ul>');*/
            }
            else if (element['group'] == 'edges'){

                /*$("#workflow_element_info").html(
                    '<ul class="items">' +
                    '<li><b>Type:</b> Link</li><hr style="margin: 0px;">' +
                    '<li><b>Name:</b><br>' + (typeof element['data']['name'] === "undefined" ? undefined : element['data']['name']) + '</li><hr style="margin: 0px;">' +
                    '<li><b>Colour:</b><br>' + (typeof element['data']['background-color'] === "undefined" ? default_edge_colour : element['data']['background-color']) + '</li>' +
                    '</ul>');*/
            }
            $("#workflow_element_info").show();
        }
        updateJSONDump();

        loadEditor();
    });

    //$( document ).off('click', '.tool-item, .selected-tool').on('click', '.tool-item, .selected-tool', function(event) {
    //    alert('you clicked a '+$(event.target).attr('class')+' element');
    //    if(event.handled !== true) {
    //        if ($(this).hasClass('selected-tool')) {
    //            $(this).removeClass('selected-tool');
    //            alert('element now has classes ' + $(event.target).attr('class'));
    //        }
    //    }
    //});
}

//var nodes = (workflow['elements']['nodes']);
//for (var i = 0; i < nodes.length; i++) {
//    if (typeof nodes[i]["data"]["name"] !== 'undefined') {
//        nodes[i]["data"]["short_name"] = truncateString(nodes[i]["data"]["name"], 30);
//    }
//}
//cy.load(workflow['elements']);

// Add functions to deselect tools from toolbar
// (i.e. if a tool is selected, the next click on the tool will deselect it)
// Select all elements whose id starts with 'tool-'
//$("span#tool-4-0").click(function(){
//    // If tool is selected - unselect it
//    if ($(this).hasClass('selected-node')){
//        $(this).removeClass('selected-node');
//    }
//    //if ($(e.cyTarget).hasClass('selected-node')){
//    //    e.cyTarget.removeClass('selected-node');
//    //    return;
//    //}
//});

function loadEditor() {
    var current_selected = cy.$(':selected').first();
    if (current_selected.isNode()) {
        $('#element-name').val(current_selected.data('name'))
        $('#element-color').val(current_selected.data('color'))
        $('#element-topic').val(current_selected.data('topic'))
    }

}

function updateStage() {
    var current_selected = cy.$(':selected').first();
    console.log(current_selected);
    if (current_selected.isEdge()) {
        console.log('edge');
    } else {
        current_selected.json();
        current_selected.data('name',$('#element-name').val());
        current_selected.style('background-color',$('#element-colour').val());
        current_selected.data('topic',$('#element-topic').val());
        console.log(current_selected.data())
    }
}

function updateJSONDump() {
    $("#dialog-div").val(JSON.stringify(window.cy.json()));
    $("#dialog-div").text(JSON.stringify(window.cy.json()));
    console.log(window.cy.json());
}

//#region node tools
function addPersonToGraph(e) {
    addObject(e, addPersonToGraph);
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
    updateJSONDump();
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
    updateJSONDump();
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
    clearPropertyEditor();
    updateJSONDump();
}
//#endregion

//#region Clear tool selection
function performClearSelectedTool(e) {
    //cy.remove(e.cyTarget);
}
//#endregion

/////////////////////////////////////////////////////

$('#show-wf').click(function(){
    updateJSONDump();
});
//
//$('#load-wf').click(function(){
//    workflow = {
//        nodes: [
//            { data: { id: 'a', parent: 'b', name: 'a' } },
//            { data: { id: 'b', name: 'b' } },
//            { data: { id: 'c', parent: 'b', name: 'c' } },
//            { data: { id: 'd', name: 'd' } },
//            { data: { id: 'e', parent: 'g', name: 'e' } },
//            { data: { id: 'f', parent: 'e', name: 'f' } },
//            { data: { id: 'g', name: 'g' } }
//        ],
//        edges: [
//            { data: { id: 'ad', source: 'a', target: 'd' } },
//            { data: { id: 'eb', source: 'e', target: 'b' } }
//
//        ]
//    };
//    drawGraph(workflow);
//});

function truncateString(str, length) {
    return str.length > length ? str.substring(0, length - 3) + '...' : str
}

function clearPropertyEditor(){
    $("#workflow_element_info").html("");
    $("#workflow_element_info").hide();
}


