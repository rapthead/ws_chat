$(function() {
    $('form').parsley();
    $('select').select2();
    $('select').closest('form').on('reset', function(event) {
        $(event.target).find("select").select2('val', '')
    });

    // csrf
    Backbone.$.ajaxSetup({
        headers: {'X-CSRFToken': Cookies.get('csrftoken')}
    });

    var Tag = Backbone.Model.extend({
        urlRoot: api_root + 'tag',
        idAttribute: 'pk'
    });
    var TagCollection = Backbone.Collection.extend({
        url: api_root + 'tag',
        model: Tag,
    });

    var Message = Backbone.Model.extend({
        urlRoot: api_root + 'message',
        idAttribute: 'pk',
        parse: function(response){
            response.time = new Date(response.time);
            response.tags = new TagCollection(response.tags);
            return response;
        },
        sync: function (method, model, options) {
            tags = model.get('tags');
            if (tags instanceof Backbone.Collection) {
                model.set('tags', tags.map(function(tag) { return tag.id }));
            }
            return Backbone.sync.call(this, method, model, options);
        }
    });

    var MessageCollection = Backbone.Collection.extend({
        url: api_root + 'message',
        model: Message,

        byTag: function (tag) {
            filtered = this.filter(function (item) {
                item_tags = item.get('tags');
                return item_tags.get(tag);
            });
            return new MessageCollection(filtered);
        }
    });

    var MessageView = Backbone.View.extend({
        tagName: 'li',
        template: _.template($('#bb-one-message-template').html()),
        events: {
            "change select": "change_tags",
        },
        change_tags: function() {
            var that = this;
            select_data = this.$tag_select.select2('data')
            new_tag_raw = _.find(select_data, function(tag_raw) { return tag_raw.isNew })
            if(new_tag_raw) {
                new_tag = new Tag({title: new_tag_raw.text})
                this.all_tags.push(new_tag);
                new_tag.save(null, {
                    success: function(model, response) {
                        that.model.get('tags').push(model);
                        that.model.save(null, {
                            success: function() {
                                that.render();
                            }
                        });
                    }
                });
            }
            else {
                that.model.set('tags', that.$tag_select.val() || []);
                that.model.save(null, {
                    success: function() {
                        that.render();
                    }
                });
            }
        },
        initialize: function(options) {
            this.all_tags = options.all_tags;
            this.listenTo(this.all_tags, 'change', this.render);
        },
        render: function() {
            if (this.$tag_select) {
                this.$tag_select.select2('destroy');
            }
            this.$el.html(this.template({item: this.model, all_tags: this.all_tags}));
            this.$tag_select = this.$el.find('select');
            this.$tag_select.select2({
                placeholder: 'Теги',
                tags: true,
                createTag: function (tag) {
                    return {
                        id: tag.term,
                        text: tag.term,
                        isNew : true
                    };
                }
            });
            return this;
        }
    });

    var MessageListView = Backbone.View.extend({
        el: '.bb-message-list',
        collection: new MessageCollection(),
        all_tags: new TagCollection(),

        initialize: function() {
            var that = this;
            $.when(this.collection.fetch(), this.all_tags.fetch()).then(function () {
                that.render();
            });

            this.$list_container = this.$el.find('.bb-message-list-inner');
            this.$spinner = this.$el.find('.bb-spinner');
        },

        addMessage: function(newMessage) {
            this.collection.push(newMessage);
            this.$list_container.append(new MessageView({model: newMessage, all_tags: this.all_tags}).render().el);
        },

        filterByTagArray: function(tags) {
            filtered_collection = this.collection;
            _.each(tags, function(tag) {
                filtered_collection = filtered_collection.byTag(tag);
            });
            this.render(filtered_collection);
        },

        render: function(result_collection) {
            var that = this;

            if (!result_collection) {
                result_collection = this.collection;
            }

            this.$list_container.empty();
            result_collection.each(function(model) {
                that.addMessage(model);
            });

            this.$spinner.hide()
            return this;
        }
    });
    messageList = new MessageListView();

    var MessageFilterView = Backbone.View.extend({
        el: '.bb-filter',
        // model: new TagCollection(),
        template: _.template($('#bb-filter-template').html()),
        message_list: messageList,
        events: {
            "change select": 'evalFilter'
        },
        initialize: function() {
            this.model = this.message_list.all_tags;
            this.render();
            this.listenTo(this.model, 'change', this.render);
            this.listenTo(this.model, 'sync', this.render);
        },
        render: function() {
            this.$el.html(this.template({all_tags: this.model, selected_tags: new TagCollection()}));
            this.$el.find('select').select2({
                placeholder: 'Фильтр'
            });
            this.$el.show();
        },
        evalFilter: function(event) {
            this.message_list.filterByTagArray($(event.target).val());
        }
    });
    messageFilter = new MessageFilterView();

    var NewMessageView = Backbone.View.extend({
        el: '.bb-new-message-form',
        events: {
            "submit form": 'addMessage'
        },
        message_list: messageList,

        addMessage: function(event) {
            var that = this;

            event.preventDefault();

            var data = {};
            $(event.target).find(':input').each(function(i, obj){
                if ($(obj).attr('name'))
                    data[$(obj).attr('name')] = $(obj).val();
            }); 

            $(event.target).parsley().reset();
            event.target.reset();

            var newMessage = new Message();

            newMessage.set({message: data['message'], tags: data['tags'] || []});
            newMessage.save(null, {
                success: function(model, response) {
                    that.message_list.addMessage(model);
                }
            });
        }
    });
    newMessageList = new NewMessageView();
});
