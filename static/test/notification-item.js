define('test/notification-item', ['exports', 'test/app'], function (exports, _app) {
  'use strict';

  Object.defineProperty(exports, "__esModule", {
    value: true
  });


  var TIMEOUT_HALF_TIME = 2;

  exports.default = _app.default.NotificationItemComponent = Ember.Component.extend({

    HIDE_DELAY: 4000,

    isHiding: false,

    tagName: 'li',
    classNames: ['item'],
    classNameBindings: ['typeClass'],

    typeClass: function () {
      return this.get('item.type');
    }.property('item.type'),

    startHideTimer: function startHideTimer(halfTime) {
      this.hideTimeout = window.setTimeout(Ember.run.bind(this, this.hide), this.HIDE_DELAY / (halfTime ? TIMEOUT_HALF_TIME : 1));
    },

    show: function () {
      Ember.run.next(Ember.run.bind(this, function () {
        this.$().addClass('show');
        this.startHideTimer();
      }));
    }.on('didInsertElement'),

    hide: function hide() {
      var item = this.$();
      if (item) {
        item.removeClass('show').one('transitionend webkitTransitionEnd', Ember.run.bind(this, function () {
          item.off('transitionend webkitTransitionEnd');
          _app.default.NotificationsManager.remove(this.get('item'));
        }));
      }
      this.isHiding = true;
    },

    mouseEnter: function mouseEnter() {
      window.clearTimeout(this.hideTimeout);
    },

    mouseLeave: function mouseLeave() {
      if (!this.isHiding) {
        this.startHideTimer(true);
      }
    },

    click: function click() {
      this.hide();
      window.clearTimeout(this.hideTimeout);
    }

  });
});