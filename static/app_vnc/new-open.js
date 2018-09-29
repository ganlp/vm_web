define(['exports','js/app'], function (exports, _app) {
  'use strict';
  Object.defineProperty(exports, "__esModule", {
    value: true
  });


  var DEFAULT_WINDOW_WIDTH = 1034,
      DEFAULT_WINDOW_HEIGHT = 848,
      DEFAULT_WINDOW_TOP_OFFSET = 0;
  exports.default = jQuery.extend(_app.default,{
    windowRef: null,
    show: function show(url) {
      var w = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : DEFAULT_WINDOW_WIDTH;
      var h = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : DEFAULT_WINDOW_HEIGHT;
      var tOffset = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : DEFAULT_WINDOW_TOP_OFFSET;
      var prefix = arguments.length > 4 && arguments[4] !== undefined ? arguments[4] : 'console-popup';
      if (!url) {
        return;
      }
      if (this.multipleWindows || this.windowRef === null || this.windowRef.closed) {
        var screenWidth = screen.availWidth;
        var width = Math.min(w, screenWidth);
        var height = Math.min(h, screen.availHeight);
        var top = tOffset;
        var left = (screenWidth - width) / 2;
        var winId = prefix + '-' + new Date().getTime();
        var windowRef = void 0;

        try {
          windowRef = window.open(url, winId, 'height=' + height + ',width=' + width + ',left=' + left + ',top=' + top);
          this.windowRef = windowRef
        } catch (error) {
          console.log(error)
        }
      } else {
        this.windowRef.focus();
      }
    }
  });
});