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
                                                             tooltip: 'Zoom In',
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
                                                             tooltip: 'Zoom Out',
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
                                                             tooltip: 'Pan Right',
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
                                                             tooltip: 'Pan Left',
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
                                                             tooltip: 'Pan Up',
                                                             action: [performPanUp]
                                                             }
                                                             ],
                                                            [
                                                             {
                                                             icon: 'fa fa-plus',
                                                             event: ['tap'],
                                                             selector: 'cy',
                                                             options: {
                                                             clazz: 'node-person'
                                                             },
                                                             bubbleToCore: false,
                                                             tooltip: 'Add node',
                                                             action: [addPersonToGraph]
                                                             },
                                                             {
                                                             icon: 'fa fa-home',
                                                             event: ['tap'],
                                                             selector: 'cy',
                                                             options: {
                                                             clazz: 'node-home'
                                                             },
                                                             bubbleToCore: false,
                                                             tooltip: 'House',
                                                             action: [addHouseToGraph]
                                                             },
                                                             {
                                                             icon: 'fa fa-building-o',
                                                             event: ['tap'],
                                                             selector: 'cy',
                                                             options: {
                                                             clazz: 'node-business'
                                                             },
                                                             bubbleToCore: false,
                                                             tooltip: 'Business',
                                                             action: [addBusinessToGraph]
                                                             },
                                                             {
                                                             icon: 'fa fa-truck',
                                                             event: ['tap'],
                                                             selector: 'cy',
                                                             options: {
                                                             clazz: 'node-automobile'
                                                             },
                                                             bubbleToCore: false,
                                                             tooltip: 'Automobile',
                                                             action: [addAutoToGraph]
                                                             }
                                                             ],
                                                            [
                                                             {
                                                             icon: 'fa fa-link',
                                                             event: ['tap'],
                                                             selector: 'node',
                                                             bubbleToCore: false,
                                                             tooltip: 'Link',
                                                             action: [performLink]
                                                             }
                                                             ],
                                                            [
                                                             {
                                                             icon: 'fa fa-trash-o',
                                                             event: ['tap'],
                                                             selector: 'edge,node',
                                                             bubbleToCore: false,
                                                             tooltip: 'Remove Node/Edge',
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
                                                 'background-color': 'green',
                                                 'line-color': 'green',
                                                 'target-arrow-color': 'green',
                                                 'source-arrow-color': 'green'
                                                 }
                                                 }
                                                 ],
                                         
                                         elements: {
                                         nodes: [
                                                 { data: { id: 'a', name: 'a' } },
                                                 { data: { id: 'b', name: 'b' } },
                                                 { data: { id: 'c', name: 'c' } }
                                                 ],
                                         edges: [
                                                 { data: { source: 'a', target: 'b' } }
                                                 ]
                                         },
                                         layout: {
                                         name: 'cose',
                                         padding: 5
                                         }
                                         
                                         });
          
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
          });
