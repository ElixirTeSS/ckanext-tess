//Modified from https://github.com/bdparrish/cytoscape.js-toolbar

/*
jQuery.noConflict();
*/

var default_node_width = 150;
var default_node_height = 30;
var default_font_size = 11;
var default_node_colour = '#7bd148';
var default_edge_colour = '#848383';
var default_selected_colour = '#2A62E4';
var action; // 'show', 'new' or 'edit'

var activity_log = []


//$( document ).one('click', '.tool-item, .selected-tool', function(event) {
//    alert('you clicked a '+$(event.target).attr('class')+' element');
//    if(event.handled !== true) {
//        if ($(this).hasClass('selected-tool')) {
//            $(this).removeClass('selected-tool');
//            alert('element now has classes ' + $(event.target).attr('class'));
//        }
//    }
//});



$('#modal_container').load('/workflow_modal.html');


function drawGraph(workflow, workflow_action) {

//    alert('action: ' + workflow_action + ' wf: ' + JSON.stringify(workflow) + ' elements: ' + JSON.stringify(workflow['elements']));

    closeWorkflowPropertyEditor();
    action = (typeof workflow_action === 'undefined') ? 'show' : workflow_action; // what kind of action we are handling - new workflow, show workflow or edit workflow

    $('#associate-training-materials').click(function(e){
        loadTrainingMaterialModal();
    })

    $('#enable_zoom').click(function(e){
        cy.zoomingEnabled(true)
        $('#enable_zoom').toggle()
        $('#disable_zoom').toggle()
    })
    $('#disable_zoom').click(function(e){
        cy.zoom({
            level: 1.0,
            renderedPosition: { x: 0, y: 0 }
        })
        cy.zoomingEnabled(false)
        $('#enable_zoom').toggle()
        $('#disable_zoom').toggle()
    })


    $('#save_workflow_element_properties').click(function(e){
        saveWorkflowElementProperties();
        updateWorkflowElement();
    });
    $('#save-workflow').click( function(e){
        clearSelectedWorkflowElements();
        updateJSONDump();
    });
    $('#element-color').change(function(e){
        updateWorkflowElement();
    });
    $('#colorpicker-longlist').change(function(e){
        updateWorkflowElement();
    });
    $('#element-name').change(function(e){
        updateWorkflowElement();
    });
    $('#element-description').change(function(e){
        updateWorkflowElement();
    });
    $('#element-topic').change(function(e){
        updateWorkflowElement();
    });
    $('#download-png-workflow').click(function(e) {
        $('#export').modal('show')
        $('#png').show().attr('src', cy.png());
        $('#json-wf').hide();
        $('#ro').hide();
    });
    $('#download-json-workflow').click(function(e) {
        $('#export').modal('show')
        $('#json-wf').show().text(JSON.stringify(window.cy.json()));
        $('#png').hide();
        $('#ro').hide();
    });
    $('#download-ro-workflow').click(function(e) {
        $('#export').modal('show')
        $('#ro').show()
        $('#json-wf').hide()
        $('#png').hide();
    });
    $('#show-help').click(function(e) {
        $('#help-modal').modal('show');
    });
    $('#hide-property-editor').click(function(e){
        closeWorkflowPropertyEditor();
        $('#associate-training-materials').toggle()
    });



    var cy = window.cy = cytoscape({
        container: document.getElementById('cy'),

        ready: function () {
            if (workflow_action != 'show') {
                cy.toolbar(createToolbar());
            }
        },

        style: [
            {
                selector: 'node',
                css: {
                    'shape': 'roundrectangle',
                    'content': 'data(short_name)',
                    'background-color': 'data(color)',
                    'text-valign': 'center',
                    'text-halign': 'center',
                    'width':default_node_width,
                    'height':default_node_height,
                    'font-size':default_font_size,
                    'border-width':'1',
                    'border-color': '#999'
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
                    'content': 'data(short_name)',
                    'line-color': default_edge_colour,
                    'source-arrow-color': default_edge_colour,
                    'target-arrow-color': default_edge_colour,
                    'font-size':default_font_size
                }
            },
            {
                selector: ':selected',
                css: {
                    'background-color': 'data[\'color\'])',
                    'line-color': default_selected_colour,
                    //'width': '5',
                    //'line-style': 'dotted',
                    'target-arrow-color': default_selected_colour,
                    'source-arrow-color': default_selected_colour,
                    'border-width':'7',
                    'border-color': default_selected_colour,//'#999',
                    'background-blacken' : '0.3'
                }
            }
        ],

        elements: (action == 'new' || (typeof workflow === 'undefined') || workflow == {})? {"nodes":[], "edges":[]} : workflow['elements'],
        layout: {
            name: 'preset',
            padding: 5
        },

        autolock: (action == "show")? true : false,

        autoungrabify: (action == "show")? true : false,

        autounselectify: (action == "show")? true : false,

        //boxSelectionEnabled: (action == "show")? false : true,

        selectionType: 'single',

        maxZoom: 1.5,
        minZoom: 0.5,
        zoomEnabled: false

    });

//    alert(JSON.stringify(window.cy.json()));

    cy.on('click', function(event){
        // cyTarget holds a reference to the originator
        // of the event (core or element)
        var evtTarget = event.cyTarget;
        if( evtTarget === cy ){
            // Tap on a background
            closeWorkflowPropertyEditor();
        } else {
            var element = cy.getElementById(evtTarget.id()); // Get wf element with this id
            //closeWorkflowPropertyEditor();
            updateJSONDump();
            openWorkflowPropertyEditor(element);
            var node_info = evtTarget.data();
            $('#node-info').val(JSON.stringify(node_info))
            $('#node-id').val(evtTarget.id())
            if (action == 'show' && evtTarget.isNode()) {
                var modal_url = '/workflow/read_training?workflow_id=' + $('#workflow-id').val() + '&node_id=' + evtTarget.id();
                /*$('#modal_container').load('/workflow_modal.html');*/
                console.log(modal_url);
                $("#myModal").modal({
                    remote: modal_url,
                    show: true
                });
            }
        }
    });

    //cy.on('select', function(event){
    //});

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


$( document ).on('click', '.tool-item, .selected-tool', function(event) {
    // For 'select-mode-tool' leave the selected element as is, for all other tools
    // on the toolbar - remove the selection
    if ( $(event.target).attr('class').indexOf("select-mode-tool") < 0 ){
        cy.$(':selected').unselect();
        closeWorkflowPropertyEditor();
    }
});

//$( document ).on('click', '.clear-selection-tool', function(event) {
//$( document ).on('click', '.clear-selection-tool', function(event) {
//    //alert('you clicked a '+$(event.target).attr('class')+' element');
//    // Firstly deselect all selected wf elements
//    // then let the toolbar handle any subsequent clicks on the graph, if any
//    $(event.target).unbind('click');
//    $(event.target).removeClass('selected-tool');
//    event.stopPropagation();
//    cy.$(':selected').unselect();
//    closeWorkflowPropertyEditor();
//    return false;
//});

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

function openWorkflowPropertyEditor(element) {
    $("#no_workflow_element_selected").hide();
    if (!(element)) {
        /*If not set, load selected*/
        var current_selected = cy.$(':selected').first();
    } else {
        var current_selected = element;
    }

    if (current_selected.isEdge()) {
        $('#element-name').val(current_selected.data('name'));
        $("#element-type").html("Link");

        $("#element-name").show();
        $("label").find("[for='element-name']").show();

        // Hide all the fields where we are not allowing modification for links/edges
        $("#element-color").hide();

        $("#element-description").hide();
        $('label[for="element-description"]').hide();

        $("#element-topic").hide();
        $('label[for="element-topic"]').hide();
    }
    else{
        $('#element-name').val(current_selected.data('name'));

        if (current_selected.data('color')){
            $('select[name="colorpicker-longlist"]').simplecolorpicker('selectColor', current_selected.data('color'));
        } else {
            $('select[name="colorpicker-longlist"]').simplecolorpicker('selectColor', default_node_colour);
        }

        $('#element-description').val(current_selected.data('description'))
        $('#element-topic').val(current_selected.data('topic'));
        $('#training-materials').val(current_selected.data('materials'));
        $("#element-type").html("Node");

        // Show all field allowed to be modified
        $("#element-name").show();
        $("#element-color").show();
        $("#element-description").show();
        $("#element-topic").show();

        $('label[for="element-name"]').show();
        $('label[for="element-color"]').show();
        $('label[for="element-description"]').show();
        $('label[for="element-topic"]').show();

    }

    $("#workflow_element_info").show();
}

function saveWorkflowElementProperties() {
    $('#element-name').val('');
    $('#element-color').val('');
    $('#element-topic').val('');
    $('#element-description').val('');
    openWorkflowPropertyEditor();
}

function closeWorkflowPropertyEditor() {
    $("#workflow_element_info").hide();
    $("#no_workflow_element_selected").show();
}

function updateWorkflowElement() {
    var current_selected = cy.$(':selected').first();

    if (current_selected.isEdge()) {
        current_selected.data('name',$('#element-name').val());
        current_selected.data('short_name',truncateString($('#element-name').val(), 20));
    } else {
        /* set model properties */
        current_selected.data('name',$('#element-name').val());
        current_selected.data('short_name',truncateString($('#element-name').val(), 30));
        current_selected.data('color',$('#colorpicker-longlist').val());
        current_selected.data('description',$('#element-description').val());
        current_selected.data('topic',$('#element-topic').val());

        /* apply properties to image and update output JSON */
        propogateStyle(current_selected);
        updateJSONDump();
    }
}

function propogateStyle(current_selected) {
    /* Set styles */
    current_selected.data('content', current_selected.data('short_name'));
    current_selected.style('background-color', current_selected.data('color'));
}


function updateJSONDump() {
    //alert(JSON.stringify(window.cy.json()));
    $("#dialog-div").val(JSON.stringify(window.cy.json()));
    $("#dialog-div").text(JSON.stringify(window.cy.json()));
}

function clearSelectedWorkflowElements() {
    //Deselect all selected wf elements
    cy.$(':selected').unselect();
}

//#region node tools

function addTrainingMaterial(e) {
    if (!e.data.canPerform(e, addTrainingMaterial)) {
        return;
    }
    loadTrainingMaterialModal(e)
}

function loadTrainingMaterialModal(e) {
    if (e){
        var evtTarget = e.cyTarget;
    } else {
        var evtTarget = cy.$(':selected').first()
    }
    var node_info = evtTarget.data();
    $('#node-info').val(JSON.stringify(node_info))
    if (action != 'show' && evtTarget.isNode()) {
        $("#myModal").modal({
            remote : '/workflow/edit_training'
        })
    }
}

function addNodeToGraph(e) {

    var evtTarget = e.cyTarget;
    if (!e.data.canPerform(e, addNodeToGraph)) {
        return;
    }
    if (evtTarget === cy) {
        addObject(e, addNodeToGraph);
    }
}

function addChildNodeToNode(e){
    var evtTarget = e.cyTarget;
    if (!e.data.canPerform(e, addChildNodeToNode)) {
        return;
    }
    if (evtTarget.isNode()) {
        evtTarget.unselect();
        var toolIndexes = e.data.data.selectedTool;
        var tool = e.data.data.options.tools[toolIndexes[0]][toolIndexes[1]];
        var object = {
            group: 'nodes',
            data: {
                name: tool.options.text,
                color: default_node_colour,
                parent: evtTarget.id(),
                materials: []
            },
            position: {
                x: e.cyPosition.x,
                y: e.cyPosition.y
            },
            selected: true
        }
        var newChild = e.cy.add(object)
        newChild.select();
        evtTarget.unselect();
        /* newChild is selected at this point in execution - but some code further on resets the parent to being
        selected! Need to find out where this is and stop it. Or maybe emergency exit execution :S
        Proof - uncomment:
            console.log(newChild.selected())
        */
        newChild.addClass('tool-node').addClass(tool.options.clazz);
        updateJSONDump();
    }
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
            name: tool.options.text,
            color: default_node_colour,
            materials: []
        },
        position: {
            x: e.cyPosition.x,
            y: e.cyPosition.y
        },
        selected: true
    }
    e.cy.add(object).addClass('tool-node').addClass(tool.options.clazz);
    openWorkflowPropertyEditor();
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
            //selected: true
        });

        src.removeClass('selected-node');
        src = undefined;
        openWorkflowPropertyEditor(tgt);
    } else {
        src = e.cyTarget;
        src.addClass('selected-node');
        openWorkflowPropertyEditor(src);
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
    closeWorkflowPropertyEditor();
    updateJSONDump();
}
//#endregion

function performClearSelection(e) {
    // Do not really need to clear selection (as this is already
    // handled when the user clicked on toolbar), but just in case
    //cy.$(':selected').unselect();
    // Close property editor as there won't be any elements selected
    //closeWorkflowPropertyEditor();
}

//#region Clear tool selection
function performClearSelectedTool(e) {
    //cy.remove(e.cyTarget);
}
//#endregion

/////////////////////////////////////////////////////

//$('#show-wf').click(function(){
//    updateJSONDump();
//});

function truncateString(str, length) {
    return str.length > length ? str.substring(0, length - 3) + '...' : str
}

var doit;
$( window ).resize(function() {
    doit = setTimeout(repositionToolbar, 200);
});

function repositionToolbar(){
    // This is the best I could do - destroy the old toolbar and
    // recreate a new one that will be positioned correctly on the
    // resized page
    if (action!='show'){
        $(".cy-overall-toolbar").remove();
        cy.toolbar(createToolbar());
    }
}

function createToolbar() {

    return {
        toolbarClass: "cy-overall-toolbar",
        tools: [
            [
                {
                    icon: 'fa fa-location-arrow select-mode-tool',
                    event: ['tap'],
                    selector: 'edge,node',
                    bubbleToCore: false,
                    select: true,
                    tooltip: 'Select mode',
                    action: []
                }
            ],
            [
                {
                    icon: 'fa fa-search-plus',
                    event: ['tap'],
                    selector: 'cy',
                    options: {
                        cy: {
                            zoom: 0.2,
                            minZoom: 0.1,
                            maxZoom: 2,
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
                            zoom: -0.2,
                            minZoom: 0.1,
                            maxZoom: 2,
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
                    tooltip: 'Pan down',
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
                    bubbleToCore: true,
                    tooltip: 'Add node',
                    action: [addNodeToGraph]
                }
            ],
            [
                {
                    icon: 'fa fa-plus-square',
                    event: ['click'],
                    selector: 'node',
                    options: {
                        clazz: 'node-person'
                    },
                    bubbleToCore: true,
                    tooltip: 'Add child node',
                    action: [addChildNodeToNode]
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
                    tooltip: 'Remove node or link',
                    action: [performRemove]
                }
            ],
            [
                 {
                    icon: 'fa fa-book',
                    event: ['tap'],
                    selector: 'node',
                    bubbleToCore: false,
                    tooltip: 'Associate Materials to a Node',
                    action: [addTrainingMaterial]
                }

            ]


            //,
            //[
            //    {
            //        icon: 'fa fa-eraser clear-selection-tool',
            //        event: ['tap'],
            //        selector: '',
            //        bubbleToCore: false,
            //        tooltip: 'Clear selection',
            //        action: [performClearSelection]
            //    }
            //]
        ],
        appendTools: false
    };
}

function isWorkflowEmptyConfirm() {
    if ($('#field-name').val() == ""){
        alert('You have to specify the name of the workflow.');
        return false;
    }
    if ((typeof window.cy.nodes() === 'undefined') || window.cy.nodes().length == 0){
        confirm('You cannot save an empty workflow. Add at least one node.');
        return false;
    }
    return true;
}

