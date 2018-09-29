require.config({
    baseUrl: "/static",
    paths: {
        jquery: "js/jquery",
        bootstrap: "js/bootstrap.min",
        popper: "js/popper.min",
        },
    shim: {
    'bootstrap': {
        deps: ['jquery']
    }
  }

});

require([ 'bootstrap']);
