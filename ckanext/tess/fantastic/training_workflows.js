    var graph = new joint.dia.Graph;
    var paper = new joint.dia.Paper({ el: $('#paper'), width: 650, height: 400, gridSize: 1, model: graph });

        var x_pos = 80;
        var y_pos = 80;
        // Create a custom element.
        // ------------------------

   joint.shapes.html = {};
   joint.shapes.html.Element = joint.shapes.basic.Rect.extend({
    defaults: joint.util.deepSupplement({
        type: 'html.Element',
            attrs: {
                rect: { stroke: 'none', 'fill-opacity': 0}
            }
        }, joint.shapes.basic.Rect.prototype.defaults)
    });

        // Create a custom view for that element that displays an HTML div above it.
        // -------------------------------------------------------------------------

    joint.shapes.html.ElementView = joint.dia.ElementView.extend({
        template: [
            '<div class="html-element">',
                '<button class="delete icon-remove"></button>',
                '<button class="clone icon-copy"></button>',
                '<input type="text" value="Stage Name" />',
                '<span></span>', '<br/>',
                '<select><option>--</option><option>Analysis</option><option>Visualization</option>' +
                '<option>-- Chromatogram Visualization</option><option>-- Map Drawing</option><option>-- Microarray Data Rendering</option>' +
                '<option>Deposition</option>' +
                '<option>Query and Retrieval</option><option>Utility Operation</option>',
                '</select>',
                '<input type="text" value="Description" />',
                '</div>'
                ].join(''),

            initialize: function() {
                _.bindAll(this, 'updateBox');
                joint.dia.ElementView.prototype.initialize.apply(this, arguments);

                this.$box = $(_.template(this.template)());
                // Prevent paper from handling pointerdown.
                this.$box.find('input,select').on('mousedown click', function(evt) { evt.stopPropagation(); });
                // This is an example of reacting on the input change and storing the input data in the cell model.
                this.$box.find('input').on('change', _.bind(function(evt) {
                    this.model.set('input', $(evt.target).val());
                }, this));
                this.$box.find('select').on('change', _.bind(function(evt) {
                    this.model.set('select', $(evt.target).val());
                }, this));

                this.$box.find('select').val(this.model.get('select'));

                this.$box.find('.delete').on('click', _.bind(this.model.remove, this.model));
                this.$box.find('.clone').on('click', _.bind(this.cloneBox, this));

                // Update the box position whenever the underlying model changes.
                this.model.on('change', this.updateBox, this);
                // Remove the box when the model gets removed from the graph.
                this.model.on('remove', this.removeBox, this);

                this.updateBox();
            },
            render: function() {
                joint.dia.ElementView.prototype.render.apply(this, arguments);
                this.paper.$el.prepend(this.$box);
                this.updateBox();
                return this;
            },
            updateBox: function() {
                // Set the position and dimension of the box so that it covers the JointJS element.
                var bbox = this.model.getBBox();
                // Example of updating the HTML with a data stored in the cell model.
                this.$box.find('label').text(this.model.get('label'));
                this.$box.find('span').text(this.model.get('select'));
                this.$box.css({ width: bbox.width, height: bbox.height, left: bbox.x, top: bbox.y, transform: 'rotate(' + (this.model.get('angle') || 0) + 'deg)' });
            },
            removeBox: function(evt) {
                console.log(this.$box);
                this.$box.remove();
            },
            cloneBox: function(evt, model) {
                var clone = this.model.clone('options.deep === true').translate(20,20);
                clone.toFront(3);
                console.log('maybe cloned ' + JSON.stringify(clone));
                graph.addCells([clone]);
                this.$box.clone();
            }
        });

    /*
    Uncomment this for an inventory kind of thing
    var legend_graph = new joint.dia.Graph;
    var legend_paper = new joint.dia.Paper({ el: $('#legend'), width: 220, height: 400, gridSize: 1, model: legend_graph });
    var inventory1 = new joint.shapes.html.Element({ position: { x: 0, y: 100}, size: { width: 100, height: 100 }, select: 'operation' });
    legend_graph.addCell(inventory1);*/