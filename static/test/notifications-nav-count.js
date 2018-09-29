define('test/notifications-nav-count', ['exports'], function (exports) {
  'use strict';

  Object.defineProperty(exports, "__esModule", {
    value: true
  });


  var MAX_NOTIFICATION_COUNT = 99;

  exports.default = Ember.Component.extend({
    tagName: 'span',
    classNames: ['notification-count'],

    displayCount: function () {
      var count = this.get('pendingNotificationsCount');
      if (count > MAX_NOTIFICATION_COUNT) {
        count = '+99';
      }
      return count;
    }.property('pendingNotificationsCount')
  });
});