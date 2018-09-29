define('test/notification-list', ['exports', 'test/app'], function (exports, _app) {
  'use strict';

  Object.defineProperty(exports, "__esModule", {
    value: true
  });


  _app.default.NotificationsManager = Ember.Object.create({

    notifications: Ember.A(),
    pendingRemovals: [],

    show: function show(message, type, link) {
      var notification = {
        message: message || '',
        type: type || '',
        link: link
      };

      this.notifications.pushObject(notification);

      return notification;
    },

    remove: function remove(notification) {

      // ensure that the list of current notifications is empty before hiding them, this keeps each
      // notification in the same place vertically until it is visually off of the screen
      // to disable this, just call this.notifications.removeObject(notification) instead

      this.pendingRemovals.push(notification);
      if (this.pendingRemovals.length === this.notifications.length) {

        this.pendingRemovals.forEach(function (n) {

          this.notifications.removeObject(n);
        }.bind(this));

        this.pendingRemovals = [];
      }
    }
  });

  _app.default.NotificationListComponent = Ember.Component.extend({

    classNames: ['aurora-notifications'],
    tagName: 'ul',

    notifications: _app.default.NotificationsManager.get('notifications'),

    setup: function () {
      if (typeof ReactRailsUJS !== 'undefined') {
        return;
      }

      var flashes = Ember.$('.flash-holder');
      var message = void 0,
          type = void 0;
      flashes.each(function (_, item) {
        message = Ember.$(item).data('message');
        type = Ember.$(item).data('type');
        _app.default.NotificationsManager.show(message, type);
      });
    }.on('didInsertElement')
  });

  exports.default = _app.default.NotificationListComponent;
});